"""
Módulo de Recolha de Dados de Contratos Públicos
Suporta dados abertos, API oficial e web scraping
"""

import requests
import logging
import time
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from io import StringIO
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ContratosPublicosScraper:
    """
    Classe para recolher dados de contratos públicos portugueses

    Métodos suportados:
    1. Dados Abertos (dados.gov.pt) - Preferencial
    2. API Portal BASE - Requer autenticação
    3. Web Scraping - Fallback
    """

    # URLs dos datasets de dados abertos
    DADOS_ABERTOS_BASE_URL = "https://dados.gov.pt"

    # Datasets conhecidos (podem estar em formato CSV ou JSON)
    DATASETS = {
        'contratos_2012_2025': 'contratos-publicos-portal-base-impic-contratos-de-2012-a-2025',
        'ocds': 'ocds-portal-base-www-base-gov-pt'
    }

    def __init__(self, user_agent: str = None):
        """
        Inicializa o scraper

        Args:
            user_agent: User agent personalizado (opcional)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.rate_limit_delay = 1.0  # Segundos entre pedidos
        self.last_request_time = 0

    def _rate_limit(self):
        """Aplica rate limiting entre pedidos"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    # ==================== DADOS ABERTOS ====================

    def obter_url_dataset_csv(self, dataset_name: str) -> Optional[str]:
        """
        Tenta obter o URL de download CSV de um dataset

        Args:
            dataset_name: Nome do dataset

        Returns:
            URL do CSV ou None
        """
        # Esta é uma URL construída com base no padrão comum do dados.gov.pt
        # Nota: Pode ser necessário ajustar após testar com o site real

        # Exemplo de padrões comuns:
        urls_to_try = [
            f"https://dados.gov.pt/pt/datasets/r/{dataset_name}.csv",
            f"https://dados.gov.pt/datasets/r/{dataset_name}.csv",
            f"https://transparencia.gov.pt/recursos/{dataset_name}.csv"
        ]

        for url in urls_to_try:
            try:
                self._rate_limit()
                response = self.session.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    logger.info(f"URL CSV encontrado: {url}")
                    return url
            except Exception as e:
                logger.debug(f"URL não disponível: {url} - {e}")
                continue

        return None

    def download_csv_dados_abertos(self, url: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Faz download de um ficheiro CSV de dados abertos

        Args:
            url: URL do ficheiro CSV
            output_path: Caminho onde guardar (opcional)

        Returns:
            Caminho do ficheiro descarregado ou None
        """
        try:
            self._rate_limit()
            logger.info(f"A descarregar CSV de: {url}")

            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            if not output_path:
                output_path = Path(f"data/contratos_{datetime.now().strftime('%Y%m%d')}.csv")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Download com barra de progresso
            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                if total_size > 0:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Download") as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            logger.info(f"CSV descarregado com sucesso: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erro ao descarregar CSV: {e}")
            return None

    def parse_csv_contratos(self, csv_path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Faz parse de um ficheiro CSV de contratos

        Args:
            csv_path: Caminho do ficheiro CSV
            limit: Limite de registos a processar (opcional)

        Returns:
            Lista de contratos
        """
        contratos = []

        try:
            logger.info(f"A processar CSV: {csv_path}")

            with open(csv_path, 'r', encoding='utf-8') as f:
                # Detectar delimitador
                sample = f.read(4096)
                f.seek(0)

                delimiter = ';' if sample.count(';') > sample.count(',') else ','

                reader = csv.DictReader(f, delimiter=delimiter)

                for i, row in enumerate(reader):
                    if limit and i >= limit:
                        break

                    # Mapear campos do CSV para o formato interno
                    contrato = self._mapear_campos_csv(row)
                    if contrato:
                        contratos.append(contrato)

            logger.info(f"Processados {len(contratos)} contratos do CSV")
            return contratos

        except Exception as e:
            logger.error(f"Erro ao processar CSV: {e}")
            return []

    def _mapear_campos_csv(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Mapeia campos do CSV para o formato interno

        Nota: Os nomes dos campos podem variar entre datasets.
        Este mapeamento pode precisar de ajustes.
        """
        try:
            # Mapeamento de campos comuns (podem ter nomes diferentes)
            # Ajustar conforme o dataset real

            campo_id = row.get('idContrato') or row.get('id') or row.get('ID')

            if not campo_id:
                return None

            contrato = {
                'id_contrato': campo_id,
                'adjudicante': row.get('nomeEntidadeAdjudicante') or row.get('adjudicante') or '',
                'adjudicante_nif': row.get('nifEntidadeAdjudicante') or row.get('adjudicante_nif') or '',
                'adjudicataria': row.get('nomeEntidadeAdjudicataria') or row.get('adjudicataria') or '',
                'adjudicataria_nif': row.get('nifEntidadeAdjudicataria') or row.get('adjudicataria_nif') or '',
                'valor': self._parse_valor(
                    row.get('precoContratual') or row.get('valor') or '0'
                ),
                'data_contrato': self._parse_data(
                    row.get('dataPublicacao') or row.get('dataCelebracaoContrato') or ''
                ),
                'data_publicacao': self._parse_data(
                    row.get('dataPublicacao') or ''
                ),
                'tipo_contrato': row.get('tipoContrato') or '',
                'tipo_procedimento': row.get('tipoProcedimento') or '',
                'descricao': row.get('descricao') or row.get('objectoContrato') or '',
                'objeto_contrato': row.get('objectoContrato') or '',
                'distrito': row.get('distrito') or '',
                'concelho': row.get('concelho') or '',
                'cpv': row.get('cpv') or '',
                'prazo_execucao': self._parse_int(row.get('prazoExecucao') or '0'),
                'link_base': f"https://www.base.gov.pt/Base4/pt/detalhe/?type=contratos&id={campo_id}"
            }

            return contrato

        except Exception as e:
            logger.error(f"Erro ao mapear campos: {e}")
            return None

    def _parse_valor(self, valor_str: str) -> float:
        """Parse de valor monetário"""
        try:
            # Remove espaços e €
            valor_clean = valor_str.replace(' ', '').replace('€', '')
            # Remove pontos (separadores de milhares) e substitui vírgula por ponto (decimal)
            valor_clean = valor_clean.replace('.', '').replace(',', '.')
            return float(valor_clean)
        except:
            return 0.0

    def _parse_data(self, data_str: str) -> Optional[str]:
        """Parse de data para formato ISO (YYYY-MM-DD)"""
        if not data_str:
            return None

        formatos = [
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%Y%m%d'
        ]

        for formato in formatos:
            try:
                dt = datetime.strptime(data_str.strip(), formato)
                return dt.strftime('%Y-%m-%d')
            except:
                continue

        logger.warning(f"Não foi possível fazer parse da data: {data_str}")
        return None

    def _parse_int(self, int_str: str) -> int:
        """Parse de inteiro"""
        try:
            return int(int_str)
        except:
            return 0

    # ==================== API PORTAL BASE ====================

    def configurar_api_base(self, api_key: str, api_url: str = None):
        """
        Configura autenticação para a API oficial do Portal BASE

        Args:
            api_key: Chave de API (obtida após registo no IMPIC)
            api_url: URL base da API (opcional)
        """
        self.api_key = api_key
        self.api_base_url = api_url or "https://www.base.gov.pt/api/v1"
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}'
        })
        logger.info("API Portal BASE configurada")

    def pesquisar_api_base(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Pesquisa contratos usando a API oficial do Portal BASE

        Nota: Este método requer configuração prévia da API

        Args:
            filtros: Filtros de pesquisa

        Returns:
            Lista de contratos
        """
        if not hasattr(self, 'api_key'):
            logger.error("API não configurada. Use configurar_api_base() primeiro.")
            return []

        try:
            # Esta é uma implementação hipotética
            # A API real pode ter endpoints e parâmetros diferentes

            endpoint = f"{self.api_base_url}/contratos"

            params = {}
            if filtros.get('distrito'):
                params['distrito'] = filtros['distrito']
            if filtros.get('ano'):
                params['ano'] = filtros['ano']
            # Adicionar mais parâmetros conforme a API real

            self._rate_limit()
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            contratos = data.get('results', [])

            logger.info(f"API retornou {len(contratos)} contratos")
            return contratos

        except Exception as e:
            logger.error(f"Erro ao consultar API: {e}")
            return []

    # ==================== WEB SCRAPING ====================

    def scrape_base_gov_pt(self, filtros: Dict[str, Any], max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Faz web scraping do site BASE.gov.pt

        ATENÇÃO: Este método deve ser usado apenas como último recurso
        e respeita as boas práticas de scraping

        Args:
            filtros: Filtros de pesquisa
            max_pages: Número máximo de páginas a processar

        Returns:
            Lista de contratos
        """
        logger.warning("Web scraping ativado - use apenas quando dados abertos/API não estiverem disponíveis")

        # Implementação básica - requer ajuste após análise do site
        # Por segurança e ética, preferir sempre dados abertos/API

        try:
            from bs4 import BeautifulSoup

            contratos = []
            base_url = "https://www.base.gov.pt/Base4/pt/pesquisa/"

            # Construir URL de pesquisa
            params = {
                'type': 'contratos'
            }

            # Adicionar filtros aos parâmetros
            # (requer análise do formulário de pesquisa do site)

            for page in range(1, max_pages + 1):
                self._rate_limit()

                params['page'] = page

                try:
                    response = self.session.get(base_url, params=params, timeout=20)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extrair contratos da página
                    # (requer análise da estrutura HTML do site)

                    # Exemplo hipotético:
                    # resultados = soup.find_all('div', class_='contrato-item')
                    # for resultado in resultados:
                    #     contrato = self._extrair_contrato_html(resultado)
                    #     if contrato:
                    #         contratos.append(contrato)

                    logger.info(f"Página {page}/{max_pages} processada")

                except Exception as e:
                    logger.error(f"Erro ao processar página {page}: {e}")
                    break

            logger.info(f"Scraping concluído: {len(contratos)} contratos encontrados")
            return contratos

        except ImportError:
            logger.error("BeautifulSoup4 não está instalado. Execute: pip install beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"Erro no web scraping: {e}")
            return []

    # ==================== MÉTODOS AUXILIARES ====================

    def validar_contrato(self, contrato: Dict[str, Any]) -> bool:
        """
        Valida se um contrato tem os campos mínimos necessários

        Args:
            contrato: Dicionário do contrato

        Returns:
            True se válido
        """
        campos_obrigatorios = ['id_contrato']

        for campo in campos_obrigatorios:
            if not contrato.get(campo):
                logger.warning(f"Contrato inválido: campo '{campo}' em falta")
                return False

        return True

    def processar_lote_contratos(self, contratos: List[Dict[str, Any]],
                                 db_manager) -> Dict[str, int]:
        """
        Processa um lote de contratos e insere na base de dados

        Args:
            contratos: Lista de contratos
            db_manager: Instância do DatabaseManager

        Returns:
            Estatísticas do processamento
        """
        stats = {
            'total': len(contratos),
            'inseridos': 0,
            'duplicados': 0,
            'invalidos': 0
        }

        logger.info(f"A processar lote de {len(contratos)} contratos...")

        for contrato in tqdm(contratos, desc="Processando contratos"):
            if not self.validar_contrato(contrato):
                stats['invalidos'] += 1
                continue

            if db_manager.inserir_contrato(contrato):
                stats['inseridos'] += 1
            else:
                stats['duplicados'] += 1

        logger.info(f"Processamento concluído: {stats}")
        return stats


# ==================== FUNÇÕES DE UTILIDADE ====================

def recolher_dados_abertos_completo(db_manager, dataset_name: str = 'contratos_2012_2025',
                                    limit: Optional[int] = None) -> Dict[str, int]:
    """
    Função de alto nível para recolher dados abertos completos

    Args:
        db_manager: Instância do DatabaseManager
        dataset_name: Nome do dataset a usar
        limit: Limite de registos (opcional, para testes)

    Returns:
        Estatísticas do processamento
    """
    scraper = ContratosPublicosScraper()

    logger.info(f"Iniciando recolha de dados abertos: {dataset_name}")

    # Tentar diferentes URLs/métodos para obter os dados
    # Esta é uma implementação simplificada

    # Exemplo: Assumindo que temos um CSV local ou URL conhecida
    csv_url = f"https://dados.gov.pt/datasets/{dataset_name}.csv"

    # Download do CSV
    csv_path = scraper.download_csv_dados_abertos(csv_url)

    if not csv_path or not csv_path.exists():
        logger.error("Não foi possível descarregar os dados")
        return {'total': 0, 'inseridos': 0, 'duplicados': 0, 'invalidos': 0}

    # Parse do CSV
    contratos = scraper.parse_csv_contratos(csv_path, limit=limit)

    # Processar e inserir na BD
    stats = scraper.processar_lote_contratos(contratos, db_manager)

    return stats
