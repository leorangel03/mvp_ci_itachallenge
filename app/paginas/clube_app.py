import streamlit as st

from estado import rodape

st.caption("CLUBE CI · PROTÓTIPO VISUAL DO APP DO CONSUMIDOR")
st.title("App do consumidor")
st.markdown("O consumidor escaneia o QR (ou aproxima o NFC nas linhas premium e collabs), entra no Clube, registra onde comprou e "
            "recebe benefícios. Cada registro vira dado verificado para a previsão.")

CSS = """
<style>
.ci-wrap{display:flex;gap:28px;flex-wrap:wrap;justify-content:center;font-family:'Source Sans Pro',Arial,sans-serif;padding:8px 0 4px}
.ci-phone{width:290px;height:600px;border-radius:42px;background:#31003E;padding:12px;box-shadow:0 18px 40px rgba(49,0,62,.25)}
.ci-screen{width:100%;height:100%;border-radius:32px;background:#FBF8FD;overflow:hidden;position:relative;display:flex;flex-direction:column}
.ci-top{background:#74008D;color:#fff;padding:22px 18px 16px}
.ci-top small{opacity:.85;font-size:11px;letter-spacing:.06em}
.ci-top h3{margin:4px 0 0;font-size:19px;color:#fff;line-height:1.2}
.ci-pill{display:inline-block;background:#F4A6CB;color:#31003E;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:700;margin-top:8px}
.ci-body{padding:14px;display:flex;flex-direction:column;gap:10px;flex:1}
.ci-card{background:#fff;border:1px solid #E9E1EE;border-radius:16px;padding:12px}
.ci-card b{color:#31003E}
.ci-card p{margin:2px 0;font-size:12.5px;color:#4A3B52;line-height:1.35}
.ci-big{font-size:26px;font-weight:800;color:#74008D;margin:2px 0}
.ci-btn{background:#74008D;color:#fff;border-radius:12px;text-align:center;padding:10px;font-weight:700;font-size:13px}
.ci-btn.alt{background:#F4A6CB;color:#31003E}
.ci-row{display:flex;gap:8px}
.ci-mini{flex:1;background:#fff;border:1px solid #E9E1EE;border-radius:14px;padding:10px;text-align:center;font-size:11.5px;color:#4A3B52}
.ci-mini b{display:block;color:#74008D;font-size:14px}
.ci-ok{background:#E8F5EE;color:#16794B;border-radius:10px;padding:6px 10px;font-size:12px;font-weight:700}
.ci-tab{position:absolute;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #E9E1EE;display:flex;justify-content:space-around;padding:9px 0 14px;font-size:10.5px;color:#6D5D73}
.ci-tab .on{color:#74008D;font-weight:700}
.ci-scan{height:120px;border-radius:16px;border:2px dashed #B07CC6;display:flex;align-items:center;justify-content:center;color:#74008D;font-weight:700;font-size:13px;background:#F6F0F9}
.ci-cap{text-align:center;color:#6D5D73;font-size:12.5px;margin-top:8px;font-family:'Source Sans Pro',Arial,sans-serif}
</style>
"""

TELA_INICIO = """
<div><div class="ci-phone"><div class="ci-screen">
 <div class="ci-top"><small>CLUBE CI</small><h3>Olá, Marina</h3><span class="ci-pill">Premium</span></div>
 <div class="ci-body">
  <div class="ci-card"><p>Seus créditos CI</p><div class="ci-big">R$ 12,40</div><p>Use até 20% em cada compra no site ou nas lojas parceiras.</p></div>
  <div class="ci-card"><b>Seu refil A5 deve acabar em ~9 dias</b><p>Pelo seu ritmo de uso informado. Reponha com 10% off e frete grátis.</p><div class="ci-btn" style="margin-top:8px">Repor agora</div></div>
  <div class="ci-row"><div class="ci-mini"><b>50%</b>Cinema</div><div class="ci-mini"><b>15%</b>Farmácias</div><div class="ci-mini"><b>30%</b>Academias</div></div>
  <div class="ci-card"><b>Drop exclusivo · collab futebol</b><p>Edição numerada com NFC. Membros Premium compram 48 h antes.</p></div>
 </div>
 <div class="ci-tab"><span class="on">Início</span><span>Escanear</span><span>Benefícios</span><span>Perfil</span></div>
</div></div><div class="ci-cap">1. Início: créditos, lembrete de refil e benefícios</div></div>
"""

