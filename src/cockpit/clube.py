"""Clube CI: captura de compra verificada por nota fiscal (fecha o ponto cego) e modelo econômico do ecossistema."""
from __future__ import annotations

import random
from dataclasses import dataclass

import pandas as pd

from .dados import DECLARADO, VERIFICADO

# CNPJs fictícios dos parceiros, criados para a simulação (a base do desafio não traz CNPJ)
CNPJ_PARCEIROS = {
    "11222333000181": "KA-01", "22333444000172": "KA-02", "33444555000163": "KA-03",
    "44555666000154": "KA-04", "55666777000145": "KA-05",
}


def dv_chave(chave43: str) -> int:
    """Dígito verificador da chave de acesso da NF-e (módulo 11, pesos 2 a 9 da direita para a esquerda)."""
    soma, peso = 0, 2
    for d in reversed(chave43):
        soma += int(d) * peso
        peso = 2 if peso == 9 else peso + 1
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def gerar_chave_exemplo(cnpj: str, aamm: str = "2610", uf: str = "41") -> str:
    corpo = f"{uf}{aamm}{cnpj}65001{random.randint(0, 999999999):09d}1{random.randint(0, 99999999):08d}"
    return corpo + str(dv_chave(corpo))


@dataclass
class CompraCapturada:
    valida: bool
    natureza: str
    parceiro: str | None
    mensagem: str


def validar_compra(chave: str, sku: str, chaves_ja_usadas: set[str]) -> CompraCapturada:
    """Valida a NF informada pelo consumidor. Sem NF válida, a compra entra como Declarada (peso baixo)."""
    chave = "".join(c for c in (chave or "") if c.isdigit())
    if not chave:
        return CompraCapturada(True, DECLARADO, None, "Sem nota fiscal: compra registrada como declarada (sinal de peso baixo).")
    if len(chave) != 44:
        return CompraCapturada(False, DECLARADO, None, "Chave inválida: a chave de acesso tem 44 dígitos.")
    if dv_chave(chave[:43]) != int(chave[43]):
        return CompraCapturada(False, DECLARADO, None, "Chave inválida: dígito verificador não confere.")
    if chave in chaves_ja_usadas:
        return CompraCapturada(False, DECLARADO, None, "Nota já utilizada: crédito e registro bloqueados (antifraude).")
    cnpj = chave[6:20]
    parceiro = CNPJ_PARCEIROS.get(cnpj)
    if parceiro is None:
        return CompraCapturada(True, VERIFICADO, None, f"NF válida de loja não cadastrada (CNPJ {cnpj}): entra como novo ponto de venda.")
    return CompraCapturada(True, VERIFICADO, parceiro, f"NF válida: compra de {sku} verificada em {parceiro}. Crédito de boas-vindas liberado.")


# --------------------------------------------------------------------------------------
# Modelo econômico (mesmo de Proposta/modelo/modelo_ecossistema.py), parametrizável na tela
# --------------------------------------------------------------------------------------
UN_ANO = 328_111
UN_DIRETO_MES = UN_ANO * 0.682 / 12
UN_KA_MES = UN_ANO * 0.318 / 12
COMPRADORES_DIRETO_MES = UN_DIRETO_MES / 2.0 * 0.7

CENARIOS = {
    "Conservador": dict(optin=0.15, scan=0.03, premium=0.03, drop_buy=0.010, refil_lift=0.15, comissao=0.10, midia=0.5, dados=0.5, mkt=0.0),
    "Base": dict(optin=0.25, scan=0.05, premium=0.05, drop_buy=0.020, refil_lift=0.25, comissao=0.20, midia=1.0, dados=1.0, mkt=1.0),
    "Otimista": dict(optin=0.35, scan=0.08, premium=0.08, drop_buy=0.030, refil_lift=0.45, comissao=0.30, midia=1.5, dados=1.5, mkt=1.5),
}


def simular(p: dict, meses: int = 36) -> pd.DataFrame:
    ativos, acum, linhas = 0.0, 0.0, []
    for m in range(1, meses + 1):
        novos = COMPRADORES_DIRETO_MES * p["optin"] + UN_KA_MES * min(1.0, m / 6) * p["scan"] / 1.2
        ativos = ativos * 0.98 + novos
        receita = (ativos * p["premium"] * 9.80 + ativos * p["comissao"] + ativos * p["drop_buy"] * 2 / 12 * 150 * 0.45
                   + ativos * p["refil_lift"] * 55 * 0.35 / 12
                   + (0 if m <= 3 else 2000 if m <= 12 else 4000 if m <= 24 else 5000) * p["midia"])
        economia = (1500 * p["dados"] + 1750 * p["mkt"]) * (m > 6)
        custos = (max(2000.0, 0.20 * ativos) + {1: 13000.0, 2: 10000.0}.get(m, 0.0) + novos * 1.20 + ativos * 1.06 / 12
                  + (0 if m <= 12 else 1000) + (3000 if m <= 12 else 6000 if m <= 24 else 11000) + 2100
                  + 13000 / 12 * (m > 3) + 2000 / 12)
        cockpit = (0 if m <= 3 else 112000 / 12 * min(1.0, (m - 3) / 6)) - (0 if m <= 3 else 5000)
        acum += receita + economia - custos + cockpit
        linhas.append({"mes": m, "membros_ativos": ativos, "premium": ativos * p["premium"], "receita_clube": receita,
                       "economia": economia, "custos_clube": custos, "cockpit_liquido": cockpit, "acumulado": acum})
    return pd.DataFrame(linhas)


def payback(df: pd.DataFrame) -> int | None:
    pos = df[(df["acumulado"] >= 0) & (df["mes"] > 2)]
    return int(pos["mes"].iloc[0]) if not pos.empty else None
