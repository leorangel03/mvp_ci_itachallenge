import pandas as pd
import streamlit as st

from estado import (badge_natureza, badge_rec, base, cabecalho, decisoes_df, jornada_df, previsao, risco_df, rodape)
from src.cockpit.dados import fmt_brl, fmt_int
from src.cockpit.decisoes import DECISOES, carregar_log, registrar_decisao

dec = decisoes_df()
skus = dec["sku"].tolist()
padrao = st.session_state.get("sku_detalhe", "CI-0004")
cabecalho("Detalhe do SKU", "Evidência, cálculo passo a passo, parceiros e decisão humana registrada")
sku = st.selectbox("SKU", skus, index=skus.index(padrao) if padrao in skus else 0,
                   format_func=lambda s: f"{s} · {dec.set_index('sku').loc[s, 'produto']}")
st.session_state["sku_detalhe"] = sku
r = dec.set_index("sku").loc[sku]

with st.container(border=True):
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(f"### {sku} · {r['descricao']}")
        st.caption(f"Família {r['familia']} · Curva {r['curva_abc']} · {r['status_sku']}")
        badge_rec(r["recomendacao"])
        st.markdown(f"**Por quê:** {r['motivo']}")
        st.markdown(f"**Ação operacional:** {r['acao']}")
        if r["recomendacao_comercial"] != "—":
            st.markdown(f"**Ação comercial:** {r['recomendacao_comercial']}")
    with c2:
        st.metric("Produção sugerida", f"{fmt_int(r['producao_sugerida'])} un.")
        st.metric("Cabe na capacidade da semana", f"{fmt_int(r['producao_executavel'])} un.",
                  delta=f"-{fmt_int(r['deficit_capacidade'])} un. sem capacidade" if r["deficit_capacidade"] else None,
                  delta_color="inverse")
        st.markdown(f"**Confiança:** {r['confianca']} · **Status:** {r['status_decisao']}")

c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("Como o número foi calculado", divider="violet")
    if pd.isna(r["necessidade_liquida"]):
        st.info("Sem histórico suficiente: o motor não calcula necessidade e recomenda investigar.", icon=":material/search:")
    else:
        passos = pd.DataFrame([
            ("Demanda considerada no horizonte", r["demanda_horizonte"], "máx(previsão out + ½ set, carteira firme)"),
            ("+ Estoque de segurança", r["seguranca"], "dias de segurança × demanda recente"),
            ("− Estoque atual", -r["estoque"], "Estoque_Atual"),
            ("− OPs que chegam até 31/10", -r["ops_no_prazo"], "OPs tardias não contam"),
            ("= Necessidade líquida", r["necessidade_liquida"], "Se positiva, arredonda ao lote"),
            ("Lote mínimo", r["lote_minimo"], "Lead_Times"),
            ("Produção sugerida", r["producao_sugerida"], "Após o lote e a regra de recomendação"),
            ("Capacidade livre da família no horizonte", r["capacidade_familia"], "Capacidade_Semanal"),
        ], columns=["Passo", "Unidades", "Regra"])
        st.dataframe(passos, hide_index=True, width="stretch",
                     column_config={"Unidades": st.column_config.NumberColumn(format="localized")})
with c2:
    st.subheader("Evidências e natureza do dado", divider="violet")
    for sinal, valor, nat, fonte in r["evidencias"]:
        a, b, c = st.columns([3, 2, 2])
        a.markdown(f"**{sinal}**  \n:gray[{fonte}]")
        b.markdown(valor)
        with c:
            badge_natureza(nat)

st.subheader("Histórico e previsão", divider="violet")
v = base()["Vendas_24m"]
hist = v[v["SKU"] == sku].groupby("Mês")["Quantidade faturada"].sum().rename("Realizado")
hist.index = pd.to_datetime(hist.index)
prev = previsao()
p = prev[(prev["sku"] == sku) & (prev["status_previsao"] == "OK")].groupby("mes")["previsao_unidades"].sum().rename("Previsto")
serie = pd.concat([hist, p], axis=1)
if serie.empty:
    st.info("SKU sem histórico de vendas.")
else:
    st.line_chart(serie, color=["#74008D", "#F4A6CB"], x_label="Mês", y_label="Unidades")

c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("Carteira do SKU", divider="violet")
    rk = risco_df()
    rk = rk[rk["sku"] == sku]
    if rk.empty:
        st.caption("Sem pedidos em carteira.")
    else:
        st.dataframe(rk[["pedido", "cliente", "quantidade", "data_prometida", "disponivel_na_data", "em_risco", "valor"]],
                     hide_index=True, width="stretch",
                     column_config={"data_prometida": st.column_config.DateColumn("Data prometida", format="DD/MM/YYYY"),
                                    "em_risco": st.column_config.CheckboxColumn("Em risco"),
                                    "valor": st.column_config.NumberColumn("Valor", format="R$ %.0f"),
                                    "disponivel_na_data": st.column_config.NumberColumn("Disponível na data")})
with c2:
    st.subheader("Parceiros (jornada B2B2C)", divider="violet")
    jp = jornada_df()
    jp = jp[jp["sku"] == sku]
    if jp.empty:
        st.caption("Sem vendas a parceiros nos últimos 12 meses.")
    else:
        st.dataframe(jp[["parceiro", "faturado_12m", "sell_in_12m", "sell_out_12m", "cobertura_parceiro_meses", "sinal", "recomendacao"]],
                     hide_index=True, width="stretch",
                     column_config={"sell_out_12m": st.column_config.NumberColumn("Sell-out 12m", help="Vazio = indisponível, nunca zero"),
                                    "cobertura_parceiro_meses": st.column_config.NumberColumn("Cobertura na loja (meses)")})

st.subheader("Decisão humana", divider="violet")
with st.form("decisao", border=True):
    a, b, c = st.columns([1, 1, 2])
    decisao = a.radio("Decisão", DECISOES, horizontal=False)
    qtd = b.number_input("Quantidade aprovada (un.)", min_value=0, value=int(r["producao_sugerida"]), step=int(r["lote_minimo"] or 1))
    responsavel = c.text_input("Responsável", value=st.session_state.get("responsavel", ""), placeholder="Ex.: PCP · Ana")
    motivo = st.text_area("Motivo (obrigatório para ajustar ou rejeitar)", placeholder="Ex.: antecipar 600 un. na linha Planner na sexta")
    if st.form_submit_button("Registrar decisão", type="primary", icon=":material/how_to_reg:"):
        try:
            registrar_decisao(sku, r["recomendacao"], int(r["producao_sugerida"]), decisao, int(qtd), responsavel, motivo)
            st.session_state["responsavel"] = responsavel
            st.success(f"Decisão '{decisao}' registrada para {sku}. Ela entra no log e alimenta a medição de erro e FVA.",
                       icon=":material/task_alt:")
        except ValueError as e:
            st.error(str(e), icon=":material/block:")

hist_log = carregar_log()
hist_log = hist_log[hist_log["sku"] == sku]
if not hist_log.empty:
    st.dataframe(hist_log, hide_index=True, width="stretch")
st.caption(f"Receita em risco deste SKU: {fmt_brl(r['valor_risco'])} · Excesso acima de 90 dias: {fmt_brl(r['excesso_valor'])}")
rodape()
