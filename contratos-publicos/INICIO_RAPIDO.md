# ⚡ INÍCIO RÁPIDO (2 minutos)

## 1️⃣ Executar

```bash
cd contratos-publicos
python main.py
```

## 2️⃣ Importar Dados de Teste

1. Aba **"Importar Dados"**
2. ☑️ Ficheiro CSV Local
3. Clicar **"Iniciar Importação"**
4. Selecionar `data/exemplo_contratos.csv`
5. Aguardar (~5 segundos)

✅ **15 contratos importados!**

---

## 3️⃣ Ver os Contratos

1. Aba **"Pesquisar Contratos"**
2. Deixar tudo vazio
3. Clicar **"Pesquisar"**

✅ **Ver todos os 15 contratos!**

---

## 4️⃣ Analisar Padrões Suspeitos ⚠️

**IMPORTANTE:** Só funciona quando VOCÊ clicar!

1. Aba **"Padrões Suspeitos 🔍"**
2. Clicar **"Analisar Todos os Contratos"**
3. Aguardar (~2 segundos)

✅ **Ver padrões detectados!**
- 🔴 Vermelho = Alta gravidade
- 🟡 Amarelo = Média
- ⚪ Branco = Baixa

---

## 5️⃣ Adicionar Associação Pessoa-Empresa

**IMPORTANTE:** Só funciona quando VOCÊ adicionar!

1. Aba **"Associações 👥"**
2. Clicar **"Adicionar Associação"**
3. Preencher:
   ```
   Nome: João Silva
   Cargo: Presidente da Câmara
   Empresa: Construtora Silva & Filhos Lda
   Tipo: dono
   ```
4. Clicar **"Guardar"**

✅ **Associação criada!**

---

## 6️⃣ Pesquisar por Pessoa

1. Ainda na aba **"Associações"**
2. Digitar: `João Silva`
3. Clicar **"Pesquisar Contratos"**

✅ **Ver TODOS os contratos:**
- Contratos diretos (em nome próprio)
- Contratos das empresas associadas
- Valor total

---

## 7️⃣ Detectar Conflitos de Interesse

**IMPORTANTE:** Só funciona quando VOCÊ clicar!

1. Menu **"Análise Avançada"**
2. Clicar **"Detectar Conflitos de Interesse"**

✅ **Ver conflitos automáticos!**
- 🔴 Crítico (político + contrato mesma entidade)
- 🟠 Alto (político + contratos públicos)

---

## 📊 O QUE CADA ABA FAZ

| Aba | Função | Automático? |
|-----|--------|-------------|
| **Dashboard** | Estatísticas gerais | ✅ Sim |
| **Pesquisar Contratos** | Pesquisa normal | ❌ Manual |
| **Figuras de Interesse** | Monitorizar pessoas/empresas | ❌ Manual |
| **Alertas** | Notificações | ✅ Auto (após importar) |
| **Importar Dados** | Carregar CSV | ❌ Manual |
| **Sincronização** | Config automática | ❌ Manual |
| **🔍 Padrões Suspeitos** | Detectar valores €74.999 | ❌ **MANUAL** |
| **👥 Associações** | Pessoa-empresa | ❌ **MANUAL** |

---

## ⚠️ REGRA DE OURO

**NADA funciona automaticamente nas análises avançadas!**

- ❌ Importar dados **NÃO** analisa padrões
- ❌ Adicionar pessoa **NÃO** detecta conflitos
- ✅ Você precisa **CLICAR** para analisar
- ✅ Total **CONTROLO** sobre o que fazer

---

## 🎯 3 CASOS DE USO PRINCIPAIS

### Caso 1: Encontrar Valores Suspeitos (€74.999)

```
Importar → Padrões Suspeitos → Analisar → Ver resultados
```

### Caso 2: Investigar Pessoa (ex: "Luís Montenegro")

```
Associações → Adicionar pessoa + empresas → Pesquisar → Ver contratos
```

### Caso 3: Auditar Autarquia

```
Pesquisar (filtrar por Câmara) → Exportar → Padrões Suspeitos → Analisar
```

---

## 📁 FICHEIROS ÚTEIS

- **COMO_USAR.md** ← Guia completo passo a passo
- **README.md** ← Documentação técnica
- **QUICK_START.md** ← Tutorial 10 minutos
- **BUILD_GUIDE.md** ← Criar executável .exe

---

## 🚀 PRÓXIMO PASSO

**Importar dados reais:**

1. Baixar CSV de [dados.gov.pt](https://dados.gov.pt/pt/datasets/contratos-publicos-portal-base-impic-contratos-de-2012-a-2025/)
2. Importar na aba "Importar Dados"
3. Analisar padrões suspeitos
4. Adicionar associações conhecidas
5. Investigar!

---

**💡 DICA:** Comece com poucos dados (1.000-10.000 contratos) para testar. Depois importe tudo!
