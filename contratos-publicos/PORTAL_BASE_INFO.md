# Como Obter Dados do Portal BASE

## Problema Atual
O download automático do Portal BASE pode não estar a funcionar devido a:
- Mudanças na API/estrutura do site
- Restrições de acesso ou rate limiting
- Portal BASE temporariamente indisponível

## Solução: Download Manual

### Opção 1: Portal BASE - Dados Abertos (Recomendado)

1. **Aceder ao Portal de Dados Abertos:**
   - URL: https://dados.gov.pt/pt/datasets/
   - Pesquisar por "contratos públicos" ou "BASE"

2. **Download direto CSV:**
   - Alguns datasets: https://www.base.gov.pt/dadosabertos

3. **Alternativa - Portal BASE antigo:**
   - URL: https://www.base.gov.pt/Base4/pt/resultados/
   - Fazer pesquisa com filtros desejados
   - Clicar em "Exportar" → "CSV"
   - Guardar o ficheiro

### Opção 2: Importar CSV Local

Depois de descarregar manualmente:

1. Abrir aplicação "Monitor de Contratos Públicos"
2. Ir para aba "Importar Dados"
3. Selecionar opção "Ficheiro CSV Local"
4. Clicar em "Iniciar Importação"
5. Escolher o ficheiro CSV descarregado

### Opção 3: API Oficial (Requer Registo)

**NOTA:** A API oficial do Portal BASE requer credenciais.

1. **Obter credenciais:**
   - Contactar IMPIC (Instituto dos Mercados Públicos, do Imobiliário e da Construção)
   - Email: info@base.gov.pt
   - Solicitar acesso à API

2. **Configurar na aplicação:**
   - Ir para "Importar Dados"
   - Selecionar "API Portal BASE"
   - Configurar API Key (ainda não implementado na GUI)

## Links Úteis

- **Portal BASE:** https://www.base.gov.pt
- **Dados Abertos:** https://dados.gov.pt
- **Documentação BASE:** https://www.base.gov.pt/Base4/pt/ajuda/
- **Contacto BASE:** info@base.gov.pt

## Datasets Úteis

Alguns datasets disponíveis em dados.gov.pt:
- Contratos Públicos (vários anos)
- Procedimentos de Contratação Pública
- Dados agregados por entidade

## Formato do CSV

O CSV deve conter colunas como:
- idContrato / id / ID
- nomeEntidadeAdjudicante / adjudicante
- nomeEntidadeAdjudicataria / adjudicataria
- precoContratual / valor
- dataPublicacao / dataCelebracaoContrato
- tipoProcedimento
- tipoContrato
- objectoContrato / descricao

A aplicação tenta detectar automaticamente os nomes das colunas.

## Contribuir

Se descobrir uma forma funcional de aceder à API/dados do Portal BASE:
- Criar issue no GitHub: https://github.com/JRG-code/Bot_Ajustos/issues
- Ou contactar o desenvolvedor

Última atualização: Janeiro 2025
