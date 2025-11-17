#!/usr/bin/env python3
"""
Test script para verificar a funcionalidade de progresso sem GUI
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from scraper import ContratosPublicosScraper

def progress_callback(percentage, message):
    """Callback para imprimir progresso"""
    print(f"[{percentage:6.2f}%] {message}")

def test_progress():
    """Testa a funcionalidade de progresso"""
    print("=" * 60)
    print("Teste de Progresso do Scraper")
    print("=" * 60)

    scraper = ContratosPublicosScraper()

    # Test CSV path
    csv_path = Path("data/test_contratos.csv")

    if not csv_path.exists():
        print(f"ERRO: Ficheiro de teste não encontrado: {csv_path}")
        return 1

    print(f"\nA testar parse de CSV com callback de progresso...")
    print(f"Ficheiro: {csv_path}\n")

    # Parse with progress callback
    contratos = scraper.parse_csv_contratos(
        csv_path,
        limit=None,
        size_limit_mb=None,
        progress_callback=progress_callback
    )

    print(f"\n✓ Parse concluído: {len(contratos)} contratos encontrados")

    # Test processing with mock database (without actually inserting)
    print(f"\nA testar validação de contratos...")
    validos = 0
    invalidos = 0
    for contrato in contratos:
        if scraper.validar_contrato(contrato):
            validos += 1
        else:
            invalidos += 1

    print(f"\n✓ Validação concluída:")
    print(f"  - Válidos: {validos}")
    print(f"  - Inválidos: {invalidos}")

    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

    return 0

if __name__ == '__main__':
    sys.exit(test_progress())
