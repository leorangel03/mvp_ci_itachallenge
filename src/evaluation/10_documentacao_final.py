from __future__ import annotations

from pathlib import Path
from datetime import datetime

import pandas as pd


class DocumentacaoFinal:
    """
    Fase 10 do MVP Caderno Inteligente.

    Objetivo:
    - consolidar toda documentação do projeto;
    - registrar decisões, premissas e limitações;
    - preparar plano de próximas etapas;
    - gerar resumo executivo para stakeholders.
    """

    def __init__(self, root_dir: str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self.docs_dir = self.root / "docs"
        self.processed_dir = self.root / "data" / "processed"

    def generate_summary(self) -> str:
        summary = f"""# Resumo Executivo — MVP Caderno Inteligente

## Data de Geração
{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

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
"""
        return summary

    def generate_execution_manual(self) -> str:
        manual = """# Manual de Execução — MVP Caderno Inteligente

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
venv\\Scripts\\activate  # Windows
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
"""
        return manual

    def save_documentation(self) -> None:
        summary = self.generate_summary()
        manual = self.generate_execution_manual()

        self.docs_dir.mkdir(parents=True, exist_ok=True)

        summary_path = self.docs_dir / "relatorio_final.md"
        summary_path.write_text(summary)

        manual_path = self.docs_dir / "MANUAL_EXECUCAO.md"
        manual_path.write_text(manual)

        print(f"Documentação salva em:\n- {summary_path}\n- {manual_path}")


if __name__ == "__main__":
    doc = DocumentacaoFinal()
    doc.save_documentation()
