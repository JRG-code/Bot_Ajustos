"""
Módulo de Gestão de Figuras de Interesse
Permite criar, gerir e analisar conexões entre entidades
"""

import logging
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class EntitiesManager:
    """Gestor de figuras de interesse e análise de conexões"""

    def __init__(self, db_manager):
        """
        Inicializa o gestor de entidades

        Args:
            db_manager: Instância do DatabaseManager
        """
        self.db = db_manager

    # ==================== GESTÃO DE FIGURAS ====================

    def adicionar_figura(self, nome: str, nif: Optional[str] = None,
                        tipo: str = 'pessoa', notas: str = '') -> int:
        """
        Adiciona uma nova figura de interesse

        Args:
            nome: Nome da entidade
            nif: NIF da entidade
            tipo: Tipo (pessoa, empresa, entidade_publica)
            notas: Notas adicionais

        Returns:
            ID da figura adicionada
        """
        figura_id = self.db.adicionar_figura_interesse(nome, nif, tipo, notas)
        logger.info(f"Figura de interesse adicionada: {nome} (ID: {figura_id})")
        return figura_id

    def remover_figura(self, figura_id: int) -> bool:
        """
        Remove (desativa) uma figura de interesse

        Args:
            figura_id: ID da figura

        Returns:
            True se removida com sucesso
        """
        return self.db.desativar_figura_interesse(figura_id)

    def listar_figuras(self, apenas_ativas: bool = True) -> List[Dict[str, Any]]:
        """Lista todas as figuras de interesse"""
        return self.db.listar_figuras_interesse(apenas_ativas)

    def obter_figura(self, figura_id: int) -> Optional[Dict[str, Any]]:
        """Obtém uma figura pelo ID"""
        figuras = self.db.listar_figuras_interesse(apenas_ativas=False)
        for figura in figuras:
            if figura['id'] == figura_id:
                return figura
        return None

    # ==================== ANÁLISE DE CONTRATOS ====================

    def analisar_contratos_figura(self, figura_id: int) -> Dict[str, Any]:
        """
        Analisa todos os contratos relacionados com uma figura

        Args:
            figura_id: ID da figura de interesse

        Returns:
            Análise detalhada dos contratos
        """
        figura = self.obter_figura(figura_id)
        if not figura:
            logger.error(f"Figura {figura_id} não encontrada")
            return {}

        contratos = self.db.pesquisar_contratos_por_figura(figura_id)

        analise = {
            'figura': figura,
            'total_contratos': len(contratos),
            'valor_total': 0,
            'como_adjudicante': 0,
            'como_adjudicataria': 0,
            'contratos_recentes': [],
            'top_parceiros': [],
            'distribuicao_anos': {},
            'tipos_contrato': {}
        }

        # Contadores
        parceiros_adjudicante = defaultdict(int)
        parceiros_adjudicataria = defaultdict(int)

        for contrato in contratos:
            # Valor total
            if contrato.get('valor'):
                analise['valor_total'] += contrato['valor']

            # Verificar papel da figura
            nome_figura = figura['nome'].lower()
            nif_figura = figura.get('nif', '')

            adjudicante = (contrato.get('adjudicante') or '').lower()
            adjudicataria = (contrato.get('adjudicataria') or '').lower()
            adjudicante_nif = contrato.get('adjudicante_nif', '')
            adjudicataria_nif = contrato.get('adjudicataria_nif', '')

            eh_adjudicante = (nome_figura in adjudicante or
                            (nif_figura and nif_figura == adjudicante_nif))
            eh_adjudicataria = (nome_figura in adjudicataria or
                              (nif_figura and nif_figura == adjudicataria_nif))

            if eh_adjudicante:
                analise['como_adjudicante'] += 1
                if contrato.get('adjudicataria'):
                    parceiros_adjudicataria[contrato['adjudicataria']] += 1

            if eh_adjudicataria:
                analise['como_adjudicataria'] += 1
                if contrato.get('adjudicante'):
                    parceiros_adjudicante[contrato['adjudicante']] += 1

            # Distribuição por ano
            if contrato.get('data_contrato'):
                ano = contrato['data_contrato'][:4]
                analise['distribuicao_anos'][ano] = analise['distribuicao_anos'].get(ano, 0) + 1

            # Tipos de contrato
            tipo = contrato.get('tipo_contrato', 'Não especificado')
            analise['tipos_contrato'][tipo] = analise['tipos_contrato'].get(tipo, 0) + 1

        # Ordenar contratos por data (mais recentes primeiro)
        contratos_ordenados = sorted(
            contratos,
            key=lambda x: x.get('data_contrato', ''),
            reverse=True
        )
        analise['contratos_recentes'] = contratos_ordenados[:10]

        # Top 5 parceiros
        todos_parceiros = {}
        for parceiro, count in parceiros_adjudicante.items():
            todos_parceiros[parceiro] = todos_parceiros.get(parceiro, 0) + count
        for parceiro, count in parceiros_adjudicataria.items():
            todos_parceiros[parceiro] = todos_parceiros.get(parceiro, 0) + count

        analise['top_parceiros'] = sorted(
            todos_parceiros.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        logger.info(f"Análise concluída para figura {figura['nome']}: {analise['total_contratos']} contratos")
        return analise

    # ==================== DETEÇÃO DE CONEXÕES ====================

    def detetar_conexoes(self, figura_id: int, profundidade: int = 2) -> List[Dict[str, Any]]:
        """
        Deteta conexões entre entidades através de contratos

        Args:
            figura_id: ID da figura de origem
            profundidade: Profundidade da análise (quantos níveis de conexão)

        Returns:
            Lista de conexões detectadas
        """
        logger.info(f"A detetar conexões para figura {figura_id} (profundidade: {profundidade})")

        conexoes = []
        visitados = set()
        fila = [(figura_id, 0, None)]  # (figura_id, nivel, contrato_origem)

        while fila:
            atual_id, nivel, contrato_origem = fila.pop(0)

            if atual_id in visitados or nivel >= profundidade:
                continue

            visitados.add(atual_id)

            # Obter contratos da figura atual
            contratos = self.db.pesquisar_contratos_por_figura(atual_id)

            for contrato in contratos:
                # Identificar entidades no contrato
                entidades_no_contrato = self._extrair_entidades_contrato(contrato)

                for entidade_nome, entidade_nif, papel in entidades_no_contrato:
                    # Verificar se já existe como figura de interesse
                    figuras_existentes = self.db.listar_figuras_interesse()

                    entidade_id = None
                    for fig in figuras_existentes:
                        if fig['nome'].lower() == entidade_nome.lower():
                            entidade_id = fig['id']
                            break

                    # Se não for a própria figura e ainda não foi visitada
                    if entidade_id and entidade_id != atual_id and entidade_id not in visitados:
                        conexao = {
                            'origem_id': atual_id,
                            'destino_id': entidade_id,
                            'destino_nome': entidade_nome,
                            'tipo_conexao': papel,
                            'nivel': nivel + 1,
                            'contrato': {
                                'id': contrato.get('id_contrato'),
                                'descricao': contrato.get('descricao'),
                                'valor': contrato.get('valor'),
                                'data': contrato.get('data_contrato')
                            }
                        }
                        conexoes.append(conexao)

                        # Adicionar à fila para exploração
                        if nivel + 1 < profundidade:
                            fila.append((entidade_id, nivel + 1, contrato.get('id_contrato')))

        logger.info(f"Encontradas {len(conexoes)} conexões")
        return conexoes

    def _extrair_entidades_contrato(self, contrato: Dict[str, Any]) -> List[Tuple[str, str, str]]:
        """
        Extrai todas as entidades presentes num contrato

        Returns:
            Lista de tuplos (nome, nif, papel)
        """
        entidades = []

        if contrato.get('adjudicante'):
            entidades.append((
                contrato['adjudicante'],
                contrato.get('adjudicante_nif', ''),
                'adjudicante'
            ))

        if contrato.get('adjudicataria'):
            entidades.append((
                contrato['adjudicataria'],
                contrato.get('adjudicataria_nif', ''),
                'adjudicataria'
            ))

        return entidades

    def criar_grafo_conexoes(self, figura_id: int) -> Dict[str, Any]:
        """
        Cria um grafo de conexões para visualização

        Args:
            figura_id: ID da figura central

        Returns:
            Estrutura de grafo (nodes e edges)
        """
        conexoes = self.detetar_conexoes(figura_id, profundidade=2)

        # Estrutura do grafo
        grafo = {
            'nodes': [],
            'edges': []
        }

        # Set de IDs já adicionados
        nodes_ids = set()

        # Adicionar figura central
        figura_central = self.obter_figura(figura_id)
        if figura_central:
            grafo['nodes'].append({
                'id': figura_id,
                'label': figura_central['nome'],
                'tipo': figura_central.get('tipo', 'pessoa'),
                'central': True
            })
            nodes_ids.add(figura_id)

        # Adicionar conexões
        for conexao in conexoes:
            # Adicionar node destino se ainda não existe
            if conexao['destino_id'] not in nodes_ids:
                figura_destino = self.obter_figura(conexao['destino_id'])
                if figura_destino:
                    grafo['nodes'].append({
                        'id': conexao['destino_id'],
                        'label': figura_destino['nome'],
                        'tipo': figura_destino.get('tipo', 'pessoa'),
                        'central': False
                    })
                    nodes_ids.add(conexao['destino_id'])

            # Adicionar edge
            grafo['edges'].append({
                'from': conexao['origem_id'],
                'to': conexao['destino_id'],
                'label': f"{conexao['tipo_conexao']}\n{conexao['contrato']['id']}",
                'valor': conexao['contrato'].get('valor', 0),
                'nivel': conexao['nivel']
            })

        logger.info(f"Grafo criado: {len(grafo['nodes'])} nós, {len(grafo['edges'])} conexões")
        return grafo

    # ==================== DETEÇÃO AUTOMÁTICA ====================

    def detetar_novas_figuras_interesse(self, contratos: List[Dict[str, Any]],
                                       min_contratos: int = 5,
                                       min_valor_total: float = 100000) -> List[Dict[str, Any]]:
        """
        Analisa contratos para sugerir novas figuras de interesse

        Args:
            contratos: Lista de contratos a analisar
            min_contratos: Número mínimo de contratos para ser sugerido
            min_valor_total: Valor total mínimo de contratos

        Returns:
            Lista de entidades sugeridas
        """
        logger.info("A analisar contratos para detetar potenciais figuras de interesse...")

        # Contadores
        entidades_stats = defaultdict(lambda: {
            'contratos': 0,
            'valor_total': 0,
            'como_adjudicante': 0,
            'como_adjudicataria': 0,
            'nifs': set()
        })

        for contrato in contratos:
            # Adjudicante
            if contrato.get('adjudicante'):
                nome = contrato['adjudicante']
                entidades_stats[nome]['contratos'] += 1
                entidades_stats[nome]['valor_total'] += contrato.get('valor', 0)
                entidades_stats[nome]['como_adjudicante'] += 1
                if contrato.get('adjudicante_nif'):
                    entidades_stats[nome]['nifs'].add(contrato['adjudicante_nif'])

            # Adjudicatária
            if contrato.get('adjudicataria'):
                nome = contrato['adjudicataria']
                entidades_stats[nome]['contratos'] += 1
                entidades_stats[nome]['valor_total'] += contrato.get('valor', 0)
                entidades_stats[nome]['como_adjudicataria'] += 1
                if contrato.get('adjudicataria_nif'):
                    entidades_stats[nome]['nifs'].add(contrato['adjudicataria_nif'])

        # Filtrar e criar lista de sugestões
        sugestoes = []

        for nome, stats in entidades_stats.items():
            if (stats['contratos'] >= min_contratos and
                stats['valor_total'] >= min_valor_total):

                nif = list(stats['nifs'])[0] if stats['nifs'] else None

                # Verificar se já existe
                ja_existe = False
                for figura in self.db.listar_figuras_interesse():
                    if figura['nome'].lower() == nome.lower():
                        ja_existe = True
                        break

                if not ja_existe:
                    sugestoes.append({
                        'nome': nome,
                        'nif': nif,
                        'total_contratos': stats['contratos'],
                        'valor_total': stats['valor_total'],
                        'como_adjudicante': stats['como_adjudicante'],
                        'como_adjudicataria': stats['como_adjudicataria']
                    })

        # Ordenar por valor total
        sugestoes.sort(key=lambda x: x['valor_total'], reverse=True)

        logger.info(f"Encontradas {len(sugestoes)} potenciais figuras de interesse")
        return sugestoes

    # ==================== ANÁLISE DE PADRÕES ====================

    def analisar_padroes_suspeitos(self, figura_id: int) -> List[Dict[str, Any]]:
        """
        Analisa padrões potencialmente suspeitos nos contratos de uma figura

        Args:
            figura_id: ID da figura a analisar

        Returns:
            Lista de padrões suspeitos detectados
        """
        contratos = self.db.pesquisar_contratos_por_figura(figura_id)

        padroes_suspeitos = []

        # Padrão 1: Contratos repetidos com as mesmas entidades
        pares = defaultdict(list)
        for contrato in contratos:
            par = (contrato.get('adjudicante', ''), contrato.get('adjudicataria', ''))
            pares[par].append(contrato)

        for par, contratos_par in pares.items():
            if len(contratos_par) >= 5:  # 5 ou mais contratos entre as mesmas entidades
                padroes_suspeitos.append({
                    'tipo': 'contratos_repetidos',
                    'descricao': f"Múltiplos contratos ({len(contratos_par)}) entre {par[0]} e {par[1]}",
                    'gravidade': 'media',
                    'contratos': len(contratos_par)
                })

        # Padrão 2: Contratos próximos do limite de ajuste direto (valor suspeito)
        limite_ajuste_direto = 75000  # Exemplo
        for contrato in contratos:
            valor = contrato.get('valor', 0)
            if 70000 <= valor <= limite_ajuste_direto:
                padroes_suspeitos.append({
                    'tipo': 'valor_proximo_limite',
                    'descricao': f"Contrato próximo do limite de ajuste direto: €{valor:,.2f}",
                    'gravidade': 'baixa',
                    'id_contrato': contrato.get('id_contrato')
                })

        # Padrão 3: Concentração temporal
        # (muitos contratos num curto período)
        from datetime import datetime, timedelta
        from collections import Counter

        datas = [c['data_contrato'] for c in contratos if c.get('data_contrato')]
        if datas:
            datas_obj = [datetime.strptime(d, '%Y-%m-%d') for d in datas]
            datas_obj.sort()

            for i, data in enumerate(datas_obj):
                # Contar contratos nos próximos 30 dias
                janela_fim = data + timedelta(days=30)
                contratos_janela = sum(1 for d in datas_obj[i:] if d <= janela_fim)

                if contratos_janela >= 10:
                    padroes_suspeitos.append({
                        'tipo': 'concentracao_temporal',
                        'descricao': f"{contratos_janela} contratos num período de 30 dias (início: {data.strftime('%Y-%m-%d')})",
                        'gravidade': 'media',
                        'contratos': contratos_janela
                    })
                    break  # Apenas reportar o primeiro padrão deste tipo

        logger.info(f"Análise de padrões concluída: {len(padroes_suspeitos)} padrões detectados")
        return padroes_suspeitos
