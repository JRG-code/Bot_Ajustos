# 📖 GUIA DE USO RÁPIDO - Monitor de Contratos Públicos

## 🚀 Como Iniciar

```bash
cd contratos-publicos
python main.py
```

A aplicação abre com 7 abas:
1. **Dashboard** - Estatísticas gerais
2. **Pesquisar Contratos** - Pesquisa normal
3. **Figuras de Interesse** - Pessoas/empresas a monitorizar
4. **Alertas** - Notificações
5. **Importar Dados** - Carregar CSV
6. **Sincronização** - Config automática
7. **🆕 Padrões Suspeitos** - Análise avançada (MANUAL)
8. **🆕 Associações** - Pessoa-empresa (MANUAL)

---

## ⚠️ IMPORTANTE: Nada Funciona Automaticamente!

**Todas as análises avançadas são MANUAIS:**
- ❌ Não analisa ao importar dados
- ❌ Não detecta padrões automaticamente
- ✅ Só funciona quando VOCÊ clicar ou pesquisar
- ✅ Total controlo sobre o que fazer

---

## 📝 PASSO A PASSO COMPLETO

### PASSO 1: Importar Dados (Primeira Vez)

1. **Abrir aba "Importar Dados"**

2. **Selecionar fonte:**
   - ☑️ Ficheiro CSV Local (recomendado para começar)

3. **Definir limite** (opcional):
   - `1000` para teste
   - `0` para todos os dados

4. **Clicar "Iniciar Importação"**

5. **Selecionar ficheiro:**
   - Usar `data/exemplo_contratos.csv` para testar
   - Ou CSV baixado de dados.gov.pt

6. **Aguardar:**
   ```
   A processar: exemplo_contratos.csv

   Parseados 15 contratos

   === RESULTADO ===
   Total processados: 15
   Inseridos: 15
   Duplicados: 0
   Inválidos: 0
   ```

✅ **Pronto!** Dados importados. Nenhuma análise foi feita ainda.

---

### PASSO 2: Pesquisa Normal de Contratos

1. **Ir para aba "Pesquisar Contratos"**

2. **Aplicar filtros** (opcional):
   - Distrito: `Lisboa`
   - Ano (de): `2024`
   - Adjudicante: `Câmara`
   - Valor Mín: `50000`

3. **Clicar "Pesquisar"**

4. **Ver resultados:**
   ```
   Encontrados 8 contratos

   ID | Adjudicante | Adjudicatária | Valor | Data
   ```

5. **Duplo clique** em qualquer linha para ver detalhes completos

✅ **Nenhuma análise avançada** - apenas pesquisa normal!

---

### PASSO 3: Analisar Padrões Suspeitos (MANUAL)

⚠️ **Esta função SÓ funciona quando você clicar!**

1. **Ir para aba "Padrões Suspeitos 🔍"**

2. **Clicar "Analisar Todos os Contratos"**
   - Agora sim, vai analisar!
   - Leva 2-5 segundos para 1000 contratos

3. **Ver resultados:**
   ```
   Análise Completa

   Detectados 5 padrões suspeitos

   🔴 Alta: 3
   🟡 Média: 2
   ⚪ Baixa: 0
   ```

4. **Resultados aparecem em tabela:**
   ```
   Tipo                    | Gravidade | Descrição
   ─────────────────────────────────────────────────
   VALOR_SUSPEITO_LIMITE   | ALTA     | Valor €74.999 apenas €1...
   FRACIONAMENTO_SUSPEITO  | ALTA     | 3 contratos totalizando...
   CONTRATOS_REPETIDOS     | MÉDIA    | Múltiplos contratos...
   ```

5. **Cores automáticas:**
   - 🔴 Vermelho = Alta gravidade
   - 🟠 Laranja = Média
   - 🟡 Amarelo = Baixa

✅ **Análise completa!** Exportar se quiser.

---

### PASSO 4: Configurar Detecção (Opcional)

**Se quiser escolher O QUE detectar:**

1. **Na aba "Padrões Suspeitos"**

2. **Clicar "Configurar Detecção"**

3. **Marcar/desmarcar:**
   ```
   ☑️ Detectar valores suspeitos (€74.999, etc)
   ☑️ Detectar fracionamento ilegal
   ☐ Detectar contratos repetidos (desligado)
   ☑️ Detectar procedimentos inadequados
   ☑️ Detectar valores 'calculados'
   ```

4. **Ver limites legais:**
   ```
   📋 Limites Legais em Portugal:
   • Ajuste Direto: até €75.000
   • Consulta Prévia: €75.000 - €214.000
   • Concurso Público: acima de €214.000
   ```

5. **Clicar "Guardar"**

✅ **Próxima análise** usa estas configurações!

---

### PASSO 5: Adicionar Associações Pessoa-Empresa (MANUAL)

⚠️ **Esta função SÓ funciona quando você adicionar!**

1. **Ir para aba "Associações 👥"**

2. **Clicar "Adicionar Associação"**