TELA_REGISTRO = """
<div><div class="ci-phone"><div class="ci-screen">
 <div class="ci-top"><small>REGISTRAR COMPRA</small><h3>Planner Semanal</h3><span class="ci-pill">Identificado pelo QR</span></div>
 <div class="ci-body">
  <div class="ci-scan">QR lido · CI-0004 · lote 2610</div>
  <div class="ci-card"><p><b>Onde comprou</b></p><p>Rede Ponto Criativo · Curitiba (PR)</p></div>
  <div class="ci-card"><p><b>Quanto pagou</b></p><p>R$ 119,90 · 14/11/2026</p></div>
  <div class="ci-card"><p><b>Nota fiscal</b></p><p>Foto enviada · chave de 44 dígitos lida</p><div class="ci-ok" style="margin-top:6px">✓ Compra verificada · +R$ 5,00 em créditos</div></div>
  <div class="ci-btn alt">Ativar garantia e lembrete de refil</div>
 </div>
 <div class="ci-tab"><span>Início</span><span class="on">Escanear</span><span>Benefícios</span><span>Perfil</span></div>
</div></div><div class="ci-cap">2. Registro: o QR identifica o produto; a NF verifica a loja</div></div>
"""

TELA_PREMIUM = """
<div><div class="ci-phone"><div class="ci-screen">
 <div class="ci-top"><small>PLANOS</small><h3>Clube CI Premium</h3><span class="ci-pill">R$ 14,90/mês</span></div>
 <div class="ci-body">
  <div class="ci-card"><b>Free</b><p>5% em créditos · lembrete de refil · indicação premiada · parceiros básicos</p></div>
  <div class="ci-card" style="border:2px solid #74008D"><b>Premium</b><p>Refil do mês com desconto ou frete grátis</p><p>Acesso antecipado a collabs e drops</p><p>Rede de parceiros: cinema, farmácia, academia, educação</p><p>Até 3 dependentes</p><div class="ci-btn" style="margin-top:8px">Assinar Premium</div></div>
  <div class="ci-card"><b>Indique e ganhe</b><p>Quem indica e quem compra ganham créditos após a primeira compra confirmada.</p></div>
 </div>
 <div class="ci-tab"><span>Início</span><span>Escanear</span><span class="on">Benefícios</span><span>Perfil</span></div>
</div></div><div class="ci-cap">3. Premium: assinatura que paga a plataforma</div></div>
"""

st.html(CSS + f'<div class="ci-wrap">{TELA_INICIO}{TELA_REGISTRO}{TELA_PREMIUM}</div>')

c1, c2, c3 = st.columns(3)
with c1.container(border=True):
    st.markdown("**QR em todo o portfólio**")
    st.caption("Impresso na capa ou no encarte. Custo marginal próximo de zero. Leva direto ao cadastro do Clube.")
with c2.container(border=True):
    st.markdown("**NFC em premium e collabs**")
    st.caption("≈ R$ 1,30 por unidade. Autenticidade, edição numerada e leitura no recebimento da loja.")
with c3.container(border=True):
    st.markdown("**Regras e privacidade**")
    st.caption("Crédito só com NF validada; chave única; teto por CPF; consentimento LGPD. O Cockpit recebe só agregados por loja, SKU e região.")
st.page_link("paginas/clube_backoffice.py", label="Ver o backoffice do Clube", icon=":material/arrow_forward:")
rodape()
