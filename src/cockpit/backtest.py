"""Camada 3 (Previsão): champion-challenger com 8 métodos no mesmo corte temporal (nível SKU).

Desenho da Semana 2: origens de ago/2025 a jul/2026, horizontes de 1 a 3 meses, só dados anteriores
à origem. 50 SKUs × 33 blocos = 1.650 previsões por método.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

METODOS = {
    "sazonal_familia_nivel_sku": "Sazonal da família × nível local do SKU",
    "ensemble_top3": "Ensemble dos 3 melhores",
    "sazonal_ingenuo": "Sazonal ingênuo",
    "ets_simples": "ETS simples (suavização exponencial)",
    "theta": "Theta clássico",
    "holt_amortecido": "Holt com tendência amortecida",
    "media_movel_3m": "Média móvel 3 meses",
    "ingenuo": "Ingênuo (repete o último mês)",
}
ALPHAS = np.round(np.arange(0.05, 1.0, 0.05), 2)


def _ses(y: np.ndarray, alpha: float) -> tuple[float, float]:
    nivel, sse = y[0], 0.0
    for v in y[1:]:
        sse += (v - nivel) ** 2
        nivel = alpha * v + (1 - alpha) * nivel
    return nivel, sse


def ets_simples(y: np.ndarray, h: int) -> float:
    nivel = min((_ses(y, a) for a in ALPHAS), key=lambda t: t[1])[0]
    return float(nivel)


def holt_amortecido(y: np.ndarray, h: int, phi: float = 0.9) -> float:
    melhor = None
    for a in ALPHAS[::2]:
        for b in (0.05, 0.1, 0.2, 0.3):
            nivel, tend, sse = y[0], y[1] - y[0], 0.0
            for v in y[1:]:
                prev = nivel + phi * tend
                sse += (v - prev) ** 2
                novo = a * v + (1 - a) * prev
                tend = b * (novo - nivel) + (1 - b) * phi * tend
                nivel = novo
            if melhor is None or sse < melhor[0]:
                melhor = (sse, nivel, tend)
    _, nivel, tend = melhor
    return float(nivel + sum(phi ** i for i in range(1, h + 1)) * tend)


def theta(y: np.ndarray, h: int) -> float:
    t = np.arange(len(y))
    inclinacao = np.polyfit(t, y, 1)[0]
    alpha = min(((a, _ses(y, a)[1]) for a in ALPHAS), key=lambda x: x[1])[0]
    nivel = _ses(y, alpha)[0]
    return float(nivel + 0.5 * inclinacao * (h - 1 + 1 / alpha))


def preparar(vendas: pd.DataFrame, produtos: pd.DataFrame) -> tuple[pd.DataFrame, list[pd.Timestamp]]:
    v = vendas.copy()
    v["mes"] = pd.to_datetime(v["Mês"]).dt.to_period("M").dt.to_timestamp()
    serie = v.groupby(["SKU", "mes"])["Quantidade faturada"].sum().unstack("mes").sort_index(axis=1)
    serie = serie.join(produtos.set_index("SKU")["Família"])
    return serie, [c for c in serie.columns if c != "Família"]


def prever_bloco(serie: pd.DataFrame, meses: list, i_origem: int, h: int) -> dict[str, pd.Series]:
    hist = serie[meses[: i_origem + 1]]
    fam_tot = hist.groupby(serie["Família"]).sum()
    ult12 = fam_tot.iloc[:, -12:]
    indice = ult12.div(ult12.mean(axis=1), axis=0)  # índice sazonal por família e mês do ano
    idx_mes = {c.month: c for c in ult12.columns}
    alvo = meses[i_origem + h]
    fam = serie["Família"]
    idx_alvo = indice[idx_mes[alvo.month]].reindex(fam).to_numpy()
    ult3 = hist.iloc[:, -3:]
    idx_ult3 = np.column_stack([indice[idx_mes[c.month]].reindex(fam).to_numpy() for c in ult3.columns])
    nivel = (ult3.to_numpy() / idx_ult3).mean(axis=1)

    out = {
        "sazonal_familia_nivel_sku": pd.Series(nivel * idx_alvo, index=serie.index),
        "sazonal_ingenuo": serie[meses[i_origem + h - 12]],
        "media_movel_3m": hist.iloc[:, -3:].mean(axis=1),
        "ingenuo": hist.iloc[:, -1],
    }
    arr = hist.to_numpy(dtype=float)
    out["ets_simples"] = pd.Series([ets_simples(y, h) for y in arr], index=serie.index)
    out["holt_amortecido"] = pd.Series([holt_amortecido(y, h) for y in arr], index=serie.index)
    out["theta"] = pd.Series([theta(y, h) for y in arr], index=serie.index)
    out["ensemble_top3"] = (out["sazonal_familia_nivel_sku"] + out["sazonal_ingenuo"] + out["ets_simples"]) / 3
    return out


def rodar_backtest(vendas: pd.DataFrame, produtos: pd.DataFrame) -> pd.DataFrame:
    serie, meses = preparar(vendas, produtos)
    linhas = []
    for i_origem in range(11, len(meses) - 1):
        for h in (1, 2, 3):
            if i_origem + h >= len(meses):
                continue
            alvo = meses[i_origem + h]
            real = serie[alvo]
            for metodo, prev in prever_bloco(serie, meses, i_origem, h).items():
                linhas.append(pd.DataFrame({
                    "sku": serie.index, "familia": serie["Família"].values, "origem": meses[i_origem],
                    "mes": alvo, "horizonte": h, "metodo": metodo,
                    "previsto": prev.reindex(serie.index).to_numpy(dtype=float).round(1),
                    "realizado": real.to_numpy(dtype=float),
                }))
    return pd.concat(linhas, ignore_index=True)


def wape(df: pd.DataFrame) -> float:
    return float((df["previsto"] - df["realizado"]).abs().sum() / df["realizado"].sum() * 100)


def vies(df: pd.DataFrame) -> float:
    return float((df["previsto"] - df["realizado"]).sum() / df["realizado"].sum() * 100)


def resumo(bt: pd.DataFrame) -> pd.DataFrame:
    g = bt.groupby("metodo")
    out = pd.DataFrame({"wape": g.apply(wape, include_groups=False), "vies": g.apply(vies, include_groups=False),
                        "n_previsoes": g.size()})
    out["metodo_nome"] = out.index.map(METODOS)
    return out.sort_values("wape")


def holdout(bt: pd.DataFrame, corte: str = "2026-02-01") -> pd.DataFrame:
    """Escolhe o método nas origens antes do corte; mede nas origens a partir do corte (não usadas na escolha)."""
    sel = bt[bt["origem"] < corte]
    teste = bt[bt["origem"] >= corte]
    r = pd.DataFrame({
        "wape_selecao": sel.groupby("metodo").apply(wape, include_groups=False),
        "wape_teste": teste.groupby("metodo").apply(wape, include_groups=False),
        "vies_teste": teste.groupby("metodo").apply(vies, include_groups=False),
    })
    r["metodo_nome"] = r.index.map(METODOS)
    return r.sort_values("wape_selecao")


def por_familia(bt: pd.DataFrame, metodo: str = "sazonal_familia_nivel_sku", ref: str = "sazonal_ingenuo") -> pd.DataFrame:
    a = bt[bt["metodo"] == metodo].groupby("familia")
    b = bt[bt["metodo"] == ref].groupby("familia")
    return pd.DataFrame({"wape_ia": a.apply(wape, include_groups=False), "wape_simples": b.apply(wape, include_groups=False),
                         "vies_ia": a.apply(vies, include_groups=False)}).sort_values("wape_ia")