3. **Preencher formulário:**
   ```
   Nome da Pessoa: António Silva
   Cargo Político: Presidente da Câmara
   Empresa: Construtora Silva & Filhos
   Tipo Relação: dono
   Fonte: Registo Comercial
   ```

4. **Clicar "Guardar"**

✅ **Associação criada!** Agora pode pesquisar.

---

### PASSO 6: Pesquisar por Pessoa/Empresa

1. **Ainda na aba "Associações"**

2. **Digitar no campo de pesquisa:**
   ```
   António Silva
   ```

3. **Clicar "Pesquisar Contratos"**

4. **Ver resultados expandidos:**
   ```
   ═══════════════════════════════════════
   PESQUISA POR ASSOCIAÇÕES: ANTÓNIO SILVA
   ═══════════════════════════════════════

   Total de Contratos: 15
   Valor Total: €3.500.000

   EMPRESAS ASSOCIADAS (2):
     • Construtora Silva & Filhos
     • Consultoria AS Lda

   CONTRATOS DIRETOS (0):
     (nenhum contrato em nome próprio)

   CONTRATOS DE EMPRESAS ASSOCIADAS (15):
     • Construtora Silva & Filhos (dono): €2.500.000
       - CM Lisboa → Construtora: €1.200.000
       - CM Porto → Construtora: €800.000
       - Junta Freguesia → Construtora: €500.000

     • Consultoria AS Lda (sócio): €1.000.000
       - Governo → Consultoria: €600.000
       - IPSS → Consultoria: €400.000
   ```

✅ **Pesquisa completa!** Vê TUDO relacionado com a pessoa.

---

### PASSO 7: Detectar Conflitos de Interesse (MANUAL)

⚠️ **Esta função SÓ funciona quando você clicar!**

1. **Menu "Análise Avançada"**

2. **Clicar "Detectar Conflitos de Interesse"**
   - Agora analisa TODAS as associações vs contratos
   - Leva 2-5 segundos

3. **Ver conflitos detectados:**
   ```
   ╔════════════════════════════════════════╗
   ║ CONFLITOS DE INTERESSE DETECTADOS      ║
   ╚════════════════════════════════════════╝

   Total: 2

   1. 🔴 CRÍTICA
      Pessoa: António Silva (Presidente da Câmara)
      Empresa: Construtora Silva & Filhos
      Contrato: CM Lisboa (€1.200.000)

      → Presidente tem empresa com contrato
        da própria Câmara!

   2. 🟠 ALTA
      Pessoa: António Silva (Presidente da Câmara)
      Empresa: Consultoria AS Lda
      Contrato: Governo (€600.000)

      → Político com cargo tem empresa
        com contratos públicos
   ```

✅ **Conflitos detectados!** Gravidade automática.

---

## 🎯 FLUXOS DE TRABALHO TÍPICOS

### Fluxo 1: Investigar Valores Suspeitos

```
1. Importar dados CSV
2. Ir para "Padrões Suspeitos"
3. Clicar "Analisar"
4. Filtrar por gravidade ALTA
5. Clicar em cada linha para ver detalhes
6. Exportar relatório
```

**Quando usar:** Procurar contratos próximos de €75k, €150k, etc.

---

### Fluxo 2: Investigar Uma Pessoa Específica

```
1. Importar dados CSV
2. Ir para "Associações"
3. Clicar "Adicionar Associação"
4. Preencher: Pessoa + Empresas
5. Clicar "Pesquisar Contratos"
6. Ver todos os contratos relacionados
7. Menu → "Detectar Conflitos" (se político)
```

**Quando usar:** Investigar "Luís Montenegro", "António Costa", etc.

---

### Fluxo 3: Analisar Uma Empresa Específica

```
1. Importar dados CSV
2. Ir para "Pesquisar Contratos"
3. Adjudicatária: "Spinumviva"
4. Pesquisar
5. Ver todos os contratos
6. (Opcional) Adicionar sócios em "Associações"
```

**Quando usar:** Investigar empresa suspeita.

---

### Fluxo 4: Monitorizar Câmara Municipal

```
1. Importar dados CSV
2. Ir para "Pesquisar Contratos"
3. Adjudicante: "Câmara Municipal de Lisboa"
4. Ano: 2024
5. Pesquisar
6. Ir para "Padrões Suspeitos"
7. Analisar (só os contratos filtrados)
```

**Quando usar:** Auditar autarquia específica.

---

## 🛠️ CONFIGURAÇÕES ESPECIAIS

### Configurar Sincronização Automática

**Se quiser dados atualizados automaticamente:**

1. **Ir para aba "Sincronização"**

2. **Marcar:**
   ```
   ☑️ Ativar sincronização automática
   Intervalo: 24 horas
   ```

3. **Clicar "Guardar Configuração"**

✅ **App sincroniza diariamente** (não precisa ficar aberta!)

**Nota:** Sincronização NÃO executa análises! Só importa dados novos.

---

### Otimizar Base de Dados

**Quando a BD ficar grande (> 100 MB):**

1. **Ir para aba "Sincronização"**

2. **Clicar "Otimizar Base de Dados"**

