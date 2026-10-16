"""Camada 4 (Motor de decisão): regras auditáveis que convertem previsão em ação.

Necessidade líquida = máx(demanda prevista no horizonte, carteira firme) + estoque de segurança
                      − estoque atual − OPs que concluem até o fim do horizonte.
Depois: arredondamento ao lote mínimo, restrição de capacidade semanal da família e uma das
recomendações do desafio, com evidências, natureza do dado e confiança. Nenhuma OP é liberada:
toda saída nasce com status "Aguardando aprovação".
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .dados import (CALCULADO, DATA_REFERENCIA, ESTIMADO, FIM_HORIZONTE, INDISPONIVEL, OBSERVADO, PREVISTO,
                    Base, demanda_recente, fmt_int, precos)

COBERTURA_EXCESSO_DIAS = 90
OP_EXCESSIVA_MESES = 6

ORDEM_PRIORIDADE = {"Priorizar produção": 0, "Produzir": 1, "Investigar": 2, "Reduzir/adiar OP": 3,
                    "Monitorar": 4, "Sem ação necessária": 5}


def deduplicar_carteira(carteira: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Remove pedidos repetidos (mesmo pedido, SKU, cliente, quantidade e data). Devolve (limpa, duplicados)."""
    chave = ["Pedido", "SKU", "Cliente/Canal", "Quantidade", "Data prometida"]
    dup = carteira[carteira.duplicated(chave, keep="first")]
    return carteira.drop_duplicates(chave, keep="first"), dup


def ops_validas(ops: pd.DataFrame, ate: pd.Timestamp = FIM_HORIZONTE) -> tuple[pd.DataFrame, pd.DataFrame]:
    """OPs que chegam a tempo (conclusão ≤ fim do horizonte) e OPs tardias, que não contam como oferta."""
    ok = ops["Conclusão prevista"].notna() & (ops["Conclusão prevista"] <= ate)
    return ops[ok], ops[~ok]


def pedidos_em_risco(base: Base, carteira: pd.DataFrame | None = None) -> pd.DataFrame:
    """Pedido em risco: demanda acumulada até a data prometida supera estoque + OPs concluídas até essa data."""
    carteira = deduplicar_carteira(base["Carteira_Pedidos"])[0] if carteira is None else carteira
    ops = base["Ordens_Producao"]
    est = base["Estoque_Atual"].set_index("SKU")["Estoque atual"]
    pr = precos(base)
    linhas = []
    for sku, g in carteira.dropna(subset=["Data prometida"]).sort_values("Data prometida").groupby("SKU"):
        acumulado = 0
        for p in g.to_dict("records"):
            acumulado += p["Quantidade"]
            data = p["Data prometida"]
            disponivel = est.get(sku, 0) + ops[(ops["SKU"] == sku) & (ops["Conclusão prevista"] <= data)]["Quantidade"].sum()
            linhas.append({"pedido": p["Pedido"], "sku": sku, "cliente": p["Cliente/Canal"], "quantidade": p["Quantidade"],
                           "data_prometida": data, "acumulado": acumulado, "disponivel_na_data": disponivel,
                           "em_risco": acumulado > disponivel, "valor": p["Quantidade"] * pr.get(sku, np.nan)})
    return pd.DataFrame(linhas)


def capacidade_horizonte(base: Base, ate: pd.Timestamp = FIM_HORIZONTE) -> pd.Series:
    cap = base["Capacidade_Semanal"]
    janela = cap[(cap["Semana inicial"] >= DATA_REFERENCIA) & (cap["Semana inicial"] <= ate)]
    return janela.groupby("Família")["Capacidade disponível"].sum()


