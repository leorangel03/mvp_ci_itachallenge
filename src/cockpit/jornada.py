"""Camada 2 (Jornada B2B2C): sell-in × sell-out por parceiro, ponto cego e recomendações comerciais."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .dados import ESTIMADO, INDISPONIVEL, OBSERVADO, Base

LIMIAR_ACUMULO = 1.04      # enviou ≥ 4% a mais do que vendeu no período
COBERTURA_ALTA_MESES = 3.0  # estoque estimado no parceiro acima de 3 meses de giro
COBERTURA_BAIXA_MESES = 1.0


def cobertura_consumo(base: Base) -> pd.DataFrame:
    """Participação do volume (12m) com consumo observado, observado pelo parceiro e ponto cego."""
    v = base["Vendas_24m"]
    v12 = v[v["Mês"].isin(sorted(v["Mês"].unique())[-12:])]
    pares_so = set(map(tuple, base["Sell_Out"][["Cliente", "SKU"]].drop_duplicates().values))
    ka = v12["Cliente/Canal"].str.startswith("KA")
    coberto = [(c, s) in pares_so for c, s in zip(v12["Cliente/Canal"], v12["SKU"])]
    q = v12["Quantidade faturada"]
    total = q.sum()
    linhas = [
        ("Canais diretos", "Consumo observado", OBSERVADO, q[~ka].sum()),
        ("KAs com sell-out", "Observado pelo parceiro", OBSERVADO, q[ka & pd.Series(coberto, index=v12.index)].sum()),
        ("KAs sem sell-out", "Ponto cego", INDISPONIVEL, q[ka & ~pd.Series(coberto, index=v12.index)].sum()),
    ]
    df = pd.DataFrame(linhas, columns=["recorte", "leitura", "natureza", "unidades"])
    df["participacao"] = df["unidades"] / total * 100
    return df


def jornada_parceiros(base: Base) -> pd.DataFrame:
    """Uma linha por parceiro (KA) × SKU vendido nos últimos 12 meses, com sinal e recomendação."""
    v = base["Vendas_24m"]
    v12 = v[v["Mês"].isin(sorted(v["Mês"].unique())[-12:]) & v["Cliente/Canal"].str.startswith("KA")]
    faturado = v12.groupby(["Cliente/Canal", "SKU"])["Quantidade faturada"].sum().rename("faturado_12m")
    si = base["Sell_In"].groupby(["Cliente", "SKU"])["Quantidade enviada"].sum().rename("sell_in_12m")
    so = base["Sell_Out"].groupby(["Cliente", "SKU"])["Quantidade vendida"].sum().rename("sell_out_12m")
    ult = base["Sell_Out"]["Mês"].max()
    est = base["Sell_Out"][base["Sell_Out"]["Mês"] == ult].set_index(["Cliente", "SKU"])["Estoque estimado cliente"].rename("estoque_parceiro")
    so3 = base["Sell_Out"][base["Sell_Out"]["Mês"].isin(sorted(base["Sell_Out"]["Mês"].unique())[-3:])]
    giro = (so3.groupby(["Cliente", "SKU"])["Quantidade vendida"].sum() / 3).rename("giro_mensal")

    df = faturado.to_frame()
    df.index.names = ["parceiro", "sku"]
    for s in (si, so, est, giro):
        s.index.names = ["parceiro", "sku"]
        df = df.join(s)
    df = df.reset_index()

    # Proxy para o ponto cego: tendência do mesmo SKU nos canais diretos (Estimado)
    d = v[~v["Cliente/Canal"].str.startswith("KA")]
    meses = sorted(d["Mês"].unique())
    rec, ant = d[d["Mês"].isin(meses[-3:])], d[d["Mês"].isin(meses[-6:-3])]
    tend = (rec.groupby("SKU")["Quantidade faturada"].sum() / ant.groupby("SKU")["Quantidade faturada"].sum() - 1) * 100
    df["tendencia_diretos_pct"] = df["sku"].map(tend).round(1)

    df["tem_sell_out"] = df["sell_out_12m"].notna()
    df["sell_in_sobre_sell_out"] = (df["sell_in_12m"] / df["sell_out_12m"]).round(3)
    df["cobertura_parceiro_meses"] = (df["estoque_parceiro"] / df["giro_mensal"]).round(1)
    df[["sinal", "recomendacao", "acao", "natureza", "evidencia"]] = df.apply(_classificar, axis=1, result_type="expand")
    return df


def _classificar(r: pd.Series) -> tuple[str, str, str, str, str]:
    if not r["tem_sell_out"]:
        t = r["tendencia_diretos_pct"]
        if pd.notna(t) and t >= 10:
            return ("Ponto cego com demanda em alta", "Investigar", "Pedir sell-out ao parceiro; demanda nos diretos sobe "
                    f"{t:.0f}%", ESTIMADO, f"Sem sell-out do parceiro. Proxy dos canais diretos: {t:+.0f}% (3m vs 3m anteriores)")
        return ("Ponto cego", "Investigar", "Sell-out indisponível: não tratar como venda zero", INDISPONIVEL,
                "Parceiro não envia sell-out deste SKU")
    ratio, cob = r["sell_in_sobre_sell_out"], r["cobertura_parceiro_meses"]
    ev = f"Sell-in {r['sell_in_12m']:.0f} × sell-out {r['sell_out_12m']:.0f} un. (12m); estoque no parceiro {r['estoque_parceiro']:.0f} un. ≈ {cob:.1f} meses de giro"
    if ratio >= LIMIAR_ACUMULO or cob > COBERTURA_ALTA_MESES:
        return ("Acúmulo no parceiro", "Monitorar", "Segurar a reposição até o giro normalizar", OBSERVADO, ev)
    if ratio < 1 and cob < COBERTURA_BAIXA_MESES:
        return ("Giro acima do abastecimento", "Repor", "Repor o parceiro antes da ruptura na loja", OBSERVADO, ev)
    return ("Equilibrado", "Sem ação necessária", "Manter a cadência de reposição", OBSERVADO, ev)


def resumo_parceiros(jp: pd.DataFrame, base: Base) -> pd.DataFrame:
    p = base["Parceiros_Canais"].set_index("Código")
    g = jp.groupby("parceiro")
    out = pd.DataFrame({
        "nome": g.size().index.map(p["Nome fictício"]),
        "regiao": g.size().index.map(p["Região"]),
        "skus_vendidos": g.size(),
        "skus_com_sell_out": g["tem_sell_out"].sum(),
        "sell_in_12m": g["sell_in_12m"].sum(min_count=1),
        "sell_out_12m": g["sell_out_12m"].sum(min_count=1),
        "estoque_parceiro": g["estoque_parceiro"].sum(min_count=1),
        "faturado_12m": g["faturado_12m"].sum(),
    })
    out["sell_in_sobre_sell_out"] = (out["sell_in_12m"] / out["sell_out_12m"]).round(3)
    out["excedente_un"] = (out["sell_in_12m"] - out["sell_out_12m"]).round(0)
    out["cobertura_sell_out_pct"] = (jp[jp["tem_sell_out"]].groupby("parceiro")["faturado_12m"].sum() / out["faturado_12m"] * 100).round(1)
    return out


def alocacao_parceiros(jp: pd.DataFrame, sku: str) -> pd.DataFrame:
    """Para produto escasso: ordena parceiros por giro observado (Priorizar parceiro)."""
    d = jp[(jp["sku"] == sku)].copy()
    d["prioridade"] = np.where(d["tem_sell_out"], d["giro_mensal"].fillna(0), 0)
    return d.sort_values(["tem_sell_out", "prioridade"], ascending=False)
