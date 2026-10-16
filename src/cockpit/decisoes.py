"""Camada 5 (Decisão humana e retroalimentação): registro versionado de cada decisão."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .dados import ROOT

LOG_PATH = ROOT / "data" / "decisoes" / "log_decisoes.csv"
VERSAO_MODELO = "sazonal_familia_nivel_sku_v1 + motor_regras_v2"
DECISOES = ("Aprovar", "Ajustar", "Rejeitar")
COLUNAS = ["registrado_em", "responsavel", "sku", "recomendacao_original", "quantidade_sugerida", "decisao",
           "quantidade_aprovada", "motivo", "versao_modelo"]


def carregar_log(path: Path = LOG_PATH) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=COLUNAS)


def registrar_decisao(sku: str, recomendacao: str, quantidade_sugerida: int, decisao: str, quantidade_aprovada: int,
                      responsavel: str, motivo: str, path: Path = LOG_PATH) -> pd.DataFrame:
    """Grava a decisão. Ajuste e rejeição exigem motivo; toda decisão exige responsável."""
    if decisao not in DECISOES:
        raise ValueError(f"Decisão inválida: {decisao}")
    if not responsavel.strip():
        raise ValueError("Informe o responsável pela decisão.")
    if decisao in ("Ajustar", "Rejeitar") and not motivo.strip():
        raise ValueError("Ajuste e rejeição exigem motivo registrado.")
    if decisao == "Aprovar":
        quantidade_aprovada = quantidade_sugerida
    if decisao == "Rejeitar":
        quantidade_aprovada = 0
    linha = pd.DataFrame([{
        "registrado_em": datetime.now().strftime("%Y-%m-%d %H:%M"), "responsavel": responsavel.strip(), "sku": sku,
        "recomendacao_original": recomendacao, "quantidade_sugerida": int(quantidade_sugerida), "decisao": decisao,
        "quantidade_aprovada": int(quantidade_aprovada), "motivo": motivo.strip(), "versao_modelo": VERSAO_MODELO,
    }])
    path.parent.mkdir(parents=True, exist_ok=True)
    log = pd.concat([carregar_log(path), linha], ignore_index=True)
    log.to_csv(path, index=False)
    return log


def resumo_retroalimentacao(log: pd.DataFrame) -> dict:
    """Indicadores do laço humano: taxa de aceite e volume ajustado (insumo do FVA quando houver realizado)."""
    if log.empty:
        return {"decisoes": 0, "aceite_pct": None, "ajustes": 0, "delta_unidades": 0}
    return {
        "decisoes": len(log),
        "aceite_pct": round((log["decisao"] == "Aprovar").mean() * 100, 1),
        "ajustes": int((log["decisao"] == "Ajustar").sum()),
        "delta_unidades": int((log["quantidade_aprovada"] - log["quantidade_sugerida"]).sum()),
    }
