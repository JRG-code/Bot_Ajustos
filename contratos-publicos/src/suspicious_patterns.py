"""
Módulo de Detecção de Padrões Suspeitos
Identifica comportamentos potencialmente irregulares em contratos públicos
"""

import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


# ==================== LIMITES LEGAIS PORTUGUESES ====================

class LimitesLegais:
    """Limites legais para contratação pública em Portugal (2024)"""

    # Código dos Contratos Públicos (CCP)
    AJUSTE_DIRETO_BENS_SERVICOS = 75000  # €75.000
    AJUSTE_DIRETO_OBRAS = 150000  # €150.000

    CONSULTA_PREVIA_BENS_SERVICOS = 214000  # €214.000
    CONSULTA_PREVIA_OBRAS = 548000  # €548.000

    CONCURSO_PUBLICO_BENS_SERVICOS = 214000  # Acima deste valor
    CONCURSO_PUBLICO_OBRAS = 548000  # Acima deste valor

    # Limites da União Europeia (contratos internacionais)
    UE_BENS_SERVICOS = 140000  # €140.000
    UE_OBRAS = 5382000  # €5.382.000

    # Margens de suspeição (% abaixo do limite)
    MARGEM_SUSPEITA_PERCENTAGEM = 5  # 5% abaixo do limite
    MARGEM_ALTA_SUSPEITA = 1  # 1% abaixo do limite (muito suspeito)

    @classmethod
    def get_limite_ajuste_direto(cls, tipo_contrato: str) -> float:
        """Retorna limite de ajuste direto baseado no tipo"""
        if 'obra' in tipo_contrato.lower() or 'empreitada' in tipo_contrato.lower():
            return cls.AJUSTE_DIRETO_OBRAS
        return cls.AJUSTE_DIRETO_BENS_SERVICOS

    @classmethod
    def get_limite_consulta_previa(cls, tipo_contrato: str) -> float:
        """Retorna limite de consulta prévia baseado no tipo"""
        if 'obra' in tipo_contrato.lower() or 'empreitada' in tipo_contrato.lower():
            return cls.CONSULTA_PREVIA_OBRAS
        return cls.CONSULTA_PREVIA_BENS_SERVICOS