3. **Aguardar 10-30 segundos**

4. **Ver resultado:**
   ```
   Base de dados otimizada!

   Espaço recuperado: 23.5 MB
   Redução: 31.2%
   ```

✅ **BD compactada!** Reduz ~30% do tamanho.

---

## 📊 EXPORTAR RESULTADOS

### Exportar Pesquisa Normal

1. Fazer pesquisa normal (aba "Pesquisar Contratos")
2. Menu → Ficheiro → **"Exportar Resultados"**
3. Escolher local: `relatorio_contratos.xlsx`
4. Abrir em Excel

### Exportar Padrões Suspeitos

1. Analisar padrões (aba "Padrões Suspeitos")
2. Clicar **"Exportar Relatório"**
3. Escolher local: `padroes_suspeitos.txt`
4. Abrir em Notepad/TextEdit

### Exportar Associações

1. Pesquisar por pessoa (aba "Associações")
2. Copiar texto dos resultados
3. Colar em Word/documento

---

## ⚙️ OPÇÕES AVANÇADAS

### Importar Associações em Lote (CSV)

**Se tiver muitas associações para adicionar:**

1. Criar ficheiro CSV:
   ```csv
   nome_pessoa,cargo_politico,partido,empresa,tipo_relacao,percentagem,fonte
   António Silva,Presidente CM,PS,Construtora Silva,dono,60,Registo Comercial
   Maria Santos,Deputada,PSD,Consultoria MS,socio,40,Dados Públicos
   ```

2. No Python:
   ```python
   from src.associations import AssociationsManager
   from src.database import DatabaseManager

   db = DatabaseManager()
   assoc = AssociationsManager(db)

   count = assoc.importar_associacoes_csv("associacoes.csv")
   print(f"Importadas {count} associações")
   ```

---

## 🚨 LIMITES E AVISOS

### O que NÃO fazer:

❌ **NÃO** importar milhões de contratos de uma vez
   → Dividir em lotes de 100k

❌ **NÃO** executar análise em BD vazia
   → Importar dados primeiro

❌ **NÃO** esperar detecção 100% perfeita
   → Sempre verificar manualmente

### O que SIM fazer:

✅ **SIM** importar dados gradualmente
✅ **SIM** verificar padrões detectados
✅ **SIM** adicionar associações conhecidas
✅ **SIM** exportar e arquivar resultados

---

## 📞 TROUBLESHOOTING

### "Nenhum padrão detectado"

**Possíveis causas:**
1. Dados não têm valores suspeitos (normal!)
2. Filtros muito restritivos
3. BD vazia

**Solução:** Verificar se há contratos na BD primeiro.

---

### "Erro ao analisar contratos"

**Possíveis causas:**
1. BD corrompida
2. Falta de memória

**Solução:**
1. Ir para "Sincronização" → "Otimizar BD"
2. Reduzir número de contratos

---

### "Associação não encontra contratos"

**Possíveis causas:**
1. Nome não exato (ex: "Silva Lda" vs "Silva, Lda")
2. Empresa não tem contratos na BD

**Solução:**
1. Pesquisar empresa manualmente primeiro
2. Verificar nome exato
3. Importar mais dados

---

## 🎓 EXEMPLOS PRÁTICOS

### Exemplo 1: Encontrar Contratos de €74.999

```
1. Importar dados
2. Padrões Suspeitos → Analisar
3. Ver linha "VALOR_SUSPEITO_LIMITE"
4. Duplo clique para ver contrato
```

### Exemplo 2: Investigar "Luís Montenegro"

```
1. Associações → Adicionar:
   - Nome: Luís Montenegro
   - Cargo: Primeiro-Ministro
   - Empresa: [adicionar empresas conhecidas]

2. Pesquisar "Luís Montenegro"
3. Ver todos os contratos
4. Detectar Conflitos
```

### Exemplo 3: Auditar Câmara de Lisboa (2024)

```
1. Pesquisar Contratos:
   - Adjudicante: Câmara Municipal de Lisboa
   - Ano: 2024

2. Exportar para Excel
3. Padrões Suspeitos → Analisar
4. Ver se há fracionamento/valores suspeitos
```

---

## ✅ CHECKLIST DE PRIMEIROS PASSOS

- [ ] 1. Executar `python main.py`
- [ ] 2. Importar `data/exemplo_contratos.csv`
- [ ] 3. Fazer uma pesquisa normal
- [ ] 4. Analisar padrões suspeitos (manual!)
- [ ] 5. Adicionar uma associação de teste
- [ ] 6. Pesquisar por pessoa
- [ ] 7. Exportar resultados

---

## 📚 DOCUMENTAÇÃO COMPLETA

- **README.md** - Visão geral
- **QUICK_START.md** - Tutorial 10 min
- **BUILD_GUIDE.md** - Criar executável
- **TAMANHOS_ESTIMADOS.md** - Espaço em disco
- **COMO_CRIAR_EXECUTAVEL.md** - Guia standalone

---

**💡 LEMBRE-SE: Nada funciona automaticamente! Você tem controlo total sobre quando analisar.**
