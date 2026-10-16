import streamlit as st

from estado import base, cabecalho, previsao, rodape
from src.cockpit import seguranca

cabecalho("Verificações de segurança", "Cada caso injeta um problema numa cópia da base e confere a saída do motor · executado ao vivo")

if st.button("Executar as verificações novamente", icon=":material/replay:"):
    st.session_state.pop("verificacoes", None)
if "verificacoes" not in st.session_state:
    with st.spinner("Executando os 6 casos…"):
        st.session_state["verificacoes"] = seguranca.executar(base(), previsao())
r = st.session_state["verificacoes"]
ok = int(r["passou"].sum())
st.metric("Verificações aprovadas", f"{ok} de {len(r)}", border=True)

for i, c in enumerate(r.itertuples(), start=1):
    with st.container(border=True):
        a, b = st.columns([5, 1])
        a.markdown(f"#### {i}. {c.verificacao}")
        with b:
            st.badge("Passou" if c.passou else "Falhou", color="green" if c.passou else "red",
                     icon=":material/check:" if c.passou else ":material/close:")
        x, y, z = st.columns(3)
        x.markdown(f"**Entrada**  \n{c.entrada}")
        y.markdown(f"**Esperado**  \n{c.esperado}")
        z.markdown(f"**Observado**  \n`{c.observado}`")
st.caption("Os mesmos casos rodam na suíte automatizada (pytest, tests/test_cockpit.py).")
rodape()
