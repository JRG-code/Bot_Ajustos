# Guia de Início Rápido

## 🚀 Instalação e Primeiro Uso (5 minutos)

### 1. Instalar Dependências

```bash
cd contratos-publicos
pip install -r requirements.txt
```

### 2. Testar a Instalação

```bash
python test_app.py
```

Deve ver: `🎉 Todos os testes passaram!`

### 3. Executar a Aplicação

```bash
python main.py
```

A interface gráfica abrirá automaticamente.

---

## 📝 Tutorial Básico (10 minutos)

### Passo 1: Importar Dados de Exemplo

1. Abra a aplicação: `python main.py`
2. Vá para a aba **"Importar Dados"**
3. Selecione **"Ficheiro CSV Local"**
4. Clique em **"Iniciar Importação"**
5. Selecione o ficheiro: `data/exemplo_contratos.csv`
6. Aguarde a importação (15 contratos de exemplo)

### Passo 2: Pesquisar Contratos

1. Vá para a aba **"Pesquisar Contratos"**
2. Experimente filtros:
   - **Distrito**: Lisboa
   - **Ano (de)**: 2024
   - Clique em **"Pesquisar"**
3. Duplo clique num contrato para ver detalhes completos

### Passo 3: Adicionar Figura de Interesse

1. Vá para a aba **"Figuras de Interesse"**
2. Adicione uma figura:
   - **Nome**: Construções Silva & Filhos Lda
   - **Tipo**: empresa
   - Clique em **"Adicionar Figura"**
3. Selecione a figura na lista
4. Clique em **"Analisar Figura"**
5. Veja estatísticas: contratos, valores, parceiros

### Passo 4: Ver Alertas

1. Vá para a aba **"Alertas"**
2. Veja alertas gerados automaticamente
3. Clique num alerta para ver detalhes
4. O alerta será marcado como lido automaticamente

### Passo 5: Exportar Resultados

1. Faça uma pesquisa (Passo 2)
2. Menu: **Ficheiro** → **Exportar Resultados**
3. Escolha onde guardar o ficheiro Excel
4. Abra em Excel/LibreOffice para análise

---

## 💡 Dicas Rápidas

### Pesquisa Eficiente

- Use pesquisa parcial: "Câmara" encontra todas as câmaras
- Combine filtros: Distrito + Ano + Valor Mínimo
- Deixe campos vazios para pesquisa abrangente

### Figuras de Interesse

- Adicione nomes EXATOS como aparecem nos contratos
- Use NIF quando disponível para maior precisão
- Marque como "empresa" ou "entidade_publica" conforme apropriado

### Alertas Automáticos

- Alertas são gerados na importação de dados
- Quanto mais figuras tiver, mais alertas receberá
- Veja dashboard para resumo de alertas não lidos

### Performance

- Primeiros 1000 contratos: ~10 segundos de importação
- Pesquisas são instantâneas (índices SQLite)
- Exportação Excel: ~5 segundos para 1000 registos

---

## 📊 Exemplos de Análise

### Encontrar Todas as Câmaras

**Filtros:**
- Adjudicante: "Câmara Municipal"
- Deixar resto vazio

**Resultado:** Todos os contratos onde uma câmara é adjudicante

---

### Contratos Acima de 100.000€

**Filtros:**
- Valor Mín: 100000
- Ano: 2024

**Resultado:** Grandes contratos de 2024

---

### Monitorizar Empresa Específica

1. Adicionar empresa como figura de interesse
2. Importar novos dados periodicamente
3. Verificar alertas na aba "Alertas"

---

## ⚠️ Resolução Rápida de Problemas

### "No module named 'tqdm'"

```bash
pip install tqdm
```

### "tkinter não encontrado" (Linux)

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Aplicação não abre

1. Verifique Python 3.10+: `python --version`
2. Execute testes: `python test_app.py`
3. Veja logs: `cat logs/app.log`

### CSV não importa

1. Verifique encoding UTF-8
2. Confirme formato (veja `data/exemplo_contratos.csv`)
3. Veja log na aba "Importar Dados"

---

## 🎯 Próximos Passos

1. **Importar Dados Reais**
   - Descarregue CSV do [dados.gov.pt](https://dados.gov.pt)
   - Dataset: "Contratos Públicos - Portal BASE"
   - Importe usando a aplicação

2. **Criar Lista de Figuras**
   - Identifique empresas/pessoas de interesse
   - Adicione à aplicação
   - Configure alertas

3. **Análise Regular**
   - Importe dados novos mensalmente
   - Verifique alertas
   - Exporte relatórios

4. **Automação (Avançado)**
   - Use módulos Python diretamente
   - Crie scripts personalizados
   - Integre com outras ferramentas

---

## 📚 Mais Informações

- **README completo**: `README.md`
- **Documentação de código**: Comentários nos ficheiros Python
- **Logs**: `logs/app.log`

---

**Precisa de ajuda?** Consulte o README.md ou os comentários no código fonte.

**Bom trabalho de investigação! 🔍📊**
