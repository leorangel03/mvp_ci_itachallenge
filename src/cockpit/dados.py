"""Camada 1 (Sinais): carga das fontes do desafio com contrato mínimo e natureza do dado."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

DATA_REFERENCIA = pd.Timestamp("2026-09-14")  # posição de set/2026 (primeira semana de capacidade)
FIM_HORIZONTE = pd.Timestamp("2026-10-31")     # decisão das próximas semanas: até o fim de outubro

# Natureza do dado (taxonomia da Semana 1, estendida pelo Clube)
OBSERVADO = "Observado"
VERIFICADO = "Verificado pelo consumidor"
DECLARADO = "Declarado pelo consumidor"
CALCULADO = "Calculado"
ESTIMADO = "Estimado"
PREVISTO = "Previsto"
INDISPONIVEL = "Indisponível"

CONTRATOS = {
    "Produtos": ["SKU", "Produto", "Família", "Curva ABC", "Status", "Lote mínimo", "Estoque segurança (dias)", "Descrição completa"],
    "Vendas_24m": ["Mês", "SKU", "Cliente/Canal", "Quantidade faturada", "Valor faturado (R$)"],
    "Estoque_Atual": ["SKU", "Estoque atual", "Estoque segurança dias", "Demanda média mensal"],
    "Carteira_Pedidos": ["Pedido", "SKU", "Cliente/Canal", "Quantidade", "Data prometida", "Status"],
    "Ordens_Producao": ["Ordem", "SKU", "Quantidade", "Início previsto", "Conclusão prevista", "Status"],
    "Capacidade_Semanal": ["Semana inicial", "Família", "Capacidade máxima", "Capacidade disponível"],
    "Lead_Times": ["SKU", "Lead time dias", "Lote mínimo"],
    "Sell_In": ["Mês", "Cliente", "SKU", "Quantidade enviada"],
    "Sell_Out": ["Mês", "Cliente", "SKU", "Quantidade vendida", "Estoque estimado cliente", "Natureza do dado"],
    "Precos_Produtos": ["SKU", "Preço unitário (R$)"],
    "Parceiros_Canais": ["Código", "Nome fictício", "Tipo", "Região", "UF"],
    "Calendario_Eventos": ["Evento", "Início", "Fim", "Famílias impactadas", "Impacto esperado"],
    "Indicadores_Atuais": ["Indicador", "Valor fictício atual", "Meta fictícia"],
    "Forecast_Comercial": ["SKU", "Mês", "Previsão unidades", "Origem previsão"],
}


@dataclass
class Base:
    tabelas: dict[str, pd.DataFrame]
    alertas: list[str] = field(default_factory=list)

    def __getitem__(self, nome: str) -> pd.DataFrame:
        return self.tabelas[nome]


def ler_fonte(nome: str, pasta: Path = RAW) -> pd.DataFrame:
    """Lê um CSV do desafio (duas linhas de título antes do cabeçalho) e valida o contrato."""
    df = pd.read_csv(pasta / f"{nome}.csv", header=2)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    faltando = [c for c in CONTRATOS.get(nome, []) if c not in df.columns]
    if faltando:
        raise ValueError(f"{nome}: colunas obrigatórias ausentes {faltando}")
    return df


def carregar_base(pasta: Path = RAW) -> Base:
    t = {nome: ler_fonte(nome, pasta) for nome in CONTRATOS}
    alertas: list[str] = []

    t["Carteira_Pedidos"]["Data prometida"] = pd.to_datetime(t["Carteira_Pedidos"]["Data prometida"], dayfirst=True, errors="coerce")
    t["Ordens_Producao"]["Conclusão prevista"] = pd.to_datetime(t["Ordens_Producao"]["Conclusão prevista"], dayfirst=True, errors="coerce")
    t["Ordens_Producao"]["Início previsto"] = pd.to_datetime(t["Ordens_Producao"]["Início previsto"], dayfirst=True, errors="coerce")
    t["Capacidade_Semanal"]["Semana inicial"] = pd.to_datetime(t["Capacidade_Semanal"]["Semana inicial"], errors="coerce")
    for nome, col in [("Carteira_Pedidos", "Data prometida"), ("Ordens_Producao", "Conclusão prevista")]:
        invalidas = int(t[nome][col].isna().sum())
        if invalidas:
            alertas.append(f"{nome}: {invalidas} data(s) inválida(s) em '{col}'; registros bloqueados no cálculo.")

    lanc = pasta / "Lancamentos_Colecao_Primavera.csv"
    t["Lancamentos"] = pd.read_csv(lanc) if lanc.exists() else pd.DataFrame(columns=["SKU", "Produto", "Família", "Lote mínimo", "Lançamento"])
    return Base(t, alertas)


def demanda_recente(vendas: pd.DataFrame, meses: int = 3) -> pd.Series:
    """Média mensal das vendas faturadas nos últimos N meses (todas as origens), por SKU."""
    ultimos = sorted(vendas["Mês"].unique())[-meses:]
    return vendas[vendas["Mês"].isin(ultimos)].groupby("SKU")["Quantidade faturada"].sum() / meses


def precos(base: Base) -> pd.Series:
    return base["Precos_Produtos"].set_index("SKU")["Preço unitário (R$)"]


def fmt_brl(v: float, casas: int = 0) -> str:
    s = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def fmt_int(v: float) -> str:
    if v is None or (isinstance(v, float) and v != v):
        return "—"
    return f"{v:,.0f}".replace(",", ".")
