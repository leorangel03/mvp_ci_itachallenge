import pandas as pd
import streamlit as st

from estado import badge_natureza, base, clube_dados, jornada_df, momento, proximo, rodape, selecionar_sku
from src.cockpit import clube, jornada
from src.cockpit.dados import fmt_int

momento(4, "Rastreabilidade da conversão", "Depois de distribuído, o produto girou? No parceiro pelo sell-out e pelo NFC; no consumidor pelo Clube.")

b = base()
cob = jornada.cobertura_consumo(b)
pc = cob.set_index("recorte")["participacao"]
st.subheader("Onde enxergamos o consumo final (unidades, 12 meses)", divider="violet")
barra = cob.set_index("recorte")[["participacao"]].T.rename(index={"participacao": "Volume"})
st.bar_chart(barra, horizontal=True, stack=True, color=["#74008D", "#B07CC6", "#F4A6CB"], height=140, y_label="", x_label="% do volume")
with st.container(horizontal=True):
    for r in cob.itertuples():
        st.metric(r.recorte, f"{r.participacao:.1f}%".replace(".", ","), r.leitura, delta_color="off", delta_arrow="off", border=True)

aba1, aba2 = st.tabs([":material/storefront: No parceiro: sell-out e NFC", ":material/person: No consumidor: Clube CI"])

with aba1:
    jp = jornada_df()
    res = jornada.resumo_parceiros(jp, b)
    st.dataframe(res, width="stretch", column_config={
        "nome": "Parceiro", "regiao": "Região", "skus_vendidos": "SKUs vendidos", "skus_com_sell_out": "SKUs com sell-out",
        "sell_in_12m": st.column_config.NumberColumn("Sell-in 12m*", format="localized"),
        "sell_out_12m": st.column_config.NumberColumn("Sell-out 12m*", format="localized"),
        "estoque_parceiro": st.column_config.NumberColumn("Estoque na loja", format="localized"),
        "faturado_12m": st.column_config.NumberColumn("Faturado 12m", format="localized"),
        "sell_in_sobre_sell_out": st.column_config.ProgressColumn("Sell-in ÷ sell-out", min_value=0.9, max_value=1.1, format="%.3f"),
        "excedente_un": st.column_config.NumberColumn("Enviado a mais (un.)", format="localized"),
        "cobertura_sell_out_pct": st.column_config.NumberColumn("% do faturado com sell-out", format="%.1f%%")})
    k = res["sell_in_sobre_sell_out"].idxmax()
    st.warning(f"**{k} · {res.loc[k, 'nome']}** recebeu {fmt_int(res.loc[k, 'excedente_un'])} un. a mais do que vendeu e tem "
               f"{fmt_int(res.loc[k, 'estoque_parceiro'])} un. estimadas na loja: segurar a reposição e oferecer sell-out completo em troca de prioridade.",
               icon=":material/inventory:")
    with st.container(border=True):
        st.markdown("**NFC nas linhas premium e collabs**")
        st.markdown("A etiqueta NFC é lida no recebimento da loja e na ativação pelo consumidor. A primeira leitura confirma que o lote chegou "
                    "ao parceiro; a segunda confirma que saiu da prateleira. É o sell-out item a item onde o parceiro não manda relatório.")
    parceiro = st.selectbox("Detalhe do parceiro", sorted(jp["parceiro"].unique()), index=1)
    v = jp[jp["parceiro"] == parceiro].sort_values(["tem_sell_out", "sell_in_sobre_sell_out"], ascending=False)
    sel = st.dataframe(v[["sku", "sell_in_12m", "sell_out_12m", "estoque_parceiro", "cobertura_parceiro_meses", "tendencia_diretos_pct",
                          "sinal", "recomendacao", "acao", "natureza"]], hide_index=True, width="stretch", height=300,
                       on_select="rerun", selection_mode="single-row", column_config={
                           "sku": "SKU", "sell_in_12m": st.column_config.NumberColumn("Sell-in 12m"),
                           "sell_out_12m": st.column_config.NumberColumn("Sell-out 12m", help="Vazio = indisponível, nunca zero"),
                           "estoque_parceiro": st.column_config.NumberColumn("Estoque na loja"),
                           "cobertura_parceiro_meses": st.column_config.NumberColumn("Cobertura (meses)"),
                           "tendencia_diretos_pct": st.column_config.NumberColumn("Tendência nos diretos (%)"),
                           "sinal": "Sinal", "recomendacao": "Recomendação", "acao": st.column_config.TextColumn("Ação", width="large"),
                           "natureza": "Natureza do dado"})
    if sel and sel.selection.rows:
        sku = v.iloc[sel.selection.rows[0]]["sku"]
        if st.button(f"Abrir {sku} no detalhe", icon=":material/arrow_forward:"):
            selecionar_sku(sku)

