"""
Módulo de verificação e atualização automática
Verifica GitHub Releases para novas versões
"""

import requests
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Configuração do repositório GitHub
GITHUB_REPO = "JRG-code/Bot_Ajustos"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# Versão atual do aplicativo
def get_current_version() -> str:
    """
    Obtém a versão atual do aplicativo
    Lê do arquivo version.txt
    """
    try:
        version_file = Path(__file__).parent.parent / "version.txt"
        if version_file.exists():
            return version_file.read_text().strip()
        else:
            logger.warning("Arquivo version.txt não encontrado")
            return "1.0.0"
    except Exception as e:
        logger.error(f"Erro ao ler versão: {e}")
        return "1.0.0"

def check_for_updates() -> Optional[Dict[str, Any]]:
    """
    Verifica se há atualizações disponíveis no GitHub

    Returns:
        Dict com informações da atualização ou None se não houver
        {
            'version': str,
            'download_url': str,
            'release_notes': str,
            'published_at': str
        }
    """
    try:
        current_version = get_current_version()
        logger.info(f"Versão atual: {current_version}")

        # Fazer requisição à API do GitHub
        response = requests.get(GITHUB_API_URL, timeout=10)

        if response.status_code != 200:
            logger.error(f"Erro ao consultar GitHub API: {response.status_code}")
            return None

        release_data = response.json()

        # Extrair informações da release
        latest_version = release_data.get('tag_name', '').lstrip('v')
        release_notes = release_data.get('body', '')
        published_at = release_data.get('published_at', '')
        download_url = release_data.get('html_url', '')

        # Verificar se há assets (ficheiros) disponíveis
        assets = release_data.get('assets', [])
        if assets:
            # Procurar por ficheiro .zip ou .exe
            for asset in assets:
                if asset.get('name', '').endswith(('.zip', '.exe')):
                    download_url = asset.get('browser_download_url', download_url)
                    break

        logger.info(f"Versão mais recente no GitHub: {latest_version}")

        # Comparar versões
        if is_newer_version(current_version, latest_version):
            logger.info(f"Nova versão disponível: {latest_version}")
            return {
                'version': latest_version,
                'download_url': download_url,
                'release_notes': release_notes,
                'published_at': published_at,
                'current_version': current_version
            }
        else:
            logger.info("Aplicação está atualizada")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede ao verificar atualizações: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro ao verificar atualizações: {e}")
        return None

def is_newer_version(current: str, latest: str) -> bool:
    """
    Compara duas versões no formato semver (X.Y.Z)

    Args:
        current: Versão atual (ex: "1.0.0")
        latest: Versão mais recente (ex: "1.0.1")

    Returns:
        True se latest é mais recente que current
    """
    try:
        # Limpar e dividir versões
        current_parts = [int(x) for x in current.replace('v', '').split('.')]
        latest_parts = [int(x) for x in latest.replace('v', '').split('.')]

        # Garantir que ambas têm 3 partes (major.minor.patch)
        while len(current_parts) < 3:
            current_parts.append(0)
        while len(latest_parts) < 3:
            latest_parts.append(0)

        # Comparar
        for i in range(3):
            if latest_parts[i] > current_parts[i]:
                return True
            elif latest_parts[i] < current_parts[i]:
                return False

        return False  # Versões são iguais

    except Exception as e:
        logger.error(f"Erro ao comparar versões: {e}")
        return False

def get_update_info_json() -> Dict[str, Any]:
    """
    Retorna informações de atualização em formato JSON
    Para uso por plugins externos

    Returns:
        {
            'current_version': str,
            'latest_version': str,
            'update_available': bool,
            'download_url': str,
            'release_notes': str
        }
    """
    current_version = get_current_version()
    update_info = check_for_updates()

    if update_info:
        return {
            'current_version': current_version,
            'latest_version': update_info['version'],
            'update_available': True,
            'download_url': update_info['download_url'],
            'release_notes': update_info['release_notes'],
            'published_at': update_info['published_at']
        }
    else:
        return {
            'current_version': current_version,
            'latest_version': current_version,
            'update_available': False,
            'download_url': '',
            'release_notes': ''
        }


if __name__ == '__main__':
    # Teste do módulo
    print("=== Monitor de Contratos Públicos - Update Checker ===")
    print(f"Versão atual: {get_current_version()}")
    print("\nVerificando atualizações no GitHub...")

    update = check_for_updates()

    if update:
        print(f"\n✓ Nova versão disponível: {update['version']}")
        print(f"  Download: {update['download_url']}")
        print(f"\nNotas da versão:\n{update['release_notes'][:200]}...")
    else:
        print("\n✓ Aplicação está atualizada!")

    print("\n=== Informações JSON ===")
    import json
    print(json.dumps(get_update_info_json(), indent=2))
