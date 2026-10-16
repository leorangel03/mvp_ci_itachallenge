import time

import pandas as pd
import streamlit as st

from estado import ROOT, base, momento, previsao, proximo, rodape
from src.cockpit import diagnostico
from src.cockpit.dados import fmt_int
from src.models.forecast_demanda import PrevisaoDemanda

momento(2, "Previsão otimizada", "Como o algoritmo transforma a temperatura e a pressão da base histórica em demanda por SKU, canal e mês?")

st.subheader("Sinais que o algoritmo considera", divider="violet")
st.dataframe(pd.DataFrame([
    ("Sazonalidade da família", "Índice dos últimos 12 meses por família e mês do ano", "Ajusta o volume de cada mês (volta às aulas, Black Friday, Natal)"),
    ("Nível recente do SKU", "Média dos 3 últimos meses, sem o efeito sazonal", "Corrige o cadastro defasado (CI-0031, CI-0004)"),
    ("Mix por canal", "Participação de cada canal nos 3 últimos meses", "Explode a previsão do SKU em 8 canais, somando 100%"),
    ("Carteira firme", "Pedidos confirmados com data prometida", "Piso da demanda no horizonte de decisão (motor, momento 3)"),
    ("Eventos do calendário", "Recorrentes já estão no índice; lançamentos sem histórico", "SKU novo vira 'Investigar'; ajuste comercial fica registrado (FVA)"),
    ("Jornada B2B2C e Clube", "Sell-out do parceiro e compras verificadas por NF", "Calibra o giro no ponto cego e a confiança da recomendação"),
    ("Capacidade e lote", "Capacidade semanal por família e lote mínimo", "Não altera a previsão: limita o plano no momento 3"),
], columns=["Sinal", "De onde vem", "Como entra"]), hide_index=True, width="stretch")

st.subheader("Rodar o algoritmo", divider="violet")
c1, c2 = st.columns([1, 3])
rodar = c1.button("Rodar a previsão out–dez/2026", type="primary", icon=":material/play_arrow:")
c2.caption("Modelo escolhido entre 8 métodos: índice sazonal da família × nível local do SKU, distribuído por canal. "
           "Erro no teste histórico: 9,18% (alternativa simples: 11,33%).")
if rodar:
    with st.status("Processando 24 meses de histórico…", expanded=True) as status:
        t0 = time.time()
        modelo = PrevisaoDemanda(ROOT)
        vendas, produtos = modelo.load_sources()
        st.write(f":material/check: {fmt_int(len(vendas))} registros de vendas validados · {produtos['sku'].nunique()} SKUs · 8 canais")
        st.write(":material/check: Índices sazonais calculados para 6 famílias (12 meses até ago/2026)")
        st.write(":material/check: Nível recente de cada SKU calculado sem o efeito sazonal (jun–ago/2026)")
        periodos = pd.date_range("2026-10-01", periods=3, freq="MS")
        resultado = modelo.predict(vendas, produtos, periodos)
        ok = resultado[resultado["status_previsao"] == "OK"]
        st.write(f":material/check: Explosão em {fmt_int(len(ok))} combinações SKU × canal × mês, reconciliadas em 100% por SKU")
        st.write(":material/check: Lançamentos sem histórico separados para investigação (sem previsão inventada)")
        status.update(label=f"Previsão concluída em {time.time() - t0:.1f} s · {fmt_int(ok['previsao_unidades'].sum())} un. no trimestre",
                      state="complete", expanded=False)
    st.session_state["previsao_rodada"] = True

p = previsao()
ok = p[p["status_previsao"] == "OK"].copy()
mvc = diagnostico.modelo_vs_comercial(base(), p)

with st.container(horizontal=True):
    st.metric("Demanda prevista out–dez", f"{fmt_int(ok['previsao_unidades'].sum())} un.", border=True)
    st.metric("Forecast comercial (fator único)", f"{fmt_int(mvc['comercial'].sum())} un.", border=True)
    st.metric("Executivo vs comercial", f"{mvc.loc['Executivo', 'diferenca_pct']:+.1f}%".replace(".", ","), "evita excesso", delta_color="off", delta_arrow="off", border=True)
    st.metric("Escolar vs comercial", f"{mvc.loc['Escolar', 'diferenca_pct']:+.1f}%".replace(".", ","), "evita ruptura", delta_color="off", delta_arrow="off", border=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Modelo × comercial por família (trimestre)**")
    st.bar_chart(mvc[["modelo", "comercial"]], stack=False, color=["#74008D", "#DDCFE4"], y_label="Unidades")
with c2:
    st.markdown("**Por que o modelo diverge do comercial**")
    sz = diagnostico.sazonalidade(base())
    expl = mvc.copy()
    expl["leitura"] = [
        "Nível recente abaixo do cadastro; família com superprevisão histórica" if f == "Executivo" else
        f"Pico de novembro ({sz.loc[f, 'nov']:.2f}) e nível recente acima do cadastro".replace(".", ",") if f in ("Escolar", "Clássico") else
        f"Dezembro forte ({sz.loc[f, 'dez']:.2f}) já no índice da família".replace(".", ",") if f == "Planner" else
        "Comportamento próximo do cadastro" for f in expl.index]
    st.dataframe(expl[["diferenca_pct", "leitura"]], width="stretch", column_config={
        "diferenca_pct": st.column_config.NumberColumn("Modelo vs comercial", format="%+.1f%%"), "leitura": "Leitura"})

st.subheader("Explosão da previsão: SKU × canal × mês", divider="violet")
a, b2 = st.columns([1, 3])
fam = a.selectbox("Família", sorted(ok["familia"].unique()), index=2)
ok["mes_txt"] = pd.to_datetime(ok["mes"]).dt.strftime("%m/%Y")
pv = ok[ok["familia"] == fam].pivot_table(index=["sku", "canal"], columns="mes_txt", values="previsao_unidades", aggfunc="sum").round(0)
b2.dataframe(pv, width="stretch", height=320)
st.caption("Cada linha soma ao total previsto do SKU; os canais KA ainda passam pela leitura de sell-out no momento 4.")

proximo("paginas/m3_plano.py", "Momento 3: converter a previsão em plano de produção e distribuição do mix")
rodape()