def calcular_decisoes(base: Base, previsao: pd.DataFrame, jornada: pd.DataFrame | None = None) -> pd.DataFrame:
    prod = base["Produtos"].set_index("SKU")
    est = base["Estoque_Atual"].set_index("SKU")
    lote = base["Lead_Times"].set_index("SKU")["Lote mínimo"]
    pr = precos(base)
    dem3 = demanda_recente(base["Vendas_24m"])
    carteira, _ = deduplicar_carteira(base["Carteira_Pedidos"])
    cart_sku = carteira.groupby("SKU")["Quantidade"].sum()
    ops_ok, ops_tardias = ops_validas(base["Ordens_Producao"])
    ops_todas = base["Ordens_Producao"].groupby("SKU")["Quantidade"].sum()
    risco = pedidos_em_risco(base, carteira)
    risco_sku = risco[risco["em_risco"]].groupby("sku").agg(
        pedidos_risco=("pedido", "count"), valor_risco=("valor", "sum"))

    prev_ok = previsao[previsao["status_previsao"] == "OK"]
    prev_out = prev_ok[pd.to_datetime(prev_ok["mes"]).dt.month == 10].groupby("sku")["previsao_unidades"].sum()
    prev_tri = prev_ok.groupby("sku")["previsao_unidades"].sum()
    insuf = previsao[previsao["status_previsao"] != "OK"].groupby("sku")["motivo_insuficiencia"].first()

    linhas = []
    for sku in prod.index:
        p = prod.loc[sku]
        d3 = float(dem3.get(sku, 0.0))
        estoque = int(est.loc[sku, "Estoque atual"]) if sku in est.index else 0
        seg_dias = int(est.loc[sku, "Estoque segurança dias"]) if sku in est.index else int(p["Estoque segurança (dias)"])
        carteira_q = int(cart_sku.get(sku, 0))
        ops_ate = int(ops_ok[ops_ok["SKU"] == sku]["Quantidade"].sum())
        ops_tard = int(ops_tardias[ops_tardias["SKU"] == sku]["Quantidade"].sum())
        ops_total = int(ops_todas.get(sku, 0))
        lt = int(lote.get(sku, p["Lote mínimo"]))
        preco = float(pr.get(sku, np.nan))

        prev_horizonte = float(prev_out.get(sku, np.nan)) + 0.5 * d3  # out (previsto) + 2ª quinzena de set (estimado)
        demanda_considerada = max(prev_horizonte, carteira_q) if not math.isnan(prev_horizonte) else carteira_q
        seguranca = seg_dias * d3 / 30
        oferta = estoque + ops_ate
        necessidade = demanda_considerada + seguranca - oferta
        producao = int(math.ceil(necessidade / lt) * lt) if necessidade > 0 else 0
        excesso_un = max(0.0, estoque + ops_total - carteira_q - COBERTURA_EXCESSO_DIAS * d3 / 30)
        maior_op = int(base["Ordens_Producao"][base["Ordens_Producao"]["SKU"] == sku]["Quantidade"].max()) if ops_total else 0
        meses_op = maior_op / d3 if d3 else np.inf
        n_risco = int(risco_sku["pedidos_risco"].get(sku, 0)) if not risco_sku.empty else 0
        v_risco = float(risco_sku["valor_risco"].get(sku, 0.0)) if not risco_sku.empty else 0.0
        falta_carteira = max(0, carteira_q - (estoque + ops_ate))

        evid = [
            ("Demanda prevista (out/26)", f"{fmt_int(prev_out.get(sku, float('nan')))} un.", PREVISTO, "Modelo sazonal família × nível SKU"),
            ("Demanda recente (média 3m)", f"{fmt_int(d3)} un./mês", OBSERVADO, "Vendas_24m"),
            ("Carteira firme", f"{fmt_int(carteira_q)} un.", OBSERVADO, "Carteira_Pedidos (deduplicada)"),
            ("Estoque atual", f"{fmt_int(estoque)} un.", OBSERVADO, "Estoque_Atual"),
            ("OPs que chegam até 31/10", f"{fmt_int(ops_ate)} un.", OBSERVADO, "Ordens_Producao"),
            ("Estoque de segurança", f"{fmt_int(seguranca)} un. ({seg_dias} dias)", CALCULADO, "Regra de segurança"),
            ("Necessidade líquida", f"{fmt_int(necessidade)} un.", CALCULADO, "Motor de decisão"),
            ("Lote mínimo", f"{fmt_int(lt)} un.", OBSERVADO, "Lead_Times"),
        ]
        if ops_tard:
            evid.append(("OPs tardias (não contam)", f"{fmt_int(ops_tard)} un.", OBSERVADO, "Conclusão após 31/10"))
        if n_risco:
            evid.append(("Pedidos em risco de atraso", f"{n_risco} pedido(s), R$ {fmt_int(v_risco)}", CALCULADO, "Carteira × disponibilidade na data"))

        motivo, acao = None, "—"
        if sku in insuf.index or math.isnan(prev_horizonte):
            rec, motivo = "Investigar", str(insuf.get(sku, "Previsão indisponível"))
            acao = "Validar o dado antes de decidir"
        elif p["Status"] != "Ativo":
            rec = "Reduzir/adiar OP" if ops_total else "Monitorar"
            motivo = f"SKU em descontinuação: não repor; {'rever OPs abertas' if ops_total else 'escoar estoque'}"
            acao = "Cancelar ou reduzir OPs abertas" if ops_total else "Escoar estoque com o Comercial"
        elif n_risco > 0:
            rec = "Priorizar produção"
            producao = max(producao, int(math.ceil(falta_carteira / lt) * lt))
            if falta_carteira > 0:
                motivo = f"{n_risco} pedido(s) da carteira sem cobertura: faltam {fmt_int(falta_carteira)} un."
                acao = f"Produzir {fmt_int(producao)} un. na frente da fila e negociar prazo com os clientes em risco"
            else:
                primeira = risco[(risco["sku"] == sku) & risco["em_risco"]]["data_prometida"].min()
                tardias = base["Ordens_Producao"][(base["Ordens_Producao"]["SKU"] == sku) & (base["Ordens_Producao"]["Conclusão prevista"] > primeira)]
                ops_txt = ", ".join(f"{o['Ordem']} ({o['Conclusão prevista']:%d/%m})" for o in tardias.to_dict("records"))
                motivo = f"{n_risco} pedido(s) em risco: a OP cobre o volume, mas conclui depois da data prometida ({primeira:%d/%m})"
                if primeira < DATA_REFERENCIA:
                    acao = f"Renegociar o prazo já vencido ({primeira:%d/%m}) e antecipar {ops_txt}"
                else:
                    acao = f"Antecipar {ops_txt} para antes de {primeira:%d/%m}"
        elif producao > 0:
            rec, motivo = "Produzir", f"Necessidade líquida de {fmt_int(necessidade)} un. no horizonte"
            acao = f"Abrir OP de {fmt_int(producao)} un. (lote mínimo {fmt_int(lt)})"
        elif maior_op and meses_op > OP_EXCESSIVA_MESES:
            rec, motivo = "Reduzir/adiar OP", f"Uma OP de {fmt_int(maior_op)} un. cobre {meses_op:.0f} meses de demanda recente ({d3:.0f} un./mês)"
            acao = f"Reduzir a OP para até {fmt_int(math.ceil(3 * d3 / lt) * lt)} un. ou adiar"
        elif excesso_un > 0:
            rec, motivo = "Monitorar", f"{fmt_int(excesso_un)} un. acima de {COBERTURA_EXCESSO_DIAS} dias de demanda"
            acao = "Não abrir novas OPs; acompanhar o giro semanalmente"
        else:
            rec, motivo = "Sem ação necessária", "Oferta cobre a demanda e a segurança no horizonte"
            acao = "Manter o plano atual"
        if rec not in ("Produzir", "Priorizar produção"):
            producao = 0

        linhas.append({
            "sku": sku, "produto": p["Produto"], "descricao": p["Descrição completa"], "familia": p["Família"],
            "curva_abc": p["Curva ABC"], "status_sku": p["Status"], "recomendacao": rec, "motivo": motivo, "acao": acao,
            "producao_sugerida": producao, "demanda_horizonte": round(demanda_considerada), "previsao_out": prev_out.get(sku, np.nan),
            "previsao_trimestre": prev_tri.get(sku, np.nan), "demanda_3m": round(d3, 1), "carteira": carteira_q,
            "estoque": estoque, "ops_no_prazo": ops_ate, "ops_tardias": ops_tard, "ops_total": ops_total,
            "seguranca": round(seguranca), "necessidade_liquida": round(necessidade), "lote_minimo": lt,
            "excesso_un": round(excesso_un), "excesso_valor": round(excesso_un * preco), "maior_op": maior_op,
            "meses_cobertos_maior_op": round(meses_op, 1) if np.isfinite(meses_op) else None,
            "pedidos_risco": n_risco, "valor_risco": round(v_risco), "preco": preco,
            "evidencias": evid, "status_decisao": "Aguardando aprovação",
        })

    for l in base["Lancamentos"].to_dict("records"):
        linhas.append({
            "sku": l["SKU"], "produto": l["Produto"], "descricao": f"{l['Produto']} (lançamento)", "familia": l["Família"], "curva_abc": "—",
            "status_sku": "Lançamento", "recomendacao": "Investigar", "acao": "Definir SKU análogo ou meta comercial aprovada",
            "motivo": "SKU sem histórico de vendas: o modelo não inventa previsão. Aprovar um SKU análogo ou meta comercial antes de produzir.",
            "producao_sugerida": 0, "demanda_horizonte": np.nan, "previsao_out": np.nan, "previsao_trimestre": np.nan,
            "demanda_3m": np.nan, "carteira": 0, "estoque": 0, "ops_no_prazo": 0, "ops_tardias": 0, "ops_total": 0,
            "seguranca": np.nan, "necessidade_liquida": np.nan, "lote_minimo": int(l["Lote mínimo"]), "excesso_un": 0, "excesso_valor": 0,
            "maior_op": 0, "meses_cobertos_maior_op": None, "pedidos_risco": 0, "valor_risco": 0, "preco": np.nan,
            "evidencias": [("Histórico de vendas", "nenhum", INDISPONIVEL, "Vendas_24m"),
                           ("Lançamento", str(l["Lançamento"]), OBSERVADO, "Calendario_Eventos / cadastro de lançamento")],
            "status_decisao": "Aguardando aprovação",
        })

    df = pd.DataFrame(linhas)
    df = _aplicar_capacidade(df, capacidade_horizonte(base))
    df = _comercial(df, jornada)
    df["confianca"] = df.apply(_confianca, axis=1)
    df["ordem"] = df["recomendacao"].map(ORDEM_PRIORIDADE)
    df["score"] = df["valor_risco"].fillna(0) + df["producao_sugerida"] * df["preco"].fillna(0) + df["excesso_valor"].fillna(0) * 0.5
    return df.sort_values(["ordem", "score"], ascending=[True, False]).drop(columns="ordem").reset_index(drop=True)


