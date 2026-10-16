"""Cockpit CI — plataforma de previsão de demanda integrada à fábrica, à distribuição, às vendas e ao Clube."""
from __future__ import annotations

import streamlit as st

from estado import LOGO

st.set_page_config(page_title="Cockpit CI · Demanda inteligente", page_icon=str(LOGO) if LOGO.exists() else ":material/insights:",
                   layout="wide")
if LOGO.exists():
    st.logo(str(LOGO), size="large")

paginas = {
    "Jornada da decisão": [
        st.Page("paginas/inicio.py", title="Visão geral do ciclo", icon=":material/autorenew:", default=True),
        st.Page("paginas/m1_diagnostico.py", title="1. Diagnóstico histórico", icon=":material/manage_search:"),
        st.Page("paginas/m2_previsao.py", title="2. Previsão otimizada", icon=":material/query_stats:"),
        st.Page("paginas/m3_plano.py", title="3. Plano de produção e mix", icon=":material/factory:"),
        st.Page("paginas/m4_rastreabilidade.py", title="4. Rastreabilidade da conversão", icon=":material/nfc:"),
        st.Page("paginas/m5_resultados.py", title="5. Resultados e retroalimentação", icon=":material/savings:"),
    ],
    "Operação": [
        st.Page("paginas/detalhe_sku.py", title="Detalhe do SKU", icon=":material/inventory_2:"),
        st.Page("paginas/log_decisoes.py", title="Log de decisões", icon=":material/history:"),
    ],
    "Clube CI": [
        st.Page("paginas/clube_site.py", title="Site do Clube", icon=":material/language:", url_path="clube-site"),
        st.Page("paginas/clube_app.py", title="App do consumidor", icon=":material/smartphone:"),
        st.Page("paginas/clube_backoffice.py", title="Backoffice do Clube", icon=":material/admin_panel_settings:"),
    ],
    "Confiança": [
        st.Page("paginas/previsao.py", title="Validação do modelo", icon=":material/fact_check:"),
        st.Page("paginas/verificacoes.py", title="Verificações de segurança", icon=":material/verified_user:"),
        st.Page("paginas/arquitetura.py", title="Arquitetura e governança", icon=":material/account_tree:"),
    ],
}
st.navigation(paginas).run()
