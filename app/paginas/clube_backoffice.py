import pandas as pd
import streamlit as st

from estado import clube_dados, rodape
from src.cockpit import clube_sim
from src.cockpit.dados import fmt_brl, fmt_int

st.caption("CLUBE CI · BACKOFFICE")
st.title("Backoffice do Clube")
st.markdown("Onde a CI controla membros, planos, campanhas, benefícios e resgates, e de onde sai o sell-out verificado que alimenta a IA.")
st.caption("Dados simulados do piloto (cenário-base, meses 1 a 6), gerados com o mix real de SKUs e parceiros da base do desafio.")

cd = clube_dados()
m, mem, comp = cd["meses"], cd["membros"], cd["compras"]
mes = st.select_slider("Mês do piloto", options=list(m["mes"]), value=int(m["mes"].max()))
r = m[m["mes"] == mes].iloc[0]
ant = m[m["mes"] == mes - 1].iloc[0] if mes > 1 else None

with st.container(horizontal=True):
    st.metric("Membros ativos", fmt_int(r["membros_ativos"]), f"+{fmt_int(r['novos_membros'])} novos", border=True)
    st.metric("Assinantes Premium", fmt_int(r["assinantes_premium"]),
              f"+{fmt_int(r['assinantes_premium'] - (ant['assinantes_premium'] if ant is not None else 0))}", border=True)
    st.metric("NFs verificadas no mês", fmt_int(r["nf_verificadas"]), border=True)
    st.metric("Créditos emitidos", fmt_brl(r["creditos_emitidos"]), border=True)
    st.metric("Créditos resgatados", fmt_brl(r["creditos_resgatados"]), f"{r['creditos_resgatados'] / r['creditos_emitidos'] * 100:.0f}% de resgate",
              delta_color="off", delta_arrow="off", border=True)
    st.metric("Receita do Clube no mês", fmt_brl(r["receita_clube"]), f"custo {fmt_brl(r['custos_clube'])}", delta_color="off", delta_arrow="off", border=True)

aba1, aba2, aba3, aba4 = st.tabs([":material/group: Membros e conversões", ":material/campaign: Campanhas e benefícios",
                                  ":material/sync_alt: Envio para a IA", ":material/tune: Regras do programa"])
with aba1:
    c1, c2 = st.columns(2)
    origem = mem[mem["mes_cadastro"] <= mes]["origem"].value_counts().rename_axis("Origem do cadastro").to_frame("membros")
    c1.markdown("**Como os membros chegaram**")
    c1.bar_chart(origem, horizontal=True, color="#74008D", y_label="")
    cs = comp[comp["mes"] <= mes]
    porp = cs.groupby(["parceiro", "natureza"]).size().unstack(fill_value=0)
    c2.markdown("**Compras registradas por parceiro**")
    c2.bar_chart(porp, stack=True, color=["#F4A6CB", "#74008D"], y_label="Compras")
    st.markdown("**Membros por cidade**")
    st.dataframe(mem[mem["mes_cadastro"] <= mes].groupby(["cidade", "uf"]).size().sort_values(ascending=False).rename("membros").reset_index(),
                 hide_index=True, width="stretch", height=240)
with aba2:
    st.markdown("**Campanhas disparadas pelo CRM do Clube**")
    st.dataframe(cd["campanhas"], hide_index=True, width="stretch", column_config={
        "campanha": "Campanha", "canal": "Canal", "enviados": st.column_config.NumberColumn("Enviados", format="localized"),
        "conversoes": st.column_config.NumberColumn("Conversões", format="localized"), "oferta": "Oferta",
        "taxa_conversao": st.column_config.ProgressColumn("Conversão", min_value=0, max_value=20, format="%.1f%%")})
    st.markdown("**Benefícios mais resgatados (rede de parceiros)**")
    st.bar_chart(cd["beneficios"].set_index("categoria")["resgates"], horizontal=True, color="#74008D", y_label="")
with aba3:
    feed = clube_sim.feed_modelo(comp[comp["mes"] <= mes])
    a, b = st.columns([1, 2])
    a.metric("Pares parceiro × SKU com sinal novo", fmt_int(len(feed)))
    a.metric("…no ponto cego do sell-out", fmt_int(int(feed["ponto_cego"].sum())))
    a.caption("Enviado à camada 2 do Cockpit como 'Verificado pelo consumidor': agregado por loja, SKU e mês, sem dado pessoal.")
    b.dataframe(feed, hide_index=True, width="stretch", height=320, column_config={
        "parceiro": "Parceiro", "sku": "SKU", "compras_verificadas": "Compras verificadas",
        "preco_medio": st.column_config.NumberColumn("Preço médio pago", format="R$ %.2f"), "ponto_cego": st.column_config.CheckboxColumn("Ponto cego")})
with aba4:
    st.dataframe(pd.DataFrame([
        ("Crédito de boas-vindas", "R$ 5,00, só com nota fiscal validada (chave de 44 dígitos única)"),
        ("Crédito por compra", "5% do valor, resgate de até 20% por pedido, sem saque"),
        ("Premium", "R$ 14,90/mês: refil com desconto/frete, collabs antecipadas, rede de parceiros, até 3 dependentes"),
        ("Indicação", "Crédito para quem indica e para quem compra, após a primeira compra confirmada; autoindicação bloqueada"),
        ("Antifraude", "NF reutilizada é recusada; teto de créditos por CPF; nenhum crédito por simples leitura do QR"),
        ("Privacidade (LGPD)", "Consentimento explícito; dado pessoal fica no Clube; o Cockpit recebe só agregados"),
        ("Plataforma", "Cobrança por vida ativa (R$ 0,20/mês, piso R$ 2 mil); parceiros remuneram o Clube pela conversão"),
    ], columns=["Regra", "Configuração no piloto"]), hide_index=True, width="stretch")
st.page_link("paginas/m5_resultados.py", label="Ver o efeito no resultado do ecossistema", icon=":material/arrow_forward:")
rodape()
