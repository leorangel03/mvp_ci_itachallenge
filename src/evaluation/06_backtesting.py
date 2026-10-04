from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.04_baseline import BaselineRisco
from src.models.05_modelo_ml import ModeloRuptura


class BacktestingRisco:
    """
    Fase 6 do MVP Caderno Inteligente.

    Objetivo:
    - comparar baseline determinístico versus modelo ML;
    - usar divisão temporal para avaliação;
    - medir ganho real em segurança operacional.
    """

    def __init__(self, root_dir: str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self.processed_dir = self.root / "data" / "processed"
        self.features_path = self.processed_dir / "features.csv"
        self.baseline_path = self.processed_dir / "baseline_scores.csv"
        self.output_path = self.processed_dir / "backtesting_resultados.csv"

    def load_features(self) -> pd.DataFrame:
        if not self.features_path.exists():
            raise FileNotFoundError(f"Arquivo de features não encontrado: {self.features_path}")
        df = pd.read_csv(self.features_path)
        df["mes"] = pd.to_datetime(df["mes"], errors="coerce")
        return df

    def compare(self) -> pd.DataFrame:
        features = self.load_features().copy().sort_values("mes").reset_index(drop=True)
        cutoff = features["mes"].quantile(0.8)
        test_df = features[features["mes"] > cutoff].copy()

        if test_df.empty:
            raise ValueError("Data de teste vazia. Verifique o tamanho do dataset.")

        baseline = BaselineRisco(self.root.as_posix())
        baseline_df = baseline.build()
        baseline_test = baseline_df[baseline_df["mes"] > cutoff].copy()

        model = ModeloRuptura(self.root.as_posix())
        model_result = model.train()
        model_pipe = model_result["model"]

        X_test = test_df[[col for col in model_result["features"] if col in test_df.columns]]
        y_test = (test_df["estoque_projetado"] < 0).astype(int)

        pred_model = model_pipe.predict(X_test)
        prob_model = model_pipe.predict_proba(X_test)[:, 1]

        comparison = pd.DataFrame({
            "sku": test_df["sku"],
            "mes": test_df["mes"],
            "real_ruptura": y_test.astype(int).values,
            "pred_model": pred_model.astype(int),
            "prob_model": prob_model,
            "baseline_label": baseline_test["baseline_label"].values if len(baseline_test) == len(test_df) else ["NA"] * len(test_df),
            "baseline_score": baseline_test["baseline_score"].values if len(baseline_test) == len(test_df) else [0.0] * len(test_df),
        })

        comparison["baseline_detectou"] = comparison["baseline_label"].isin(["ALTO", "MEDIO"])
        comparison["modelo_detectou"] = comparison["pred_model"] == 1

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(self.output_path, index=False)
        return comparison


if __name__ == "__main__":
    backtest = BacktestingRisco()
    df = backtest.compare()
    print(df.head())
    print(f"Registros de teste: {df.shape[0]}")
