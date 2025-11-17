#!/usr/bin/env pythonw
"""
Lançador GUI para Monitor de Contratos Públicos
Ficheiro .pyw - Abre sem janela de console (como GitHub Desktop)
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Criar diretórios necessários
for diretorio in ['data', 'logs', 'exports']:
    Path(diretorio).mkdir(exist_ok=True)

# Configurar logging apenas para ficheiro (sem console)
import logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[logging.FileHandler('logs/app.log', encoding='utf-8')]
)

# Importar e iniciar GUI
import tkinter as tk
from tkinter import messagebox

try:
    from gui import ContratosPublicosGUI

    # Criar janela principal
    root = tk.Tk()

    # Iniciar aplicação
    app = ContratosPublicosGUI(root)

    # Loop principal
    root.mainloop()

except ImportError as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Erro de Dependências",
        f"Erro ao importar módulos: {e}\n\n"
        f"Execute: pip install -r requirements.txt"
    )

except Exception as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Erro Fatal",
        f"Erro: {e}\n\n"
        f"Consulte logs/app.log para detalhes"
    )
