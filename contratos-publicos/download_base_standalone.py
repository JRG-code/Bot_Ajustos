#!/usr/bin/env python3
"""
Script standalone para descarregar dados do Portal BASE
EXECUTAR NO SEU COMPUTADOR LOCAL (não no servidor)

Uso:
    python3 download_base_standalone.py

O script irá descarregar todos os contratos disponíveis (sem limite de 500)
"""

import requests
import sys
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("DOWNLOAD DE CONTRATOS DO PORTAL BASE")
print("=" * 80)

# Verificar conectividade
print("\n1. Verificando conexão à internet...")
try:
    test = requests.get("https://google.com", timeout=5)
    print("   ✓ Internet OK")
except:
    print("   ✗ SEM INTERNET! Execute este script no seu computador, não no servidor.")
    sys.exit(1)

# Perguntar ano
print("\n2. Configuração do download:")
print("   Deseja filtrar por ano? (deixe vazio para TODOS os anos)")
ano_input = input("   Ano (2012-2025) ou Enter para todos: ").strip()

ano = None
if ano_input:
    try:
        ano = int(ano_input)
        if ano < 2012 or ano > 2025:
            print("   ⚠️  Ano inválido, usando TODOS os anos")
            ano = None
    except:
        print("   ⚠️  Entrada inválida, usando TODOS os anos")
        ano = None

# URLs para tentar
urls_to_try = [
    "https://www.base.gov.pt/Base4/pt/resultados/",
    "https://www.base.gov.pt/base4/pt/resultados/",
]

params = {
    'type': 'csv_contratos',
    'texto': '',
    'tipo': '0',
    'tipocontrato': '0',
}

if ano:
    params['ano'] = str(ano)
    print(f"   → Filtrando por ano: {ano}")
else:
    print(f"   → Sem filtro de ano (TODOS)")

# Headers de browser real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Accept': 'text/csv,application/csv,text/html,*/*',
    'Accept-Language': 'pt-PT,pt;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

print("\n3. Conectando ao Portal BASE...")

response = None
for url in urls_to_try:
    try:
        print(f"   Tentando: {url}")
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=180,  # 3 minutos
            stream=True
        )

        if response.status_code == 200:
            print(f"   ✓ Conectado!")
            break
        else:
            print(f"   ✗ Status {response.status_code}")
            response = None

    except Exception as e:
        print(f"   ✗ Erro: {e}")
        continue

if not response:
    print("\n✗ FALHA: Não foi possível conectar ao Portal BASE")
    print("\nPossíveis causas:")
    print("  - Portal BASE está em manutenção")
    print("  - Mudaram a estrutura do site")
    print("  - Requerem autenticação agora")
    print("\nAlternativa: Aceder manualmente a https://www.base.gov.pt")
    sys.exit(1)

# Criar pasta data se não existir
Path("data").mkdir(exist_ok=True)

# Nome do ficheiro
sufixo = f"_{ano}" if ano else "_todos"
output_file = Path(f"data/contratos_base{sufixo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

print(f"\n4. A descarregar para: {output_file}")

# Download com progresso
total_size = int(response.headers.get('content-length', 0))
downloaded = 0

with open(output_file, 'wb') as f:
    if total_size > 0:
        print(f"   Tamanho total: {total_size / (1024*1024):.2f} MB")

    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
            downloaded += len(chunk)

            # Mostrar progresso a cada MB
            if downloaded % (1024 * 1024) == 0:
                mb = downloaded / (1024 * 1024)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"   Descarregado: {mb:.1f} MB ({percent:.1f}%)")
                else:
                    print(f"   Descarregado: {mb:.1f} MB")

file_size = output_file.stat().st_size

if file_size == 0:
    print("\n✗ ERRO: Ficheiro vazio!")
    output_file.unlink()
    sys.exit(1)

print(f"\n✓ SUCESSO!")
print(f"  Ficheiro: {output_file}")
print(f"  Tamanho: {file_size / (1024*1024):.2f} MB")

# Verificar conteúdo
try:
    with open(output_file, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if ';' in first_line or ',' in first_line:
            num_colunas = len(first_line.split(';' if ';' in first_line else ','))
            print(f"  Colunas: {num_colunas}")
            print(f"  ✓ Parece ser CSV válido!")
        else:
            print(f"  ⚠️  Aviso: Pode não ser CSV")
            print(f"  Primeira linha: {first_line[:100]}")
except Exception as e:
    print(f"  ⚠️  Não foi possível verificar conteúdo: {e}")

print("\n" + "=" * 80)
print("PRÓXIMO PASSO:")
print("  1. Copiar o ficheiro CSV para o servidor (se aplicável)")
print("  2. Ou importar localmente usando 'Ficheiro CSV Local'")
print("=" * 80)
