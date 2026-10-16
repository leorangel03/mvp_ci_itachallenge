import pandas as pd
import streamlit as st

from estado import base, clube_dados, jornada_df, momento, proximo, risco_df, rodape
from src.cockpit import diagnostico, jornada
from src.cockpit.dados import fmt_brl, fmt_int

momento(1, "Diagnóstico histórico", "Como o PCP decide hoje, e o que a base histórica revela?")

b = base()
ind = b["Indicadores_Atuais"]
st.subheader("Como o processo está hoje", divider="violet")
with st.container(horizontal=True):
    for r in ind.itertuples(index=False):
        st.metric(r[0], r[1], f"meta {r[2]}", delta_color="off", delta_arrow="off", border=True)

st.subheader("O que o algoritmo encontrou nos 24 meses", divider="violet")
fat = diagnostico.fator_unico(b)
saz = diagnostico.sazonalidade(b)
re = diagnostico.ruptura_excesso(b)
cad = diagnostico.cadastro_defasado(b)
ocup = diagnostico.ocupacao(b)
risco = risco_df()
cob = jornada.cobertura_consumo(b).set_index("recorte")
res = jornada.resumo_parceiros(jornada_df(), b)


def insight(n: int, titulo: str, achado: str, implicacao: str) -> None:
    st.markdown(f"#### {n}. {titulo}")
    st.markdown(achado)
    st.markdown(f":violet[→ {implicacao}]")


c1, c2 = st.columns(2)
with c1.container(border=True):
    f10 = fat.iloc[0]
    insight(1, "O plano usa um fator único por mês",
            f"O forecast comercial é o cadastro de demanda × **{f10['fator_mediano']:.2f}** em outubro para **{f10['pct_no_fator']:.0f}%** dos SKUs, "
            f"× {fat.iloc[1]['fator_mediano']:.2f} em novembro e × {fat.iloc[2]['fator_mediano']:.2f} em dezembro.".replace(".", ","),
            "a sazonalidade de cada família fica de fora; o modelo substitui o fator por índices por família.")
    st.dataframe(fat[["Mês", "fator_mediano", "pct_no_fator"]], hide_index=True, width="stretch", column_config={
        "fator_mediano": st.column_config.NumberColumn("Fator aplicado", format="%.2f"),
        "pct_no_fator": st.column_config.ProgressColumn("% dos SKUs com o mesmo fator", min_value=0, max_value=100, format="%.0f%%")})
with c2.container(border=True):
    insight(2, "Cada família tem seu calendário",
            f"Escolar chega a **{saz.loc['Escolar', 'fev']:.2f}** em fevereiro (volta às aulas); Planner a **{saz.loc['Planner', 'dez']:.2f}** em dezembro; "
            f"todas sobem em novembro (Black Friday).".replace(".", ","),
            "um índice sazonal por família captura essa pressão; o fator único não.")
    st.dataframe(saz.style.background_gradient(cmap="Purples", axis=None).format("{:.2f}"), width="stretch")

c1, c2 = st.columns(2)
with c1.container(border=True):
    insight(3, "Ruptura e excesso no mesmo mês, todo mês",
            f"Entre **{re.iloc[:, 0].min()} e {re.iloc[:, 0].max()} SKUs** ficaram abaixo do estoque de segurança e "
            f"**{re.iloc[:, 1].min()} a {re.iloc[:, 1].max()} SKUs** acima de 90 dias em cada mês.",
            "o problema não é o estoque total, é a alocação por SKU.")
    st.line_chart(re, color=["#B3261E", "#F4A6CB"], x_label="Mês", y_label="SKUs")
with c2.container(border=True):
    top = cad.head(6)
    insight(4, "O cadastro de demanda está defasado",
            f"Desvio médio de **{cad['desvio_pct'].abs().mean():.0f}%** entre o cadastro e as vendas dos últimos 3 meses. "
            f"CI-0031 está **{cad.loc['CI-0031', 'desvio_pct']:+.0f}%** acima (OP de 1.000 refis) e CI-0004 **{cad.loc['CI-0004', 'desvio_pct']:+.0f}%** abaixo (ruptura).",
            "a mesma causa gera excesso num SKU e falta no outro; o modelo usa o nível recente.")
    st.dataframe(top, width="stretch", column_config={
        "cadastro_mensal": st.column_config.NumberColumn("Cadastro (un./mês)"), "vendas_3m": st.column_config.NumberColumn("Vendas 3m (un./mês)"),
        "desvio_pct": st.column_config.NumberColumn("Desvio %", format="%+.0f%%")})

c1, c2, c3 = st.columns(3)
with c1.container(border=True, height=330):
    insight(5, "A carteira está sob pressão",
            f"**{int(risco['em_risco'].sum())} de {len(risco)} pedidos** não são cobertos a tempo: "
            f"**{fmt_brl(risco.loc[risco['em_risco'], 'valor'].sum())}** expostos a preço de tabela.",
            "a carteira vira piso da previsão e define a prioridade da fila.")
with c2.container(border=True, height=330):
    insight(6, "O ponto cego está nos parceiros",
            f"**{cob.loc['KAs sem sell-out', 'participacao']:.1f}%** do volume vai a parceiros sem sell-out. "
            f"KA-02 recebeu **{fmt_int(res.loc['KA-02', 'excedente_un'])} un.** a mais do que vendeu.".replace("24.9", "24,9"),
            "o Clube e o sell-out verificado reduzem essa lacuna (momento 4).")
with c3.container(border=True, height=330):
    insight(7, "A fábrica tem uma linha no limite",
            f"A linha Escolar opera com **{ocup.iloc[0] * 100:.0f}%** de ocupação média; Acessórios com {ocup.iloc[-1] * 100:.0f}%.",
            "subprevisão em Escolar custa ruptura na volta às aulas; capacidade precisa ser reservada.")

st.subheader("Sinais internos que também entram no diagnóstico", divider="violet")
cd = clube_dados()
eventos = b["Calendario_Eventos"]
c1, c2 = st.columns([3, 2])
c1.dataframe(eventos, hide_index=True, width="stretch")
with c2.container(border=True):
    st.markdown("**Clube CI (simulação do piloto, 6 meses)**")
    m = cd["meses"]
    st.metric("Compras verificadas por nota fiscal", fmt_int(m["nf_verificadas"].sum()))
    st.metric("Compras no ponto cego (verificadas ou declaradas)", fmt_int(int(cd["compras"]["ponto_cego"].sum())))
    st.caption("Onde o consumidor comprou, quanto pagou e quando: sinal que a base histórica não tinha.")

proximo("paginas/m2_previsao.py", "Momento 2: rodar a previsão otimizada com esses sinais")
rodape()
