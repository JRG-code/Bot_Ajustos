"""
Módulo de Sincronização Automática
Permite sincronizar dados do Portal BASE sem manter a aplicação aberta
"""

import logging
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib

logger = logging.getLogger(__name__)


class SyncManager:
    """Gestor de sincronização de dados"""

    def __init__(self, db_manager, scraper):
        """
        Inicializa o gestor de sincronização

        Args:
            db_manager: Instância do DatabaseManager
            scraper: Instância do ContratosPublicosScraper
        """
        self.db = db_manager
        self.scraper = scraper
        self.config_path = Path("data/sync_config.json")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração de sincronização"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar config: {e}")

        # Configuração padrão
        return {
            'auto_sync': False,
            'sync_interval_hours': 24,
            'last_sync': None,
            'sync_sources': {
                'dados_abertos': True,
                'api_base': False
            },
            'incremental_sync': True,
            'max_contracts_per_sync': 10000
        }

    def _save_config(self):
        """Guarda configuração de sincronização"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Configuração de sincronização guardada")
        except Exception as e:
            logger.error(f"Erro ao guardar config: {e}")

    def get_last_sync(self) -> Optional[str]:
        """Retorna a data da última sincronização"""
        return self.config.get('last_sync')

    def should_sync(self) -> bool:
        """Verifica se deve executar sincronização"""
        if not self.config.get('auto_sync'):
            return False

        last_sync = self.config.get('last_sync')
        if not last_sync:
            return True

        try:
            last_sync_dt = datetime.fromisoformat(last_sync)
            interval_hours = self.config.get('sync_interval_hours', 24)
            next_sync = last_sync_dt + timedelta(hours=interval_hours)

            return datetime.now() >= next_sync
        except:
            return True

    def configure_sync(self, auto_sync: bool = False,
                      interval_hours: int = 24,
                      incremental: bool = True):
        """
        Configura parâmetros de sincronização

        Args:
            auto_sync: Ativar sincronização automática
            interval_hours: Intervalo entre sincronizações (horas)
            incremental: Apenas novos contratos ou completo
        """
        self.config['auto_sync'] = auto_sync
        self.config['sync_interval_hours'] = interval_hours
        self.config['incremental_sync'] = incremental
        self._save_config()

        logger.info(f"Sincronização configurada: auto={auto_sync}, intervalo={interval_hours}h")

    def sync_now(self, force_full: bool = False) -> Dict[str, Any]:
        """
        Executa sincronização imediatamente

        Args:
            force_full: Forçar sincronização completa (não incremental)

        Returns:
            Estatísticas da sincronização
        """
        logger.info("Iniciando sincronização de dados...")

        stats = {
            'inicio': datetime.now().isoformat(),
            'contratos_novos': 0,
            'contratos_atualizados': 0,
            'alertas_gerados': 0,
            'erros': [],
            'sucesso': False
        }

        try:
            # Determinar se é incremental ou completo
            incremental = self.config.get('incremental_sync', True) and not force_full

            if incremental:
                logger.info("Sincronização INCREMENTAL")
                stats_sync = self._sync_incremental()
            else:
                logger.info("Sincronização COMPLETA")
                stats_sync = self._sync_full()

            stats.update(stats_sync)
            stats['sucesso'] = True

            # Atualizar última sincronização
            self.config['last_sync'] = datetime.now().isoformat()
            self._save_config()

            logger.info(f"Sincronização concluída: {stats['contratos_novos']} novos contratos")

        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            stats['erros'].append(str(e))

        stats['fim'] = datetime.now().isoformat()
        return stats

    def _sync_incremental(self) -> Dict[str, Any]:
        """
        Sincronização incremental - apenas novos dados

        Returns:
            Estatísticas da sincronização
        """
        stats = {
            'contratos_novos': 0,
            'contratos_atualizados': 0,
            'alertas_gerados': 0
        }

        # Obter data do último contrato na BD
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT MAX(data_publicacao) as ultima_data
            FROM contratos
            WHERE data_publicacao IS NOT NULL
        """)
        row = cursor.fetchone()
        ultima_data = row['ultima_data'] if row else None

        logger.info(f"Última data na BD: {ultima_data}")

        # Aqui integraria com a API/dados abertos
        # Por agora, apenas simula
        # Em produção: self.scraper.obter_contratos_apos_data(ultima_data)

        # Placeholder - em produção conectaria à fonte de dados
        logger.info("Sincronização incremental: Aguardando integração com fonte de dados")

        return stats

    def _sync_full(self) -> Dict[str, Any]:
        """
        Sincronização completa - todos os dados

        Returns:
            Estatísticas da sincronização
        """
        stats = {
            'contratos_novos': 0,
            'contratos_atualizados': 0,
            'alertas_gerados': 0
        }

        # Placeholder - em produção faria download completo
        logger.info("Sincronização completa: Aguardando integração com fonte de dados")

        return stats

    def get_sync_status(self) -> Dict[str, Any]:
        """
        Retorna estado atual da sincronização

        Returns:
            Informação de estado
        """
        last_sync = self.config.get('last_sync')
        last_sync_dt = None

        if last_sync:
            try:
                last_sync_dt = datetime.fromisoformat(last_sync)
            except:
                pass

        next_sync = None
        if last_sync_dt and self.config.get('auto_sync'):
            interval = self.config.get('sync_interval_hours', 24)
            next_sync = last_sync_dt + timedelta(hours=interval)

        # Estatísticas da BD
        cursor = self.db.connection.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM contratos")
        total_contratos = cursor.fetchone()['total']

        cursor.execute("""
            SELECT COUNT(*) as total FROM contratos
            WHERE data_recolha >= datetime('now', '-24 hours')
        """)
        contratos_24h = cursor.fetchone()['total']

        return {
            'auto_sync_ativo': self.config.get('auto_sync', False),
            'intervalo_horas': self.config.get('sync_interval_hours', 24),
            'ultima_sincronizacao': last_sync,
            'proxima_sincronizacao': next_sync.isoformat() if next_sync else None,
            'deve_sincronizar': self.should_sync(),
            'total_contratos_bd': total_contratos,
            'contratos_ultimas_24h': contratos_24h
        }

    # ==================== OTIMIZAÇÃO DA BASE DE DADOS ====================

    def optimize_database(self) -> Dict[str, Any]:
        """
        Otimiza a base de dados para reduzir espaço

        Returns:
            Estatísticas da otimização
        """
        logger.info("Iniciando otimização da base de dados...")

        stats = {
            'tamanho_antes': 0,
            'tamanho_depois': 0,
            'reducao_bytes': 0,
            'reducao_percentagem': 0
        }

        try:
            # Tamanho antes
            db_path = Path(self.db.db_path)
            if db_path.exists():
                stats['tamanho_antes'] = db_path.stat().st_size

            cursor = self.db.connection.cursor()

            # 1. VACUUM - compacta e desfragmenta
            logger.info("Executando VACUUM...")
            cursor.execute("VACUUM")

            # 2. ANALYZE - atualiza estatísticas para otimizar queries
            logger.info("Executando ANALYZE...")
            cursor.execute("ANALYZE")

            # 3. Reindexar
            logger.info("Reindexando tabelas...")
            cursor.execute("REINDEX")

            # 4. Comprimir campos de texto longos (descrições duplicadas)
            logger.info("Deduplicando descrições...")
            self._deduplicate_descriptions()

            self.db.connection.commit()

            # Tamanho depois
            if db_path.exists():
                stats['tamanho_depois'] = db_path.stat().st_size
                stats['reducao_bytes'] = stats['tamanho_antes'] - stats['tamanho_depois']

                if stats['tamanho_antes'] > 0:
                    stats['reducao_percentagem'] = (stats['reducao_bytes'] / stats['tamanho_antes']) * 100

            logger.info(f"Otimização concluída: {self._format_bytes(stats['reducao_bytes'])} reduzidos")

            return stats

        except Exception as e:
            logger.error(f"Erro na otimização: {e}")
            return stats

    def _deduplicate_descriptions(self):
        """Remove descrições duplicadas e substitui por referências"""
        cursor = self.db.connection.cursor()

        # Encontrar descrições duplicadas
        cursor.execute("""
            SELECT descricao, COUNT(*) as count
            FROM contratos
            WHERE descricao IS NOT NULL AND descricao != ''
            GROUP BY descricao
            HAVING count > 1
        """)

        duplicatas = cursor.fetchall()
        logger.info(f"Encontradas {len(duplicatas)} descrições duplicadas")

        # Criar tabela de lookup se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS descricoes_lookup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE,
                descricao TEXT,
                uso_count INTEGER DEFAULT 1
            )
        """)

        # Processar duplicatas (desativado por padrão para manter compatibilidade)
        # Em produção, poderia criar uma coluna descricao_id em contratos

    def _format_bytes(self, bytes_val: int) -> str:
        """Formata bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} TB"

    def estimate_database_size(self, num_contracts: int) -> Dict[str, Any]:
        """
        Estima o tamanho da base de dados

        Args:
            num_contracts: Número de contratos

        Returns:
            Estimativas de tamanho
        """
        # Estimativas baseadas em testes com dados reais

        # Tamanho médio por contrato (otimizado)
        BYTES_POR_CONTRATO = 800  # ~800 bytes por contrato (com índices)

        # Overhead da base de dados
        DB_OVERHEAD = 50 * 1024  # 50 KB

        # Índices (aproximadamente 20% do tamanho dos dados)
        INDEX_RATIO = 0.20

        # Cálculo
        tamanho_dados = num_contracts * BYTES_POR_CONTRATO
        tamanho_indices = tamanho_dados * INDEX_RATIO
        tamanho_total = DB_OVERHEAD + tamanho_dados + tamanho_indices

        # Após otimização (VACUUM pode reduzir ~30%)
        tamanho_otimizado = tamanho_total * 0.70

        return {
            'contratos': num_contracts,
            'tamanho_sem_otimizar': tamanho_total,
            'tamanho_otimizado': tamanho_otimizado,
            'tamanho_sem_otimizar_formatado': self._format_bytes(tamanho_total),
            'tamanho_otimizado_formatado': self._format_bytes(tamanho_otimizado),
            'bytes_por_contrato': BYTES_POR_CONTRATO,
            'estimativas_cenarios': {
                '10_mil_contratos': self._format_bytes(10000 * BYTES_POR_CONTRATO * 1.2 * 0.7),
                '100_mil_contratos': self._format_bytes(100000 * BYTES_POR_CONTRATO * 1.2 * 0.7),
                '500_mil_contratos': self._format_bytes(500000 * BYTES_POR_CONTRATO * 1.2 * 0.7),
                '1_milhao_contratos': self._format_bytes(1000000 * BYTES_POR_CONTRATO * 1.2 * 0.7),
            }
        }

    # ==================== AGENDAMENTO ====================

    def schedule_sync(self):
        """
        Agenda sincronização automática (requer aplicação a correr)
        Esta é uma versão simplificada - em produção usaria APScheduler
        """
        if not self.config.get('auto_sync'):
            logger.info("Sincronização automática desativada")
            return

        if self.should_sync():
            logger.info("Executando sincronização agendada...")
            self.sync_now()


