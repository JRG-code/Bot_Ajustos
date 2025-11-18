#!/usr/bin/env python3
"""
Script de teste para debug do download do Portal BASE
Testa diferentes métodos de acesso ao portal
"""

import requests
import sys
from pathlib import Path

print("=" * 70)
print("TESTE DE CONEXÃO AO PORTAL BASE")
print("=" * 70)

# URLs para testar
urls_to_test = [
    "https://www.base.gov.pt",
    "https://www.base.gov.pt/Base4/pt/",
    "https://www.base.gov.pt/Base4/pt/resultados/",
    "https://dados.gov.pt",
]

print("\n1. Testando conectividade básica...")
print("-" * 70)

for url in urls_to_test:
    try:
        print(f"\n  Testando: {url}")
        response = requests.get(url, timeout=10, allow_redirects=True)
        print(f"  ✓ Status: {response.status_code}")
        print(f"  ✓ Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"  ✓ Tamanho: {len(response.content)} bytes")
        if response.history:
            print(f"  ℹ Redirects: {[r.url for r in response.history]}")
    except requests.exceptions.Timeout:
        print(f"  ✗ TIMEOUT após 10s")
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ ERRO DE CONEXÃO: {e}")
    except Exception as e:
        print(f"  ✗ ERRO: {e}")

print("\n" + "=" * 70)
print("\n2. Testando exportação CSV do Portal BASE...")
print("-" * 70)

# Testar diferentes formatos de parâmetros
test_configs = [
    {
        "nome": "Exportação básica",
        "url": "https://www.base.gov.pt/Base4/pt/resultados/",
        "params": {
            'type': 'csv_contratos',
        }
    },
    {
        "nome": "Com filtros completos",
        "url": "https://www.base.gov.pt/Base4/pt/resultados/",
        "params": {
            'type': 'csv_contratos',
            'texto': '',
            'tipo': '0',
            'tipocontrato': '0',
        }
    },
    {
        "nome": "Com ano específico (2024)",
        "url": "https://www.base.gov.pt/Base4/pt/resultados/",
        "params": {
            'type': 'csv_contratos',
            'ano': '2024',
        }
    },
    {
        "nome": "URL alternativo",
        "url": "https://www.base.gov.pt/base4/pt/resultados/",
        "params": {
            'type': 'csv_contratos',
        }
    },
]

for config in test_configs:
    print(f"\n  Teste: {config['nome']}")
    print(f"  URL: {config['url']}")
    print(f"  Params: {config['params']}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/csv,application/csv,text/plain,*/*',
        }

        response = requests.get(
            config['url'],
            params=config['params'],
            headers=headers,
            timeout=30,
            stream=True
        )

        print(f"  ✓ Status: {response.status_code}")
        print(f"  ✓ Content-Type: {response.headers.get('content-type', 'N/A')}")

        # Ler primeiros bytes para verificar conteúdo
        content_sample = b''
        for chunk in response.iter_content(chunk_size=1024):
            content_sample += chunk
            if len(content_sample) > 2048:
                break

        print(f"  ✓ Primeiros bytes recebidos: {len(content_sample)}")

        # Tentar decodificar início do conteúdo
        try:
            decoded = content_sample.decode('utf-8', errors='ignore')[:200]
            print(f"  ℹ Início do conteúdo:")
            print(f"    {decoded[:100]}...")

            # Verificar se parece CSV
            if ';' in decoded or ',' in decoded:
                print(f"  ✓ Parece ser CSV!")
            elif '<html' in decoded.lower() or '<!doctype' in decoded.lower():
                print(f"  ✗ É HTML, não CSV!")
            else:
                print(f"  ? Formato desconhecido")

        except Exception as e:
            print(f"  ✗ Erro ao decodificar: {e}")

    except requests.exceptions.Timeout:
        print(f"  ✗ TIMEOUT após 30s")
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ ERRO DE CONEXÃO: {e}")
    except Exception as e:
        print(f"  ✗ ERRO: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("\n3. Verificando dados.gov.pt...")
print("-" * 70)

try:
    print("\n  Acessando página principal...")
    response = requests.get("https://dados.gov.pt/pt/datasets/", timeout=10)
    print(f"  ✓ Status: {response.status_code}")

    # Procurar links de datasets
    if 'contrato' in response.text.lower():
        print(f"  ✓ Encontrou referências a 'contrato' na página")

except Exception as e:
    print(f"  ✗ ERRO: {e}")

print("\n" + "=" * 70)
print("\n4. Recomendações baseadas nos testes:")
print("-" * 70)

print("""
  Baseado nos resultados acima:

  - Se os testes retornaram HTML em vez de CSV:
    → O portal pode ter mudado a forma de exportação
    → Pode requerer autenticação ou session

  - Se houve timeout ou erro de conexão:
    → Verificar firewall/proxy
    → Portal pode estar bloqueando requests automáticos

  - Se retornou 403/401:
    → Portal requer autenticação
    → Pode estar a bloquear bots

  - Se funcionou:
    → Verificar porque não funciona na aplicação
    → Pode ser problema de threading ou GUI
""")

print("=" * 70)
print("FIM DOS TESTES")
print("=" * 70)
