# Sistema de Atualização Automática

Este projeto inclui um sistema de verificação automática de atualizações via GitHub Releases.

## Como Funciona

1. **Versão atual**: Armazenada em `version.txt`
2. **GitHub Releases**: Verifica a tag mais recente no repositório
3. **Comparação**: Compara versões usando semantic versioning (X.Y.Z)

## Arquivos Importantes

- `version.txt` - Versão atual do aplicativo (ex: 1.0.3)
- `src/updater.py` - Módulo de verificação de atualizações
- `update_check_api.py` - Script standalone para plugins externos

## Uso na Aplicação GUI

Os utilizadores podem verificar atualizações via menu:
```
Menu > Ajuda > Verificar Atualizações
```

## Uso Programático (para plugins)

### Opção 1: Importar o módulo Python

```python
from src.updater import get_update_info_json

# Retorna dict com informações
info = get_update_info_json()
print(info['update_available'])  # True/False
print(info['latest_version'])     # "1.0.4"
```

### Opção 2: Script standalone (ideal para Hostinger)

```bash
python3 update_check_api.py
```

Retorna JSON:
```json
{
  "current_version": "1.0.3",
  "latest_version": "1.0.4",
  "update_available": true,
  "download_url": "https://github.com/JRG-code/Bot_Ajustos/releases/download/v1.0.4/release.zip",
  "release_notes": "- Adicionar visualização de ligações...",
  "published_at": "2025-01-15T10:30:00Z"
}
```

### Opção 3: Via HTTP (se configurar servidor web)

```bash
# No servidor
cd contratos-publicos
python3 -m http.server 8000

# Cliente consulta
curl http://localhost:8000/update_check_api.py | python3
```

## Como Criar uma Release no GitHub

1. Atualizar `version.txt` para nova versão (ex: `1.0.4`)
2. Commit e push das alterações
3. Criar release no GitHub:
   ```bash
   git tag v1.0.4
   git push origin v1.0.4
   ```
4. Ou criar via interface web:
   - Ir em "Releases" > "Draft a new release"
   - Tag: `v1.0.4`
   - Título: `Versão 1.0.4`
   - Descrição: Notas da versão
   - Anexar ficheiros (opcional): .zip, .exe, etc.
   - Publicar

## Formato de Versionamento

Usa **Semantic Versioning** (semver):
- `MAJOR.MINOR.PATCH` (ex: 1.0.3)
- MAJOR: Mudanças incompatíveis
- MINOR: Novas funcionalidades compatíveis
- PATCH: Correções de bugs

Exemplos:
- `1.0.3` → `1.0.4`: Correção de bug
- `1.0.4` → `1.1.0`: Nova funcionalidade
- `1.1.0` → `2.0.0`: Mudança major incompatível

## Integração com Plugin do Hostinger

O plugin no Hostinger pode chamar o script e processar o JSON:

```php
<?php
// Exemplo em PHP
$output = shell_exec('python3 /path/to/update_check_api.py');
$info = json_decode($output, true);

if ($info['update_available']) {
    echo "Nova versão disponível: " . $info['latest_version'];
    echo "<a href='" . $info['download_url'] . "'>Download</a>";
} else {
    echo "Versão atual: " . $info['current_version'];
}
?>
```

```python
# Exemplo em Python
import subprocess
import json

result = subprocess.run(
    ['python3', 'update_check_api.py'],
    capture_output=True,
    text=True
)

info = json.loads(result.stdout)
if info['update_available']:
    print(f"Nova versão: {info['latest_version']}")
```

## Testando o Sistema

```bash
# Testar módulo updater
cd contratos-publicos
python3 -c "from src.updater import *; print(get_current_version())"

# Testar verificação de atualizações
python3 -m src.updater

# Testar API standalone
python3 update_check_api.py
```

## Variáveis de Configuração

No arquivo `src/updater.py`:
- `GITHUB_REPO`: Repositório GitHub (default: "JRG-code/Bot_Ajustos")
- `GITHUB_API_URL`: URL da API do GitHub

## Resolução de Problemas

### "Nenhuma atualização encontrada" mas há nova release
- Verificar se a tag da release começa com 'v' (ex: v1.0.4)
- Verificar se o `version.txt` está atualizado no código
- Verificar conectividade com api.github.com

### Erro 403 ao consultar API
- GitHub limita requisições não autenticadas (60/hora)
- Adicionar token se necessário (ver documentação GitHub API)

### Plugin não detecta atualização
- Verificar se está a ler o `version.txt` correto
- Verificar logs do módulo updater
- Testar manualmente: `python3 update_check_api.py`