class SuspiciousPatternDetector:
    """Detector de padrões suspeitos em contratos públicos"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o detector

        Args:
            config: Configurações personalizadas (opcional)
        """
        self.config = config or self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Configurações padrão de detecção"""
        return {
            # Valores suspeitos
            'detectar_valores_suspeitos': True,
            'margem_suspeita_percentagem': 5,  # 5% abaixo do limite
            'margem_alta_suspeita_percentagem': 1,  # 1% abaixo (muito suspeito)

            # Fracionamento
            'detectar_fracionamento': True,
            'janela_fracionamento_dias': 365,  # 1 ano
            'min_contratos_fracionamento': 3,

            # Contratos repetidos
            'detectar_contratos_repetidos': True,
            'min_contratos_repetidos': 5,

            # Concentração temporal
            'detectar_concentracao_temporal': True,
            'janela_concentracao_dias': 30,
            'min_contratos_concentracao': 10,

            # Valores redondos suspeitos
            'detectar_valores_redondos': True,
            'valores_redondos_suspeitos': [
                74900, 74950, 74990, 74999,  # Logo abaixo de 75k
                149900, 149950, 149990, 149999,  # Logo abaixo de 150k
                213900, 213950, 213990, 213999,  # Logo abaixo de 214k
            ],

            # Procedimentos inadequados
            'detectar_procedimento_inadequado': True,

            # Padrões temporais
            'detectar_vesperas_feriados': True,
            'detectar_finais_mandato': True,
        }

    # ==================== DETECÇÃO DE PADRÕES ====================

    def analisar_contratos(self, contratos: List[Dict[str, Any]],
                          figura_id: int = None) -> List[Dict[str, Any]]:
        """
        Analisa uma lista de contratos para padrões suspeitos

        Args:
            contratos: Lista de contratos
            figura_id: ID da figura de interesse (opcional)

        Returns:
            Lista de padrões suspeitos detectados
        """
        padroes = []

        if self.config['detectar_valores_suspeitos']:
            padroes.extend(self._detectar_valores_suspeitos(contratos))

        if self.config['detectar_fracionamento']:
            padroes.extend(self._detectar_fracionamento(contratos))

        if self.config['detectar_contratos_repetidos']:
            padroes.extend(self._detectar_contratos_repetidos(contratos))

        if self.config['detectar_concentracao_temporal']:
            padroes.extend(self._detectar_concentracao_temporal(contratos))

        if self.config['detectar_valores_redondos']:
            padroes.extend(self._detectar_valores_redondos(contratos))

        if self.config['detectar_procedimento_inadequado']:
            padroes.extend(self._detectar_procedimento_inadequado(contratos))

        if self.config['detectar_vesperas_feriados']:
            padroes.extend(self._detectar_vesperas_feriados(contratos))

        logger.info(f"Detectados {len(padroes)} padrões suspeitos")
        return padroes

    def _detectar_valores_suspeitos(self, contratos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detecta valores estrategicamente abaixo dos limites legais

        Exemplo: €74.950 (€50 abaixo do limite de €75.000)
        """
        padroes = []

        for contrato in contratos:
            valor = contrato.get('valor', 0)
            tipo = contrato.get('tipo_contrato', '')
            procedimento = contrato.get('tipo_procedimento', '').lower()

            if valor <= 0:
                continue

            # Determinar limite relevante
            limite_ajuste = LimitesLegais.get_limite_ajuste_direto(tipo)
            limite_consulta = LimitesLegais.get_limite_consulta_previa(tipo)

            # Calcular margens
            margem_normal = limite_ajuste * (self.config['margem_suspeita_percentagem'] / 100)
            margem_alta = limite_ajuste * (self.config['margem_alta_suspeita_percentagem'] / 100)

            # Verificar se está próximo do limite de ajuste direto
            if limite_ajuste - margem_normal <= valor <= limite_ajuste:
                distancia = limite_ajuste - valor
                percentagem = (distancia / limite_ajuste) * 100

                gravidade = 'alta' if distancia <= margem_alta else 'media'

                # Verificar se o procedimento é ajuste direto (mais suspeito)
                if 'ajuste' in procedimento:
                    gravidade = 'alta'

                padroes.append({
                    'tipo': 'valor_suspeito_limite',
                    'subtipo': 'ajuste_direto',
                    'descricao': f"Valor €{valor:,.2f} apenas €{distancia:,.2f} ({percentagem:.2f}%) abaixo do limite de ajuste direto (€{limite_ajuste:,.0f})",
                    'gravidade': gravidade,
                    'id_contrato': contrato.get('id_contrato'),
                    'valor': valor,
                    'limite': limite_ajuste,
                    'distancia': distancia,
                    'percentagem_abaixo': percentagem,
                    'procedimento': procedimento
                })

        return padroes

    def _detectar_fracionamento(self, contratos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detecta possível fracionamento ilegal de contratos

        Fracionamento: dividir artificialmente um contrato em vários menores
        para evitar procedimentos mais rigorosos
        """
        padroes = []

        # Agrupar por pares adjudicante-adjudicatária
        pares = defaultdict(list)
        for contrato in contratos:
            par = (
                contrato.get('adjudicante', ''),
                contrato.get('adjudicataria', ''),
                contrato.get('tipo_contrato', ''),
                contrato.get('objeto_contrato', '')[:50]  # Primeiras 50 chars do objeto
            )
            pares[par].append(contrato)

        # Analisar cada par
        for par, contratos_par in pares.items():
            if len(contratos_par) < self.config['min_contratos_fracionamento']:
                continue

            # Ordenar por data
            contratos_par.sort(key=lambda x: x.get('data_contrato', ''))

            # Analisar janela temporal
            janela_dias = self.config['janela_fracionamento_dias']

            for i, contrato in enumerate(contratos_par):
                data_inicio = contrato.get('data_contrato')
                if not data_inicio:
                    continue

                dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
                dt_fim = dt_inicio + timedelta(days=janela_dias)

                # Contar contratos na janela
                contratos_janela = [
                    c for c in contratos_par[i:]
                    if c.get('data_contrato') and
                    datetime.strptime(c['data_contrato'], '%Y-%m-%d') <= dt_fim
                ]

                if len(contratos_janela) >= self.config['min_contratos_fracionamento']:
                    valor_total = sum(c.get('valor', 0) for c in contratos_janela)
                    tipo = contratos_janela[0].get('tipo_contrato', '')
                    limite = LimitesLegais.get_limite_ajuste_direto(tipo)

                    # Se o total ultrapassa o limite, é suspeito
                    if valor_total > limite:
                        padroes.append({
                            'tipo': 'fracionamento_suspeito',
                            'descricao': f"Possível fracionamento: {len(contratos_janela)} contratos em {janela_dias} dias totalizando €{valor_total:,.2f} (limite: €{limite:,.0f})",
                            'gravidade': 'alta',
                            'adjudicante': par[0],
                            'adjudicataria': par[1],
                            'num_contratos': len(contratos_janela),
                            'valor_total': valor_total,
                            'periodo_dias': janela_dias,
                            'contratos_ids': [c.get('id_contrato') for c in contratos_janela]
                        })
                        break  # Apenas reportar uma vez por par

        return padroes

    def _detectar_contratos_repetidos(self, contratos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detecta contratos excessivamente repetidos entre mesmas entidades"""
        padroes = []

        pares = defaultdict(list)
        for contrato in contratos:
            par = (contrato.get('adjudicante', ''), contrato.get('adjudicataria', ''))
            pares[par].append(contrato)

        for par, contratos_par in pares.items():
            if len(contratos_par) >= self.config['min_contratos_repetidos']:
                valor_total = sum(c.get('valor', 0) for c in contratos_par)

                padroes.append({
                    'tipo': 'contratos_repetidos',
                    'descricao': f"Múltiplos contratos ({len(contratos_par)}) entre {par[0]} e {par[1]} totalizando €{valor_total:,.2f}",
                    'gravidade': 'media',
                    'num_contratos': len(contratos_par),
                    'valor_total': valor_total
                })

        return padroes

    def _detectar_concentracao_temporal(self, contratos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detecta concentração anormal de contratos num curto período"""
        padroes = []

        datas = [c for c in contratos if c.get('data_contrato')]
        if not datas:
            return padroes

        datas.sort(key=lambda x: x['data_contrato'])

        for i, contrato in enumerate(datas):
            data_inicio = datetime.strptime(contrato['data_contrato'], '%Y-%m-%d')
            data_fim = data_inicio + timedelta(days=self.config['janela_concentracao_dias'])

            contratos_janela = [
                c for c in datas[i:]
                if datetime.strptime(c['data_contrato'], '%Y-%m-%d') <= data_fim
            ]

            if len(contratos_janela) >= self.config['min_contratos_concentracao']:
                valor_total = sum(c.get('valor', 0) for c in contratos_janela)

                padroes.append({
                    'tipo': 'concentracao_temporal',
                    'descricao': f"{len(contratos_janela)} contratos em {self.config['janela_concentracao_dias']} dias (€{valor_total:,.2f})",
                    'gravidade': 'media',
                    'data_inicio': contrato['data_contrato'],
                    'num_contratos': len(contratos_janela),
                    'valor_total': valor_total
                })
                break  # Apenas reportar o primeiro

        return padroes

    def _detectar_valores_redondos(self, contratos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detecta valores suspeitos muito específicos

        Exemplo: €74.999,00 (€1 abaixo do limite)
        """
        padroes = []

        for contrato in contratos:
            valor = contrato.get('valor', 0)

            if valor in self.config['valores_redondos_suspeitos']:
                padroes.append({
                    'tipo': 'valor_exato_suspeito',
                    'descricao': f"Valor suspeito exato: €{valor:,.2f}",
                    'gravidade': 'alta',
                    'id_contrato': contrato.get('id_contrato'),
                    'valor': valor
                })

            # Detectar valores "quase redondos" (ex: 74999, 74990, etc)
            # que são claramente calculados para evitar limites
            for limite in [75000, 150000, 214000, 548000]:
                if limite - 100 <= valor < limite:
                    diferenca = limite - valor
                    if diferenca in [1, 10, 50, 100]:
                        padroes.append({
                            'tipo': 'valor_calculado_suspeito',
                            'descricao': f"Valor aparentemente calculado: €{valor:,.2f} (€{diferenca:,.0f} abaixo de €{limite:,.0f})",
                            'gravidade': 'alta',
                            'id_contrato': contrato.get('id_contrato'),
                            'valor': valor,
                            'limite_evitado': limite
                        })

        return padroes

    def _detectar_procedimento_inadequado(self, contratos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detecta uso de procedimento inadequado para o valor

        Exemplo: Ajuste direto para valor que deveria ser consulta prévia
        """
        padroes = []

        for contrato in contratos:
            valor = contrato.get('valor', 0)
            procedimento = contrato.get('tipo_procedimento', '').lower()
            tipo = contrato.get('tipo_contrato', '')

            if valor <= 0 or not procedimento:
                continue

            limite_ajuste = LimitesLegais.get_limite_ajuste_direto(tipo)
            limite_consulta = LimitesLegais.get_limite_consulta_previa(tipo)

            # Ajuste direto acima do limite
            if 'ajuste' in procedimento and valor > limite_ajuste:
                padroes.append({
                    'tipo': 'procedimento_inadequado',
                    'descricao': f"Ajuste direto (€{valor:,.2f}) acima do limite legal (€{limite_ajuste:,.0f})",
                    'gravidade': 'alta',
                    'id_contrato': contrato.get('id_contrato'),
                    'valor': valor,
                    'procedimento': procedimento
                })

            # Consulta prévia acima do limite
            if 'consulta' in procedimento and valor > limite_consulta:
                padroes.append({
                    'tipo': 'procedimento_inadequado',
                    'descricao': f"Consulta prévia (€{valor:,.2f}) acima do limite legal (€{limite_consulta:,.0f}) - deveria ser concurso público",
                    'gravidade': 'alta',
                    'id_contrato': contrato.get('id_contrato'),
                    'valor': valor,
                    'procedimento': procedimento
                })

        return padroes

    def _detectar_vesperas_feriados(self, contratos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detecta contratos publicados em vésperas de feriados/fins de semana"""
        padroes = []

        # Feriados nacionais portugueses (simplificado)
        feriados = [
            '01-01', '04-25', '05-01', '06-10', '08-15',
            '10-05', '11-01', '12-01', '12-08', '12-25'
        ]

        for contrato in contratos:
            data_str = contrato.get('data_publicacao') or contrato.get('data_contrato')
            if not data_str:
                continue

            try:
                data = datetime.strptime(data_str, '%Y-%m-%d')

                # Véspera de fim de semana (sexta após 18h, assumindo)
                if data.weekday() == 4:  # Sexta
                    padroes.append({
                        'tipo': 'publicacao_vespera',
                        'subtipo': 'fim_semana',
                        'descricao': f"Publicado sexta-feira ({data_str})",
                        'gravidade': 'baixa',
                        'id_contrato': contrato.get('id_contrato'),
                        'data': data_str
                    })

                # Véspera de feriado
                mes_dia = data.strftime('%m-%d')
                if mes_dia in feriados:
                    padroes.append({
                        'tipo': 'publicacao_vespera',
                        'subtipo': 'feriado',
                        'descricao': f"Publicado em feriado ({data_str})",
                        'gravidade': 'media',
                        'id_contrato': contrato.get('id_contrato'),
                        'data': data_str
                    })

            except:
                continue

        return padroes

    # ==================== RELATÓRIOS ====================

    def gerar_relatorio(self, padroes: List[Dict[str, Any]]) -> str:
        """Gera relatório textual dos padrões detectados"""

        if not padroes:
            return "Nenhum padrão suspeito detectado."

        # Agrupar por gravidade
        alta = [p for p in padroes if p.get('gravidade') == 'alta']
        media = [p for p in padroes if p.get('gravidade') == 'media']
        baixa = [p for p in padroes if p.get('gravidade') == 'baixa']

        relatorio = f"""
╔════════════════════════════════════════════════════════════════╗
║     RELATÓRIO DE PADRÕES SUSPEITOS                             ║
╚════════════════════════════════════════════════════════════════╝

Total de padrões detectados: {len(padroes)}

🔴 GRAVIDADE ALTA: {len(alta)}
🟡 GRAVIDADE MÉDIA: {len(media)}
⚪ GRAVIDADE BAIXA: {len(baixa)}

"""

        if alta:
            relatorio += "\n🔴 PADRÕES DE GRAVIDADE ALTA:\n" + "=" * 64 + "\n\n"
            for i, p in enumerate(alta[:10], 1):  # Top 10
                relatorio += f"{i}. {p['tipo'].upper()}\n"
                relatorio += f"   {p['descricao']}\n"
                if p.get('id_contrato'):
                    relatorio += f"   Contrato: {p['id_contrato']}\n"
                relatorio += "\n"

        if media:
            relatorio += "\n🟡 PADRÕES DE GRAVIDADE MÉDIA:\n" + "=" * 64 + "\n\n"
            for i, p in enumerate(media[:5], 1):  # Top 5
                relatorio += f"{i}. {p['tipo'].upper()}\n"
                relatorio += f"   {p['descricao']}\n\n"

        relatorio += "\n" + "=" * 64 + "\n"

        return relatorio


# ==================== FUNÇÕES DE UTILIDADE ====================

def analisar_todos_contratos(db_manager, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Analisa todos os contratos na base de dados

    Args:
        db_manager: Instância do DatabaseManager
        config: Configurações do detector

    Returns:
        Lista de padrões suspeitos
    """
    detector = SuspiciousPatternDetector(config)

    # Obter todos os contratos
    contratos = db_manager.pesquisar_contratos({})

    # Analisar
    padroes = detector.analisar_contratos(contratos)

    return padroes
