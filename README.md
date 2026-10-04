# Caderno Inteligente — MVP de Risco Operacional

Protótipo de solução baseada em dados e IA para apoio à decisão em planejamento de demanda, estoque e produção.

**Objetivo:** Identificar antecipadamente riscos de ruptura e excesso de estoque, melhorando a priorização de produção e planejamento de demanda.

**Status:** Versão 0.1 — Protótipo Funcional

---

## 📋 Visão Geral

Este repositório contém um MVP (Minimum Viable Product) completo de um sistema de inteligência operacional para supply chain. O projeto foi desenvolvido de forma incremental, em 10 fases, combinando análise de dados, engenharia de features, baseline determinístico e modelo de machine learning.

### Hipótese Principal

> "Ao integrar demanda, forecast, estoque, carteira de pedidos, produção, capacidade e lead time, podemos identificar antecipadamente riscos de ruptura/excesso e melhorar a priorização de produção e estoque."

### Tecnologias

- **Python 3.9+**
- **pandas, numpy** — manipulação de dados
- **scikit-learn** — machine learning
- **joblib** — serialização de modelos
- **streamlit** — painel executivo
- **pytest** — testes automatizados

---

## 🏗️ Arquitetura do Projeto

O MVP segue uma estrutura modular dividida em **10 fases**:

```
Fase 1: Pipeline de Dados
    ↓
Fase 2: Dataset Analítico (SKU × Período)
    ↓
Fase 3: Feature Engineering
    ↓
Fase 4: Baseline Determinístico
    ↓
Fase 5: Modelo de Machine Learning
    ↓
Fase 6: Backtesting (Baseline vs Modelo)
    ↓
Fase 7: Priorização Final (Ranking + Recomendação)
    ↓
Fase 8: Painel Executivo (Streamlit)
    ↓
Fase 9: Relatório de Execução (Métricas)
    ↓
Fase 10: Documentação Final
```

### Estrutura de Arquivos

```
prototipo-ia-dados/
├── README.md                           # Este arquivo
├── requirements.txt                    # Dependências Python
├── .gitignore                          # Controle de versão
├── config/
│   └── config.yaml                    # Configuração centralizada
├── data/
│   ├── raw/                           # Dados originais (processados)
│   ├── processed/                     # Dados tratados e features
│   └── README.md                      # Documentação de dados
├── docs/
│   ├── desafio.md                     # Descrição do problema
│   ├── diagnostico_dados.md           # Análise inicial dos dados
│   ├── hipotese_solucao.md            # Hipótese do MVP
│   ├── planejamento_prototipo.md      # Plano de execução
│   ├── relatorio_final.md             # Resumo executivo (gerado)
│   └── MANUAL_EXECUCAO.md             # Passo a passo de execução (gerado)
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── 01_pipeline_dados.py       # Fase 1: Carregamento e tratamento
│   │   └── 02_dataset_analitico.py    # Fase 2: Integração por SKU×mês
│   ├── features/
│   │   ├── __init__.py
│   │   └── 03_feature_engineering.py  # Fase 3: Features operacionais
│   ├── models/
│   │   ├── __init__.py
│   │   ├── 04_baseline.py             # Fase 4: Baseline determinístico
│   │   ├── 05_modelo_ml.py            # Fase 5: Modelo de classificação
│   │   └── 07_priorizacao.py          # Fase 7: Ranking final
│   └── evaluation/
│       ├── __init__.py
│       ├── 06_backtesting.py          # Fase 6: Comparação de modelos
│       ├── 09_relatorio_execucao.py   # Fase 9: Métricas de performance
│       └── 10_documentacao_final.py   # Fase 10: Documentação
├── app/
│   ├── __init__.py
│   └── streamlit_app.py               # Fase 8: Painel executivo
├── tests/
│   └── test_dataset_analitico.py      # Testes automatizados
└── notebooks/                          # Notebooks de análise (opcional)
```

---

## 🚀 Quick Start

### 1. Clonar o Repositório

```bash
git clone https://github.com/leorangel03/prototipo-ia-dados.git
cd prototipo-ia-dados
```

### 2. Criar Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Executar o Pipeline Completo

```bash
# Fase 1 + 2: Pipeline e Dataset Analítico
python -m src.data.01_pipeline_dados
python -m src.data.02_dataset_analitico

# Fase 3: Features
python -m src.features.03_feature_engineering

# Fase 4: Baseline
python -m src.models.04_baseline

# Fase 5: Modelo ML
python -m src.models.05_modelo_ml

# Fase 6: Backtesting
python -m src.evaluation.06_backtesting

# Fase 7: Priorização
python -m src.models.07_priorizacao

# Fase 9: Relatório
python -m src.evaluation.09_relatorio_execucao

# Fase 10: Documentação
python -m src.evaluation.10_documentacao_final
```

