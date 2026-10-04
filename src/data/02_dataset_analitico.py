from __future__ import annotations

from pathlib import Path

import pandas as pd


class DatasetAnalitico:
    """
    Fase 2 do MVP Caderno Inteligente.

    Objetivo:
    - construir uma tabela analítica por SKU x período;
    - integrar demanda, estoque, pedidos, produção, capacidade e lead time;
    - validar cardinalidade e baixe rasas de relacionamento;
    - preparar dataset para feature engineering e modelagem.
    """

    def __init__(self, root_dir: str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self.processed_dir = self.root / "data" / "processed"
        self.output_path = self.processed_dir / "dataset_analitico.csv"

    def _read_processed(self, name: str) -> pd.DataFrame:
        path = self.processed_dir / f"{name}_processado.csv"
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        return pd.read_csv(path)

    def _safe_to_datetime(self, series: pd.Series) -> pd.Series:
        return pd.to_datetime(series, errors="coerce")

    def _choose_column(self, df: pd.DataFrame, candidates: list[str]) -> str | None:
        for candidate in candidates:
            if candidate in df.columns:
                return candidate
        return None

    def build(self) -> pd.DataFrame:
        produtos = self._read_processed("Produtos")
        vendas = self._read_processed("Vendas_24m")
        forecast = self._read_processed("Forecast_Comercial")
        estoque_atual = self._read_processed("Estoque_Atual")
        historico_estoque = self._read_processed("Historico_Estoque")
        pedidos = self._read_processed("Carteira_Pedidos")
        ordens = self._read_processed("Ordens_Producao")
        lead = self._read_processed("Lead_Times")

        # Normalização inicial de colunas principais
        produtos = produtos.copy()
        produtos["sku"] = produtos.get("sku", produtos.get("SKU", produtos.iloc[:, 0]))
        produtos["familia"] = produtos.get("familia", produtos.get("Família"))

        vendas = vendas.copy()
        vendas["sku"] = vendas.get("sku", vendas.get("SKU"))
        vendas["mes"] = self._safe_to_datetime(vendas.get("mes", vendas.get("Mês")))
        vendas["quantidade_faturada"] = pd.to_numeric(vendas.get("quantidade_faturada", vendas.get("Quantidade faturada")), errors="coerce")
        vendas["valor_faturado_r"] = pd.to_numeric(vendas.get("valor_faturado_r", vendas.get("Valor faturado (R$)")), errors="coerce")

        forecast = forecast.copy()
        forecast["sku"] = forecast.get("sku", forecast.get("SKU"))
        forecast["mes"] = self._safe_to_datetime(forecast.get("mes", forecast.get("Mês")))
        forecast["previsao_unidades"] = pd.to_numeric(forecast.get("previsao_unidades", forecast.get("Previsão unidades")), errors="coerce")

        estoque_atual = estoque_atual.copy()
        estoque_atual["sku"] = estoque_atual.get("sku", estoque_atual.get("SKU"))
        estoque_atual["estoque_atual"] = pd.to_numeric(estoque_atual.get("estoque_atual", estoque_atual.get("Estoque atual")), errors="coerce")
        estoque_atual["cobertura_dias"] = pd.to_numeric(estoque_atual.get("cobertura_dias", estoque_atual.get("Cobertura dias")), errors="coerce")
        estoque_atual["estoque_segurança_dias"] = pd.to_numeric(estoque_atual.get("estoque_segurança_dias", estoque_atual.get("Estoque segurança dias")), errors="coerce")
        estoque_atual["demanda_media_mensal"] = pd.to_numeric(estoque_atual.get("demanda_media_mensal", estoque_atual.get("Demanda média mensal")), errors="coerce")

        historico_estoque = historico_estoque.copy()
        historico_estoque["sku"] = historico_estoque.get("sku", historico_estoque.get("SKU"))
        historico_estoque["mes"] = self._safe_to_datetime(historico_estoque.get("mes", historico_estoque.get("Mês")))
        historico_estoque["estoque_fechamento"] = pd.to_numeric(historico_estoque.get("estoque_fechamento", historico_estoque.get("Estoque fechamento")), errors="coerce")

        pedidos = pedidos.copy()
        pedidos["sku"] = pedidos.get("sku", pedidos.get("SKU"))
        pedidos["mes"] = self._safe_to_datetime(pedidos.get("data_prometida", pedidos.get("Data prometida")))
        pedidos["quantidade"] = pd.to_numeric(pedidos.get("quantidade", pedidos.get("Quantidade")), errors="coerce")

        ordens = ordens.copy()
        ordens["sku"] = ordens.get("sku", ordens.get("SKU"))
        ordens["quantidade"] = pd.to_numeric(ordens.get("quantidade", ordens.get("Quantidade")), errors="coerce")
        ordens["inicio_previsto"] = self._safe_to_datetime(ordens.get("inicio_previsto", ordens.get("Início previsto")))
        ordens["conclusao_prevista"] = self._safe_to_datetime(ordens.get("conclusao_prevista", ordens.get("Conclusão prevista")))

        lead = lead.copy()
        lead["sku"] = lead.get("sku", lead.get("SKU"))
        lead["lead_time_dias"] = pd.to_numeric(lead.get("lead_time_dias", lead.get("Lead time dias")), errors="coerce")
        lead["familia"] = lead.get("familia", lead.get("Família"))

        # Agregação mensal de demanda
        vendas_month = (
            vendas.groupby(["sku", pd.Grouper(key="mes", freq="M")], as_index=False)
            .agg(
                quantidade_faturada=("quantidade_faturada", "sum"),
                valor_faturado_r=("valor_faturado_r", "sum"),
            )
        )
        vendas_month["mes"] = pd.to_datetime(vendas_month["mes"])

        forecast_month = (
            forecast.groupby(["sku", pd.Grouper(key="mes", freq="M")], as_index=False)
            .agg(previsao_unidades=("previsao_unidades", "sum"))
        )
        forecast_month["mes"] = pd.to_datetime(forecast_month["mes"])

        pedidos_month = (
            pedidos.groupby(["sku", pd.Grouper(key="mes", freq="M")], as_index=False)
            .agg(quantidade_pedidos=("quantidade", "sum"))
        )
        pedidos_month["mes"] = pd.to_datetime(pedidos_month["mes"])

        ordens_month = (
            ordens.groupby(["sku", pd.Grouper(key="inicio_previsto", freq="M")], as_index=False)
            .agg(quantidade_ordens=("quantidade", "sum"))
        )
        ordens_month = ordens_month.rename(columns={"inicio_previsto": "mes"})
        ordens_month["mes"] = pd.to_datetime(ordens_month["mes"])

        # histórico de estoque mensal por sku
        historico_month = (
            historico_estoque.groupby(["sku", pd.Grouper(key="mes", freq="M")], as_index=False)
            .agg(estoque_fechamento=("estoque_fechamento", "mean"))
        )
        historico_month["mes"] = pd.to_datetime(historico_month["mes"])

        # montar base por SKU x mês
        dataset = vendas_month.merge(forecast_month, on=["sku", "mes"], how="outer")
        dataset = dataset.merge(pedidos_month, on=["sku", "mes"], how="left")
        dataset = dataset.merge(ordens_month, on=["sku", "mes"], how="left")
        dataset = dataset.merge(historico_month, on=["sku", "mes"], how="left")

        # Dados de produto
        produto_key = produtos[["sku", "familia", "lead_time_dias", "lote_minimo", "estoque_segurança_dias"]].copy()
        dataset = dataset.merge(produto_key, on="sku", how="left")

        # Dados de estoque atual por SKU
        estoque_key = estoque_atual[[
            "sku",
            "estoque_atual",
            "cobertura_dias",
            "estoque_segurança_dias",
            "demanda_media_mensal",
        ]].copy()
        dataset = dataset.merge(estoque_key, on="sku", how="left")

        # Dados de lead time por SKU (se existir em arquivo de lead)
        lead_key = lead[["sku", "lead_time_dias"]].copy()
        dataset = dataset.merge(lead_key, on="sku", how="left", suffixes=("_prod", "_lead"))

        # Normalização de nomes finais
        dataset["mes"] = pd.to_datetime(dataset["mes"])
        dataset = dataset.sort_values(["sku", "mes"]).reset_index(drop=True)

        # Features centrais de risco e planejamento
        dataset["demanda_prevista"] = dataset["previsao_unidades"].fillna(dataset["quantidade_faturada"])
        dataset["estoque_projetado"] = (
            dataset["estoque_atual"].fillna(dataset["estoque_fechamento"]).fillna(0)
            + dataset["quantidade_ordens"].fillna(0)
            - dataset["demanda_prevista"].fillna(0)
        )
        dataset["cobertura_estimativa_dias"] = (
            dataset["estoque_projetado"].fillna(0) / dataset["demanda_media_mensal"].replace(0, pd.NA)
        ) * 30

        dataset["pressao_demanda"] = dataset["demanda_prevista"].fillna(0) / dataset["estoque_atual"].replace(0, pd.NA)
        dataset["pressao_pedidos"] = dataset["quantidade_pedidos"].fillna(0) / dataset["demanda_prevista"].replace(0, pd.NA)

        dataset["risco_ruptura_hipotese"] = (dataset["estoque_projetado"] < 0).astype(int)
        dataset["risco_excesso_hipotese"] = (dataset["estoque_projetado"] > dataset["demanda_media_mensal"].fillna(0) * 3).astype(int)

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        dataset.to_csv(self.output_path, index=False)
        return dataset


if __name__ == "__main__":
    dataset = DatasetAnalitico()
    df = dataset.build()
    print(df.head())
    print(f"Dataset analítico gerado: {df.shape[0]} linhas | {df.shape[1]} colunas")
