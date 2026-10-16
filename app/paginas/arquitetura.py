import pandas as pd
import streamlit as st

from estado import cabecalho, rodape

cabecalho("Arquitetura e governança", "Modelo especializado + workflow determinístico + decisão humana, em cinco camadas")

st.graphviz_chart("""
digraph G {
  rankdir=LR; bgcolor="transparent"; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, margin="0.2,0.12"];
  edge [color="#74008D", penwidth=1.6];
  s [label="1. Sinais\\nvendas, sell-in, sell-out,\\nestoque, carteira, OPs,\\ncapacidade + natureza do dado", fillcolor="#DDCFE4", color="#DDCFE4"];
  j [label="2. Jornada B2B2C\\nsell-in × sell-out,\\nponto cego, proxy dos diretos", fillcolor="#DDCFE4", color="#DDCFE4"];
  p [label="3. Previsão (IA)\\nsazonal família × nível SKU\\n8 métodos, champion-challenger", fillcolor="#74008D", color="#74008D", fontcolor="white"];
  m [label="4. Motor de decisão\\nnecessidade, lote,\\ncapacidade, 9 ações", fillcolor="#DDCFE4", color="#DDCFE4"];
  h [label="5. Decisão humana\\naprovar · ajustar · rejeitar\\n+ motivo, log versionado", fillcolor="#31003E", color="#31003E", fontcolor="white"];
  c [label="Clube CI\\nQR/NFC + NF verificada", fillcolor="#F4A6CB", color="#F4A6CB"];
  s -> j -> p -> m -> h;
  h -> p [label=" realizado + decisão → erro, viés, FVA → recalibra", fontsize=9, fontcolor="#74008D", style=dashed, constraint=false];
  c -> j [label=" sell-out verificado", fontsize=9, fontcolor="#74008D", style=dashed];
}
""", width="stretch")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Natureza do dado", divider="violet")
    st.dataframe(pd.DataFrame([
        ("Observado", "Vendas diretas, sell-out do parceiro, estoque", "Fonte, período e granularidade visíveis"),
        ("Verificado pelo consumidor", "Compra com NF validada no Clube", "Peso alto; é amostra, não censo"),
        ("Declarado pelo consumidor", "Loja e preço informados sem NF", "Peso baixo; sinal direcional"),
        ("Calculado", "Necessidade líquida, segurança, risco", "Fórmula exibida no detalhe do SKU"),
        ("Estimado", "Proxy dos diretos no ponto cego", "Reduz a confiança da recomendação"),
        ("Previsto", "Demanda out–dez/2026", "Erro e viés do backtest exibidos"),
        ("Indisponível", "Parceiro × SKU sem sell-out", "Nunca vira zero; recomendação Investigar"),
    ], columns=["Natureza", "Exemplo", "Tratamento"]), hide_index=True, width="stretch")
with c2:
    st.subheader("Controles", divider="violet")
    st.dataframe(pd.DataFrame([
        ("Decisão", "Nenhuma OP é liberada automaticamente; tudo nasce 'Aguardando aprovação'"),
        ("Auditoria", "Log com responsável, motivo, quantidade e versão do modelo"),
        ("Qualidade", "Contrato de colunas por fonte; datas inválidas bloqueadas; carteira deduplicada"),
        ("Monitoramento", "WAPE, viés, holdout, FVA (quando houver realizado), cobertura de sell-out"),
        ("Privacidade", "Dado pessoal do Clube fica fora do Cockpit; só agregados (LGPD)"),
        ("IA generativa", "Fora do caminho crítico: só explica e lê NF; não altera números"),
    ], columns=["Controle", "Regra"]), hide_index=True, width="stretch")

st.subheader("Componentes deste protótipo", divider="violet")
st.markdown("""
| Camada | Módulo | O que faz |
|---|---|---|
| 1. Sinais | `src/cockpit/dados.py` | Carrega as fontes, valida contrato e rotula a natureza do dado |
| 2. Jornada | `src/cockpit/jornada.py` | Sell-in × sell-out, ponto cego, recomendações comerciais |
| 3. Previsão | `src/models/forecast_demanda.py`, `src/cockpit/backtest.py` | Previsão SKU × canal e backtest de 8 métodos com holdout |
| 4. Motor | `src/cockpit/motor.py` | Necessidade líquida, lote, capacidade, pedidos em risco, recomendações |
| 5. Decisão | `src/cockpit/decisoes.py` | Registro versionado e indicadores do laço humano |
| Segurança | `src/cockpit/seguranca.py` | 6 verificações executáveis (também no pytest) |
| Clube | `src/cockpit/clube.py` | Validação de NF (chave de 44 dígitos) e modelo econômico |
| Diagnóstico | `src/cockpit/diagnostico.py` | Insights da base histórica: fator único, sazonalidade, cadastro defasado, ruptura × excesso |
| Clube (piloto) | `src/cockpit/clube_sim.py` | Simulação do piloto para o backoffice e o envio de sell-out verificado à IA |
""")
rodape()
