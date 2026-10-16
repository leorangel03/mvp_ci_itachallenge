# Caderno Inteligente — Cockpit de Decisão Semanal B2B2C

Protótipo do **Golden Squad (G09)** para o Desafio 3 do ITA Challenge Sprint (AllevoTech).
Toda segunda-feira, PCP e Comercial recebem uma **fila priorizada de decisões**: o que produzir ou repor, quanto,
para quem, com a evidência, a natureza do dado e a confiança de cada recomendação. Uma pessoa aprova, ajusta ou
rejeita, e a decisão volta para o modelo.

> Base fictícia do desafio (posição de 14/09/2026, horizonte até 31/10/2026). Nenhuma OP é liberada automaticamente.

## Arquitetura (5 camadas = menu do app)

| Camada | Módulo | O que faz |
|---|---|---|
| 1. Sinais | `src/cockpit/dados.py` | Carrega as 14 fontes, valida o contrato de colunas e rotula a natureza do dado (observado, verificado, declarado, calculado, estimado, previsto, indisponível) |
| 2. Jornada B2B2C | `src/cockpit/jornada.py` | Sell-in × sell-out por parceiro, ponto cego (24,9% do volume), acúmulo (KA-02), recomendações comerciais |
| 3. Previsão (IA) | `src/models/forecast_demanda.py`, `src/cockpit/backtest.py` | Sazonal da família × nível do SKU, escolhido entre 8 métodos (WAPE 9,18% × 11,33% do sazonal ingênuo) e confirmado em holdout temporal |
| 4. Motor de decisão | `src/cockpit/motor.py` | Necessidade = máx(previsão, carteira) + segurança − estoque − OPs no prazo; lote mínimo; capacidade semanal; pedidos em risco; recomendações |
| 5. Decisão humana | `src/cockpit/decisoes.py` | Aprovar, ajustar ou rejeitar com responsável e motivo; log versionado para erro, viés e FVA |
| Segurança | `src/cockpit/seguranca.py` | 6 verificações executáveis (sell-out ausente, SKU novo, pedido duplicado, OP tardia, capacidade, aprovação humana) |
| Clube CI | `src/cockpit/clube.py` | Captura de compra por QR/NF (validação da chave de 44 dígitos, CNPJ → parceiro) e modelo econômico do ecossistema |

## Páginas (a história em cinco momentos)

| Menu | Página | Pergunta que responde |
|---|---|---|
| Jornada da decisão | Visão geral do ciclo | Onde estamos e como os cinco momentos se conectam? |
| | 1. Diagnóstico histórico | Como o PCP decide hoje e o que 24 meses revelam (fator único, sazonalidade, cadastro defasado, ruptura × excesso, ponto cego, capacidade) |
| | 2. Previsão otimizada | Quais sinais o algoritmo usa; rodar a previsão; modelo × comercial; explosão SKU × canal × mês |
| | 3. Plano de produção e mix | Fila de decisões, carga × capacidade e distribuição do mix por canal e parceiro |
| | 4. Rastreabilidade da conversão | Sell-out e NFC no parceiro; funil, mapa e captura de NF no consumidor |
| | 5. Resultados e retroalimentação | Economia operacional, receita do Clube, dados de volta para a IA e projeção de 36 meses |
| Operação | Detalhe do SKU · Log de decisões | Cálculo, evidências, aprovação humana e histórico |
| Clube CI | App do consumidor · Backoffice do Clube | Protótipo visual do app; controle de membros, campanhas, resgates e envio para a IA |
| Confiança | Validação do modelo · Verificações de segurança · Arquitetura e governança | 8 métodos e holdout; 6 casos ao vivo; camadas e controles |

Os números do Clube vêm de `src/cockpit/clube_sim.py`, uma simulação determinística do piloto (cenário-base, 6 meses) que usa o mix
real de SKUs e parceiros; a interface rotula esses dados como simulação.

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
pytest -q          # 20 testes: motor, jornada, backtest, segurança, Clube e pipeline legado
```

Para regenerar a previsão out–dez/2026: `python -m src.models.forecast_demanda`.

## Números de referência (reproduzidos pelos testes)

| Indicador | Valor |
|---|---|
| Pedidos em risco de atraso | 23 de 53 · R$ 641.796 a preço de tabela |
| Excesso acima de 90 dias | R$ 226.376 hoje → R$ 681.297 se as OPs abertas forem executadas |
| Ponto cego do sell-out | 24,9% do volume (KAs sem sell-out) |
| Previsão: modelo × alternativa simples | WAPE 9,18% × 11,33% (1.650 previsões por método); holdout fev–jul/26: 9,42% × 11,49% |
| Verificações de segurança | 6 de 6 |
| Clube (cenário-base) | payback do ecossistema no mês 9 · R$ 919.530 em 36 meses |

## Dados adicionados pelo grupo

`data/raw/Lancamentos_Colecao_Primavera.csv`: dois SKUs de lançamento sem histórico, criados a partir do evento
"Lançamento Coleção Primavera" do `Calendario_Eventos` para testar o comportamento diante de dado insuficiente.
Os CNPJs dos parceiros usados na validação de NF são fictícios.

## Legado

Os módulos `src/data`, `src/features`, `src/models/04–07` e `src/evaluation` são o pipeline da V1 (risco por regressão
logística). Eles continuam no repositório e nos testes, mas não alimentam o Cockpit.
