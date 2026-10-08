import sys
from importlib import import_module
from pathlib import Path

import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Módulo iniciado por dígito não é importável com `import`.
PriorizacaoFinal = import_module("src.models.07_priorizacao").PriorizacaoFinal

st.set_page_config(page_title="Caderno Inteligente", layout="wide")
st.title("Painel de Risco Operacional — Caderno Inteligente")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(ROOT / "data/processed/priorizacao_final.csv")
    except FileNotFoundError:
        obj = PriorizacaoFinal()
        df = obj.build()
    if "mes" in df.columns:
        df["mes"] = pd.to_datetime(df["mes"], errors="coerce")
    return df


df = load_data()

if df.empty:
    st.warning("Nenhum dado disponível para exibir.")
    st.stop()

periodos = sorted(df["mes"].dropna().unique().tolist()) if "mes" in df.columns else []
selected_period = st.selectbox("Período", periodos[-12:] if len(periodos) > 12 else periodos)

if "mes" in df.columns:
    filtered = df[df["mes"] == selected_period].copy()
else:
    filtered = df.copy()

if filtered.empty:
    st.warning("Sem dados para o período selecionado.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de SKUs", filtered["sku"].nunique())
col2.metric("Risco Alto", int((filtered["nivel_risco"] == "ALTO").sum()))
col3.metric("Risco Médio", int((filtered["nivel_risco"] == "MEDIO").sum()))
col4.metric("Score médio", round(filtered["score_risco_final"].mean(), 3) if "score_risco_final" in filtered.columns else 0.0)

st.subheader("Ranking de prioridade")
show_columns = [
    "sku",
    "familia",
    "mes",
    "score_risco_final",
    "nivel_risco",
    "baseline_score",
    "demanda_media_6m",
    "estoque_projetado",
    "recomendacao",
]
show_columns = [c for c in show_columns if c in filtered.columns]

st.dataframe(filtered[show_columns].sort_values("score_risco_final", ascending=False), use_container_width=True)

st.subheader("Distribuição por nível de risco")
if "nivel_risco" in filtered.columns:
    st.bar_chart(filtered["nivel_risco"].value_counts())

st.subheader("Top 10 SKUs com maior risco")
if "score_risco_final" in filtered.columns:
    top = filtered.sort_values("score_risco_final", ascending=False).head(10)
    st.dataframe(top[show_columns], use_container_width=True)

st.caption("Painel focado em risco operacional, demanda, estoque e priorização por SKU.")
