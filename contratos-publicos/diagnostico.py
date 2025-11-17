#!/usr/bin/env python
"""
Lançador de DIAGNÓSTICO - Mostra erros em janela
Use este ficheiro para ver o que está errado
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Criar diretórios necessários
for diretorio in ['data', 'logs', 'exports']:
    Path(diretorio).mkdir(exist_ok=True)

# Configurar logging
import logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

print("="*60)
print("DIAGNÓSTICO - Monitor de Contratos Públicos")
print("="*60)

# Verificar dependências uma a uma
print("\n1. A verificar Python...")
print(f"   Python: {sys.version}")
print(f"   ✓ OK")

print("\n2. A verificar módulos necessários...")

dependencias = {
    'tkinter': 'Interface gráfica (incluído no Python)',
    'sqlite3': 'Base de dados (incluído no Python)',
    'requests': 'HTTP requests',
    'bs4': 'BeautifulSoup4 - parsing HTML',
    'pandas': 'Manipulação de dados',
    'openpyxl': 'Exportar para Excel',
    'tqdm': 'Barras de progresso'
}

faltando = []
for modulo, descricao in dependencias.items():
    try:
        __import__(modulo)
        print(f"   ✓ {modulo}: OK")
    except ImportError:
        print(f"   ✗ {modulo}: FALTA - {descricao}")
        faltando.append(modulo)

if faltando:
    print("\n" + "="*60)
    print("ERRO: Dependências em falta!")
    print("="*60)
    print("\nExecute este comando para instalar tudo:")
    print("   pip install -r requirements.txt")
    print("\nOu instale individualmente:")
    for dep in faltando:
        if dep not in ['tkinter', 'sqlite3']:
            print(f"   pip install {dep}")
    print("="*60)
    input("\nPressione ENTER para fechar...")
    sys.exit(1)

print("\n3. A verificar módulos da aplicação...")
try:
    from gui import ContratosPublicosGUI
    print("   ✓ gui.py: OK")
except ImportError as e:
    print(f"   ✗ gui.py: ERRO - {e}")
    print("\nERRO: Ficheiro gui.py não encontrado ou tem erros")
    print("Verifique se a pasta 'src/' existe e contém os ficheiros.")
    input("\nPressione ENTER para fechar...")
    sys.exit(1)

print("\n4. A iniciar interface gráfica...")

try:
    import tkinter as tk

    # Criar janela principal
    root = tk.Tk()

    print("   ✓ Janela criada")

    # Iniciar aplicação
    app = ContratosPublicosGUI(root)

    print("   ✓ Aplicação iniciada\n")
    print("="*60)
    print("SUCESSO! A abrir interface...")
    print("="*60)

    # Loop principal
    root.mainloop()

    print("\nAplicação encerrada normalmente")

except Exception as e:
    print(f"\n✗ ERRO FATAL: {e}")
    print(f"\nTipo de erro: {type(e).__name__}")

    import traceback
    print("\nDetalhes completos:")
    print(traceback.format_exc())

    # Tentar mostrar erro numa janela
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Erro ao Iniciar",
            f"Erro: {e}\n\nVeja os detalhes na consola ou em logs/app.log"
        )
    except:
        pass

    input("\nPressione ENTER para fechar...")
    sys.exit(1)