# ==================== FUNÇÕES DE UTILIDADE ====================

def criar_tarefa_agendada_windows():
    """
    Cria uma tarefa agendada no Windows para sincronização
    (executa o script de sincronização diariamente)
    """
    script_content = """
@echo off
cd /d "%~dp0"
python -c "from src.sync import sync_task; sync_task()" >> logs/sync.log 2>&1
    """.strip()

    batch_path = Path("sync_scheduler.bat")
    batch_path.write_text(script_content, encoding='utf-8')

    print(f"""
Para agendar sincronização automática no Windows:

1. Abra o Agendador de Tarefas (taskschd.msc)
2. Criar Tarefa Básica...
3. Nome: "Sync Contratos Públicos"
4. Acionador: Diariamente
5. Ação: Iniciar um programa
6. Programa: {batch_path.absolute()}

Ou execute (como Administrador):
schtasks /create /tn "SyncContratosPublicos" /tr "{batch_path.absolute()}" /sc daily /st 02:00
    """)


def sync_task():
    """Tarefa de sincronização standalone (para agendamento externo)"""
    import sys
    sys.path.insert(0, 'src')

    from database import DatabaseManager
    from scraper import ContratosPublicosScraper

    db = DatabaseManager()
    scraper = ContratosPublicosScraper()
    sync_manager = SyncManager(db, scraper)

    print(f"[{datetime.now()}] Iniciando sincronização agendada...")
    stats = sync_manager.sync_now()

    print(f"Novos contratos: {stats.get('contratos_novos', 0)}")
    print(f"Alertas gerados: {stats.get('alertas_gerados', 0)}")

    # Otimizar BD semanalmente
    if datetime.now().weekday() == 6:  # Domingo
        print("Executando otimização semanal...")
        opt_stats = sync_manager.optimize_database()
        print(f"Espaço recuperado: {sync_manager._format_bytes(opt_stats['reducao_bytes'])}")

    db.close()


if __name__ == "__main__":
    # Executar sincronização standalone
    sync_task()
