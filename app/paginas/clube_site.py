import base64
import mimetypes
import re

import streamlit as st
import streamlit.components.v1 as components

from estado import ROOT, rodape

PASTA = ROOT / "assets" / "clube"

st.caption("CLUBE CI · PROTÓTIPO VISUAL DO SITE")
st.title("Site do Clube")
st.markdown("Onde o consumidor chega pelo QR do caderno: créditos, refil no ritmo certo, drops das collabs da loja e a rede de parceiros.")


@st.cache_data
def pagina(versao: float) -> str:
    html = (PASTA / "clube_web.html").read_text(encoding="utf-8")

    def embutir(m: re.Match) -> str:
        arq = PASTA / m.group(1)
        tipo = mimetypes.guess_type(arq.name)[0] or "image/png"
        if arq.suffix == ".svg":
            tipo = "image/svg+xml"
        return f'src="data:{tipo};base64,{base64.b64encode(arq.read_bytes()).decode()}"'

    return re.sub(r'src="([^"]+)"', embutir, html)


components.html(pagina((PASTA / "clube_web.html").stat().st_mtime), height=1420, scrolling=True)
st.caption("Fotos e produtos reais da loja cadernointeligente.com.br. Parceiros da rede da plataforma de clube; benefícios ilustrativos, a confirmar no piloto.")
rodape()
