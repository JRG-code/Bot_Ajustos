"""
Módulo de Sistema de Alertas
Monitoriza novos contratos e gera alertas para figuras de interesse
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlertsManager:
    """Gestor do sistema de alertas"""

    def __init__(self, db_manager):
        """
        Inicializa o gestor de alertas

        Args:
            db_manager: Instância do DatabaseManager
        """
        self.db = db_manager

    # ==================== VERIFICAÇÃO DE NOVOS CONTRATOS ====================

    def verificar_novos_contratos(self, contratos_novos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verifica se novos contratos envolvem figuras de interesse
        e cria alertas automáticos

        Args:
            contratos_novos: Lista de contratos a verificar

        Returns:
            Lista de alertas criados
        """
        logger.info(f"A verificar {len(contratos_novos)} contratos para figuras de interesse...")

        figuras = self.db.listar_figuras_interesse(apenas_ativas=True)

        if not figuras:
            logger.info("Nenhuma figura de interesse configurada")
            return []

        alertas_criados = []

        for contrato in contratos_novos:
            alertas = self._verificar_contrato_individual(contrato, figuras)
            alertas_criados.extend(alertas)

        logger.info(f"{len(alertas_criados)} alertas criados")
        return alertas_criados

    def _verificar_contrato_individual(self, contrato: Dict[str, Any],
                                      figuras: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verifica um contrato individual contra todas as figuras de interesse

        Args:
            contrato: Contrato a verificar
            figuras: Lista de figuras de interesse

        Returns:
            Lista de alertas para este contrato
        """
        alertas = []

        adjudicante = (contrato.get('adjudicante') or '').lower()
        adjudicataria = (contrato.get('adjudicataria') or '').lower()
        adjudicante_nif = contrato.get('adjudicante_nif', '')
        adjudicataria_nif = contrato.get('adjudicataria_nif', '')

        for figura in figuras:
            nome_figura = figura['nome'].lower()
            nif_figura = figura.get('nif', '')

            # Verificar se a figura está envolvida no contrato
            match_adjudicante = (nome_figura in adjudicante or
                               (nif_figura and nif_figura == adjudicante_nif))
            match_adjudicataria = (nome_figura in adjudicataria or
                                  (nif_figura and nif_figura == adjudicataria_nif))

            if match_adjudicante or match_adjudicataria:
                papel = []
                if match_adjudicante:
                    papel.append('adjudicante')
                if match_adjudicataria:
                    papel.append('adjudicatária')

                papel_str = ' e '.join(papel)

                # Criar mensagem do alerta
                mensagem = self._criar_mensagem_alerta(contrato, figura, papel_str)

                # Determinar tipo de alerta
                tipo_alerta = self._determinar_tipo_alerta(contrato, figura)

                # Inserir na base de dados
                alerta_id = self.db.criar_alerta(
                    id_contrato=contrato['id_contrato'],
                    figura_interesse_id=figura['id'],
                    tipo_alerta=tipo_alerta,
                    mensagem=mensagem
                )

                if alerta_id > 0:
                    alertas.append({
                        'id': alerta_id,
                        'figura': figura['nome'],
                        'contrato_id': contrato['id_contrato'],
                        'tipo': tipo_alerta,
                        'mensagem': mensagem
                    })

                    logger.debug(f"Alerta criado: {tipo_alerta} - {figura['nome']}")

        return alertas

    def _criar_mensagem_alerta(self, contrato: Dict[str, Any],
                              figura: Dict[str, Any],
                              papel: str) -> str:
        """Cria mensagem detalhada do alerta"""

        valor_str = f"€{contrato.get('valor', 0):,.2f}" if contrato.get('valor') else "Valor não especificado"

        mensagem = f"""
Novo contrato envolvendo {figura['nome']}

Papel: {papel}
Adjudicante: {contrato.get('adjudicante', 'N/D')}
Adjudicatária: {contrato.get('adjudicataria', 'N/D')}
Valor: {valor_str}
Data: {contrato.get('data_contrato', 'N/D')}
Tipo: {contrato.get('tipo_contrato', 'N/D')}
Descrição: {(contrato.get('descricao') or contrato.get('objeto_contrato', 'N/D'))[:200]}
        """.strip()

        return mensagem

    def _determinar_tipo_alerta(self, contrato: Dict[str, Any],
                                figura: Dict[str, Any]) -> str:
        """
        Determina o tipo/prioridade do alerta baseado em critérios

        Returns:
            Tipo: 'alto_valor', 'frequente', 'normal'
        """
        valor = contrato.get('valor', 0)

        # Alto valor (> 500.000€)
        if valor > 500000:
            return 'alto_valor'

        # Verificar se é frequente (precisa de análise histórica)
        # Por agora, apenas retorna normal
        return 'normal'

    # ==================== GESTÃO DE ALERTAS ====================

    def listar_alertas(self, apenas_nao_lidos: bool = True,
                      figura_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista alertas com filtros

        Args:
            apenas_nao_lidos: Se True, apenas alertas não lidos
            figura_id: Filtrar por figura específica

        Returns:
            Lista de alertas
        """
        alertas = self.db.listar_alertas(apenas_nao_lidos)

        if figura_id:
            alertas = [a for a in alertas if a['figura_interesse_id'] == figura_id]

        return alertas

    def marcar_lido(self, alerta_id: int) -> bool:
        """Marca um alerta como lido"""
        return self.db.marcar_alerta_lido(alerta_id)

    def marcar_todos_lidos(self) -> int:
        """
        Marca todos os alertas como lidos

        Returns:
            Número de alertas marcados
        """
        alertas = self.db.listar_alertas(apenas_nao_lidos=True)
        count = 0

        for alerta in alertas:
            if self.db.marcar_alerta_lido(alerta['id']):
                count += 1

        logger.info(f"{count} alertas marcados como lidos")
        return count

    # ==================== ANÁLISE DE ALERTAS ====================

    def obter_estatisticas_alertas(self) -> Dict[str, Any]:
        """Retorna estatísticas dos alertas"""

        todos_alertas = self.db.listar_alertas(apenas_nao_lidos=False)
        nao_lidos = self.db.listar_alertas(apenas_nao_lidos=True)

        # Contar por tipo
        tipos = {}
        for alerta in todos_alertas:
            tipo = alerta.get('tipo_alerta', 'desconhecido')
            tipos[tipo] = tipos.get(tipo, 0) + 1

        # Contar por figura
        por_figura = {}
        for alerta in todos_alertas:
            figura = alerta.get('figura_nome', 'Desconhecido')
            por_figura[figura] = por_figura.get(figura, 0) + 1

        # Alertas recentes (últimos 7 dias)
        data_limite = (datetime.now() - timedelta(days=7)).isoformat()
        recentes = [a for a in todos_alertas
                   if a.get('data_alerta', '') >= data_limite]

        estatisticas = {
            'total': len(todos_alertas),
            'nao_lidos': len(nao_lidos),
            'lidos': len(todos_alertas) - len(nao_lidos),
            'ultimos_7_dias': len(recentes),
            'por_tipo': tipos,
            'por_figura': sorted(por_figura.items(), key=lambda x: x[1], reverse=True)[:5]
        }

        return estatisticas

    def obter_alertas_prioritarios(self, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna os alertas mais prioritários (não lidos, ordenados por critérios)

        Args:
            limite: Número máximo de alertas a retornar

        Returns:
            Lista de alertas prioritários
        """
        alertas = self.db.listar_alertas(apenas_nao_lidos=True)

        # Definir prioridade
        prioridades = {
            'alto_valor': 3,
            'frequente': 2,
            'normal': 1
        }

        # Adicionar score de prioridade
        for alerta in alertas:
            tipo = alerta.get('tipo_alerta', 'normal')
            alerta['prioridade_score'] = prioridades.get(tipo, 1)

            # Aumentar prioridade se for recente (últimas 24h)
            data_alerta = alerta.get('data_alerta', '')
            if data_alerta:
                try:
                    dt_alerta = datetime.fromisoformat(data_alerta.replace(' ', 'T'))
                    idade_horas = (datetime.now() - dt_alerta).total_seconds() / 3600

                    if idade_horas < 24:
                        alerta['prioridade_score'] += 2
                    elif idade_horas < 72:
                        alerta['prioridade_score'] += 1
                except:
                    pass

        # Ordenar por prioridade
        alertas_ordenados = sorted(alertas, key=lambda x: x['prioridade_score'], reverse=True)

        return alertas_ordenados[:limite]

    # ==================== NOTIFICAÇÕES ====================

    def gerar_relatorio_alertas(self, periodo_dias: int = 7) -> str:
        """
        Gera um relatório textual dos alertas de um período

        Args:
            periodo_dias: Número de dias para o relatório

        Returns:
            Texto do relatório
        """
        data_limite = (datetime.now() - timedelta(days=periodo_dias)).isoformat()
        todos_alertas = self.db.listar_alertas(apenas_nao_lidos=False)

        alertas_periodo = [a for a in todos_alertas
                          if a.get('data_alerta', '') >= data_limite]

        relatorio = f"""
═══════════════════════════════════════════════════════════════
        RELATÓRIO DE ALERTAS - ÚLTIMOS {periodo_dias} DIAS
═══════════════════════════════════════════════════════════════

Total de alertas no período: {len(alertas_periodo)}
Alertas não lidos: {sum(1 for a in alertas_periodo if not a.get('lido', False))}

"""

        if alertas_periodo:
            relatorio += "ALERTAS RECENTES:\n\n"

            for i, alerta in enumerate(sorted(alertas_periodo,
                                             key=lambda x: x.get('data_alerta', ''),
                                             reverse=True)[:10], 1):

                status = "✓ Lido" if alerta.get('lido') else "✗ NÃO LIDO"
                tipo = alerta.get('tipo_alerta', 'normal').upper()
                figura = alerta.get('figura_nome', 'Desconhecido')
                data = alerta.get('data_alerta', 'N/D')[:19]  # Remove milissegundos

                relatorio += f"{i}. [{status}] {tipo}\n"
                relatorio += f"   Figura: {figura}\n"
                relatorio += f"   Data: {data}\n"
                relatorio += f"   Contrato: {alerta.get('id_contrato', 'N/D')}\n"

                # Valor do contrato se disponível
                if alerta.get('valor'):
                    relatorio += f"   Valor: €{alerta['valor']:,.2f}\n"

                relatorio += "\n"

        else:
            relatorio += "Nenhum alerta no período especificado.\n"

        relatorio += "═══════════════════════════════════════════════════════════════\n"

        return relatorio

    # ==================== CONFIGURAÇÃO ====================

    def configurar_filtros_alerta(self, figura_id: int,
                                  valor_minimo: Optional[float] = None,
                                  tipos_contrato: Optional[List[str]] = None) -> bool:
        """
        Configura filtros personalizados para alertas de uma figura
        (Funcionalidade futura - requer extensão da BD)

        Args:
            figura_id: ID da figura
            valor_minimo: Valor mínimo para gerar alerta
            tipos_contrato: Tipos de contrato a monitorizar

        Returns:
            True se configurado com sucesso
        """
        # Esta funcionalidade requer uma tabela adicional na BD
        # Por agora, apenas loga a intenção
        logger.info(f"Configuração de filtros para figura {figura_id} (não implementado)")
        return False


# ==================== FUNÇÕES DE UTILIDADE ====================

def monitorizar_contratos_batch(db_manager, contratos_novos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Função de alto nível para monitorizar um lote de contratos

    Args:
        db_manager: Instância do DatabaseManager
        contratos_novos: Lista de contratos a monitorizar

    Returns:
        Resumo da monitorização
    """
    alerts_manager = AlertsManager(db_manager)

    alertas_criados = alerts_manager.verificar_novos_contratos(contratos_novos)

    resumo = {
        'contratos_verificados': len(contratos_novos),
        'alertas_gerados': len(alertas_criados),
        'alertas_por_tipo': {}
    }

    # Contar por tipo
    for alerta in alertas_criados:
        tipo = alerta['tipo']
        resumo['alertas_por_tipo'][tipo] = resumo['alertas_por_tipo'].get(tipo, 0) + 1

    logger.info(f"Monitorização concluída: {resumo}")

    return resumo
