# Resumo Executivo — MVP Caderno Inteligente

## Data de Geração
07/10/2026 23:29:52

## Objetivo do Protótipo
Prototipo de solução baseada em dados e IA para apoio à decisão em planejamento de demanda, estoque e produção.
Foco: identificar riscos de ruptura e excesso de estoque por SKU e período.

## Arquitetura do Projeto
O projeto segue uma abordagem incremental dividida em 10 fases:
- Fase 1: Pipeline de dados (carga, validação, normalização)
- Fase 2: Dataset analítico (integração por SKU × mês)
- Fase 3: Feature engineering (indicadores operacionais)
- Fase 4: Baseline determinístico (regras de negócio simples)
- Fase 5: Modelo ML (classificação para risco de ruptura)
- Fase 6: Backtesting (comparação baseline vs modelo)
- Fase 7: Priorização final (ranking e recomendação)
- Fase 8: Painel executivo (Streamlit)
- Fase 9: Relatório de execução (métricas e conclusões)
- Fase 10: Documentação final (este documento)

## Dados Utilizados
- Origem: Base fictícia do ITA Challenge Sprint
- Período: setembro 2025 — setembro 2026
- Granularidade: SKU × período (mensal)
- Tabelas principais:
  - Produtos: catálogo e características
  - Vendas_24m: histórico de 24 meses
  - Estoque: atual e histórico
  - Forecast: previsão de demanda
  - Pedidos: carteira confirmada
  - Ordens: planejamento de produção
  - Capacidade: recursos disponíveis

## Decisões Técnicas Principais
1. **Preservação de dados brutos**: arquivos originais mantidos intactos em `/` e copiados para `data/raw/`
2. **Divisão temporal**: 80% treino (dados antigos) × 20% teste (dados recentes) — evita leakage
3. **Baseline determinístico**: antes de ML, validar com regras de negócio simples e explicáveis
4. **Features operacionais**: demanda média, cobertura, pressão, lead time, risco
5. **Modelo simples**: regressão logística com pipeline de pré-processamento
6. **Combinação ensemble**: score final = 45% baseline + 30% modelo + 15% sinais + ajustes

## Limitações Conhecidas
- Base fictícia: não representa cenários reais de ruptura
- Cobertura parcial de sell-out: dados não disponíveis para todos os SKU/canal
- Lead time fixo: não modela variabilidade de produção
- Sem contexto de sazonalidade extrema ou eventos especiais
- Modelo sem validação cruzada temporal mais robusta

## Próximos Passos Recomendados
1. **Validação com usuários**: apresentar painel a stakeholders operacionais
2. **Coleta de feedback**: ajustar pesos de risco baseado em experiência do negócio
3. **Integração de dados reais**: substituir base fictícia por dados históricos reais
4. **Refinamento de features**: adicionar sazonalidade, eventos e variáveis externas
5. **Modelo avançado**: testar XGBoost, LightGBM ou ensemble com melhor calibração
6. **Deploy em produção**: API REST, pipeline automático, alertas em tempo real
7. **Monitoramento contínuo**: tracked de performance do modelo em produção

## Estrutura de Arquivos
```
prototipo-ia-dados/
├── README.md
├── .gitignore
├── requirements.txt
├── config/
│   └── config.yaml (configuração centralizada)
├── data/
│   ├── raw/ (dados originais processados)
│   └── processed/ (features, dataset analítico, resultados)
├── docs/
│   ├── desafio.md
│   ├── diagnostico_dados.md
│   ├── hipotese_solucao.md
│   ├── planejamento_prototipo.md
│   └── relatorio_final.md (este)
├── src/
│   ├── data/
│   │   ├── 01_pipeline_dados.py
│   │   └── 02_dataset_analitico.py
│   ├── features/
│   │   └── 03_feature_engineering.py
│   ├── models/
│   │   ├── 04_baseline.py
│   │   ├── 05_modelo_ml.py
│   │   └── 07_priorizacao.py
│   └── evaluation/
│       ├── 06_backtesting.py
│       └── 09_relatorio_execucao.py
├── app/
│   └── streamlit_app.py (painel executivo)
└── tests/
    └── test_dataset_analitico.py
```

## Como Executar o Projeto
Veja o arquivo MANUAL_EXECUCAO.md para instruções passo a passo.

## Autores
Desenvolvido como MVP usando IA como apoio ao desenvolvimento (Tech Lead).

## Status
Versão 0.1 — Protótipo Funcional