### 5. Iniciar o Painel Streamlit (Fase 8)

```bash
streamlit run app/streamlit_app.py
```

Acesse em: http://localhost:8501

### 6. Executar Testes

```bash
pytest tests/ -v
```

---

## 📊 Dados Utilizados

### Fonte
Base fictícia do **ITA Challenge Sprint** — todos os dados, nomes, preços e valores são simulados.

### Período
- Histórico realizado: até agosto de 2026
- Posição atual: setembro de 2026
- Previsão: outubro a dezembro de 2026

### Tabelas Principais

| Tabela | Descrição | Granularidade |
|--------|-----------|---|
| **Produtos** | Catálogo com SKU, família, lead time, estoque, cobertura | SKU |
| **Vendas_24m** | Histórico de faturamento por SKU, cliente/canal e mês | SKU × Mês × Cliente |
| **Estoque_Atual** | Posição atual de estoque por SKU | SKU |
| **Historico_Estoque** | Estoque mensal histórico | SKU × Mês |
| **Forecast_Comercial** | Previsão de demanda (out-dez/26) | SKU × Mês |
| **Carteira_Pedidos** | Pedidos confirmados com data prometida | Pedido × SKU |
| **Ordens_Producao** | Ordens de produção planejadas | Ordem × SKU |
| **Capacidade_Semanal** | Capacidade por linha e ocupação | Linha × Semana |
| **Lead_Times** | Tempo de produção/disponibilidade | SKU × Família |
| **Parceiros_Canais** | Parceiros B2B e canais diretos | Cliente × Região |

---

## 🔍 Como Funciona

### Fase 1 — Pipeline de Dados
Carrega CSVs originais, normaliza colunas, trata tipos, converte datas, remove duplicatas e salva versões processadas em `data/processed/`.

### Fase 2 — Dataset Analítico
Integra demanda, forecast, estoque, pedidos, ordens e lead time por **SKU × mês**. Cria base consolidada para análise.

### Fase 3 — Feature Engineering
Gera indicadores operacionais:
- Demanda: média móvel, tendência, variabilidade
- Estoque: cobertura em dias, relativo à demanda, vs. mínimo
- Pedidos: quantidade, proporção da demanda
- Capacidade: disponível, comprometida, ocupação
- Lead time: dias, vs. horizonte
- Risco: pressão de demanda, score operacional

### Fase 4 — Baseline Determinístico
Aplica regras de negócio simples para classificar risco:
- **ALTO:** estoque negativo ou cobertura abaixo do mínimo
- **MEDIO:** estoque baixo ou demanda alta
- **BAIXO:** situação equilibrada

Score = 45% baseline + 30% modelo + 15% sinais + ajustes

### Fase 5 — Modelo de Machine Learning
Treina **regressão logística** com validação temporal (80% treino, 20% teste).
- Sem leakage temporal
- Pipeline de pré-processamento (imputação + normalização)
- Métricas: accuracy, precision, recall, F1, ROC-AUC

### Fase 6 — Backtesting
Compara baseline vs modelo em dados de teste.
Mede: recall, precision, F1-score, detecção de ruptura.

### Fase 7 — Priorização Final
Gera ranking final por SKU/mês:
- Score de risco (0-1)
- Nível (ALTO, MEDIO, BAIXO)
- Prioridade (1, 2, 3...)
- Recomendação operacional

### Fase 8 — Painel Executivo
Dashboard Streamlit com:
- Visão geral de risco
- Ranking de prioridade
- Distribuição por nível
- Top 10 SKUs críticos
- Filtros por período e SKU

### Fase 9 — Relatório de Execução
Consolida métricas:
- Performance do baseline
- Performance do modelo
- Ganho relativo
- Conclusão e recomendação

### Fase 10 — Documentação Final
Gera:
- Resumo executivo (`docs/relatorio_final.md`)
- Manual de execução (`docs/MANUAL_EXECUCAO.md`)

---

## 📈 Resultados Esperados

Após executar o pipeline completo, você terá:

### Artefatos de Dados
- `dataset_analitico.csv` — Base por SKU × mês
- `features.csv` — Todas as features engenheiradas
- `baseline_scores.csv` — Scores do baseline
- `modelo_ruptura.joblib` — Modelo serializado
- `backtesting_resultados.csv` — Comparação baseline vs modelo
- `priorizacao_final.csv` — Ranking final com recomendações
- `relatorio_execucao.csv` — Métricas consolidadas

### Documentação Gerada
- `docs/relatorio_final.md` — Resumo executivo
- `docs/MANUAL_EXECUCAO.md` — Passo a passo completo

### Painel Executivo
- http://localhost:8501 — Dashboard interativo

---

## 🎯 Decisões de Design

### 1. Preservação de Dados Brutos
Arquivos originais mantidos intactos. Cópias processadas em `data/processed/`.

