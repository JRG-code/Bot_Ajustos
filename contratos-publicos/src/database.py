"""
Módulo de Gestão de Base de Dados SQLite
Responsável pela criação e gestão da base de dados de contratos públicos
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor da base de dados SQLite para contratos públicos"""

    def __init__(self, db_path: str = "data/contratos.db"):
        """
        Inicializa o gestor de base de dados

        Args:
            db_path: Caminho para o ficheiro da base de dados
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Estabelece conexão com a base de dados"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Conexão estabelecida com a base de dados: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar à base de dados: {e}")
            raise

    def _create_tables(self):
        """Cria as tabelas necessárias na base de dados"""
        cursor = self.connection.cursor()

        try:
            # Tabela de contratos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contratos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_contrato TEXT UNIQUE NOT NULL,
                    adjudicante TEXT,
                    adjudicante_nif TEXT,
                    adjudicataria TEXT,
                    adjudicataria_nif TEXT,
                    valor REAL,
                    data_contrato DATE,
                    data_publicacao DATE,
                    tipo_contrato TEXT,
                    tipo_procedimento TEXT,
                    descricao TEXT,
                    objeto_contrato TEXT,
                    distrito TEXT,
                    concelho TEXT,
                    cpv TEXT,
                    prazo_execucao INTEGER,
                    link_base TEXT,
                    data_recolha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id_contrato)
                )
            """)

            # Tabela de figuras de interesse (entidades vigiadas)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS figuras_interesse (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    nif TEXT,
                    tipo TEXT CHECK(tipo IN ('pessoa', 'empresa', 'entidade_publica')),
                    cargo_governamental TEXT,
                    partido TEXT,
                    notas TEXT,
                    ativo BOOLEAN DEFAULT 1,
                    data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(nome, nif)
                )
            """)

            # Migração: Adicionar colunas se não existirem (para BDs antigas)
            try:
                cursor.execute("ALTER TABLE figuras_interesse ADD COLUMN cargo_governamental TEXT")
            except sqlite3.OperationalError:
                pass  # Coluna já existe

            try:
                cursor.execute("ALTER TABLE figuras_interesse ADD COLUMN partido TEXT")
            except sqlite3.OperationalError:
                pass  # Coluna já existe

            # Tabela de conexões entre entidades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conexoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entidade_origem_id INTEGER,
                    entidade_destino_id INTEGER,
                    tipo_conexao TEXT,
                    id_contrato_referencia TEXT,
                    descricao TEXT,
                    data_detecao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (entidade_origem_id) REFERENCES figuras_interesse(id),
                    FOREIGN KEY (entidade_destino_id) REFERENCES figuras_interesse(id),
                    FOREIGN KEY (id_contrato_referencia) REFERENCES contratos(id_contrato)
                )
            """)

            # Tabela de alertas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_contrato TEXT,
                    figura_interesse_id INTEGER,
                    tipo_alerta TEXT,
                    mensagem TEXT,
                    lido BOOLEAN DEFAULT 0,
                    data_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_contrato) REFERENCES contratos(id_contrato),
                    FOREIGN KEY (figura_interesse_id) REFERENCES figuras_interesse(id)
                )
            """)

            # Índices para melhorar performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contratos_adjudicante ON contratos(adjudicante)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contratos_adjudicataria ON contratos(adjudicataria)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contratos_data ON contratos(data_contrato)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contratos_valor ON contratos(valor)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contratos_distrito ON contratos(distrito)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contratos_tipo_procedimento ON contratos(tipo_procedimento)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_figuras_nome ON figuras_interesse(nome)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alertas_lido ON alertas(lido)")

            self.connection.commit()
            logger.info("Tabelas criadas/verificadas com sucesso")

        except sqlite3.Error as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise

    # ==================== CONTRATOS ====================

    def inserir_contrato(self, contrato: Dict[str, Any]) -> bool:
        """
        Insere um contrato na base de dados

        Args:
            contrato: Dicionário com os dados do contrato

        Returns:
            True se inserido com sucesso, False se já existe
        """
        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO contratos (
                    id_contrato, adjudicante, adjudicante_nif, adjudicataria,
                    adjudicataria_nif, valor, data_contrato, data_publicacao,
                    tipo_contrato, tipo_procedimento, descricao, objeto_contrato,
                    distrito, concelho, cpv, prazo_execucao, link_base
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contrato.get('id_contrato'),
                contrato.get('adjudicante'),
                contrato.get('adjudicante_nif'),
                contrato.get('adjudicataria'),
                contrato.get('adjudicataria_nif'),
                contrato.get('valor'),
                contrato.get('data_contrato'),
                contrato.get('data_publicacao'),
                contrato.get('tipo_contrato'),
                contrato.get('tipo_procedimento'),
                contrato.get('descricao'),
                contrato.get('objeto_contrato'),
                contrato.get('distrito'),
                contrato.get('concelho'),
                contrato.get('cpv'),
                contrato.get('prazo_execucao'),
                contrato.get('link_base')
            ))
            self.connection.commit()
            logger.debug(f"Contrato {contrato.get('id_contrato')} inserido com sucesso")
            return True

        except sqlite3.IntegrityError:
            logger.debug(f"Contrato {contrato.get('id_contrato')} já existe na base de dados")
            return False
        except sqlite3.Error as e:
            logger.error(f"Erro ao inserir contrato: {e}")
            return False

    def pesquisar_contratos(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Pesquisa contratos com base em filtros

        Args:
            filtros: Dicionário com os filtros de pesquisa
                - distrito: str
                - concelho: str
                - ano_inicio: int
                - ano_fim: int
                - adjudicante: str (LIKE)
                - adjudicataria: str (LIKE)
                - valor_min: float
                - valor_max: float
                - tipo_contrato: str

        Returns:
            Lista de contratos que correspondem aos filtros
        """
        cursor = self.connection.cursor()

        query = "SELECT * FROM contratos WHERE 1=1"
        params = []

        if filtros.get('distrito'):
            query += " AND distrito = ?"
            params.append(filtros['distrito'])

        if filtros.get('concelho'):
            query += " AND concelho = ?"
            params.append(filtros['concelho'])

        if filtros.get('ano_inicio'):
            query += " AND strftime('%Y', data_contrato) >= ?"
            params.append(str(filtros['ano_inicio']))

        if filtros.get('ano_fim'):
            query += " AND strftime('%Y', data_contrato) <= ?"
            params.append(str(filtros['ano_fim']))

        if filtros.get('adjudicante'):
            query += " AND adjudicante LIKE ?"
            params.append(f"%{filtros['adjudicante']}%")

        if filtros.get('adjudicataria'):
            query += " AND adjudicataria LIKE ?"
            params.append(f"%{filtros['adjudicataria']}%")

        if filtros.get('valor_min'):
            query += " AND valor >= ?"
            params.append(filtros['valor_min'])

        if filtros.get('valor_max'):
            query += " AND valor <= ?"
            params.append(filtros['valor_max'])

        if filtros.get('tipo_contrato'):
            query += " AND tipo_contrato = ?"
            params.append(filtros['tipo_contrato'])

        if filtros.get('tipo_procedimento'):
            query += " AND tipo_procedimento = ?"
            params.append(filtros['tipo_procedimento'])

        query += " ORDER BY data_contrato DESC"

        cursor.execute(query, params)
        resultados = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Encontrados {len(resultados)} contratos com os filtros aplicados")
        return resultados

    def obter_contrato_por_id(self, id_contrato: str) -> Optional[Dict[str, Any]]:
        """Obtém um contrato pelo seu ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM contratos WHERE id_contrato = ?", (id_contrato,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # ==================== FIGURAS DE INTERESSE ====================

    def adicionar_figura_interesse(self, nome: str, nif: Optional[str] = None,
                                   tipo: str = 'pessoa', notas: str = '',
                                   cargo_governamental: Optional[str] = None,
                                   partido: Optional[str] = None) -> int:
        """
        Adiciona uma figura de interesse

        Args:
            nome: Nome da entidade
            nif: NIF da entidade (opcional)
            tipo: Tipo da entidade (pessoa, empresa, entidade_publica)
            notas: Notas adicionais
            cargo_governamental: Cargo governamental se aplicável (opcional)
            partido: Partido político se aplicável (opcional)

        Returns:
            ID da figura inserida ou existente
        """
        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO figuras_interesse (nome, nif, tipo, notas, cargo_governamental, partido)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, nif, tipo, notas, cargo_governamental, partido))
            self.connection.commit()
            figura_id = cursor.lastrowid
            logger.info(f"Figura de interesse '{nome}' adicionada com ID {figura_id}")
            return figura_id

        except sqlite3.IntegrityError:
            # Já existe, retorna o ID existente
            cursor.execute("""
                SELECT id FROM figuras_interesse
                WHERE nome = ? AND (nif = ? OR (nif IS NULL AND ? IS NULL))
            """, (nome, nif, nif))
            row = cursor.fetchone()
            if row:
                logger.debug(f"Figura de interesse '{nome}' já existe com ID {row['id']}")
                return row['id']
            raise

    def listar_figuras_interesse(self, apenas_ativas: bool = True) -> List[Dict[str, Any]]:
        """Lista todas as figuras de interesse"""
        cursor = self.connection.cursor()

        query = "SELECT * FROM figuras_interesse"
        if apenas_ativas:
            query += " WHERE ativo = 1"
        query += " ORDER BY nome"

        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def desativar_figura_interesse(self, figura_id: int) -> bool:
        """Desativa uma figura de interesse"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE figuras_interesse SET ativo = 0 WHERE id = ?
            """, (figura_id,))
            self.connection.commit()
            logger.info(f"Figura de interesse {figura_id} desativada")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erro ao desativar figura: {e}")
            return False

    def pesquisar_contratos_por_figura(self, figura_id: int) -> List[Dict[str, Any]]:
        """
        Pesquisa contratos relacionados com uma figura de interesse

        Args:
            figura_id: ID da figura de interesse

        Returns:
            Lista de contratos relacionados
        """
        cursor = self.connection.cursor()

        # Obter os dados da figura
        cursor.execute("SELECT nome, nif FROM figuras_interesse WHERE id = ?", (figura_id,))
        figura = cursor.fetchone()

        if not figura:
            return []

        nome = figura['nome']
        nif = figura['nif']

        # Pesquisar contratos onde a figura aparece como adjudicante ou adjudicatária
        query = """
            SELECT * FROM contratos
            WHERE adjudicante LIKE ?
               OR adjudicataria LIKE ?
        """
        params = [f"%{nome}%", f"%{nome}%"]

        if nif:
            query += " OR adjudicante_nif = ? OR adjudicataria_nif = ?"
            params.extend([nif, nif])

        query += " ORDER BY data_contrato DESC"

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================== ALERTAS ====================

    def criar_alerta(self, id_contrato: str, figura_interesse_id: int,
                     tipo_alerta: str, mensagem: str) -> int:
        """Cria um novo alerta"""
        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO alertas (id_contrato, figura_interesse_id, tipo_alerta, mensagem)
                VALUES (?, ?, ?, ?)
            """, (id_contrato, figura_interesse_id, tipo_alerta, mensagem))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Erro ao criar alerta: {e}")
            return -1

    def listar_alertas(self, apenas_nao_lidos: bool = True) -> List[Dict[str, Any]]:
        """Lista alertas"""
        cursor = self.connection.cursor()

        query = """
            SELECT a.*, f.nome as figura_nome, c.adjudicante, c.adjudicataria, c.valor
            FROM alertas a
            LEFT JOIN figuras_interesse f ON a.figura_interesse_id = f.id
            LEFT JOIN contratos c ON a.id_contrato = c.id_contrato
        """

        if apenas_nao_lidos:
            query += " WHERE a.lido = 0"

        query += " ORDER BY a.data_alerta DESC"

        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def marcar_alerta_lido(self, alerta_id: int) -> bool:
        """Marca um alerta como lido"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE alertas SET lido = 1 WHERE id = ?", (alerta_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Erro ao marcar alerta como lido: {e}")
            return False

    # ==================== ESTATÍSTICAS ====================

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas da base de dados"""
        cursor = self.connection.cursor()

        stats = {}

        # Total de contratos
        cursor.execute("SELECT COUNT(*) as total FROM contratos")
        stats['total_contratos'] = cursor.fetchone()['total']

        # Total de figuras de interesse
        cursor.execute("SELECT COUNT(*) as total FROM figuras_interesse WHERE ativo = 1")
        stats['total_figuras'] = cursor.fetchone()['total']

        # Total de alertas não lidos
        cursor.execute("SELECT COUNT(*) as total FROM alertas WHERE lido = 0")
        stats['alertas_nao_lidos'] = cursor.fetchone()['total']

        # Valor total dos contratos
        cursor.execute("SELECT SUM(valor) as total FROM contratos WHERE valor IS NOT NULL")
        total_valor = cursor.fetchone()['total']
        stats['valor_total_contratos'] = total_valor if total_valor else 0

        # Contratos por ano
        cursor.execute("""
            SELECT strftime('%Y', data_contrato) as ano, COUNT(*) as total
            FROM contratos
            WHERE data_contrato IS NOT NULL
            GROUP BY ano
            ORDER BY ano DESC
            LIMIT 5
        """)
        stats['contratos_por_ano'] = [dict(row) for row in cursor.fetchall()]

        return stats

    def close(self):
        """Fecha a conexão com a base de dados"""
        if self.connection:
            self.connection.close()
            logger.info("Conexão com a base de dados fechada")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