with aba2:
    cd = clube_dados()
    m, mem, comp = cd["meses"], cd["membros"], cd["compras"]
    st.caption("Simulação do piloto do Clube (cenário-base, 6 meses), gerada com o mix real de SKUs e parceiros da base.")
    qr = mem[mem["origem"].str.startswith("QR")]
    verif = comp[comp["natureza"] == "Verificado pelo consumidor"]
    funil = pd.DataFrame({"etapa": ["1. Membros (checkout + QR)", "2. Cadastros via QR na loja", "3. Compras informadas", "4. Verificadas por NF",
                                    "5. Verificadas no ponto cego", "6. Assinantes Premium (mês 6)"],
                          "pessoas": [len(mem), len(qr), len(comp), len(verif), int(verif["ponto_cego"].sum()), int(m["assinantes_premium"].iloc[-1])]})
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**Funil de conversão do consumidor**")
        st.bar_chart(funil.set_index("etapa"), horizontal=True, color="#74008D", x_label="Pessoas / compras", y_label="")
    with c2:
        st.markdown("**Onde as compras verificadas aconteceram**")
        st.map(verif.assign(size=60), latitude="lat", longitude="lon", size="size", color="#74008D", zoom=3)

    st.markdown("#### Capturar uma compra agora (QR → nota fiscal)")
    if "compras" not in st.session_state:
        st.session_state["compras"] = []
    prod = b["Produtos"]
    with st.form("captura", border=True):
        a, b2, c = st.columns(3)
        sku = a.selectbox("Produto escaneado", prod["SKU"], index=3, format_func=lambda s: f"{s} · {prod.set_index('SKU').loc[s, 'Produto']}")
        valor = b2.number_input("Quanto pagou (R$)", min_value=0.0, value=119.90, step=1.0)
        cidade = c.text_input("Cidade da compra", value="Curitiba")
        chave = st.text_input("Chave de acesso da NF (44 dígitos) — opcional", value=st.session_state.get("chave_exemplo", ""))
        enviar = st.form_submit_button("Enviar cadastro da compra", type="primary", icon=":material/send:")
    if st.button("Gerar NF de exemplo de uma loja KA-02", icon=":material/receipt_long:"):
        st.session_state["chave_exemplo"] = clube.gerar_chave_exemplo("22333444000172")
        st.rerun()
    if enviar:
        usadas = {c["chave"] for c in st.session_state["compras"] if c["chave"]}
        r = clube.validar_compra(chave, sku, usadas)
        if r.valida:
            st.session_state["compras"].append({"sku": sku, "parceiro": r.parceiro or "—", "valor_pago": valor, "cidade": cidade,
                                                "chave": "".join(ch for ch in chave if ch.isdigit()), "natureza": r.natureza})
            st.success(r.mensagem, icon=":material/task_alt:")
        else:
            st.error(r.mensagem, icon=":material/block:")
        badge_natureza(r.natureza)
    if st.session_state["compras"]:
        st.dataframe(pd.DataFrame(st.session_state["compras"]), hide_index=True, width="stretch")
        st.info("Compras verificadas entram na camada 2 como 'Verificado pelo consumidor' e calibram o giro no ponto cego.", icon=":material/insights:")

proximo("paginas/m5_resultados.py", "Momento 5: ver a economia, a receita do Clube e o que volta para a IA")
rodape()
