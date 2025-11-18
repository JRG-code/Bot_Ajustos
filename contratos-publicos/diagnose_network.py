#!/usr/bin/env python3
"""
Script de diagnóstico avançado para identificar tipo de bloqueio
Detecta: Cloudflare, firewall local, proxy, WAF, etc.
"""

import requests
import socket
import sys
from urllib.parse import urlparse

print("=" * 80)
print("DIAGNÓSTICO AVANÇADO DE REDE - Portal BASE")
print("=" * 80)

# ============================================================================
# TESTE 1: DNS Resolution
# ============================================================================
print("\n1. TESTE DE DNS")
print("-" * 80)

hosts_to_check = [
    "www.base.gov.pt",
    "dados.gov.pt",
    "google.com"  # Controle
]

dns_ok = False
for host in hosts_to_check:
    try:
        ip = socket.gethostbyname(host)
        print(f"  ✓ {host} → {ip}")
        if host == "google.com":
            dns_ok = True
    except socket.gaierror as e:
        print(f"  ✗ {host} → ERRO DNS: {e}")

if not dns_ok:
    print("\n  ⚠️  PROBLEMA: DNS não está a resolver domínios!")
    print("     Causa provável: Sem acesso à internet ou DNS bloqueado")
    sys.exit(1)

# ============================================================================
# TESTE 2: Conectividade TCP
# ============================================================================
print("\n2. TESTE DE CONECTIVIDADE TCP")
print("-" * 80)

tcp_tests = [
    ("www.base.gov.pt", 443),
    ("www.base.gov.pt", 80),
    ("dados.gov.pt", 443),
    ("google.com", 443),  # Controle
]

tcp_ok = False
for host, port in tcp_tests:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"  ✓ {host}:{port} → CONECTADO")
            if host == "google.com":
                tcp_ok = True
        else:
            print(f"  ✗ {host}:{port} → RECUSADO (código {result})")
    except Exception as e:
        print(f"  ✗ {host}:{port} → ERRO: {e}")

if not tcp_ok:
    print("\n  ⚠️  PROBLEMA: Conexões TCP estão bloqueadas!")
    print("     Causa provável: Firewall bloqueando tráfego HTTPS")
    sys.exit(1)

# ============================================================================
# TESTE 3: Detecção de Cloudflare
# ============================================================================
print("\n3. DETECÇÃO DE CLOUDFLARE / WAF")
print("-" * 80)

