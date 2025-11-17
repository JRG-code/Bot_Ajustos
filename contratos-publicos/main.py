#!/usr/bin/env python3
"""
Monitor de Contratos Públicos Portugueses
Aplicação Desktop para monitorizar contratos do BASE.gov.pt

Autor: Sistema de Monitorização
Data: 2025
"""

import sys
import os
import logging
from pathlib import Path

# Adicionar o diretório src ao PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def setup_logging():
    """Configura o sistema de logging"""
    # Criar diretório de logs se não existir
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    # Configurar formato de logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Configurar handlers
    handlers = [
        logging.FileHandler(log_dir / 'app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]

    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )

    # Configurar níveis para bibliotecas externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    dependencias = {
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl',
    }

    faltando = []

    for modulo, nome_pip in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltando.append(nome_pip)

    if faltando:
        print("=" * 60)
        print("ERRO: Dependências em falta!")
        print("=" * 60)
        print("\nAs seguintes bibliotecas precisam ser instaladas:")
        for dep in faltando:
            print(f"  • {dep}")
        print("\nPara instalar todas as dependências, execute:")
        print("  pip install -r requirements.txt")
        print("=" * 60)
        return False

    return True


def criar_diretorios():
    """Cria os diretórios necessários para a aplicação"""
    diretorios = [
        'data',
        'logs',
        'exports'
    ]

    for diretorio in diretorios:
        Path(diretorio).mkdir(exist_ok=True)


def main():
    """Função principal da aplicação"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║    MONITOR DE CONTRATOS PÚBLICOS PORTUGUESES                  ║
║    Base de Dados: BASE.gov.pt                                 ║
║                                                                ║
║    Versão 1.0 - 2025                                          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)

    # Verificar dependências
    print("A verificar dependências...")
    if not verificar_dependencias():
        sys.exit(1)

    print("✓ Dependências verificadas\n")

    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Iniciando Monitor de Contratos Públicos")
    logger.info("=" * 60)

    # Criar diretórios necessários
    criar_diretorios()
    logger.info("Diretórios criados/verificados")

    try:
        # Importar e iniciar GUI
        import tkinter as tk
        from gui import ContratosPublicosGUI

        logger.info("A iniciar interface gráfica...")

        # Criar janela principal
        root = tk.Tk()

        # Iniciar aplicação
        app = ContratosPublicosGUI(root)

        logger.info("Aplicação iniciada com sucesso")

        # Loop principal
        root.mainloop()

        logger.info("Aplicação encerrada")

    except ImportError as e:
        logger.error(f"Erro ao importar módulos: {e}")
        print(f"\nERRO: {e}")
        print("\nCertifique-se de que todos os módulos estão no diretório 'src/'")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        print(f"\nERRO FATAL: {e}")
        print("\nConsulte o ficheiro logs/app.log para mais detalhes")
        sys.exit(1)


if __name__ == "__main__":
    main()
