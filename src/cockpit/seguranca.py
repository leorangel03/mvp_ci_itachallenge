"""Verificações de comportamento seguro: cada caso injeta um problema numa cópia da base e confere a saída."""
from __future__ import annotations

import copy
import tempfile
from pathlib import Path

import pandas as pd

from . import decisoes, jornada, motor
from .dados import ESTIMADO, INDISPONIVEL, Base


def _copia(base: Base) -> Base:
    return Base({k: v.copy() for k, v in base.tabelas.items()}, list(base.alertas))


def _caso(nome, entrada, esperado, observado, passou):
    return {"verificacao": nome, "entrada": entrada, "esperado": esperado, "observado": observado, "passou": bool(passou)}


def executar(base: Base, previsao: pd.DataFrame) -> pd.DataFrame:
    casos = []

    # 1. Sell-out ausente nunca vira zero
    jp = jornada.jornada_parceiros(base)
    cego = jp[~jp["tem_sell_out"]].iloc[0]
    casos.append(_caso(
        "Sell-out ausente → indisponível, nunca zero",
        f"{cego['parceiro']} × {cego['sku']}: parceiro não envia sell-out",
        "Sell-out vazio (não 0), natureza Indisponível/Estimado, recomendação Investigar",
        f"sell-out={cego['sell_out_12m']}, natureza={cego['natureza']}, recomendação={cego['recomendacao']}",
        pd.isna(cego["sell_out_12m"]) and cego["natureza"] in (INDISPONIVEL, ESTIMADO) and cego["recomendacao"] == "Investigar"))

    # 2. SKU sem histórico → Investigar
    dec = motor.calcular_decisoes(base, previsao, jp)
    novo = dec[dec["status_sku"] == "Lançamento"].iloc[0]
    casos.append(_caso(
        "SKU sem histórico → Investigar",
        f"{novo['sku']} ({novo['produto']}), lançamento sem vendas",
        "Sem previsão inventada; produção 0; recomendação Investigar",
        f"previsão={novo['previsao_out']}, produção={novo['producao_sugerida']}, recomendação={novo['recomendacao']}",
        pd.isna(novo["previsao_out"]) and novo["producao_sugerida"] == 0 and novo["recomendacao"] == "Investigar"))

    # 3. Pedido duplicado → bloqueado
    b3 = _copia(base)
    cart = b3["Carteira_Pedidos"]
    b3.tabelas["Carteira_Pedidos"] = pd.concat([cart, cart[cart["Pedido"] == "PED-004-1"]], ignore_index=True)
    limpa, dup = motor.deduplicar_carteira(b3["Carteira_Pedidos"])
    d3 = motor.calcular_decisoes(b3, previsao, jp)
    q = int(d3.loc[d3["sku"] == "CI-0004", "carteira"].iloc[0])
    casos.append(_caso(
        "Pedido duplicado → bloqueado",
        "PED-004-1 (487 un.) inserido duas vezes na carteira",
        "1 duplicata detectada; carteira do CI-0004 continua 866 un.",
        f"duplicatas={len(dup)}, carteira CI-0004={q}",
        len(dup) == 1 and q == 866))

    # 4. OP tardia não conta como oferta
    b4 = _copia(base)
    ops = b4["Ordens_Producao"]
    nova = pd.DataFrame([{"Ordem": "OP-TESTE", "SKU": "CI-0004", "Quantidade": 1000, "Início previsto": pd.Timestamp("2026-11-10"),
                          "Conclusão prevista": pd.Timestamp("2026-11-30"), "Status": "Planejada"}])
    b4.tabelas["Ordens_Producao"] = pd.concat([ops, nova], ignore_index=True)
    r4 = motor.calcular_decisoes(b4, previsao, jp).set_index("sku").loc["CI-0004"]
    casos.append(_caso(
        "OP que chega tarde → não conta",
        "OP de 1.000 un. do CI-0004 com conclusão em 30/11 (após o horizonte)",
        "OP fora da oferta; continua 'Priorizar produção'",
        f"OPs no prazo={r4['ops_no_prazo']}, OPs tardias={r4['ops_tardias']}, recomendação={r4['recomendacao']}",
        r4["ops_no_prazo"] == 0 and r4["ops_tardias"] == 1000 and r4["recomendacao"] == "Priorizar produção"))

    # 5. Capacidade estourada → gap explícito
    b5 = _copia(base)
    cap = b5["Capacidade_Semanal"]
    cap.loc[cap["Família"] == "Planner", "Capacidade disponível"] = 100
    r5 = motor.calcular_decisoes(b5, previsao, jp).set_index("sku").loc["CI-0004"]
    casos.append(_caso(
        "Capacidade estourada → gap explícito",
        "Capacidade da linha Planner reduzida a 100 un./semana",
        "Plano não excede a capacidade; déficit aparece na tela",
        f"sugerido={r5['producao_sugerida']}, executável={r5['producao_executavel']}, déficit={r5['deficit_capacidade']}",
        r5["producao_executavel"] <= 700 and r5["deficit_capacidade"] > 0
        and r5["producao_executavel"] + r5["deficit_capacidade"] == r5["producao_sugerida"]))

    # 6. Nenhuma OP sem aprovação humana
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "log.csv"
        bloqueou = False
        try:
            decisoes.registrar_decisao("CI-0004", "Priorizar produção", 1000, "Ajustar", 800, "PCP", "", path=log_path)
        except ValueError:
            bloqueou = True
        decisoes.registrar_decisao("CI-0004", "Priorizar produção", 1000, "Ajustar", 800, "PCP", "Lote extra na sexta", path=log_path)
        log = decisoes.carregar_log(log_path)
    pendentes = (dec["status_decisao"] == "Aguardando aprovação").all()
    casos.append(_caso(
        "Nenhuma OP sem aprovação humana",
        "Recomendações geradas + tentativa de ajuste sem motivo",
        "Todas aguardam aprovação; ajuste sem motivo é recusado; com motivo é registrado",
        f"aguardando={pendentes}, ajuste sem motivo recusado={bloqueou}, registros no log={len(log)}",
        pendentes and bloqueou and len(log) == 1))

    return pd.DataFrame(casos)
