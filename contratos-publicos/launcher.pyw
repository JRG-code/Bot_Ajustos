#!/usr/bin/env pythonw
"""
Lançador GUI para Monitor de Contratos Públicos
Ficheiro .pyw - Abre sem janela de console (como GitHub Desktop)
"""

import sys
import os
from pathlib import Path
import traceback

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

logger = logging.getLogger(__name__)
logger.info("="*60)
logger.info("Iniciando aplicação (launcher.pyw)")
logger.info("="*60)

# Importar e iniciar GUI
try:
    import tkinter as tk
    from tkinter import messagebox
    logger.info("Tkinter importado com sucesso")
except ImportError as e:
    # Tkinter não disponível - escrever no log e sair
    logger.error(f"Tkinter não disponível: {e}")
    with open('logs/erro_launcher.txt', 'w', encoding='utf-8') as f:
        f.write(f"ERRO: Tkinter não disponível\n")
        f.write(f"Detalhes: {e}\n\n")
        f.write("Solução: Reinstale Python incluindo tkinter/tcl\n")
    sys.exit(1)

try:
    logger.info("A importar módulo GUI...")
    from gui import ContratosPublicosGUI
    logger.info("Módulo GUI importado com sucesso")

    logger.info("A criar janela principal...")
    # Criar janela principal
    root = tk.Tk()
    logger.info("Janela criada")

    logger.info("A iniciar aplicação...")
    # Iniciar aplicação
    app = ContratosPublicosGUI(root)
    logger.info("Aplicação iniciada com sucesso - entrando em loop principal")

    # Loop principal
    root.mainloop()

    logger.info("Aplicação encerrada normalmente")

except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}", exc_info=True)
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Erro de Dependências",
            f"Erro ao importar módulos:\n{e}\n\n"
            f"Execute: pip install -r requirements.txt\n\n"
            f"Veja logs/app.log para mais detalhes"
        )
    except:
        pass

except Exception as e:
    logger.error(f"Erro fatal: {e}", exc_info=True)
    try:
        root = tk.Tk()
        root.withdraw()
        erro_msg = f"Erro: {e}\n\n"
        erro_msg += f"Tipo: {type(e).__name__}\n\n"
        erro_msg += f"Consulte logs/app.log para detalhes completos"
        messagebox.showerror("Erro Fatal", erro_msg)
    except:
        # Se nem a messagebox funcionar, escrever erro em ficheiro
        with open('logs/erro_launcher.txt', 'w', encoding='utf-8') as f:
            f.write(f"ERRO FATAL ao iniciar aplicação\n")
            f.write(f"Erro: {e}\n")
            f.write(f"Tipo: {type(e).__name__}\n\n")
            f.write("Traceback completo:\n")
            f.write(traceback.format_exc())
