"""Carga em cache e componentes visuais compartilhados pelas páginas."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cockpit import backtest, clube_sim, jornada, motor  # noqa: E402
from src.cockpit.dados import (CALCULADO, DECLARADO, ESTIMADO, INDISPONIVEL, OBSERVADO, PREVISTO,  # noqa: E402
                               VERIFICADO, carregar_base)
from src.models.forecast_demanda import PrevisaoDemanda  # noqa: E402

LOGO = ROOT / "assets" / "logo_caderno_inteligente.png"
ROXO, AUBERGINE, ROSA, LAVANDA = "#74008D", "#31003E", "#F4A6CB", "#DDCFE4"

COR_REC = {
    "Priorizar produção": "red", "Produzir": "violet", "Investigar": "orange", "Reduzir/adiar OP": "blue",
    "Monitorar": "gray", "Sem ação necessária": "green", "Repor": "violet",
}
ICONE_REC = {
    "Priorizar produção": ":material/priority_high:", "Produzir": ":material/factory:", "Investigar": ":material/search:",
    "Reduzir/adiar OP": ":material/schedule:", "Monitorar": ":material/visibility:", "Sem ação necessária": ":material/check_circle:",
    "Repor": ":material/local_shipping:",
}
COR_NATUREZA = {OBSERVADO: "green", VERIFICADO: "green", CALCULADO: "violet", PREVISTO: "blue", ESTIMADO: "orange",
                DECLARADO: "orange", INDISPONIVEL: "red"}


@st.cache_data(show_spinner="Carregando as fontes do desafio…")
def base():
    return carregar_base()


@st.cache_data(show_spinner="Gerando a previsão out–dez/2026…")
def previsao() -> pd.DataFrame:
    path = ROOT / "data" / "processed" / "forecast_demanda.csv"
    if path.exists():
        return pd.read_csv(path, parse_dates=["mes", "data_corte"])
    return PrevisaoDemanda(ROOT).build()


@st.cache_data(show_spinner="Rodando o backtest dos 8 métodos…")
def bt() -> pd.DataFrame:
    b = base()
    return backtest.rodar_backtest(b["Vendas_24m"], b["Produtos"])


@st.cache_data
def jornada_df() -> pd.DataFrame:
    return jornada.jornada_parceiros(base())


@st.cache_data(show_spinner="Calculando as decisões da semana…")
def decisoes_df() -> pd.DataFrame:
    return motor.calcular_decisoes(base(), previsao(), jornada_df())


@st.cache_data
def risco_df() -> pd.DataFrame:
    return motor.pedidos_em_risco(base())


@st.cache_data(show_spinner="Carregando a simulação do piloto do Clube…")
def clube_dados() -> dict:
    return clube_sim.gerar(base())


def momento(numero: int, titulo: str, pergunta: str) -> None:
    """Cabeçalho padrão de cada momento da jornada."""
    st.caption(f"MOMENTO {numero} DE 5")
    st.title(titulo)
    st.markdown(f":violet[**{pergunta}**]")


def proximo(pagina: str, rotulo: str) -> None:
    st.divider()
    st.page_link(pagina, label=rotulo, icon=":material/arrow_forward:")


def badge_rec(rec: str) -> None:
    st.badge(rec, color=COR_REC.get(rec, "gray"), icon=ICONE_REC.get(rec))


def badge_natureza(nat: str) -> None:
    st.badge(nat, color=COR_NATUREZA.get(nat, "gray"))


def cabecalho(titulo: str, subtitulo: str) -> None:
    st.title(titulo)
    st.caption(subtitulo)


def rodape() -> None:
    st.divider()
    st.caption("Protótipo do Golden Squad (G09) · ITA Challenge Sprint · Base fictícia do desafio Caderno Inteligente. "
               "Toda recomendação aguarda aprovação humana; nenhuma OP é liberada automaticamente.")


def selecionar_sku(sku: str) -> None:
    st.session_state["sku_detalhe"] = sku
    st.switch_page("paginas/detalhe_sku.py")
