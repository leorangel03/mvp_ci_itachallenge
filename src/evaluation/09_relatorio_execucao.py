from __future__ import annotations

from pathlib import Path

import pandas as pd


class RelatorioExecucao:
    """
    Fase 9 do MVP Caderno Inteligente.

    Objetivo:
    - gerar relatório executivo de performance;
    - comparar baseline vs modelo;
    - medir ganho operacional real;
    - documentar limitações e recomendações.
    """

    def __init__(self, root_dir: str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self.processed_dir = self.root / "data" / "processed"
        self.features_path = self.processed_dir / "features.csv"
        self.baseline_path = self.processed_dir / "baseline_scores.csv"
        self.backtesting_path = self.processed_dir / "backtesting_resultados.csv"
        self.priorizacao_path = self.processed_dir / "priorizacao_final.csv"
        self.output_path = self.processed_dir / "relatorio_execucao.csv"

    def load_backtesting(self) -> pd.DataFrame:
        if not self.backtesting_path.exists():
            raise FileNotFoundError(f"Arquivo de backtesting não encontrado: {self.backtesting_path}")
        return pd.read_csv(self.backtesting_path)

    def load_priorizacao(self) -> pd.DataFrame:
        if not self.priorizacao_path.exists():
            raise FileNotFoundError(f"Arquivo de priorização não encontrado: {self.priorizacao_path}")
        return pd.read_csv(self.priorizacao_path)

    def calculate_metrics(self) -> dict:
        try:
            backtest = self.load_backtesting()
        except FileNotFoundError:
            return self._empty_metrics()

        # Métricas de baseline
        if "baseline_detectou" in backtest.columns and "real_ruptura" in backtest.columns:
            baseline_tp = ((backtest["baseline_detectou"]) & (backtest["real_ruptura"])).sum()
            baseline_fp = ((backtest["baseline_detectou"]) & (~backtest["real_ruptura"])).sum()
            baseline_fn = ((~backtest["baseline_detectou"]) & (backtest["real_ruptura"])).sum()
            baseline_tn = ((~backtest["baseline_detectou"]) & (~backtest["real_ruptura"])).sum()

            baseline_recall = baseline_tp / (baseline_tp + baseline_fn) if (baseline_tp + baseline_fn) > 0 else 0
            baseline_precision = baseline_tp / (baseline_tp + baseline_fp) if (baseline_tp + baseline_fp) > 0 else 0
            baseline_f1 = (
                2 * (baseline_precision * baseline_recall) / (baseline_precision + baseline_recall)
                if (baseline_precision + baseline_recall) > 0
                else 0
            )
        else:
            baseline_recall = baseline_precision = baseline_f1 = 0

        # Métricas de modelo
        if "modelo_detectou" in backtest.columns and "real_ruptura" in backtest.columns:
            model_tp = ((backtest["modelo_detectou"]) & (backtest["real_ruptura"])).sum()
            model_fp = ((backtest["modelo_detectou"]) & (~backtest["real_ruptura"])).sum()
            model_fn = ((~backtest["modelo_detectou"]) & (backtest["real_ruptura"])).sum()
            model_tn = ((~backtest["modelo_detectou"]) & (~backtest["real_ruptura"])).sum()

            model_recall = model_tp / (model_tp + model_fn) if (model_tp + model_fn) > 0 else 0
            model_precision = model_tp / (model_tp + model_fp) if (model_tp + model_fp) > 0 else 0
            model_f1 = (
                2 * (model_precision * model_recall) / (model_precision + model_recall)
                if (model_precision + model_recall) > 0
                else 0
            )
        else:
            model_recall = model_precision = model_f1 = 0

        return {
            "baseline_recall": round(baseline_recall, 4),
            "baseline_precision": round(baseline_precision, 4),
            "baseline_f1": round(baseline_f1, 4),
            "model_recall": round(model_recall, 4),
            "model_precision": round(model_precision, 4),
            "model_f1": round(model_f1, 4),
            "total_registros_teste": len(backtest),
            "rupturas_reais": int(backtest["real_ruptura"].sum()) if "real_ruptura" in backtest.columns else 0,
        }

    def _empty_metrics(self) -> dict:
        return {
            "baseline_recall": 0.0,
            "baseline_precision": 0.0,
            "baseline_f1": 0.0,
            "model_recall": 0.0,
            "model_precision": 0.0,
            "model_f1": 0.0,
            "total_registros_teste": 0,
            "rupturas_reais": 0,
        }

    def build(self) -> dict:
        metrics = self.calculate_metrics()

        priorizacao = self.load_priorizacao()
        skus_alto_risco = int((priorizacao["nivel_risco"] == "ALTO").sum())
        skus_medio_risco = int((priorizacao["nivel_risco"] == "MEDIO").sum())
        skus_baixo_risco = int((priorizacao["nivel_risco"] == "BAIXO").sum())

        relatorio = {
            **metrics,
            "skus_alto_risco": skus_alto_risco,
            "skus_medio_risco": skus_medio_risco,
            "skus_baixo_risco": skus_baixo_risco,
            "conclusao": self._generate_conclusion(metrics),
        }

        df_relatorio = pd.DataFrame([relatorio])
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        df_relatorio.to_csv(self.output_path, index=False)

        return relatorio

    def _generate_conclusion(self, metrics: dict) -> str:
        if metrics["model_f1"] > metrics["baseline_f1"]:
            return "Modelo apresenta melhor desempenho que baseline; recomenda-se integração gradual."
        elif metrics["model_f1"] == metrics["baseline_f1"]:
            return "Modelo equivalente ao baseline; manter baseline até próximas iterações."
        else:
            return "Baseline superior ao modelo; otimizar features e retreinar antes de produção."


if __name__ == "__main__":
    relatorio = RelatorioExecucao()
    resultado = relatorio.build()
    print(resultado)
