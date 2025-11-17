# Monitor de Contratos Públicos Portugueses

Aplicação desktop em Python para monitorizar, pesquisar e analisar contratos públicos portugueses do [Portal BASE](https://www.base.gov.pt).

## 📋 Características

- ✅ **Pesquisa Avançada**: Filtre contratos por distrito, concelho, ano, adjudicante, adjudicatária, valor e tipo
- 👥 **Figuras de Interesse**: Crie listas de entidades (pessoas/empresas) para monitorizar
- 🔔 **Sistema de Alertas**: Receba alertas automáticos quando figuras de interesse aparecem em novos contratos
- 🔍 **Análise de Conexões**: Detecte relações entre entidades através de contratos
- 📊 **Dashboard**: Visualize estatísticas e alertas recentes
- 📁 **Exportação**: Exporte resultados para Excel
- 💾 **Base de Dados Local**: SQLite para armazenamento eficiente

## 🚀 Instalação

### Requisitos

- Python 3.10 ou superior
- pip (gestor de pacotes Python)

### Passo a Passo

1. **Clone ou descarregue o projeto**
   ```bash
   cd contratos-publicos
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**

   **Opção 1 - Launchers Simplificados (Recomendado):**

   - **Windows**: Duplo clique em `Iniciar.bat`
   - **Linux/Mac**: Execute `bash iniciar.sh` ou `./iniciar.sh`

   **Opção 2 - Comando direto:**
   ```bash
   python launcher.pyw
   ```

   **Opção 3 - Modo diagnóstico (se houver problemas):**
   ```bash
   python diagnostico.py
   ```

   **Opção 4 - Modo tradicional:**
   ```bash
   python main.py
   ```

## 📖 Como Usar

### 1. Importar Dados

Na aba **"Importar Dados"**:

- **Opção 1: Ficheiro CSV Local**
  - Clique em "Iniciar Importação"
  - Selecione um ficheiro CSV com dados de contratos
  - Os dados serão processados e inseridos na base de dados

- **Opção 2: Dados Abertos** *(em desenvolvimento)*
  - Importa dados diretamente do [dados.gov.pt](https://dados.gov.pt)

- **Opção 3: API Portal BASE** *(requer configuração)*
  - Acesso direto à API oficial do Portal BASE
  - Requer chave de API (pedido ao IMPIC)

### 2. Pesquisar Contratos

Na aba **"Pesquisar Contratos"**:

1. Preencha os filtros desejados:
   - **Distrito/Concelho**: Localização geográfica
   - **Ano**: Período de contratos
   - **Adjudicante/Adjudicatária**: Pesquisa por nome (parcial)
   - **Valor**: Intervalo de valores em euros

2. Clique em **"Pesquisar"**

3. Duplo clique num contrato para ver detalhes completos

4. Use **"Exportar Resultados"** no menu Ficheiro para exportar para Excel

### 3. Gerir Figuras de Interesse

Na aba **"Figuras de Interesse"**:

1. **Adicionar uma figura**:
   - Preencha: Nome, NIF (opcional), Tipo, Notas
   - Clique em "Adicionar Figura"

2. **Analisar uma figura**:
   - Selecione a figura na lista
   - Clique em "Analisar Figura" para ver estatísticas detalhadas

3. **Ver contratos**:
   - Selecione a figura
   - Clique em "Ver Contratos" para pesquisar automaticamente

### 4. Monitorizar Alertas

Na aba **"Alertas"**:

- Veja alertas de novos contratos envolvendo figuras de interesse
- Clique num alerta para ver detalhes
- Use "Marcar Todos como Lidos" para limpar alertas
- Alertas são gerados automaticamente ao importar novos dados

### 5. Dashboard

Na aba **"Dashboard"**:

- Visualize estatísticas gerais:
  - Total de contratos na base de dados
  - Número de figuras de interesse
  - Alertas não lidos
  - Valor total de contratos
- Veja os alertas mais recentes

## 📁 Estrutura do Projeto

```
contratos-publicos/
├── src/                    # Código fonte
│   ├── database.py         # Gestão da base de dados SQLite
│   ├── scraper.py          # Recolha de dados (API/CSV/Scraping)
│   ├── entities.py         # Gestão de figuras de interesse
│   ├── alerts.py           # Sistema de alertas
│   └── gui.py              # Interface gráfica (Tkinter)
├── data/                   # Base de dados SQLite
│   └── contratos.db
├── logs/                   # Ficheiros de log
│   └── app.log
├── exports/                # Ficheiros exportados
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências Python
└── README.md              # Este ficheiro
```

## 🔧 Configuração Avançada

### API Portal BASE

Para usar a API oficial do Portal BASE:

1. Registe-se no Portal BASE
2. Solicite acesso à API através de: Help Topic → "Contratos Públicos/Pedido de acesso à API Portal Base"
3. Após receber a chave de API, configure no código:

```python
from scraper import ContratosPublicosScraper

scraper = ContratosPublicosScraper()
scraper.configurar_api_base(api_key='SUA_CHAVE_API')
```

### Formato CSV de Importação

O ficheiro CSV deve conter as seguintes colunas (os nomes podem variar):

- `idContrato` ou `id` ou `ID`
- `nomeEntidadeAdjudicante` ou `adjudicante`
- `nifEntidadeAdjudicante` ou `adjudicante_nif`
- `nomeEntidadeAdjudicataria` ou `adjudicataria`
- `nifEntidadeAdjudicataria` ou `adjudicataria_nif`
- `precoContratual` ou `valor`
- `dataPublicacao` ou `dataCelebracaoContrato`
- `tipoContrato`
- `tipoProcedimento`
- `descricao` ou `objectoContrato`
- `distrito`
- `concelho`
- `cpv`
- `prazoExecucao`

Exemplo:
```csv
idContrato,adjudicante,adjudicataria,valor,dataPublicacao,tipoContrato
123456,Câmara Municipal de Lisboa,Empresa XYZ Lda,50000,2024-01-15,Aquisição de Serviços
```

## 🎯 Casos de Uso

### 1. Jornalismo de Investigação
- Monitorize contratos de autarquias específicas
- Detecte padrões suspeitos em adjudicações
- Acompanhe empresas ou pessoas de interesse

### 2. Transparência e Fiscalização
- Cidadãos podem acompanhar contratação pública local
- Análise de concentração de contratos
- Identificação de potenciais conflitos de interesse

### 3. Análise de Mercado
- Empresas podem analisar concorrentes
- Identificar oportunidades de negócio
- Estudar tendências de contratação pública

### 4. Investigação Académica
- Estudos sobre contratação pública
- Análise de redes de entidades
- Estatísticas de adjudicações

## ⚠️ Avisos Importantes

### Dados e Privacidade
- Todos os dados são **públicos** e provenientes do Portal BASE
- A aplicação **não recolhe dados pessoais** dos utilizadores
- Base de dados local armazenada no seu computador

### Uso Responsável
- Respeite as políticas do Portal BASE
- Não sobrecarregue servidores com pedidos excessivos
- Use dados abertos quando disponíveis (preferencial)
- Verifique sempre a informação na fonte oficial

### Web Scraping
- O scraping direto do site BASE.gov.pt deve ser **último recurso**
- Sempre preferir: Dados Abertos > API Oficial > Scraping
- Rate limiting está implementado (1 pedido/segundo)

## 🐛 Resolução de Problemas

### Erro: "Dependências em falta"
```bash
pip install -r requirements.txt
```

### Erro: "tkinter não encontrado" (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Base de dados corrompida
- Apague o ficheiro `data/contratos.db`
- A aplicação criará uma nova base de dados ao iniciar

### Importação CSV falha
- Verifique o encoding do ficheiro (deve ser UTF-8)
- Confirme que as colunas necessárias existem
- Veja logs em `logs/app.log` para detalhes do erro

## 📊 Exemplos de Análise

### Exemplo 1: Monitorizar uma Empresa
```
1. Adicionar "Empresa XYZ Lda" como figura de interesse
2. Importar dados de contratos
3. Sistema gera alertas automáticos quando a empresa aparece
4. Analisar figura para ver: total de contratos, valores, parceiros frequentes
```

### Exemplo 2: Investigar uma Autarquia
```
1. Pesquisar contratos com filtro: Adjudicante = "Câmara Municipal de XXX"
2. Adicionar principais adjudicatárias como figuras de interesse
3. Analisar padrões: empresas que ganham mais contratos, valores, tipos
4. Detectar conexões entre entidades
```

## 🔜 Funcionalidades Futuras

- [ ] Integração com Bot Discord para alertas em tempo real
- [ ] Gráficos e visualizações de dados
- [ ] Análise de texto com NLP (detetar similaridades em descrições)
- [ ] Exportação de relatórios em PDF
- [ ] Comparação temporal de entidades
- [ ] Mapa de calor geográfico de contratos
- [ ] API REST para integração com outras ferramentas

## 📝 Licença

Este projeto é de código aberto para fins educacionais e de transparência.

## 🤝 Contribuir

Sugestões e melhorias são bem-vindas!

## 📞 Suporte

Para questões sobre:
- **Portal BASE**: [www.base.gov.pt](https://www.base.gov.pt)
- **Dados Abertos**: [dados.gov.pt](https://dados.gov.pt)
- **IMPIC**: [www.impic.pt](https://www.impic.pt)

---

**Desenvolvido com Python 🐍 | Para Transparência e Cidadania 🇵🇹**
