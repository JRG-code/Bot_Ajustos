#!/usr/bin/env python3
"""
Lançador GUI para Monitor de Contratos Públicos
NOTA: Este ficheiro agora usa python3 normal (não pythonw) para melhor diagnóstico
"""

import sys
import os
from pathlib import Path

def main():
    """Função principal do launcher"""

    # Criar diretórios necessários PRIMEIRO
    try:
        for diretorio in ['data', 'logs', 'exports']:
            Path(diretorio).mkdir(exist_ok=True)
    except Exception as e:
        print(f"Erro ao criar diretórios: {e}")
        input("Pressione ENTER para fechar...")
        return 1

    # Adicionar o diretório src ao PYTHONPATH
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    # Configurar logging
    import logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    try:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('logs/app.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    except Exception as e:
        print(f"Erro ao configurar logging: {e}")
        logging.basicConfig(level=logging.INFO, format=log_format)

    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info("Iniciando Monitor de Contratos Públicos")
    logger.info("="*60)

    # Verificar Tkinter
    try:
        import tkinter as tk
        from tkinter import messagebox
        logger.info("✓ Tkinter disponível")
    except ImportError as e:
        logger.error(f"✗ Tkinter não disponível: {e}")
        print("\n" + "="*60)
        print("ERRO: Tkinter não está instalado!")
        print("="*60)
        print("\nO Tkinter é necessário para a interface gráfica.")
        print("Solução: Reinstale Python incluindo tkinter/tcl")
        print("\nNo Ubuntu/Debian: sudo apt-get install python3-tk")
        print("="*60)
        input("\nPressione ENTER para fechar...")
        return 1

    # Verificar dependências críticas
    dependencias_criticas = ['requests', 'bs4', 'pandas', 'openpyxl', 'tqdm']
    faltando = []

    for dep in dependencias_criticas:
        try:
            __import__(dep)
            logger.info(f"✓ {dep} disponível")
        except ImportError:
            logger.warning(f"✗ {dep} não encontrado")
            faltando.append(dep)

    if faltando:
        logger.warning(f"Dependências em falta: {faltando}")
        root = tk.Tk()
        root.withdraw()
        resposta = messagebox.askyesno(
            "Dependências em Falta",
            f"Algumas dependências não estão instaladas:\n{', '.join(faltando)}\n\n"
            f"A aplicação pode ter funcionalidades limitadas.\n\n"
            f"Deseja continuar mesmo assim?\n\n"
            f"Execute: pip install -r requirements.txt"
        )
        root.destroy()

        if not resposta:
            return 1

    # Importar GUI
    try:
        logger.info("A importar módulo GUI...")
        from gui import ContratosPublicosGUI
        logger.info("✓ Módulo GUI importado")
    except ImportError as e:
        logger.error(f"✗ Erro ao importar GUI: {e}", exc_info=True)
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Erro ao Carregar",
            f"Erro ao importar módulos:\n{e}\n\n"
            f"Verifique logs/app.log para detalhes."
        )
        root.destroy()
        input("\nPressione ENTER para fechar...")
        return 1

    # Iniciar aplicação
    try:
        logger.info("A criar janela principal...")
        root = tk.Tk()
        logger.info("✓ Janela criada")

        logger.info("A iniciar aplicação...")
        app = ContratosPublicosGUI(root)
        logger.info("✓ Aplicação iniciada com sucesso")

        logger.info("Entrando em loop principal...")
        root.mainloop()

        logger.info("Aplicação encerrada normalmente")
        return 0

    except Exception as e:
        logger.error(f"✗ Erro fatal: {e}", exc_info=True)

        # Guardar erro em ficheiro
        try:
            with open('logs/erro_launcher.txt', 'w', encoding='utf-8') as f:
                import traceback
                f.write("ERRO FATAL AO INICIAR APLICAÇÃO\n")
                f.write("="*60 + "\n\n")
                f.write(f"Erro: {e}\n")
                f.write(f"Tipo: {type(e).__name__}\n\n")
                f.write("Traceback completo:\n")
                f.write(traceback.format_exc())
        except:
            pass

        # Mostrar erro
        try:
            root = tk.Tk()
            root.withdraw()
            import traceback
            erro_msg = f"Erro fatal ao iniciar:\n\n{e}\n\n"
            erro_msg += f"Tipo: {type(e).__name__}\n\n"
            erro_msg += "Veja logs/erro_launcher.txt para detalhes completos"
            messagebox.showerror("Erro Fatal", erro_msg)
            root.destroy()
        except:
            pass

        input("\nPressione ENTER para fechar...")
        return 1


if __name__ == '__main__':
    sys.exit(main())
