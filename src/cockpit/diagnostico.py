"""Momento 1 (Diagnóstico histórico): como o PCP decide hoje e o que a base histórica revela."""
from __future__ import annotations

import math

import pandas as pd

from .dados import Base, demanda_recente, ler_fonte, precos

MESES_PT = {1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun", 7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez"}
MAPA_FC = {"Out/26": 10, "Nov/26": 11, "Dez/26": 12}


def fator_unico(base: Base) -> pd.DataFrame:
    """O forecast comercial é o cadastro de demanda × um fator por mês, igual para todos os SKUs?"""
    fc = base["Forecast_Comercial"].copy()
    fc["u"] = pd.to_numeric(fc["Previsão unidades"], errors="coerce")
    cad = base["Produtos"].set_index("SKU")["Venda média/dia"] * 30
    fc["fator"] = fc["u"] / fc["SKU"].map(cad)
    fc["mes_n"] = fc["Mês"].map(MAPA_FC)
    g = fc.groupby(["mes_n", "Mês"])["fator"]
    out = pd.DataFrame({"fator_mediano": g.median(), "skus": g.size(),
                        "skus_no_fator": g.apply(lambda s: int((abs(s - s.median()) < 0.01).sum()))}).reset_index()
    out["pct_no_fator"] = out["skus_no_fator"] / out["skus"] * 100
    return out.sort_values("mes_n")


def sazonalidade(base: Base) -> pd.DataFrame:
    """Índice sazonal por família e mês do ano (média dos 24 meses), base 1,00 = mês médio."""
    v = base["Vendas_24m"].merge(base["Produtos"][["SKU", "Família"]], on="SKU")
    v["m"] = pd.to_datetime(v["Mês"]).dt.month
    g = v.groupby(["Família", "m"])["Quantidade faturada"].sum().unstack("m")
    idx = g.div(g.mean(axis=1), axis=0).round(2)
    idx.columns = [MESES_PT[c] for c in idx.columns]
    return idx


def ruptura_excesso(base: Base) -> pd.DataFrame:
    h = ler_fonte("Historico_Estoque")
    seg = base["Produtos"].set_index("SKU")["Estoque segurança (dias)"]
    h["abaixo"] = h["Cobertura estimada dias"] < h["SKU"].map(seg)
    h["acima90"] = h["Cobertura estimada dias"] > 90
    out = h.groupby("Mês")[["abaixo", "acima90"]].sum()
    out.columns = ["SKUs abaixo da segurança", "SKUs acima de 90 dias"]
    return out


def cadastro_defasado(base: Base) -> pd.DataFrame:
    p = base["Produtos"].set_index("SKU")
    cad = p["Venda média/dia"] * 30
    rec = demanda_recente(base["Vendas_24m"])
    df = pd.DataFrame({"produto": p["Produto"], "familia": p["Família"], "cadastro_mensal": cad.round(0), "vendas_3m": rec.round(0)})
    df["desvio_pct"] = ((df["cadastro_mensal"] - df["vendas_3m"]) / df["vendas_3m"] * 100).round(1)
    return df.sort_values("desvio_pct", key=abs, ascending=False)


def ocupacao(base: Base) -> pd.Series:
    return base["Capacidade_Semanal"].groupby("Família")["Ocupação"].mean().sort_values(ascending=False)


def modelo_vs_comercial(base: Base, previsao: pd.DataFrame) -> pd.DataFrame:
    """Trimestre out–dez por família: previsão do modelo × forecast comercial."""
    fc = base["Forecast_Comercial"].copy()
    fc["u"] = pd.to_numeric(fc["Previsão unidades"], errors="coerce")
    fc = fc.merge(base["Produtos"][["SKU", "Família"]], on="SKU")
    com = fc.groupby("Família")["u"].sum().rename("comercial")
    mod = previsao[previsao["status_previsao"] == "OK"].groupby("familia")["previsao_unidades"].sum().rename("modelo")
    df = pd.concat([mod, com], axis=1)
    df["diferenca_pct"] = ((df["modelo"] / df["comercial"] - 1) * 100).round(1)
    return df


def economia_operacional(decisoes: pd.DataFrame, base: Base) -> dict:
    """Quanto o plano deixa de gastar ou de expor (preço de tabela), a partir das recomendações do motor."""
    pr = precos(base)
    red = decisoes[decisoes["recomendacao"] == "Reduzir/adiar OP"]
    evitado = 0.0
    for r in red.itertuples():
        if r.demanda_3m and r.lote_minimo and not math.isnan(r.demanda_3m):
            alvo = math.ceil(3 * r.demanda_3m / r.lote_minimo) * r.lote_minimo
            evitado += max(0, r.maior_op - alvo) * pr.get(r.sku, 0)
    cobre = decisoes[(decisoes["recomendacao"] == "Priorizar produção")]
    return {
        "producao_evitada_valor": evitado,
        "ops_revisadas": len(red),
        "receita_coberta": float(cobre["valor_risco"].sum()),
        "horas_pcp_ano": 14 * 48,
        "valor_horas_ano": 14 * 48 * 80,
        "estoque_meta": 180_000,
    }
