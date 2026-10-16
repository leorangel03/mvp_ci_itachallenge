import streamlit as st

from estado import base, clube_dados, decisoes_df, previsao, risco_df, rodape
from src.cockpit import diagnostico, jornada, motor
from src.cockpit.dados import fmt_brl, fmt_int

st.caption("CADERNO INTELIGENTE · PLATAFORMA DE DEMANDA INTEGRADA À FÁBRICA, À DISTRIBUIÇÃO, ÀS VENDAS E AO CLUBE")
st.title("Do histórico à receita: o ciclo que se paga")
st.markdown("A plataforma lê o que aconteceu, prevê o que vai acontecer, decide o que produzir e para onde enviar, "
            "acompanha o produto até o consumidor e devolve tudo para a IA. **Cinco momentos, um ciclo.**")

b = base()
dec = decisoes_df()
risco = risco_df()
cd = clube_dados()
fat = diagnostico.fator_unico(b)
mvc = diagnostico.modelo_vs_comercial(b, previsao())
eco = diagnostico.economia_operacional(dec, b)
cob = jornada.cobertura_consumo(b).set_index("recorte")
ult = cd["meses"].iloc[-1]

etapas = [
    ("1", "Diagnóstico histórico", ":material/manage_search:", "paginas/m1_diagnostico.py",
     f"O plano atual aplica o mesmo fator a {fat['pct_no_fator'].iloc[0]:.0f}% dos SKUs",
     "24 meses de vendas, estoque, carteira e capacidade viram insights"),
    ("2", "Previsão otimizada", ":material/query_stats:", "paginas/m2_previsao.py",
     f"Executivo {mvc.loc['Executivo', 'diferenca_pct']:+.0f}% · Escolar {mvc.loc['Escolar', 'diferenca_pct']:+.0f}% vs comercial",
     "Sazonalidade por família, nível do SKU, canal e carteira"),
    ("3", "Plano de produção e mix", ":material/factory:", "paginas/m3_plano.py",
     f"{int(risco['em_risco'].sum())} pedidos em risco · {fmt_int(dec['producao_sugerida'].sum())} un. a produzir",
     "Quanto produzir, o que adiar e para quem distribuir"),
    ("4", "Rastreabilidade da conversão", ":material/nfc:", "paginas/m4_rastreabilidade.py",
     f"Ponto cego de {cob.loc['KAs sem sell-out', 'participacao']:.1f}% do volume".replace(".", ","),
     "Sell-out e NFC no parceiro · Clube no consumidor"),
    ("5", "Resultados e retroalimentação", ":material/savings:", "paginas/m5_resultados.py",
     f"{fmt_brl(eco['producao_evitada_valor'])} em produção evitada · {fmt_int(ult['assinantes_premium'])} assinantes",
     "Economia, receita do Clube e dados de volta para a IA"),
]
cols = st.columns(5)
for col, (n, t, ic, pg, numero, desc) in zip(cols, etapas):
    with col.container(border=True, height=340):
        st.markdown(f"### {n}")
        st.markdown(f"**{t}**")
        st.markdown(f":violet[**{numero}**]")
        st.caption(desc)
        st.page_link(pg, label="Entrar", icon=ic)

st.info("**Retroalimentação:** cada decisão aprovada, cada venda realizada e cada compra verificada no Clube voltam para o momento 2. "
        "A previsão melhora, o plano erra menos e a economia financia mais rastreabilidade.", icon=":material/autorenew:")

st.subheader("Onde estamos hoje", divider="violet")
with st.container(horizontal=True):
    st.metric("MAPE do forecast atual", "31%", "meta ≤ 20%", delta_color="off", delta_arrow="off", border=True)
    st.metric("Erro do modelo no teste histórico", "9,18%", "WAPE · 8 métodos comparados", delta_color="off", delta_arrow="off", border=True)
    st.metric("Receita exposta em pedidos", fmt_brl(risco.loc[risco["em_risco"], "valor"].sum()), "23 de 53 pedidos", delta_color="off", delta_arrow="off", border=True)
    ex = motor.excesso_resumo(b)
    st.metric("Excesso acima de 90 dias", fmt_brl(ex["atual"]), f"{fmt_brl(ex['com_ops'])} com as OPs abertas", delta_color="off", delta_arrow="off", border=True)
    st.metric("Análise manual do PCP", "22 h/semana", "meta ≤ 8 h", delta_color="off", delta_arrow="off", border=True)
st.caption("Base fictícia do desafio · posição de 14/09/2026. Os números do Clube vêm da simulação do piloto (cenário-base, 6 meses).")
rodape()
