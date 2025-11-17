#!/usr/bin/env python3
"""
Script de Teste da Aplicação
Verifica se todos os módulos estão funcionais
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("=" * 60)
    print("TESTE 1: Importação de Módulos")
    print("=" * 60)

    modulos = [
        'database',
        'scraper',
        'entities',
        'alerts'
    ]

    sucesso = True

    for modulo in modulos:
        try:
            __import__(modulo)
            print(f"✓ {modulo}.py - OK")
        except Exception as e:
            print(f"✗ {modulo}.py - ERRO: {e}")
            sucesso = False

    return sucesso


def test_database():
    """Testa a criação e operações básicas da base de dados"""
    print("\n" + "=" * 60)
    print("TESTE 2: Base de Dados")
    print("=" * 60)

    try:
        from database import DatabaseManager

        # Criar BD de teste
        db = DatabaseManager("data/test.db")
        print("✓ Base de dados criada")

        # Testar inserção de contrato
        contrato_teste = {
            'id_contrato': 'TEST001',
            'adjudicante': 'Entidade Teste',
            'adjudicante_nif': '999999999',
            'adjudicataria': 'Empresa Teste Lda',
            'adjudicataria_nif': '888888888',
            'valor': 50000.00,
            'data_contrato': '2024-01-15',
            'data_publicacao': '2024-01-20',
            'tipo_contrato': 'Teste',
            'tipo_procedimento': 'Teste',
            'descricao': 'Contrato de teste',
            'objeto_contrato': 'Teste',
            'distrito': 'Lisboa',
            'concelho': 'Lisboa',
            'cpv': '00000000',
            'prazo_execucao': 90,
            'link_base': 'http://teste.pt'
        }

        db.inserir_contrato(contrato_teste)
        print("✓ Contrato inserido")

        # Testar pesquisa
        resultados = db.pesquisar_contratos({'distrito': 'Lisboa'})
        print(f"✓ Pesquisa executada: {len(resultados)} resultado(s)")

        # Testar figura de interesse
        figura_id = db.adicionar_figura_interesse(
            nome='Entidade Teste',
            nif='999999999',
            tipo='empresa',
            notas='Teste'
        )
        print(f"✓ Figura de interesse criada: ID {figura_id}")

        # Testar estatísticas
        stats = db.obter_estatisticas()
        print(f"✓ Estatísticas obtidas: {stats['total_contratos']} contrato(s)")

        db.close()

        # Limpar ficheiro de teste
        import os
        if os.path.exists("data/test.db"):
            os.remove("data/test.db")
            print("✓ Ficheiro de teste removido")

        return True

    except Exception as e:
        print(f"✗ ERRO no teste de base de dados: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scraper():
    """Testa o módulo de scraper"""
    print("\n" + "=" * 60)
    print("TESTE 3: Scraper")
    print("=" * 60)

    try:
        from scraper import ContratosPublicosScraper

        scraper = ContratosPublicosScraper()
        print("✓ Scraper inicializado")

        # Testar parse de valores
        valor = scraper._parse_valor("50.000,00 €")
        assert valor == 50000.00
        print("✓ Parse de valor funcionando")

        # Testar parse de data
        data = scraper._parse_data("15-01-2024")
        assert data == "2024-01-15"
        print("✓ Parse de data funcionando")

        return True

    except Exception as e:
        print(f"✗ ERRO no teste de scraper: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_entities_and_alerts():
    """Testa os módulos de entities e alerts"""
    print("\n" + "=" * 60)
    print("TESTE 4: Entities & Alerts")
    print("=" * 60)

    try:
        from database import DatabaseManager
        from entities import EntitiesManager
        from alerts import AlertsManager

        # Criar BD de teste
        db = DatabaseManager("data/test2.db")

        # Testar Entities
        entities = EntitiesManager(db)
        figura_id = entities.adicionar_figura('Teste', tipo='pessoa')
        print(f"✓ Entities Manager: Figura criada com ID {figura_id}")

        # Testar Alerts
        alerts = AlertsManager(db)

        # Inserir contrato de teste
        contrato = {
            'id_contrato': 'TEST002',
            'adjudicante': 'Teste',
            'adjudicante_nif': '',
            'adjudicataria': 'Outra Empresa',
            'adjudicataria_nif': '',
            'valor': 10000.00,
            'data_contrato': '2024-02-01',
            'tipo_contrato': 'Teste'
        }
        db.inserir_contrato(contrato)

        # Verificar alertas
        alertas_criados = alerts.verificar_novos_contratos([contrato])
        print(f"✓ Alerts Manager: {len(alertas_criados)} alerta(s) criado(s)")

        db.close()

        # Limpar
        import os
        if os.path.exists("data/test2.db"):
            os.remove("data/test2.db")

        return True

    except Exception as e:
        print(f"✗ ERRO no teste de entities/alerts: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_example():
    """Testa o parsing do ficheiro CSV de exemplo"""
    print("\n" + "=" * 60)
    print("TESTE 5: CSV de Exemplo")
    print("=" * 60)

    try:
        from scraper import ContratosPublicosScraper
        from pathlib import Path

        csv_path = Path("data/exemplo_contratos.csv")

        if not csv_path.exists():
            print("⚠ Ficheiro de exemplo não encontrado")
            return True

        scraper = ContratosPublicosScraper()
        contratos = scraper.parse_csv_contratos(csv_path, limit=5)

        print(f"✓ CSV parseado: {len(contratos)} contrato(s)")

        if len(contratos) > 0:
            print(f"  Exemplo: {contratos[0].get('adjudicante')} → {contratos[0].get('adjudicataria')}")

        return True

    except Exception as e:
        print(f"✗ ERRO no teste de CSV: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║         TESTES DA APLICAÇÃO DE CONTRATOS PÚBLICOS              ║
╚════════════════════════════════════════════════════════════════╝
    """)

    # Criar diretórios necessários
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    testes = [
        ("Importação de Módulos", test_imports),
        ("Base de Dados", test_database),
        ("Scraper", test_scraper),
        ("Entities & Alerts", test_entities_and_alerts),
        ("CSV de Exemplo", test_csv_example)
    ]

    resultados = []

    for nome, teste in testes:
        try:
            sucesso = teste()
            resultados.append((nome, sucesso))
        except Exception as e:
            print(f"\n✗ ERRO FATAL no teste '{nome}': {e}")
            resultados.append((nome, False))

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    total = len(resultados)
    passou = sum(1 for _, sucesso in resultados if sucesso)

    for nome, sucesso in resultados:
        status = "✓ PASSOU" if sucesso else "✗ FALHOU"
        print(f"{status} - {nome}")

    print("\n" + "=" * 60)
    print(f"Total: {passou}/{total} testes passaram")
    print("=" * 60)

    if passou == total:
        print("\n🎉 Todos os testes passaram! A aplicação está pronta para usar.")
        print("\nPara executar a aplicação, use:")
        print("  python main.py")
        return 0
    else:
        print("\n⚠ Alguns testes falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
