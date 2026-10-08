from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


class FeatureEngineering:
    """
    Fase 3 do MVP Caderno Inteligente.

    Gera features operacionais explicáveis para apoio à decisão.
    """

    def __init__(self, root_dir: str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self.processed_dir = self.root / "data" / "processed"
        self.input_path = self.processed_dir / "dataset_analitico.csv"
        self.output_path = self.processed_dir / "features.csv"

    def load_dataset(self) -> pd.DataFrame:
        if not self.input_path.exists():
            raise FileNotFoundError(f"Dataset analítico não encontrado: {self.input_path}")
        return pd.read_csv(self.input_path, parse_dates=["mes"])

    def build(self) -> pd.DataFrame:
        df = self.load_dataset().copy()
        df = df.sort_values(["sku", "mes"]).reset_index(drop=True)

        df["demanda_media_3m"] = (
            df.groupby("sku")["quantidade_faturada"]
            .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
        )

        df["demanda_media_6m"] = (
            df.groupby("sku")["quantidade_faturada"]
            .transform(lambda s: s.shift(1).rolling(6, min_periods=1).mean())
        )

        df["desvio_demanda_6m"] = (
            df.groupby("sku")["quantidade_faturada"]
            .transform(lambda s: s.shift(1).rolling(6, min_periods=1).std().fillna(0))
        )

        df["coeficiente_variacao"] = (
            df["desvio_demanda_6m"] / df["demanda_media_6m"].replace(0, np.nan)
        ).fillna(0)

        df["tendencia_demanda"] = (
            df.groupby("sku")["quantidade_faturada"]
            .transform(lambda s: s.shift(1).diff().rolling(3, min_periods=1).mean())
        )

        df["demanda_recente"] = df["quantidade_faturada"].shift(1).fillna(0)

        df["estoque_relativo_demanda"] = (
            df["estoque_atual"].fillna(0) / df["demanda_media_6m"].replace(0, np.nan)
        ).fillna(0)

        df["cobertura_dias"] = (
            df["estoque_atual"].fillna(0) / df["demanda_media_6m"].replace(0, np.nan) * 30
        ).fillna(0)

        df["estoque_vs_segurança"] = (
            df["estoque_atual"].fillna(0) / df["estoque_segurança_dias"].replace(0, np.nan)
        ).fillna(0)

        df["quantidade_pedidos"] = df["quantidade_pedidos"].fillna(0)
        df["pedidos_vs_demanda"] = (
            df["quantidade_pedidos"] / df["demanda_media_6m"].replace(0, np.nan)
        ).fillna(0)

        df["quantidade_ordens"] = df["quantidade_ordens"].fillna(0)
        df["ordens_vs_demanda"] = (
            df["quantidade_ordens"] / df["demanda_media_6m"].replace(0, np.nan)
        ).fillna(0)

        df["pressao_demanda"] = df["pressao_demanda"].fillna(0)
        df["pressao_pedidos"] = df["pressao_pedidos"].fillna(0)

        df["lead_time_dias"] = df["lead_time_dias"].fillna(0)
        df["lead_time_vs_horizonte"] = df["lead_time_dias"] / 30

        df["periodo"] = df["mes"].dt.to_period("M").astype(str)

        df["risco_ruptura_score"] = np.where(
            (df["estoque_projetado"] < 0) | (df["cobertura_dias"] < df["estoque_segurança_dias"].fillna(0)),
            1,
            0,
        )

        df["risco_excesso_score"] = np.where(
            df["estoque_atual"].fillna(0) > df["demanda_media_6m"].fillna(0) * 3,
            1,
            0,
        )

        df["score_operacional"] = (
            0.4 * df["pressao_demanda"].fillna(0)
            + 0.25 * df["pedidos_vs_demanda"].fillna(0)
            + 0.2 * df["lead_time_vs_horizonte"].fillna(0)
            + 0.15 * df["coeficiente_variacao"].fillna(0)
        )

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_path, index=False)
        return df


if __name__ == "__main__":
    feature_engineering = FeatureEngineering()
    df = feature_engineering.build()
    print(df.head())
    print(f"Features geradas: {df.shape[0]} linhas | {df.shape[1]} colunas")
