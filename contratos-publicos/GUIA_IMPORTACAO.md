# Guia de Importação de Dados

Este guia explica como importar contratos públicos para a aplicação.

---

## 🎯 Métodos de Importação

A aplicação suporta **3 formas** de importar dados:

### 1. **Portal BASE (RECOMENDADO)** - Download Automático ✨

Faz download automático direto do Portal BASE (BASE.gov.pt)

**Como usar:**
1. Abra a aplicação
2. Vá para aba **"Importar Dados"**
3. Selecione: **"Portal BASE (download automático - BASE.gov.pt)"**
4. Clique **"Iniciar Importação"**
5. Escolha:
   - **SIM**: Importar um ano específico (ex: 2024) → Mais rápido
   - **NÃO**: Importar TODOS os anos (2012-2025) → Pode demorar!
6. Aguarde o download e processamento

**Vantagens:**
- ✅ Sempre atualizado
- ✅ Dados oficiais do governo
- ✅ Não precisa procurar ficheiros
- ✅ Download direto pela aplicação

**Desvantagens:**
- ⚠️ Requer internet
- ⚠️ Downloads grandes podem demorar (especialmente TODOS os anos)
- ⚠️ Pode ter timeout se conexão lenta

**Recomendação:**
- **Primeira vez**: Importar apenas 1 ano (ex: 2024) para testar
- **Depois**: Importar outros anos conforme necessário

---

### 2. **Ficheiro CSV Local** - Importação Manual

Use quando tiver um ficheiro CSV de contratos no computador.

**Como usar:**
1. Obtenha um ficheiro CSV:
   - Exportado do Portal BASE
   - Descarregado de dados.gov.pt
   - Fornecido por terceiros
2. Vá para aba **"Importar Dados"**
3. Selecione: **"Ficheiro CSV Local"**
4. Clique **"Iniciar Importação"**
5. Selecione o ficheiro CSV no seu computador
6. Aguarde o processamento

**Vantagens:**
- ✅ Funciona offline
- ✅ Pode importar ficheiros personalizados
- ✅ Controlo total sobre os dados

**Formato esperado do CSV:**
```csv
idContrato,nomeEntidadeAdjudicante,nomeEntidadeAdjudicataria,precoContratual,dataPublicacao,...
12345,Câmara Municipal de Lisboa,Empresa Xpto Lda,50000.00,2024-01-15,...
```

---

### 3. **API Portal BASE** - Não Disponível

Importação via API oficial requer credenciais do IMPIC (não público).

Para obter acesso:
1. Contactar IMPIC através de https://www.base.gov.pt
2. Solicitar credenciais de API
3. Configurar na aplicação (funcionalidade futura)

---

## 📊 Configurações de Importação

### Limite de Registos

Na aba "Importar Dados", pode definir um limite:
- **0 ou vazio**: Importar TODOS os contratos do ficheiro/ano
- **1000**: Importar apenas os primeiros 1000 (útil para testar)
- **10000**: Importar 10 mil contratos

**Quando usar limite:**
- 🧪 Testar a aplicação pela primeira vez
- 💻 Computador com pouco espaço em disco
- ⚡ Quer ver resultados rapidamente

---

## ⏱️ Tempo Estimado de Importação

| Fonte | Quantidade | Tempo Estimado |
|-------|------------|----------------|
| Portal BASE (1 ano) | ~50k contratos | 2-5 minutos |
| Portal BASE (TODOS) | ~500k contratos | 15-30 minutos |
| CSV Local (pequeno) | 1-10k contratos | 10-30 segundos |
| CSV Local (grande) | 100k+ contratos | 3-10 minutos |

*Tempos variam conforme velocidade da internet e do computador

---

## 🔍 O Que Acontece Durante a Importação

A aplicação:

1. **Download** (se Portal BASE):
   - Conecta ao BASE.gov.pt
   - Faz download do CSV com os contratos
   - Mostra progresso em MB

2. **Parse**:
   - Lê o ficheiro CSV linha a linha
   - Extrai informações de cada contrato
   - Valida dados (NIF, valores, datas, etc.)

3. **Processamento**:
   - Insere contratos novos na base de dados
   - Detecta duplicados (não insere de novo)
   - Marca inválidos (dados incorretos)

