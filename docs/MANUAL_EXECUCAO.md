# Manual de Execução — MVP Caderno Inteligente

## Pré-requisitos
- Python 3.9+
- pip ou conda
- Git

## Passo 1: Clonar o repositório
```bash
git clone https://github.com/leorangel03/prototipo-ia-dados.git
cd prototipo-ia-dados
```

## Passo 2: Criar ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

## Passo 3: Instalar dependências
```bash
pip install -r requirements.txt
```

## Passo 4: Executar o pipeline de dados (Fase 1 + 2)
```bash
python -m src.data.01_pipeline_dados
python -m src.data.02_dataset_analitico
```
Saída esperada: arquivos em `data/processed/`

## Passo 5: Gerar features (Fase 3)
```bash
python -m src.features.03_feature_engineering
```
Saída esperada: `data/processed/features.csv`

## Passo 6: Calcular baseline (Fase 4)
```bash
python -m src.models.04_baseline
```
Saída esperada: `data/processed/baseline_scores.csv`

## Passo 7: Treinar modelo ML (Fase 5)
```bash
python -m src.models.05_modelo_ml
```
Saída esperada: `data/processed/modelo_ruptura.joblib` e métricas

## Passo 8: Executar backtesting (Fase 6)
```bash
python -m src.evaluation.06_backtesting
```
Saída esperada: `data/processed/backtesting_resultados.csv`

## Passo 9: Gerar priorização final (Fase 7)
```bash
python -m src.models.07_priorizacao
```
Saída esperada: `data/processed/priorizacao_final.csv`

## Passo 10: Executar relatório (Fase 9)
```bash
python -m src.evaluation.09_relatorio_execucao
```
Saída esperada: `data/processed/relatorio_execucao.csv`

## Passo 11: Iniciar painel Streamlit (Fase 8)
```bash
streamlit run app/streamlit_app.py
```
Acesse: http://localhost:8501

## Passo 12: Executar testes
```bash
pytest tests/ -v
```

## Verificação de Sucesso
Após executar, verifique se os seguintes arquivos foram criados:
- `data/processed/Vendas_24m_processado.csv`
- `data/processed/Estoque_Atual_processado.csv`
- `data/processed/dataset_analitico.csv`
- `data/processed/features.csv`
- `data/processed/baseline_scores.csv`
- `data/processed/modelo_ruptura.joblib`
- `data/processed/backtesting_resultados.csv`
- `data/processed/priorizacao_final.csv`
- `data/processed/relatorio_execucao.csv`

Se todos os arquivos estão presentes, o pipeline foi executado com sucesso.

## Solução de Problemas

### Erro: "Arquivo não encontrado"
- Verifique se os CSVs originais estão no nível raiz do projeto
- Confirme que o path está correto em config/config.yaml

### Erro: "KeyError" em colunas
- Verifique o dicionário de dados em Dicionario_Dados.csv
- Adapte os nomes de coluna em cada módulo conforme necessário

### Erro: "ImportError"
- Confirme que o ambiente virtual está ativado
- Reinstale com: pip install -r requirements.txt --force-reinstall

### Painel Streamlit não abre
- Verifique se Streamlit foi instalado: pip install streamlit
- Tente: streamlit run app/streamlit_app.py --logger.level=debug

## Estrutura de Saída

### data/processed/
```
dataset_analitico.csv          # Base analítica por SKU×mês
features.csv                   # Features engenheiradas
baseline_scores.csv            # Scores do baseline determinístico
modelo_ruptura.joblib          # Modelo ML serializado
backtesting_resultados.csv     # Comparação baseline vs modelo
priorizacao_final.csv          # Ranking final de risco
relatorio_execucao.csv         # Métricas e conclusões
```

## Próximas Execuções
Se você precisar re-executar apenas uma etapa:
- Apague o arquivo de saída (ex: features.csv)
- Execute o módulo específico
- Mantenha as dependências anteriores intactas

## Contato e Suporte
Para dúvidas, refira-se à documentação em `docs/`
