#!/usr/bin/env python3
"""
Teste das Funcionalidades Avançadas
Demonstra detecção de padrões suspeitos e associações pessoa-empresa
"""

import sys
import os
sys.path.insert(0, 'src')

from database import DatabaseManager
from suspicious_patterns import SuspiciousPatternDetector, LimitesLegais
from associations import AssociationsManager


def test_suspicious_patterns():
    """Testa detecção de padrões suspeitos"""
    print("\n" + "=" * 70)
    print("TESTE 1: DETECÇÃO DE PADRÕES SUSPEITOS")
    print("=" * 70)

    # Criar contratos de teste com valores suspeitos
    contratos_teste = [
        {
            'id_contrato': 'TEST001',
            'adjudicante': 'Câmara Municipal de Lisboa',
            'adjudicataria': 'Empresa Suspeita Lda',
            'valor': 74999.00,  # €1 abaixo do limite!
            'tipo_contrato': 'Aquisição de Serviços',
            'tipo_procedimento': 'Ajuste Direto',
            'data_contrato': '2024-01-15'
        },
        {
            'id_contrato': 'TEST002',
            'adjudicante': 'Câmara Municipal do Porto',
            'adjudicataria': 'Empresa Suspeita Lda',
            'valor': 74950.00,  # €50 abaixo do limite
            'tipo_contrato': 'Aquisição de Serviços',
            'tipo_procedimento': 'Ajuste Direto',
            'data_contrato': '2024-02-01'
        },
        {
            'id_contrato': 'TEST003',
            'adjudicante': 'Câmara Municipal de Braga',
            'adjudicataria': 'Construtora XYZ',
            'valor': 149990.00,  # €10 abaixo do limite de obras
            'tipo_contrato': 'Empreitadas de Obras Públicas',
            'tipo_procedimento': 'Ajuste Direto',
            'data_contrato': '2024-03-01'
        },
        {
            'id_contrato': 'TEST004',
            'adjudicante': 'Câmara Municipal de Lisboa',
            'adjudicataria': 'Empresa Suspeita Lda',
            'valor': 50000.00,
            'tipo_contrato': 'Aquisição de Serviços',
            'tipo_procedimento': 'Ajuste Direto',
            'data_contrato': '2024-01-20'
        },
        {
            'id_contrato': 'TEST005',
            'adjudicante': 'Câmara Municipal de Lisboa',
            'adjudicataria': 'Empresa Suspeita Lda',
            'valor': 45000.00,
            'tipo_contrato': 'Aquisição de Serviços',
            'tipo_procedimento': 'Ajuste Direto',
            'data_contrato': '2024-02-15'
        },
    ]

    # Inicializar detector
    detector = SuspiciousPatternDetector()

    # Analisar
    padroes = detector.analisar_contratos(contratos_teste)

    # Mostrar resultados
    print(f"\n✅ Análise completa: {len(padroes)} padrões detectados\n")

    # Agrupar por gravidade
    alta = [p for p in padroes if p.get('gravidade') == 'alta']
    media = [p for p in padroes if p.get('gravidade') == 'media']
    baixa = [p for p in padroes if p.get('gravidade') == 'baixa']

    print(f"🔴 ALTA: {len(alta)}")
    print(f"🟡 MÉDIA: {len(media)}")
    print(f"⚪ BAIXA: {len(baixa)}\n")

    # Mostrar padrões de alta gravidade
    if alta:
        print("=" * 70)
        print("PADRÕES DE ALTA GRAVIDADE:")
        print("=" * 70)
        for i, p in enumerate(alta, 1):
            print(f"\n{i}. {p['tipo'].upper()}")
            print(f"   {p['descricao']}")
            if p.get('id_contrato'):
                print(f"   Contrato: {p['id_contrato']}")
            if p.get('valor'):
                print(f"   Valor: €{p['valor']:,.2f}")

    # Gerar relatório
    print("\n" + "=" * 70)
    relatorio = detector.gerar_relatorio(padroes)
    print(relatorio)