4. **Alertas**:
   - Verifica se algum contrato envolve "Figuras de Interesse"
   - Gera alertas automáticos se encontrar

5. **Resultado**:
   - Mostra estatísticas:
     - ✓ Inseridos: Contratos novos adicionados
     - ⊗ Duplicados: Já existiam na BD (ignorados)
     - ✗ Inválidos: Dados incorretos (não inseridos)
     - 🔔 Alertas: Contratos de interesse encontrados

---

## ❓ Problemas Comuns

### "Erro ao descarregar dados"

**Causas:**
- Sem internet
- Portal BASE offline
- Timeout (ficheiro muito grande)

**Solução:**
1. Verificar conexão à internet
2. Tentar importar um ano específico (ficheiro menor)
3. Se persistir, usar "Ficheiro CSV Local"

### "Nenhum contrato encontrado"

**Causas:**
- Ficheiro CSV vazio
- Formato incompatível
- Colunas com nomes diferentes

**Solução:**
1. Abrir o CSV num editor de texto
2. Verificar se tem dados
3. Verificar cabeçalhos (primeira linha)
4. Usar ficheiro de exemplo: `data/exemplo_contratos.csv`

### "Muitos duplicados"

**Normal!** Se já importou dados antes, ao reimportar o mesmo período terá duplicados.

A aplicação **não insere duplicados** - é seguro reimportar.

### Importação muito lenta

**Causas:**
- Ficheiro muito grande
- Computador lento
- Muitos contratos

**Solução:**
- Use limite de registos (ex: 10000)
- Importe por ano (em vez de todos os anos)
- Feche outros programas

---

## 💡 Dicas e Boas Práticas

### Primeira Importação

1. **Comece pequeno**: Importe apenas 2024 (limite: 1000)
2. **Teste**: Veja se tudo funciona
3. **Expanda**: Importe anos completos
4. **Histórico**: Importe anos anteriores conforme necessário

### Importações Regulares

- Use **"Portal BASE"** para obter dados mais recentes
- Importe **apenas o ano corrente** mensalmente
- Duplicados são automaticamente ignorados

### Gestão de Espaço

Um ano de contratos (~50k) ocupa aproximadamente:
- **~40 MB** na base de dados (otimizada)

Para gerir espaço:
- Importe apenas anos relevantes
- Use a opção "Otimizar Base de Dados" (aba Sincronização)

---

## 📝 Exemplo Prático: Primeira Importação

```
PASSO 1: Abrir a aplicação
→ Duplo clique em launcher.pyw

PASSO 2: Ir para "Importar Dados"
→ Clicar na aba

PASSO 3: Selecionar "Portal BASE"
→ Marcar o radio button

PASSO 4: Configurar limite
→ Digite: 1000

PASSO 5: Iniciar
→ Clicar "Iniciar Importação"

PASSO 6: Escolher ano
→ SIM → Digite: 2024

PASSO 7: Aguardar
→ Ver o progresso no log
→ Aguardar mensagem "Importação concluída!"

PASSO 8: Ver resultados
→ Ir para aba "Dashboard"
→ Ver estatísticas atualizadas
```

---

## 🎓 Próximos Passos Após Importação

Depois de importar dados, pode:

1. **Pesquisar Contratos** (aba "Pesquisa")
   - Filtrar por entidade, valor, ano, etc.

2. **Adicionar Figuras de Interesse** (aba "Figuras de Interesse")
   - Adicionar empresas ou pessoas para monitorizar

3. **Analisar Padrões Suspeitos** (aba "Padrões Suspeitos")
   - Detectar valores suspeitos, fracionamento, etc.

4. **Ver Alertas** (aba "Alertas")
   - Ver contratos relacionados com figuras de interesse

5. **Exportar para Excel** (Menu Ficheiro → Exportar)
   - Criar relatórios personalizados

---

**Precisa de ajuda?** Consulte os outros guias:
- `COMO_USAR.md` - Guia completo da aplicação
- `INICIO_RAPIDO.md` - Tutorial rápido de 2 minutos
- `COMO_ABRIR.md` - Como abrir a aplicação sem console
