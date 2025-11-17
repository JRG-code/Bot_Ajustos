# Como Abrir a Aplicação (Sem PowerShell)

Existem **3 formas** de abrir a aplicação sem ver janelas do PowerShell/CMD, como o GitHub Desktop:

---

## 🎯 Forma 1: Duplo Clique no Ficheiro .pyw (RECOMENDADO)

**Windows:**
1. Abra a pasta do projeto
2. **Duplo clique em `launcher.pyw`**
3. A aplicação abre diretamente, sem consola! ✨

> **Nota:** Ficheiros `.pyw` são Python GUI - abrem sem janela de console.

---

## 🎯 Forma 2: Duplo Clique no Ficheiro .bat

**Windows:**
1. **Duplo clique em `Abrir Contratos Publicos.bat`**
2. A aplicação abre sem console (usa `pythonw.exe`)

---

## 🎯 Forma 3: Criar Executável Standalone

**Para distribuir ou ter um .exe como app normal:**

```bash
# 1. Instalar PyInstaller
pip install pyinstaller pillow

# 2. Criar executável
python build_executable.py

# 3. O executável estará em dist/
# Windows: dist/ContratosPublicos.exe
# Mac: dist/ContratosPublicos.app
# Linux: dist/ContratosPublicos
```

**Vantagens do executável:**
- ✅ Funciona sem Python instalado
- ✅ Pode criar atalho no Desktop
- ✅ Abre como qualquer aplicação (GitHub Desktop, Chrome, etc.)
- ✅ Ficheiro único de ~80-120 MB

---

## 📌 Criar Atalho no Desktop

### Windows:

1. **Clique direito** em `launcher.pyw` ou `Abrir Contratos Publicos.bat`
2. **Enviar para > Desktop (criar atalho)**
3. Renomear o atalho para "Contratos Públicos"
4. Agora pode clicar no ícone do Desktop para abrir! 🎉

### Se usou o executável:

1. **Clique direito** em `dist/ContratosPublicos.exe`
2. **Enviar para > Desktop (criar atalho)**
3. Pronto! Funciona como qualquer app instalada

---

## ⚠️ NÃO Usar main.py

- **main.py** → Abre com console (PowerShell)
- **launcher.pyw** → Abre SEM console ✅

---

## 🔧 Troubleshooting

### **Problema:** Duplo clique no launcher.pyw não faz nada

**SOLUÇÃO RÁPIDA:**

1. **Duplo clique em `diagnostico.py`** ← Mostra exatamente o que está errado!

   O diagnóstico verifica:
   - ✓ Python instalado?
   - ✓ Todas as dependências instaladas?
   - ✓ Ficheiros do projeto existem?
   - ✓ Onde está o erro exato?

2. **Se faltar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Se continuar com problema:**
   - Veja `logs/app.log` (detalhes completos)
   - Veja `logs/erro_launcher.txt` (se existir)

### **Problema:** Python não encontrado

**Solução:**
- Instale Python 3.10+ de https://www.python.org/downloads/
- Durante instalação, marque ✅ "Add Python to PATH"
- Depois instale dependências: `pip install -r requirements.txt`

### **Problema:** "No module named 'tkinter'"

**Solução (Windows):**
- Reinstale Python marcando "tcl/tk and IDLE" durante instalação

**Solução (Linux):**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

---

## 📝 Resumo

| Ficheiro | Descrição | Console? |
|----------|-----------|----------|
| `launcher.pyw` | Lançador GUI direto | ❌ Não |
| `Abrir Contratos Publicos.bat` | Batch que usa pythonw | ❌ Não |
| `main.py` | Lançador com logs | ✅ Sim |
| `build_executable.py` | Cria .exe standalone | - |
| `dist/ContratosPublicos.exe` | Executável final | ❌ Não |

**Para usar diariamente:** Duplo clique em `launcher.pyw` ou criar atalho no Desktop! 🚀