def check_cloudflare(url):
    """Verifica se site usa Cloudflare"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=False)
        headers = response.headers

        # Sinais de Cloudflare
        cloudflare_signs = []

        if 'CF-RAY' in headers or 'cf-ray' in headers:
            cloudflare_signs.append("Header CF-RAY detectado")
        if 'cloudflare' in headers.get('Server', '').lower():
            cloudflare_signs.append("Server: cloudflare")
        if 'CF-Cache-Status' in headers:
            cloudflare_signs.append("Header CF-Cache-Status")

        return cloudflare_signs, response.status_code
    except Exception as e:
        return [], str(e)

for url in ["https://www.base.gov.pt", "https://dados.gov.pt"]:
    signs, status = check_cloudflare(url)
    print(f"\n  URL: {url}")
    print(f"  Status: {status}")
    if signs:
        print(f"  ✓ CLOUDFLARE DETECTADO:")
        for sign in signs:
            print(f"    - {sign}")
    else:
        print(f"  ℹ  Cloudflare não detectado (ou bloqueio antes do Cloudflare)")

# ============================================================================
# TESTE 4: Diferentes User-Agents
# ============================================================================
print("\n4. TESTE DE USER-AGENTS DIFERENTES")
print("-" * 80)

user_agents = [
    ("Python/requests", requests.utils.default_headers()['User-Agent']),
    ("Chrome", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    ("Firefox", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"),
    ("Edge", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"),
    ("Safari", "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"),
]

url = "https://www.base.gov.pt"
for name, ua in user_agents:
    try:
        response = requests.get(url, headers={'User-Agent': ua}, timeout=5)
        print(f"  {name:15s} → Status {response.status_code} ({len(response.content)} bytes)")
    except Exception as e:
        print(f"  {name:15s} → ERRO: {e}")

# ============================================================================
# TESTE 5: Bypass de Cloudflare
# ============================================================================
print("\n5. TENTATIVAS DE BYPASS")
print("-" * 80)

def try_cloudflare_bypass(url):
    """Tenta diferentes técnicas de bypass"""

    techniques = [
        {
            "name": "Headers completos de browser",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
        },
        {
            "name": "Session com cookies",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            },
            "use_session": True
        },
        {
            "name": "Sem verificação SSL",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            },
            "verify": False
        },
    ]

    for tech in techniques:
        print(f"\n  Técnica: {tech['name']}")
        try:
            if tech.get('use_session'):
                session = requests.Session()
                response = session.get(url, headers=tech['headers'], timeout=10)
            else:
                verify = tech.get('verify', True)
                response = requests.get(url, headers=tech['headers'], timeout=10, verify=verify)

            print(f"    Status: {response.status_code}")
            print(f"    Tamanho: {len(response.content)} bytes")

            # Verificar se é HTML ou acesso negado
            content_start = response.text[:100].lower()
            if 'access denied' in content_start or 'forbidden' in content_start:
                print(f"    ✗ BLOQUEADO: Access Denied")
            elif '<html' in content_start:
                print(f"    ⚠️  Retornou HTML (esperado CSV)")
            elif response.status_code == 200:
                print(f"    ✓ SUCESSO!")

        except requests.exceptions.SSLError as e:
            print(f"    ✗ ERRO SSL: {e}")
        except Exception as e:
            print(f"    ✗ ERRO: {type(e).__name__}: {e}")

try_cloudflare_bypass("https://www.base.gov.pt/Base4/pt/resultados/?type=csv_contratos")

# ============================================================================
# TESTE 6: Proxy Detection
# ============================================================================
print("\n6. DETECÇÃO DE PROXY")
print("-" * 80)

try:
    # Verificar se há proxy configurado
    session = requests.Session()
    proxies = session.proxies or requests.utils.get_environ_proxies(session.trust_env)

    if proxies:
        print("  ⚠️  PROXY DETECTADO:")
        for key, value in proxies.items():
            print(f"    {key}: {value}")
    else:
        print("  ✓ Nenhum proxy configurado")

except Exception as e:
    print(f"  ✗ Erro ao verificar proxy: {e}")

# ============================================================================
# TESTE 7: Verificar IP público
# ============================================================================
print("\n7. IP PÚBLICO E LOCALIZAÇÃO")
print("-" * 80)

try:
    response = requests.get("https://api.ipify.org?format=json", timeout=5)
    if response.status_code == 200:
        ip = response.json().get('ip')
        print(f"  IP público: {ip}")

        # Tentar obter info do IP
        try:
            info_response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
            if info_response.status_code == 200:
                info = info_response.json()
                print(f"  País: {info.get('country_name')}")
                print(f"  Cidade: {info.get('city')}")
                print(f"  ISP: {info.get('org')}")
        except:
            pass
    else:
        print("  ✗ Não foi possível obter IP público")
except Exception as e:
    print(f"  ✗ Erro: {e}")

# ============================================================================
# CONCLUSÕES E RECOMENDAÇÕES
# ============================================================================
print("\n" + "=" * 80)
print("CONCLUSÕES E RECOMENDAÇÕES")
print("=" * 80)

print("""
Baseado nos testes acima:

1. Se TODOS retornaram 403 "Access Denied":
   └─ CAUSA: Cloudflare ou WAF está bloqueando pedidos
   └─ SOLUÇÃO: Implementar bypass com cloudscraper ou selenium

2. Se DNS falhou:
   └─ CAUSA: Sem internet ou DNS bloqueado
   └─ SOLUÇÃO: Verificar conexão de rede

3. Se TCP falhou mas DNS OK:
   └─ CAUSA: Firewall bloqueando portas 80/443
   └─ SOLUÇÃO: Abrir portas no firewall

4. Se diferentes User-Agents têm resultados diferentes:
   └─ CAUSA: WAF bloqueando bots
   └─ SOLUÇÃO: Usar headers de browser real

5. Se proxy foi detectado:
   └─ CAUSA: Proxy corporativo pode estar bloqueando
   └─ SOLUÇÃO: Configurar bypass de proxy ou whitelist

PRÓXIMOS PASSOS:
- Se for Cloudflare: Posso adicionar biblioteca 'cloudscraper'
- Se for firewall: Precisas abrir as portas
- Se for proxy: Configurar exceções no proxy

Executar novamente este script após cada mudança para verificar progresso.
""")

print("=" * 80)
