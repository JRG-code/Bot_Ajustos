#!/usr/bin/env python3
"""
API endpoint simples para verificação de atualizações
Pode ser usado por plugins externos (como no Hostinger)

Uso:
    python3 update_check_api.py

Retorna JSON com informações de atualização:
{
    "current_version": "1.0.3",
    "latest_version": "1.0.3",
    "update_available": false,
    "download_url": "",
    "release_notes": ""
}
"""

import sys
import json
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from updater import get_update_info_json

if __name__ == '__main__':
    # Obter informações de atualização
    update_info = get_update_info_json()

    # Retornar como JSON
    print(json.dumps(update_info, indent=2, ensure_ascii=False))