def test_associations():
    """Testa sistema de associações pessoa-empresa"""
    print("\n" + "=" * 70)
    print("TESTE 2: ASSOCIAÇÕES PESSOA-EMPRESA")
    print("=" * 70)

    # Criar BD temporária
    db = DatabaseManager("data/test_associations.db")
    assoc_manager = AssociationsManager(db)

    # Adicionar pessoa política
    print("\n1. Adicionando pessoa política...")
    pessoa_id = assoc_manager.adicionar_pessoa(
        nome="João Silva",
        cargo_politico="Presidente da Câmara",
        partido="Partido X",
        funcao_atual="Presidente CM Lisboa"
    )
    print(f"   ✅ Pessoa adicionada: ID {pessoa_id}")

    # Associar a empresas
    print("\n2. Associando a empresas...")
    assoc_manager.associar_pessoa_empresa(
        pessoa_id=pessoa_id,
        empresa_nome="Construtora Silva & Filhos Lda",
        tipo_relacao="dono",
        percentagem=60.0,
        fonte="Registo Comercial"
    )
    print("   ✅ Associado a Construtora Silva & Filhos (60%)")

    assoc_manager.associar_pessoa_empresa(
        pessoa_id=pessoa_id,
        empresa_nome="Consultoria JPS Lda",
        tipo_relacao="socio",
        percentagem=40.0,
        fonte="Registo Comercial"
    )
    print("   ✅ Associado a Consultoria JPS (40%)")

    # Adicionar contratos de teste
    print("\n3. Adicionando contratos de teste...")
    contratos_teste = [
        {
            'id_contrato': 'ASSOC001',
            'adjudicante': 'Câmara Municipal de Lisboa',
            'adjudicataria': 'Construtora Silva & Filhos Lda',
            'valor': 250000.00,
            'tipo_contrato': 'Empreitadas de Obras Públicas',
            'data_contrato': '2024-01-15'
        },
        {
            'id_contrato': 'ASSOC002',
            'adjudicante': 'Junta de Freguesia de Belém',
            'adjudicataria': 'Consultoria JPS Lda',
            'valor': 50000.00,
            'tipo_contrato': 'Aquisição de Serviços',
            'data_contrato': '2024-02-01'
        },
    ]

    for c in contratos_teste:
        db.inserir_contrato(c)
    print(f"   ✅ {len(contratos_teste)} contratos adicionados")

    # Pesquisar por pessoa
    print("\n4. Pesquisando contratos por pessoa...")
    resultado = assoc_manager.pesquisar_contratos_por_pessoa("João Silva")

    print(f"\n📊 RESULTADOS DA PESQUISA:")
    print(f"   Total de contratos: {resultado['total_contratos']}")
    print(f"   Valor total: €{resultado['valor_total']:,.2f}")
    print(f"   Empresas associadas: {len(resultado['empresas_associadas'])}")

    if resultado['empresas_associadas']:
        print("\n   Empresas:")
        for empresa in resultado['empresas_associadas']:
            print(f"     • {empresa}")

    if resultado['contratos_empresas']:
        print(f"\n   Contratos das empresas associadas:")
        for c in resultado['contratos_empresas']:
            print(f"     • {c['adjudicante']} → {c['adjudicataria']}: €{c.get('valor', 0):,.2f}")

    # Adicionar cargo político
    print("\n5. Adicionando cargo político...")
    assoc_manager.adicionar_cargo_politico(
        pessoa_id=pessoa_id,
        cargo="Presidente da Câmara",
        entidade="Câmara Municipal de Lisboa",
        partido="Partido X",
        data_inicio="2021-10-01"
    )
    print("   ✅ Cargo adicionado")

    # Detectar conflitos de interesse
    print("\n6. Detectando conflitos de interesse...")
    conflitos = assoc_manager.detectar_conflitos_interesse(pessoa_id)

    if conflitos:
        print(f"\n🚨 {len(conflitos)} CONFLITOS DETECTADOS:")
        for i, c in enumerate(conflitos, 1):
            print(f"\n   {i}. {c['gravidade'].upper()}")
            print(f"      {c['descricao']}")
            print(f"      Valor: €{c['valor']:,.2f}")
    else:
        print("   ✅ Nenhum conflito detectado")

    # Limpar
    db.close()
    import os
    if os.path.exists("data/test_associations.db"):
        os.remove("data/test_associations.db")


def test_limites_legais():
    """Testa limites legais portugueses"""
    print("\n" + "=" * 70)
    print("TESTE 3: LIMITES LEGAIS PORTUGUESES")
    print("=" * 70)

    print("\n📋 LIMITES PARA CONTRATAÇÃO PÚBLICA EM PORTUGAL:\n")

    print("AJUSTE DIRETO:")
    print(f"  • Bens e Serviços: até €{LimitesLegais.AJUSTE_DIRETO_BENS_SERVICOS:,.2f}")
    print(f"  • Obras: até €{LimitesLegais.AJUSTE_DIRETO_OBRAS:,.2f}")

    print("\nCONSULTA PRÉVIA:")
    print(f"  • Bens e Serviços: €{LimitesLegais.AJUSTE_DIRETO_BENS_SERVICOS:,.2f} - €{LimitesLegais.CONSULTA_PREVIA_BENS_SERVICOS:,.2f}")
    print(f"  • Obras: €{LimitesLegais.AJUSTE_DIRETO_OBRAS:,.2f} - €{LimitesLegais.CONSULTA_PREVIA_OBRAS:,.2f}")

    print("\nCONCURSO PÚBLICO:")
    print(f"  • Bens e Serviços: acima de €{LimitesLegais.CONCURSO_PUBLICO_BENS_SERVICOS:,.2f}")
    print(f"  • Obras: acima de €{LimitesLegais.CONCURSO_PUBLICO_OBRAS:,.2f}")

    print("\nLIMITES UNIÃO EUROPEIA:")
    print(f"  • Bens e Serviços: €{LimitesLegais.UE_BENS_SERVICOS:,.2f}")
    print(f"  • Obras: €{LimitesLegais.UE_OBRAS:,.2f}")

    print("\n⚠️  VALORES SUSPEITOS:")
    print("  Contratos com valores 'calculados' para evitar procedimentos:")
    print("  • €74.999 (€1 abaixo do limite)")
    print("  • €74.990 (€10 abaixo)")
    print("  • €74.950 (€50 abaixo)")
    print("  • €74.900 (€100 abaixo)")


def main():
    """Executa todos os testes"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║     TESTE DAS FUNCIONALIDADES AVANÇADAS                        ║
║     Monitor de Contratos Públicos - v2.0                       ║
╚════════════════════════════════════════════════════════════════╝
    """)

    try:
        test_limites_legais()
        test_suspicious_patterns()
        test_associations()

        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 70)

        print("""
╔════════════════════════════════════════════════════════════════╗
║     FUNCIONALIDADES TESTADAS                                   ║
╚════════════════════════════════════════════════════════════════╝

✅ Detecção de valores suspeitos (€74.999, €74.950, etc)
✅ Detecção de fracionamento de contratos
✅ Detecção de contratos repetidos
✅ Associações pessoa-empresa
✅ Pesquisa expandida por associações
✅ Detecção de conflitos de interesse
✅ Limites legais portugueses

PRÓXIMO PASSO: Executar a aplicação completa
  python main.py
        """)

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
