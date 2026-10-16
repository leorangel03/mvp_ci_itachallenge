import pandas as pd
import streamlit as st

from estado import base, decisoes_df, jornada_df, momento, previsao, proximo, risco_df, rodape, selecionar_sku
from src.cockpit import diagnostico, motor
from src.cockpit.dados import fmt_brl, fmt_int
from src.cockpit.decisoes import carregar_log

momento(3, "Plano de produção e distribuição do mix", "O que produzir, o que adiar e para quem enviar nas próximas semanas?")
st.caption("Posição de 14/09/2026 · horizonte até 31/10/2026 · toda recomendação aguarda aprovação humana")

b = base()
dec = decisoes_df()
risco = risco_df()
em_risco = risco[risco["em_risco"]]
eco = diagnostico.economia_operacional(dec, b)
ex = motor.excesso_resumo(b)

with st.container(horizontal=True):
    st.metric("Pedidos em risco de atraso", f"{len(em_risco)} de {len(risco)}", border=True)
    st.metric("Receita exposta (preço de tabela)", fmt_brl(em_risco["valor"].sum()), border=True)
    st.metric("Produção sugerida", f"{fmt_int(dec['producao_sugerida'].sum())} un.", border=True)
    st.metric("OPs a reduzir ou adiar", eco["ops_revisadas"], f"{fmt_brl(eco['producao_evitada_valor'])} sem demanda", delta_color="off", delta_arrow="off", border=True)
    st.metric("Excesso acima de 90 dias", fmt_brl(ex["atual"]), f"{fmt_brl(ex['com_ops'])} se as OPs forem executadas", delta_color="inverse", border=True)
    st.metric("Decisões registradas", fmt_int(len(carregar_log())), border=True)

aba1, aba2, aba3 = st.tabs([":material/checklist: Fila de decisões", ":material/factory: Carga × capacidade", ":material/hub: Distribuição do mix"])

with aba1:
    c1, c2, c3 = st.columns([2, 2, 1])
    recs = c1.multiselect("Recomendação", sorted(dec["recomendacao"].unique()), placeholder="Todas")
    fams = c2.multiselect("Família", sorted(dec["familia"].unique()), placeholder="Todas")
    busca = c3.text_input("Buscar SKU ou produto", placeholder="CI-0004")
    f = dec.copy()
    if recs:
        f = f[f["recomendacao"].isin(recs)]
    if fams:
        f = f[f["familia"].isin(fams)]
    if busca:
        f = f[f["sku"].str.contains(busca, case=False) | f["produto"].str.contains(busca, case=False)]
    tabela = f[["sku", "produto", "familia", "recomendacao", "acao", "producao_sugerida", "producao_executavel",
                "valor_risco", "confianca", "recomendacao_comercial", "status_decisao"]].reset_index(drop=True)
    tabela.insert(0, "prioridade", range(1, len(tabela) + 1))
    sel = st.dataframe(tabela, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row", height=420,
                       column_config={
                           "prioridade": st.column_config.NumberColumn("#", width="small"), "sku": "SKU", "produto": "Produto",
                           "familia": "Família", "recomendacao": "Recomendação",
                           "acao": st.column_config.TextColumn("Ação operacional", width="large"),
                           "producao_sugerida": st.column_config.NumberColumn("Produzir (un.)", format="localized"),
                           "producao_executavel": st.column_config.NumberColumn("Cabe na capacidade", format="localized"),
                           "valor_risco": st.column_config.NumberColumn("Receita em risco", format="R$ %.0f"),
                           "confianca": "Confiança", "recomendacao_comercial": st.column_config.TextColumn("Recomendação comercial", width="large"),
                           "status_decisao": "Status"})
    linhas = sel.selection.rows if sel and sel.selection else []
    if linhas:
        sku = tabela.iloc[linhas[0]]["sku"]
        if st.button(f"Abrir {sku}: evidências, cálculo e aprovação", type="primary", icon=":material/arrow_forward:"):
            selecionar_sku(sku)
    else:
        st.caption("Selecione uma linha para abrir o detalhe com evidências, cálculo e aprovação.")

with aba2:
    cap = motor.capacidade_horizonte(b)
    carga = dec.groupby("familia")["producao_sugerida"].sum()
    oc = diagnostico.ocupacao(b)
    df = pd.DataFrame({"Produção sugerida": carga, "Capacidade livre até 31/10": cap}).fillna(0)
    st.bar_chart(df, stack=False, color=["#74008D", "#DDCFE4"], y_label="Unidades", x_label="Família")
    df["Uso da capacidade livre"] = (df["Produção sugerida"] / df["Capacidade livre até 31/10"] * 100).round(1)
    df["Ocupação média da linha"] = (oc * 100).round(0)
    st.dataframe(df, width="stretch", column_config={
        "Uso da capacidade livre": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%"),
        "Ocupação média da linha": st.column_config.NumberColumn(format="%.0f%%")})
    semanal = b["Capacidade_Semanal"]
    semanal = semanal[semanal["Família"] == "Escolar"].set_index("Semana inicial")[["Capacidade máxima", "Capacidade comprometida"]]
    st.markdown("**Linha Escolar, semana a semana (a mais ocupada da fábrica)**")
    st.line_chart(semanal, color=["#DDCFE4", "#74008D"], y_label="Unidades")
    st.caption("O plano nunca passa da capacidade livre: o excedente aparece como déficit no detalhe do SKU (verificação 5).")

with aba3:
    p = previsao()
    out = p[(p["status_previsao"] == "OK") & (pd.to_datetime(p["mes"]).dt.month == 10)]
    mix = out.pivot_table(index="familia", columns="canal", values="previsao_unidades", aggfunc="sum").round(0)
    st.markdown("**Para onde vai a demanda de outubro, por família e canal**")
    st.bar_chart(mix, stack=True, y_label="Unidades", x_label="Família")
    st.markdown("**Prioridade de distribuição quando o produto é escasso**")
    jp = jornada_df()
    pri = dec[dec["recomendacao"] == "Priorizar produção"][["sku", "produto", "recomendacao_comercial"]]
    st.dataframe(pri, hide_index=True, width="stretch", column_config={"recomendacao_comercial": st.column_config.TextColumn("Para quem priorizar", width="large")})
    st.caption("Regra: produto escasso vai primeiro ao parceiro com maior giro observado no sell-out; parceiro com acúmulo segura a reposição.")

proximo("paginas/m4_rastreabilidade.py", "Momento 4: acompanhar a conversão no parceiro e no consumidor")
rodape()
