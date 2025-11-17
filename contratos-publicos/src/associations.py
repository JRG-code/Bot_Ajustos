"""
Módulo de Associações Pessoa-Empresa
Permite associar pessoas (donos, sócios, políticos) a empresas
para detectar conflitos de interesse
"""

import logging
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AssociationsManager:
    """Gestor de associações entre pessoas e empresas"""

    def __init__(self, db_manager):
        """
        Inicializa o gestor de associações

        Args:
            db_manager: Instância do DatabaseManager
        """
        self.db = db_manager
        self._criar_tabelas()

    def _criar_tabelas(self):
        """Cria tabelas para associações"""
        cursor = self.db.connection.cursor()

        try:
            # Tabela de pessoas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    cargo_politico TEXT,
                    partido TEXT,
                    funcao_atual TEXT,
                    notas TEXT,
                    data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de associações pessoa-empresa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS associacoes_pessoa_empresa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pessoa_id INTEGER,
                    empresa_nome TEXT NOT NULL,
                    empresa_nif TEXT,
                    tipo_relacao TEXT CHECK(tipo_relacao IN (
                        'dono', 'socio', 'gerente', 'administrador',
                        'familiar', 'conselheiro', 'outro'
                    )),
                    percentagem_participacao REAL,
                    data_inicio DATE,
                    data_fim DATE,
                    ativo BOOLEAN DEFAULT 1,
                    fonte TEXT,
                    notas TEXT,
                    data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
                )
            """)

            # Tabela de cargos políticos históricos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cargos_politicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pessoa_id INTEGER,
                    cargo TEXT NOT NULL,
                    entidade TEXT,
                    partido TEXT,
                    data_inicio DATE,
                    data_fim DATE,
                    ativo BOOLEAN DEFAULT 1,
                    data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
                )
            """)

            # Tabela de conflitos de interesse detectados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conflitos_interesse (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pessoa_id INTEGER,
                    empresa_nome TEXT,
                    id_contrato TEXT,
                    tipo_conflito TEXT,
                    descricao TEXT,
                    gravidade TEXT CHECK(gravidade IN ('baixa', 'media', 'alta', 'critica')),
                    verificado BOOLEAN DEFAULT 0,
                    data_detecao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id),
                    FOREIGN KEY (id_contrato) REFERENCES contratos(id_contrato)
                )
            """)

            # Índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pessoas_nome ON pessoas(nome)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_associacoes_pessoa ON associacoes_pessoa_empresa(pessoa_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_associacoes_empresa ON associacoes_pessoa_empresa(empresa_nome)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conflitos_pessoa ON conflitos_interesse(pessoa_id)")

            self.db.connection.commit()
            logger.info("Tabelas de associações criadas/verificadas")

        except sqlite3.Error as e:
            logger.error(f"Erro ao criar tabelas de associações: {e}")
            raise

    # ==================== GESTÃO DE PESSOAS ====================

    def adicionar_pessoa(self, nome: str, cargo_politico: str = '',
                        partido: str = '', funcao_atual: str = '',
                        notas: str = '') -> int:
        """
        Adiciona uma pessoa

        Args:
            nome: Nome completo
            cargo_politico: Cargo político atual
            partido: Partido político
            funcao_atual: Função atual
            notas: Notas adicionais

        Returns:
            ID da pessoa
        """
        cursor = self.db.connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO pessoas (nome, cargo_politico, partido, funcao_atual, notas)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, cargo_politico, partido, funcao_atual, notas))

            self.db.connection.commit()
            pessoa_id = cursor.lastrowid

            logger.info(f"Pessoa '{nome}' adicionada com ID {pessoa_id}")
            return pessoa_id

        except sqlite3.IntegrityError:
            # Já existe, retornar ID
            cursor.execute("SELECT id FROM pessoas WHERE nome = ?", (nome,))
            row = cursor.fetchone()
            if row:
                logger.debug(f"Pessoa '{nome}' já existe com ID {row['id']}")
                return row['id']
            raise

    def listar_pessoas(self) -> List[Dict[str, Any]]:
        """Lista todas as pessoas"""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM pessoas ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

    def obter_pessoa(self, pessoa_id: int) -> Optional[Dict[str, Any]]:
        """Obtém uma pessoa pelo ID"""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM pessoas WHERE id = ?", (pessoa_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def pesquisar_pessoa(self, nome: str) -> List[Dict[str, Any]]:
        """Pesquisa pessoas por nome (parcial)"""
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT * FROM pessoas
            WHERE nome LIKE ?
            ORDER BY nome
        """, (f"%{nome}%",))
        return [dict(row) for row in cursor.fetchall()]

    # ==================== ASSOCIAÇÕES PESSOA-EMPRESA ====================

    def associar_pessoa_empresa(self, pessoa_id: int, empresa_nome: str,
                               tipo_relacao: str, empresa_nif: str = '',
                               percentagem: float = 0.0,
                               data_inicio: str = None,
                               data_fim: str = None,
                               fonte: str = '',
                               notas: str = '') -> int:
        """
        Cria associação entre pessoa e empresa

        Args:
            pessoa_id: ID da pessoa
            empresa_nome: Nome da empresa
            tipo_relacao: Tipo (dono, socio, gerente, etc)
            empresa_nif: NIF da empresa (opcional)
            percentagem: % de participação
            data_inicio: Data de início
            data_fim: Data de fim (se não ativo)
            fonte: Fonte da informação
            notas: Notas adicionais

        Returns:
            ID da associação
        """
        cursor = self.db.connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO associacoes_pessoa_empresa
                (pessoa_id, empresa_nome, empresa_nif, tipo_relacao,
                 percentagem_participacao, data_inicio, data_fim, ativo, fonte, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pessoa_id, empresa_nome, empresa_nif, tipo_relacao,
                  percentagem, data_inicio, data_fim,
                  1 if not data_fim else 0, fonte, notas))

            self.db.connection.commit()
            assoc_id = cursor.lastrowid

            logger.info(f"Associação criada: Pessoa {pessoa_id} ↔ {empresa_nome} ({tipo_relacao})")
            return assoc_id

        except sqlite3.Error as e:
            logger.error(f"Erro ao criar associação: {e}")
            raise

    def listar_associacoes_pessoa(self, pessoa_id: int) -> List[Dict[str, Any]]:
        """Lista todas as empresas associadas a uma pessoa"""
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT * FROM associacoes_pessoa_empresa
            WHERE pessoa_id = ?
            ORDER BY ativo DESC, data_inicio DESC
        """, (pessoa_id,))
        return [dict(row) for row in cursor.fetchall()]

    def listar_pessoas_empresa(self, empresa_nome: str) -> List[Dict[str, Any]]:
        """Lista todas as pessoas associadas a uma empresa"""
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT p.*, a.tipo_relacao, a.percentagem_participacao, a.ativo
            FROM pessoas p
            JOIN associacoes_pessoa_empresa a ON p.id = a.pessoa_id
            WHERE a.empresa_nome LIKE ?
            ORDER BY a.ativo DESC, p.nome
        """, (f"%{empresa_nome}%",))
        return [dict(row) for row in cursor.fetchall()]

    # ==================== CARGOS POLÍTICOS ====================

    def adicionar_cargo_politico(self, pessoa_id: int, cargo: str,
                                 entidade: str = '', partido: str = '',
                                 data_inicio: str = None,
                                 data_fim: str = None) -> int:
        """Adiciona cargo político a uma pessoa"""
        cursor = self.db.connection.cursor()

        cursor.execute("""
            INSERT INTO cargos_politicos
            (pessoa_id, cargo, entidade, partido, data_inicio, data_fim, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pessoa_id, cargo, entidade, partido, data_inicio, data_fim,
              1 if not data_fim else 0))

        self.db.connection.commit()
        return cursor.lastrowid

    def listar_cargos_pessoa(self, pessoa_id: int) -> List[Dict[str, Any]]:
        """Lista cargos políticos de uma pessoa"""
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT * FROM cargos_politicos
            WHERE pessoa_id = ?
            ORDER BY ativo DESC, data_inicio DESC
        """, (pessoa_id,))
        return [dict(row) for row in cursor.fetchall()]

    # ==================== PESQUISA EXPANDIDA ====================

    def pesquisar_contratos_por_pessoa(self, nome_pessoa: str) -> Dict[str, Any]:
        """
        Pesquisa contratos associados a uma pessoa

        Inclui:
        - Contratos diretos (pessoa como adjudicante/adjudicatária)
        - Contratos de empresas associadas

        Args:
            nome_pessoa: Nome da pessoa

        Returns:
            Dicionário com contratos diretos e indiretos
        """
        resultado = {
            'pessoa': nome_pessoa,
            'contratos_diretos': [],
            'contratos_empresas': [],
            'empresas_associadas': [],
            'total_contratos': 0,
            'valor_total': 0
        }

        # Procurar pessoa
        pessoas = self.pesquisar_pessoa(nome_pessoa)
        if not pessoas:
            logger.info(f"Pessoa '{nome_pessoa}' não encontrada")
            return resultado

        pessoa = pessoas[0]
        pessoa_id = pessoa['id']

        # 1. Contratos diretos (pessoa no nome)
        contratos_diretos = self.db.pesquisar_contratos({
            'adjudicante': nome_pessoa
        })
        contratos_diretos.extend(self.db.pesquisar_contratos({
            'adjudicataria': nome_pessoa
        }))

        resultado['contratos_diretos'] = contratos_diretos

        # 2. Empresas associadas
        associacoes = self.listar_associacoes_pessoa(pessoa_id)
        empresas = [a['empresa_nome'] for a in associacoes]
        resultado['empresas_associadas'] = empresas

        # 3. Contratos das empresas
        for empresa in empresas:
            contratos_empresa = self.db.pesquisar_contratos({
                'adjudicataria': empresa
            })
            for c in contratos_empresa:
                c['_empresa_associada'] = empresa
                c['_tipo_associacao'] = next(
                    (a['tipo_relacao'] for a in associacoes if a['empresa_nome'] == empresa),
                    'desconhecido'
                )
            resultado['contratos_empresas'].extend(contratos_empresa)

        # Estatísticas
        todos_contratos = resultado['contratos_diretos'] + resultado['contratos_empresas']
        resultado['total_contratos'] = len(todos_contratos)
        resultado['valor_total'] = sum(c.get('valor', 0) for c in todos_contratos)

        logger.info(f"Pessoa '{nome_pessoa}': {resultado['total_contratos']} contratos (€{resultado['valor_total']:,.2f})")
        return resultado

    # ==================== DETECÇÃO DE CONFLITOS ====================

    def detectar_conflitos_interesse(self, pessoa_id: int = None) -> List[Dict[str, Any]]:
        """
        Detecta potenciais conflitos de interesse

        Conflito: Pessoa com cargo político + empresa com contratos públicos

        Args:
            pessoa_id: ID da pessoa (None = todas)

        Returns:
            Lista de conflitos detectados
        """
        conflitos = []

        # Obter pessoas com cargos políticos
        cursor = self.db.connection.cursor()

        if pessoa_id:
            cursor.execute("""
                SELECT DISTINCT p.*, c.cargo, c.entidade
                FROM pessoas p
                JOIN cargos_politicos c ON p.id = c.pessoa_id
                WHERE p.id = ? AND c.ativo = 1
            """, (pessoa_id,))
        else:
            cursor.execute("""
                SELECT DISTINCT p.*, c.cargo, c.entidade
                FROM pessoas p
                JOIN cargos_politicos c ON p.id = c.pessoa_id
                WHERE c.ativo = 1
            """)

        pessoas_politicas = [dict(row) for row in cursor.fetchall()]

        # Para cada pessoa política
        for pessoa in pessoas_politicas:
            # Obter empresas associadas
            associacoes = self.listar_associacoes_pessoa(pessoa['id'])

            for assoc in associacoes:
                if not assoc['ativo']:
                    continue

                empresa = assoc['empresa_nome']

                # Pesquisar contratos da empresa
                contratos = self.db.pesquisar_contratos({
                    'adjudicataria': empresa
                })

                for contrato in contratos:
                    # Verificar se é com entidade pública
                    adjudicante = contrato.get('adjudicante', '').lower()

                    # Palavras-chave de entidades públicas
                    entidades_publicas = [
                        'câmara', 'junta', 'assembleia', 'governo', 'ministério',
                        'instituto', 'agência', 'autarquia', 'município', 'freguesia'
                    ]

                    eh_entidade_publica = any(kw in adjudicante for kw in entidades_publicas)

                    if eh_entidade_publica:
                        # Determinar gravidade
                        gravidade = 'media'

                        # Alta se é cargo alto
                        cargos_altos = ['ministro', 'secretário', 'presidente', 'deputado']
                        if any(cargo in pessoa['cargo'].lower() for cargo in cargos_altos):
                            gravidade = 'alta'

                        # Crítica se é com mesma entidade
                        if pessoa.get('entidade', '').lower() in adjudicante:
                            gravidade = 'critica'

                        conflito = {
                            'tipo': 'cargo_politico_empresa_contratos',
                            'pessoa_id': pessoa['id'],
                            'pessoa_nome': pessoa['nome'],
                            'cargo': pessoa['cargo'],
                            'empresa': empresa,
                            'id_contrato': contrato['id_contrato'],
                            'adjudicante': contrato['adjudicante'],
                            'valor': contrato.get('valor', 0),
                            'gravidade': gravidade,
                            'descricao': f"{pessoa['nome']} ({pessoa['cargo']}) tem {assoc['tipo_relacao']} em {empresa}, que tem contrato com {contrato['adjudicante']}"
                        }

                        conflitos.append(conflito)

                        # Registar na BD
                        self._registar_conflito(conflito)

        logger.info(f"Detectados {len(conflitos)} potenciais conflitos de interesse")
        return conflitos

    def _registar_conflito(self, conflito: Dict[str, Any]):
        """Regista conflito na base de dados"""
        cursor = self.db.connection.cursor()

        # Verificar se já existe
        cursor.execute("""
            SELECT id FROM conflitos_interesse
            WHERE pessoa_id = ? AND id_contrato = ?
        """, (conflito['pessoa_id'], conflito['id_contrato']))

        if cursor.fetchone():
            return  # Já existe

        cursor.execute("""
            INSERT INTO conflitos_interesse
            (pessoa_id, empresa_nome, id_contrato, tipo_conflito, descricao, gravidade)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conflito['pessoa_id'],
            conflito['empresa'],
            conflito['id_contrato'],
            conflito['tipo'],
            conflito['descricao'],
            conflito['gravidade']
        ))

        self.db.connection.commit()

    def listar_conflitos(self, apenas_nao_verificados: bool = True) -> List[Dict[str, Any]]:
        """Lista conflitos de interesse detectados"""
        cursor = self.db.connection.cursor()

        query = """
            SELECT c.*, p.nome as pessoa_nome, p.cargo_politico
            FROM conflitos_interesse c
            JOIN pessoas p ON c.pessoa_id = p.id
        """

        if apenas_nao_verificados:
            query += " WHERE c.verificado = 0"

        query += " ORDER BY c.gravidade DESC, c.data_detecao DESC"

        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    # ==================== IMPORTAÇÃO DE DADOS ====================

    def importar_associacoes_csv(self, csv_path: str) -> int:
        """
        Importa associações de um CSV

        Formato esperado:
        nome_pessoa,cargo_politico,partido,empresa,tipo_relacao,percentagem,fonte

        Returns:
            Número de associações importadas
        """
        import csv

        count = 0

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Adicionar pessoa
                    pessoa_id = self.adicionar_pessoa(
                        nome=row['nome_pessoa'],
                        cargo_politico=row.get('cargo_politico', ''),
                        partido=row.get('partido', '')
                    )

                    # Adicionar associação
                    self.associar_pessoa_empresa(
                        pessoa_id=pessoa_id,
                        empresa_nome=row['empresa'],
                        tipo_relacao=row['tipo_relacao'],
                        percentagem=float(row.get('percentagem', 0)),
                        fonte=row.get('fonte', '')
                    )

                    count += 1

                except Exception as e:
                    logger.error(f"Erro ao importar linha: {e}")
                    continue

        logger.info(f"Importadas {count} associações")
        return count

    # ==================== MÉTODOS AUXILIARES ====================

    def listar_associacoes(self) -> List[Dict[str, Any]]:
        """
        Lista todas as associações pessoa-empresa

        Returns:
            Lista de associações
        """
        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT * FROM associacoes_pessoa_empresa
            ORDER BY data_adicao DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    def obter_pessoa(self, pessoa_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém dados de uma pessoa pelo ID

        Args:
            pessoa_id: ID da pessoa

        Returns:
            Dicionário com dados da pessoa ou None
        """
        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT * FROM pessoas WHERE id = ?
        """, (pessoa_id,))

        row = cursor.fetchone()
        return dict(row) if row else None

    def obter_associacao(self, associacao_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém dados de uma associação pelo ID

        Args:
            associacao_id: ID da associação

        Returns:
            Dicionário com dados da associação ou None
        """
        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT * FROM associacoes_pessoa_empresa WHERE id = ?
        """, (associacao_id,))

        row = cursor.fetchone()
        return dict(row) if row else None