def _aplicar_capacidade(df: pd.DataFrame, cap: pd.Series) -> pd.DataFrame:
    df = df.copy()
    df["capacidade_familia"] = df["familia"].map(cap).fillna(0)
    df["producao_executavel"] = 0
    df["deficit_capacidade"] = 0
    ordem = df.assign(_o=df["recomendacao"].map(ORDEM_PRIORIDADE)).sort_values(["_o", "valor_risco"], ascending=[True, False])
    saldo = cap.to_dict()
    for i, r in ordem.iterrows():
        q = int(r["producao_sugerida"] or 0)
        if q <= 0:
            continue
        livre = max(0, int(saldo.get(r["familia"], 0)))
        exe = min(q, livre)
        saldo[r["familia"]] = livre - exe
        df.at[i, "producao_executavel"] = exe
        df.at[i, "deficit_capacidade"] = q - exe
    return df


def _comercial(df: pd.DataFrame, jornada: pd.DataFrame | None) -> pd.DataFrame:
    df = df.copy()
    df["recomendacao_comercial"] = "—"
    if jornada is None:
        return df
    for i, r in df.iterrows():
        j = jornada[jornada["sku"] == r["sku"]]
        if j.empty:
            continue
        if r["recomendacao"] == "Priorizar produção":
            top = j[j["tem_sell_out"]].sort_values("giro_mensal", ascending=False)
            if not top.empty:
                t = top.iloc[0]
                df.at[i, "recomendacao_comercial"] = f"Priorizar parceiro {t['parceiro']} (maior giro observado: {t['giro_mensal']:.0f} un./mês)"
            else:
                df.at[i, "recomendacao_comercial"] = "Negociar prazo com os clientes em risco"
        elif (j["recomendacao"] == "Monitorar").any() and r["recomendacao"] in ("Sem ação necessária", "Monitorar", "Reduzir/adiar OP"):
            acum = j[j["recomendacao"] == "Monitorar"]["parceiro"].tolist()
            df.at[i, "recomendacao_comercial"] = f"Segurar reposição em {', '.join(acum)} (acúmulo no parceiro)"
        elif (j["recomendacao"] == "Repor").any():
            rep = j[j["recomendacao"] == "Repor"]["parceiro"].tolist()
            df.at[i, "recomendacao_comercial"] = f"Repor {', '.join(rep)}: giro acima do abastecimento"
        elif (j["tendencia_diretos_pct"] >= 10).any() and r["excesso_un"] == 0 and r["recomendacao"] != "Investigar":
            df.at[i, "recomendacao_comercial"] = "Ampliar mix nos parceiros: demanda em alta nos canais diretos"
        elif ((j["cobertura_parceiro_meses"] > 1) & (j["cobertura_parceiro_meses"] <= 1.5)).any():
            alvo = j[(j["cobertura_parceiro_meses"] > 1) & (j["cobertura_parceiro_meses"] <= 1.5)]["parceiro"].tolist()
            df.at[i, "recomendacao_comercial"] = f"Recomendar recompra a {', '.join(alvo)} (estoque na loja para ~1 mês)"
    return df


def _confianca(r: pd.Series) -> str:
    if r["recomendacao"] == "Investigar":
        return "Baixa"
    naturezas = [e[2] for e in r["evidencias"]]
    if INDISPONIVEL in naturezas or ESTIMADO in naturezas:
        return "Média"
    return "Alta" if r["familia"] != "Executivo" else "Média (família com viés alto: revisão humana)"


def excesso_resumo(base: Base, dias: int = COBERTURA_EXCESSO_DIAS) -> dict[str, float]:
    """Valor (preço de tabela) acima de N dias de demanda recente: hoje e se as OPs abertas forem executadas."""
    est = base["Estoque_Atual"].set_index("SKU")["Estoque atual"]
    ops = base["Ordens_Producao"].groupby("SKU")["Quantidade"].sum().reindex(est.index, fill_value=0)
    diario = demanda_recente(base["Vendas_24m"]).reindex(est.index, fill_value=0) / 30
    pr = precos(base).reindex(est.index)
    atual = float(((est - diario * dias).clip(lower=0) * pr).sum())
    com_ops = float(((est + ops - diario * dias).clip(lower=0) * pr).sum())
    return {"atual": atual, "com_ops": com_ops}
