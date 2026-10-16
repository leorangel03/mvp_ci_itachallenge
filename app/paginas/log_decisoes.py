import streamlit as st

from estado import cabecalho, rodape
from src.cockpit.decisoes import carregar_log, resumo_retroalimentacao

cabecalho("Log de decisões", "Cada aprovação, ajuste ou rejeição fica registrada e alimenta a retroalimentação do modelo")

log = carregar_log()
r = resumo_retroalimentacao(log)
with st.container(horizontal=True):
    st.metric("Decisões registradas", r["decisoes"], border=True)
    st.metric("Aceite sem ajuste", f"{r['aceite_pct']:.1f}%".replace(".", ",") if r["aceite_pct"] is not None else "—", border=True)
    st.metric("Ajustes humanos", r["ajustes"], border=True)
    st.metric("Diferença líquida (un.)", r["delta_unidades"], border=True,
              help="Quantidade aprovada − sugerida. Com o realizado, vira o FVA: o ajuste humano melhorou ou piorou a previsão?")
if log.empty:
    st.info("Ainda não há decisões. Abra um SKU na Decisão da semana e registre a decisão.", icon=":material/info:")
else:
    st.dataframe(log.sort_values("registrado_em", ascending=False), hide_index=True, width="stretch")
    st.download_button("Baixar log (CSV)", log.to_csv(index=False).encode("utf-8"), "log_decisoes.csv", "text/csv",
                       icon=":material/download:")
st.caption("No piloto, o log vai para um banco com perfis de acesso; o realizado de cada mês fecha o ciclo: erro, viés e FVA por SKU.")
rodape()