### 2. Divisão Temporal vs. Aleatória
**80% treino** (dados antigos) + **20% teste** (dados recentes) para evitar leakage temporal.

### 3. Baseline Antes de ML
Regras determinísticas simples e explicáveis, antes de complexidade de IA.

### 4. Features Operacionais
Indicadores ligados diretamente à decisão de supply chain, não features genéricas.

### 5. Ensemble Simples
Score final = combinação ponderada de baseline + modelo + sinais de negócio.

---

## ⚠️ Limitações Conhecidas

- **Base fictícia:** Não representa cenários reais de ruptura
- **Cobertura parcial:** Sell-out não disponível para todos os SKU/canal
- **Lead time fixo:** Não modela variabilidade de produção
- **Sem sazonalidade extrema:** Calendário de eventos não capturado completamente
- **Modelo inicial:** Regressão logística, sem hiperfinetuning
- **Janela de teste pequena:** 20% dos dados para validação temporal

---

## 🔄 Próximos Passos Recomendados

### Curto Prazo (1-2 semanas)
1. **Validação com usuários** — apresentar painel a stakeholders operacionais
2. **Coleta de feedback** — ajustar pesos de risco baseado em experiência
3. **Refinamento de features** — adicionar variáveis externas

### Médio Prazo (1-2 meses)
1. **Integração de dados reais** — substituir base fictícia
2. **Modelos avançados** — testar XGBoost, LightGBM, ensemble
3. **Validação cruzada robusta** — time series cross-validation

### Longo Prazo (3+ meses)
1. **Deploy em produção** — API REST, pipeline automático
2. **Alertas em tempo real** — notificações para ruptura iminente
3. **Monitoramento contínuo** — drift de modelo, performance em produção
4. **Integração com ERP** — sincronização automática de dados

---

## 🧪 Testes Automatizados

```bash
pytest tests/ -v
```

Testes cobrem:
- Carregamento e validação de dados
- Geração de features
- Cálculo de baseline
- Construção do modelo
- Priorização final

---

## 📚 Documentação Adicional

- **[docs/desafio.md](docs/desafio.md)** — Descrição do problema de negócio
- **[docs/diagnostico_dados.md](docs/diagnostico_dados.md)** — Análise inicial dos dados
- **[docs/hipotese_solucao.md](docs/hipotese_solucao.md)** — Hipótese do MVP
- **[docs/planejamento_prototipo.md](docs/planejamento_prototipo.md)** — Plano de execução
- **[docs/relatorio_final.md](docs/relatorio_final.md)** — Resumo executivo (gerado)
- **[docs/MANUAL_EXECUCAO.md](docs/MANUAL_EXECUCAO.md)** — Passo a passo (gerado)

---

## 🤝 Contribuições

Este é um protótipo aberto para evolução. Contribuições e feedback são bem-vindos!

**Pontos de melhoria identificados:**
- Melhorar explicabilidade das features
- Adicionar visualizações de SHAP
- Implementar data drift detection
- Otimizar performance para grande volume

---

## 📝 Licença

Este projeto foi desenvolvido como protótipo de pesquisa e educação.

---

## 👤 Autor

**Desenvolvido como MVP**  
Tech Lead: Leonardo Rangel 
Data: Outubro de 2026

---

## 📞 Suporte

Para dúvidas:
1. Consulte a documentação em `docs/`
2. Revise o arquivo `MANUAL_EXECUCAO.md`
3. Verifique os logs e mensagens de erro
4. Execute os testes para validar o ambiente

---

## ✅ Checklist de Validação

Após executar o projeto, verifique:

- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (pip install -r requirements.txt)
- [ ] Pipeline executado (Phase 1-2)
- [ ] Features geradas (Phase 3)
- [ ] Baseline calculado (Phase 4)
- [ ] Modelo treinado (Phase 5)
- [ ] Backtesting executado (Phase 6)
- [ ] Priorização gerada (Phase 7)
- [ ] Painel abre sem erros (Phase 8)
- [ ] Relatório gerado (Phase 9)
- [ ] Documentação criada (Phase 10)
- [ ] Testes passam (pytest)
- [ ] Todos os artefatos em `data/processed/`

---

## 🎓 Entender o Projeto

**Fluxo de Dados:**
```
CSV original → Pipeline (normalizar) → Dataset Analítico 
    ↓
Features → Baseline + Modelo ML → Backtesting
    ↓
Priorização → Painel Streamlit → Decisão Operacional
```

**Modelo de Risco:**
- **Risco de Ruptura:** Estoque projetado < 0 ou cobertura < mínimo
- **Risco de Excesso:** Estoque > demanda média × 3
- **Score Final:** Combinação ponderada de sinais

---

**Versão:** 0.1  
**Status:** Protótipo Funcional  
**Última Atualização:** Outubro de 2026

