import pandas as pd
import streamlit as st

from estado import base, bt, cabecalho, previsao, rodape
from src.cockpit import backtest
from src.cockpit.dados import fmt_int


def pc(v: float, casas: int = 2, sinal: bool = False) -> str:
    return (f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}").replace(".", ",")


cabecalho("Validação do modelo", "Champion-challenger com 8 métodos no mesmo corte temporal · só dados anteriores a cada previsão")

b = bt()
res = backtest.resumo(b)
camp, simples = res.loc["sazonal_familia_nivel_sku"], res.loc["sazonal_ingenuo"]
with st.container(horizontal=True):
    st.metric("Erro do modelo escolhido (WAPE)", f"{pc(camp['wape'])}%", border=True)
    st.metric("Alternativa simples (sazonal ingênuo)", f"{pc(simples['wape'])}%", border=True)
    st.metric("Redução relativa do erro", f"{(1 - camp['wape'] / simples['wape']) * 100:.0f}%", border=True)
    st.metric("Previsões por método", fmt_int(camp["n_previsoes"]), help="50 SKUs × 33 blocos (origem × horizonte)", border=True)

c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("8 métodos, mesmas condições", divider="violet")
    st.dataframe(res[["metodo_nome", "wape", "vies", "n_previsoes"]], hide_index=True, width="stretch", column_config={
        "metodo_nome": "Método", "wape": st.column_config.NumberColumn("WAPE %", format="%.2f"),
        "vies": st.column_config.NumberColumn("Viés %", format="%.2f", help="Negativo = subprevisão"), "n_previsoes": "Previsões"})
with c2:
    st.subheader("Erro por método", divider="violet")
    graf = res.reset_index(drop=True)
    graf["metodo_nome"] = [f"{i + 1}. {n}" for i, n in enumerate(graf["metodo_nome"])]
    st.bar_chart(graf.set_index("metodo_nome")["wape"], horizontal=True, color="#74008D", x_label="WAPE %", y_label="")

st.subheader("Casos não usados no ajuste: holdout temporal", divider="violet")
h = backtest.holdout(b)
st.markdown("O método é **escolhido** nas origens de ago/2025 a jan/2026 e **testado** nas origens de fev a jul/2026, que não participaram da escolha.")
st.dataframe(h[["metodo_nome", "wape_selecao", "wape_teste", "vies_teste"]], hide_index=True, width="stretch", column_config={
    "metodo_nome": "Método", "wape_selecao": st.column_config.NumberColumn("WAPE na seleção %", format="%.2f"),
    "wape_teste": st.column_config.NumberColumn("WAPE no teste %", format="%.2f"),
    "vies_teste": st.column_config.NumberColumn("Viés no teste %", format="%.2f")})
hc, hs = h.loc["sazonal_familia_nivel_sku"], h.loc["sazonal_ingenuo"]
he = h.loc["ensemble_top3"]
a, bcol = st.columns(2)
a.success(f"**Acerto:** escolhido na seleção, o modelo mantém o ganho no período reservado: "
          f"{pc(hc['wape_teste'])}% contra {pc(hs['wape_teste'])}% da alternativa simples.", icon=":material/check_circle:")
bcol.warning(f"**Desafiante a monitorar:** no período reservado, o ensemble errou {pc(he['wape_teste'])}% "
             f"({pc(hc['wape_teste'] - he['wape_teste'])} p.p. melhor). Pela regra champion-challenger, ele só é promovido se repetir no próximo ciclo.",
             icon=":material/compare_arrows:")

st.subheader("Acertos e falhas por família", divider="violet")
fam = backtest.por_familia(b)
st.dataframe(fam, width="stretch", column_config={
    "wape_ia": st.column_config.NumberColumn("WAPE modelo %", format="%.1f"),
    "wape_simples": st.column_config.NumberColumn("WAPE simples %", format="%.1f"),
    "vies_ia": st.column_config.NumberColumn("Viés modelo %", format="%+.1f")})
cap = base()["Capacidade_Semanal"]
ocup = cap.groupby("Família")["Ocupação"].mean().sort_values(ascending=False)
x, y = st.columns(2)
x.error(f"**Executivo:** erro de {pc(fam.loc['Executivo', 'wape_ia'], 1)}% e superprevisão de {pc(fam.loc['Executivo', 'vies_ia'], 1, True)}% "
        "→ risco de excesso. A família recebe confiança 'Média' e revisão humana obrigatória.", icon=":material/error:")
y.error(f"**Escolar:** subprevisão de {pc(fam.loc['Escolar', 'vies_ia'], 1)}% na linha mais ocupada da fábrica "
        f"({ocup.iloc[0] * 100:.0f}% de ocupação média) → reforçar a segurança e reservar capacidade para a volta às aulas.",
        icon=":material/error:")

st.subheader("Previsão out–dez/2026 × forecast comercial", divider="violet")
p = previsao()
modelo = p[p["status_previsao"] == "OK"].groupby("mes")["previsao_unidades"].sum().rename("Modelo")
fc = base()["Forecast_Comercial"]
mapa = {"Out/26": "2026-10-01", "Nov/26": "2026-11-01", "Dez/26": "2026-12-01"}
fc = fc.assign(mes=pd.to_datetime(fc["Mês"].map(mapa)), u=pd.to_numeric(fc["Previsão unidades"], errors="coerce"))
comercial = fc.groupby("mes")["u"].sum().rename("Comercial")
comp = pd.concat([modelo, comercial], axis=1)
comp.index = ["1. Out/26", "2. Nov/26", "3. Dez/26"]
st.bar_chart(comp, stack=False, color=["#74008D", "#DDCFE4"], y_label="Unidades")
st.caption(f"Modelo: {fmt_int(modelo.sum())} un. no trimestre · Comercial: {fmt_int(comercial.sum())} un. "
           "Previsão contra previsão: o realizado de out–dez ainda não existe. Teste retrospectivo em base fictícia; o ganho operacional é medido no piloto.")
rodape()
