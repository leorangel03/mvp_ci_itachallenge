"""Simulação determinística do piloto do Clube (cenário-base, meses 1 a 6) para o backoffice.

A base do desafio não traz dados de consumidor. Esta simulação usa o mix real de SKUs e parceiros da base e as
premissas do cenário-base do modelo econômico. Tudo o que sai daqui é rotulado como simulação na interface.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .clube import CENARIOS, COMPRADORES_DIRETO_MES, UN_KA_MES, simular
from .dados import DECLARADO, VERIFICADO, Base, precos

MESES_PILOTO = 6
TAXA_NF = 0.40          # membros que enviam nota fiscal no cadastro
TAXA_DECLARADO = 0.20   # informam loja e preço sem NF
RESGATE = 0.60
CIDADES = {"KA-01": ("São Paulo", "SP", -23.55, -46.63), "KA-02": ("Curitiba", "PR", -25.43, -49.27),
           "KA-03": ("Belo Horizonte", "MG", -19.92, -43.94), "KA-04": ("Recife", "PE", -8.05, -34.88),
           "KA-05": ("Brasília", "DF", -15.79, -47.88)}
CIDADES_DIRETO = [("São Paulo", "SP", -23.55, -46.63), ("Rio de Janeiro", "RJ", -22.91, -43.17), ("Porto Alegre", "RS", -30.03, -51.23),
                  ("Salvador", "BA", -12.97, -38.50), ("Fortaleza", "CE", -3.73, -38.52), ("Campinas", "SP", -22.91, -47.06),
                  ("Goiânia", "GO", -16.68, -49.25), ("Florianópolis", "SC", -27.59, -48.55)]


def gerar(base: Base, seed: int = 42) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    p = CENARIOS["Base"]
    sim = simular(p, meses=MESES_PILOTO)
    v = base["Vendas_24m"]
    v12 = v[v["Mês"].isin(sorted(v["Mês"].unique())[-12:])]
    ka = v12[v12["Cliente/Canal"].str.startswith("KA")]
    mix_ka = ka.groupby(["Cliente/Canal", "SKU"])["Quantidade faturada"].sum()
    mix_ka = mix_ka / mix_ka.sum()
    mix_dir = v12[~v12["Cliente/Canal"].str.startswith("KA")].groupby("SKU")["Quantidade faturada"].sum()
    mix_dir = mix_dir / mix_dir.sum()
    pr = precos(base)
    pares_so = set(map(tuple, base["Sell_Out"][["Cliente", "SKU"]].drop_duplicates().values))

    membros, compras = [], []
    mid = 0
    for m in range(1, MESES_PILOTO + 1):
        n_dir = int(round(COMPRADORES_DIRETO_MES * p["optin"]))
        n_qr = int(round(UN_KA_MES * min(1.0, m / 6) * p["scan"] / 1.2))
        for origem, n in (("Checkout dos canais diretos", n_dir), ("QR no produto (loja parceira)", n_qr)):
            for _ in range(n):
                mid += 1
                if origem.startswith("QR"):
                    idx = rng.choice(len(mix_ka), p=mix_ka.values)
                    parceiro, sku = mix_ka.index[idx]
                    cidade, uf, lat, lon = CIDADES[parceiro]
                else:
                    parceiro = rng.choice(["E-commerce", "Marketplace", "Loja própria"], p=[0.41, 0.33, 0.26])
                    sku = rng.choice(mix_dir.index, p=mix_dir.values)
                    cidade, uf, lat, lon = CIDADES_DIRETO[rng.integers(len(CIDADES_DIRETO))]
                membros.append({"membro": f"M{mid:05d}", "mes_cadastro": m, "origem": origem, "cidade": cidade, "uf": uf})
                r = rng.random()
                natureza = VERIFICADO if r < TAXA_NF else DECLARADO if r < TAXA_NF + TAXA_DECLARADO else None
                if natureza and origem.startswith("QR"):
                    compras.append({"membro": f"M{mid:05d}", "mes": m, "sku": sku, "parceiro": parceiro, "cidade": cidade,
                                    "uf": uf, "lat": lat + rng.normal(0, 0.05), "lon": lon + rng.normal(0, 0.05),
                                    "valor_pago": round(float(pr.get(sku, 60)) * rng.uniform(0.85, 1.0), 2), "natureza": natureza,
                                    "ponto_cego": (parceiro, sku) not in pares_so})
    membros = pd.DataFrame(membros)
    compras = pd.DataFrame(compras)

    # Status em cada mês: ativos (inatividade 2%/mês) e Premium (5% dos ativos)
    meses = []
    for m in range(1, MESES_PILOTO + 1):
        s = sim.iloc[m - 1]
        novos = int((membros["mes_cadastro"] == m).sum())
        nf = int(((compras["mes"] == m) & (compras["natureza"] == VERIFICADO)).sum()) if not compras.empty else 0
        creditos = nf * 5.0 + s["premium"] * 14.90 * 0.05
        meses.append({
            "mes": m, "novos_membros": novos, "membros_ativos": round(s["membros_ativos"]), "assinantes_premium": round(s["premium"]),
            "nf_verificadas": nf, "creditos_emitidos": round(creditos, 2), "creditos_resgatados": round(creditos * RESGATE, 2),
            "receita_clube": round(s["receita_clube"], 2), "custos_clube": round(s["custos_clube"], 2),
            "economia_cockpit": round(s["cockpit_liquido"] + 5000 * (m > 3), 2),
        })
    meses = pd.DataFrame(meses)

    campanhas = pd.DataFrame([
        ("Lembrete de refil no ritmo de uso", "WhatsApp (utilidade)", 9800, 1470, "Refis A5"),
        ("Pré-venda Premium: refil do mês", "E-mail + push", 12400, 620, "Assinatura Premium"),
        ("Drop exclusivo collab futebol", "Push + Instagram", 10100, 240, "Edição numerada com NFC"),
        ("Volta às aulas antecipada", "WhatsApp (marketing)", 6000, 390, "Família Escolar"),
    ], columns=["campanha", "canal", "enviados", "conversoes", "oferta"])
    campanhas["taxa_conversao"] = (campanhas["conversoes"] / campanhas["enviados"] * 100).round(1)

    beneficios = pd.DataFrame([
        ("Cinema", "Até 50% no ingresso", 3120), ("Farmácias", "15% em medicamentos", 2480), ("Refis e acessórios CI", "10% + frete grátis (Premium)", 2210),
        ("Academias", "Até 30% na mensalidade", 940), ("Educação e idiomas", "Até 30%", 610), ("Delivery", "Cupons semanais", 1730),
    ], columns=["categoria", "beneficio", "resgates"])
    return {"membros": membros, "compras": compras, "meses": meses, "campanhas": campanhas, "beneficios": beneficios}


def feed_modelo(compras: pd.DataFrame) -> pd.DataFrame:
    """Sell-out verificado agregado por parceiro × SKU, como entra na camada 2 do Cockpit."""
    v = compras[compras["natureza"] == VERIFICADO]
    g = v.groupby(["parceiro", "sku"]).agg(compras_verificadas=("membro", "count"), preco_medio=("valor_pago", "mean"),
                                           ponto_cego=("ponto_cego", "first")).reset_index()
    return g.sort_values("compras_verificadas", ascending=False)
