import pandas as pd
import streamlit as st

from estado import base, clube_dados, decisoes_df, jornada_df, momento, rodape
from src.cockpit import clube, clube_sim, diagnostico
from src.cockpit.dados import fmt_brl, fmt_int
from src.cockpit.decisoes import carregar_log, resumo_retroalimentacao

momento(5, "Resultados e retroalimentação", "Quanto deixamos de gastar, quanto o Clube traz e o que volta para a IA?")

b = base()
dec = decisoes_df()
eco = diagnostico.economia_operacional(dec, b)
cd = clube_dados()
m = cd["meses"]

st.subheader("Economia operacional: o que o plano deixa de gastar ou de expor", divider="violet")
with st.container(horizontal=True):
    st.metric("Produção sem demanda evitada", fmt_brl(eco["producao_evitada_valor"]), f"{eco['ops_revisadas']} OPs reduzidas ou adiadas", delta_color="off", delta_arrow="off", border=True,
              help="Diferença entre a OP aberta e até 3 meses de demanda recente, a preço de tabela.")
    st.metric("Receita em risco coberta pelo plano", fmt_brl(eco["receita_coberta"]), "pedidos priorizados na fila", delta_color="off", delta_arrow="off", border=True,
              help="Valor dos pedidos em risco cujos SKUs entraram em 'Priorizar produção'. Meta conservadora no piloto: preservar 10%.")
    st.metric("Capital de estoque a liberar", fmt_brl(eco["estoque_meta"]), "meta: −10% do estoque médio", delta_color="off", delta_arrow="off", border=True)
    st.metric("Horas do PCP devolvidas", f"{eco['horas_pcp_ano']} h/ano", f"{fmt_brl(eco['valor_horas_ano'])}/ano (22 → 8 h/semana)", delta_color="off", delta_arrow="off", border=True)

st.subheader("Clube CI: receita e engajamento (simulação do piloto, 6 meses)", divider="violet")
ult = m.iloc[-1]
with st.container(horizontal=True):
    st.metric("Membros ativos", fmt_int(ult["membros_ativos"]), f"+{fmt_int(ult['novos_membros'])} no mês", border=True)
    st.metric("Assinantes Premium", fmt_int(ult["assinantes_premium"]), "R$ 14,90/mês", delta_color="off", delta_arrow="off", border=True)
    st.metric("Compras verificadas (dados novos)", fmt_int(m["nf_verificadas"].sum()), f"{fmt_int(ult['nf_verificadas'])} no mês 6", border=True)
    st.metric("Créditos resgatados", fmt_brl(m["creditos_resgatados"].sum()), f"de {fmt_brl(m['creditos_emitidos'].sum())} emitidos", delta_color="off", delta_arrow="off", border=True)
    st.metric("Receita do Clube no mês 6", fmt_brl(ult["receita_clube"]), f"custo {fmt_brl(ult['custos_clube'])}", delta_color="off", delta_arrow="off", border=True)
c1, c2 = st.columns(2)
c1.markdown("**Membros e assinantes por mês**")
c1.line_chart(m.set_index("mes")[["membros_ativos", "assinantes_premium"]].rename(columns={"membros_ativos": "Membros ativos", "assinantes_premium": "Assinantes Premium"}),
              color=["#74008D", "#F4A6CB"], x_label="Mês do piloto")
c2.markdown("**Receita × custo do Clube por mês**")
c2.bar_chart(m.set_index("mes")[["receita_clube", "custos_clube"]].rename(columns={"receita_clube": "Receita", "custos_clube": "Custo"}),
             stack=False, color=["#74008D", "#DDCFE4"], x_label="Mês do piloto", y_label="R$")

st.subheader("Retroalimentação: o que volta para a IA", divider="violet")
feed = clube_sim.feed_modelo(cd["compras"])
jp = jornada_df()
pares_cegos = int((~jp["tem_sell_out"]).sum())
pares_com_sinal = int(feed["ponto_cego"].sum())
log = carregar_log()
r = resumo_retroalimentacao(log)
with st.container(horizontal=True):
    st.metric("Pares parceiro × SKU no ponto cego", fmt_int(pares_cegos), border=True)
    st.metric("…que já têm sinal verificado do consumidor", fmt_int(pares_com_sinal), f"{pares_com_sinal / pares_cegos * 100:.0f}% do ponto cego em 6 meses", delta_color="off", delta_arrow="off", border=True)
    st.metric("Decisões humanas registradas", r["decisoes"], f"{r['ajustes']} ajustes (FVA)", delta_color="off", delta_arrow="off", border=True)
    st.metric("Ciclo de recalibração", "mensal", "realizado × previsto × aprovado", delta_color="off", delta_arrow="off", border=True)
c1, c2 = st.columns([3, 2])
c1.markdown("**Sell-out verificado enviado à camada 2 (maiores volumes)**")
c1.dataframe(feed.head(12), hide_index=True, width="stretch", column_config={
    "parceiro": "Parceiro", "sku": "SKU", "compras_verificadas": "Compras verificadas",
    "preco_medio": st.column_config.NumberColumn("Preço médio pago", format="R$ %.2f"), "ponto_cego": st.column_config.CheckboxColumn("Ponto cego")})
with c2.container(border=True):
    st.markdown("**Como o ciclo fecha**")
    st.markdown("1. O realizado do mês entra e o erro de cada SKU é recalculado.\n"
                "2. Ajustes humanos são comparados com a previsão original (FVA).\n"
                "3. Compras verificadas recalibram o giro estimado no ponto cego.\n"
                "4. Um desafiante só vira campeão se errar menos no mesmo corte.\n"
                "5. A economia financia mais rastreabilidade, e o ciclo recomeça.")

st.subheader("Projeção do ecossistema (36 meses)", divider="violet")
nome = st.radio("Cenário", list(clube.CENARIOS), index=1, horizontal=True)
sim = clube.simular(clube.CENARIOS[nome])
pb = clube.payback(sim)
with st.container(horizontal=True):
    st.metric("Payback do ecossistema", f"mês {pb}" if pb else "> 36 meses", border=True)
    st.metric("Resultado acumulado em 36 meses", fmt_brl(sim["acumulado"].iloc[-1]), border=True)
    st.metric("Maior exposição de caixa", fmt_brl(-sim["acumulado"].min()), border=True)
st.line_chart(sim.set_index("mes")[["acumulado"]].rename(columns={"acumulado": "Resultado acumulado (R$)"}), color="#74008D", x_label="Mês")
st.caption("Economia do Cockpit + receita do Clube (Premium, comissões de parceiros, drops, refis via CRM, mídia) − custos. "
           "Gate do mês 3: opt-in ≥ 20%, ≥ 4,5 mil membros, pré-venda Premium ≥ 4%.")
rodape()
