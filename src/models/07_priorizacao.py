from __future__ import annotations

from pathlib import Path

import pandas as pd


class PriorizacaoFinal:
    """
    Fase 7 do MVP Caderno Inteligente.

    Objetivo:
    - gerar um ranking final de risco por SKU/mês;
    - combinar baseline + score do modelo + sinais operacionais;
    - entregar recomendação executiva e priorização.
    """

    def __init__(self, root_dir: str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self.processed_dir = self.root / "data" / "processed"
        self.features_path = self.processed_dir / "features.csv"
        self.baseline_path = self.processed_dir / "baseline_scores.csv"
        self.output_path = self.processed_dir / "priorizacao_final.csv"

    def load_features(self) -> pd.DataFrame:
        if not self.features_path.exists():
            raise FileNotFoundError(f"Arquivo de features não encontrado: {self.features_path}")
        df = pd.read_csv(self.features_path)
        df["mes"] = pd.to_datetime(df["mes"], errors="coerce")
        return df

    def load_baseline(self) -> pd.DataFrame:
        if not self.baseline_path.exists():
            raise FileNotFoundError(f"Arquivo de baseline não encontrado: {self.baseline_path}")
        df = pd.read_csv(self.baseline_path)
        df["mes"] = pd.to_datetime(df["mes"], errors="coerce")
        return df

    def _final_score(self, row: pd.Series) -> float:
        baseline = float(row.get("baseline_score", 0.0))
        prob = float(row.get("prob_ruptura", 0.0))
        risco_signal = float(row.get("risco_ruptura_score", 0.0))
        estoque_proj = float(row.get("estoque_projetado", 0.0))
        cobertura = float(row.get("cobertura_dias", 0.0))
        estoque_seg = float(row.get("estoque_segurança_dias", 0.0))
        demanda_media = float(row.get("demanda_media_6m", 0.0))

        score = 0.45 * baseline + 0.30 * prob + 0.15 * risco_signal

        if estoque_proj < 0:
            score += 0.15
        if cobertura < estoque_seg:
            score += 0.10
        if demanda_media > 0 and estoque_proj < demanda_media * 0.2:
            score += 0.10

        score = min(score, 1.0)
        return round(score, 4)

    def _classify(self, score: float) -> str:
        if score >= 0.75:
            return "ALTO"
        if score >= 0.45:
            return "MEDIO"
        return "BAIXO"

    def _recommendation(self, row: pd.Series) -> str:
        if row["score_risco_final"] >= 0.75:
            return "Priorizar revisão de estoques, produção e pedidos; avaliar reposição imediata."
        if row["score_risco_final"] >= 0.45:
            return "Monitorar com atenção; confirmar demanda e capacidade do próximo ciclo."
        return "Manter rotina operacional normal; revisar apenas em acompanhamento programado."

    def build(self) -> pd.DataFrame:
        features = self.load_features().copy()
        baseline = self.load_baseline().copy()

        merged = features.merge(
            baseline[["sku", "mes", "baseline_label", "baseline_score"]],
            on=["sku", "mes"],
            how="left",
        )

        merged["prob_ruptura"] = 0.0
        if "prob_ruptura" not in merged.columns:
            merged["prob_ruptura"] = 0.0

        merged["score_risco_final"] = merged.apply(self._final_score, axis=1)
        merged["nivel_risco"] = merged["score_risco_final"].apply(self._classify)
        merged["prioridade"] = merged["score_risco_final"].rank(method="dense", ascending=False, na_option="top")
        merged["recomendacao"] = merged.apply(self._recommendation, axis=1)

        merged = merged.sort_values(["score_risco_final", "prioridade"], ascending=[False, True]).reset_index(drop=True)

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        merged.to_csv(self.output_path, index=False)
        return merged

    def summary_by_sku(self) -> pd.DataFrame:
        df = pd.read_csv(self.output_path)
        summary = (
            df.groupby("sku")
            .agg(
                maior_risco=("score_risco_final", "max"),
                ultimo_nivel=("nivel_risco", "last"),
                ultimo_mes=("mes", "last"),
            )
            .reset_index()
            .sort_values("maior_risco", ascending=False)
        )
        return summary


if __name__ == "__main__":
    priorizacao = PriorizacaoFinal()
    df = priorizacao.build()
    print(df.head())
    print(f"Registros priorizados: {df.shape[0]}")
    print(df["nivel_risco"].value_counts().to_dict())
