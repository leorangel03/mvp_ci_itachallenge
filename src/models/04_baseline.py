from __future__ import annotations

from pathlib import Path

import pandas as pd


class BaselineRisco:
    """
    Fase 4 do MVP Caderno Inteligente.

    Objetivo:
    - criar uma linha de base determinística e explicável;
    - classificar risco de ruptura e excesso por SKU/mês;
    - gerar uma ordem de priorização operacional.
    """

    def __init__(self, root_dir: str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self.processed_dir = self.root / "data" / "processed"
        self.input_path = self.processed_dir / "features.csv"
        self.output_path = self.processed_dir / "baseline_scores.csv"

    def load_features(self) -> pd.DataFrame:
        if not self.input_path.exists():
            raise FileNotFoundError(f"Arquivo de features não encontrado: {self.input_path}")
        df = pd.read_csv(self.input_path)
        df["mes"] = pd.to_datetime(df["mes"], errors="coerce")
        return df

    def classify_risk(self, row: pd.Series) -> tuple[str, float]:
        score = 0.0

        if pd.notna(row.get("estoque_projetado")) and row["estoque_projetado"] < 0:
            score += 0.55

        if pd.notna(row.get("cobertura_dias")) and pd.notna(row.get("estoque_segurança_dias")):
            if row["cobertura_dias"] < row["estoque_segurança_dias"]:
                score += 0.25

        if pd.notna(row.get("pressao_demanda")) and row["pressao_demanda"] > 1.0:
            score += 0.10

        if pd.notna(row.get("pedidos_vs_demanda")) and row["pedidos_vs_demanda"] > 1.0:
            score += 0.10

        if pd.notna(row.get("lead_time_dias")) and row["lead_time_dias"] > 30:
            score += 0.05

        if pd.notna(row.get("risco_excesso_score")) and row["risco_excesso_score"] == 1:
            score += 0.20

        score = min(score, 1.0)

        if score >= 0.70:
            label = "ALTO"
        elif score >= 0.35:
            label = "MEDIO"
        else:
            label = "BAIXO"

        return label, round(score, 4)

    def build(self) -> pd.DataFrame:
        df = self.load_features().copy()

        df["baseline_label"], df["baseline_score"] = zip(*df.apply(self.classify_risk, axis=1))

        df["prioridade"] = df["baseline_score"].rank(method="dense", ascending=False, na_option="top")
        df = df.sort_values(["baseline_score", "prioridade"], ascending=[False, True]).reset_index(drop=True)

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_path, index=False)
        return df


if __name__ == "__main__":
    baseline = BaselineRisco()
    df = baseline.build()
    print(df.head())
    print(f"Linhas baseline: {df.shape[0]}")
    print(df["baseline_label"].value_counts().to_dict())
