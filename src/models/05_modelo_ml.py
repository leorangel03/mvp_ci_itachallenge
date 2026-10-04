from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class ModeloRuptura:
    """
    Fase 5 do MVP Caderno Inteligente.

    Objetivo:
    - treinar um modelo inicial de classificação para risco de ruptura;
    - usar validação temporal em vez de split aleatório;
    - manter a abordagem simples, explicável e comparável ao baseline.
    """

    def __init__(self, root_dir: str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self.processed_dir = self.root / "data" / "processed"
        self.input_path = self.processed_dir / "features.csv"
        self.model_path = self.processed_dir / "modelo_ruptura.joblib"
        self.metrics_path = self.processed_dir / "metricas_modelo_ruptura.csv"

    def load_features(self) -> pd.DataFrame:
        if not self.input_path.exists():
            raise FileNotFoundError(f"Arquivo de features não encontrado: {self.input_path}")
        df = pd.read_csv(self.input_path)
        df["mes"] = pd.to_datetime(df["mes"], errors="coerce")
        return df

    def _feature_columns(self, df: pd.DataFrame) -> list[str]:
        exclude = {
            "sku",
            "mes",
            "periodo",
            "risco_ruptura_hipotese",
            "risco_excesso_hipotese",
            "baseline_label",
            "baseline_score",
            "prioridade",
        }
        columns = [
            col for col in df.columns
            if col not in exclude and pd.api.types.is_numeric_dtype(df[col])
        ]
        return columns

    def _build_target(self, df: pd.DataFrame) -> pd.Series:
        if "risco_ruptura_hipotese" in df.columns:
            target = df["risco_ruptura_hipotese"].astype(int)
        elif "ruptura_real" in df.columns:
            target = df["ruptura_real"].astype(int)
        else:
            target = (df["estoque_projetado"] < 0).astype(int)
        return target

    def train(self) -> dict:
        df = self.load_features().copy()
        df = df.sort_values("mes").reset_index(drop=True)

        target = self._build_target(df)
        features = self._feature_columns(df)

        if len(features) == 0:
            raise ValueError("Nenhuma feature numérica útil encontrada para treino.")

        X = df[features]
        y = target

        cutoff = df["mes"].quantile(0.8)
        train_mask = df["mes"] <= cutoff
        test_mask = ~train_mask

        X_train = X.loc[train_mask]
        y_train = y.loc[train_mask]
        X_test = X.loc[test_mask]
        y_test = y.loc[test_mask]

        if len(X_train) == 0 or len(X_test) == 0:
            raise ValueError("Divisão temporal inválida: treino/test vazios.")

        numeric_features = X_train.columns.tolist()

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]), numeric_features),
            ],
            remainder="drop",
        )

        model = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
        )

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_prob),
            "n_train": len(X_train),
            "n_test": len(X_test),
            "cutoff": str(cutoff.date()),
        }

        result = {
            "model": pipeline,
            "features": features,
            "metrics": metrics,
        }

        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, self.model_path)

        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_csv(self.metrics_path, index=False)

        return result

    def predict(self, df: pd.DataFrame | None = None) -> pd.DataFrame:
        if df is None:
            df = self.load_features().copy()

        model = joblib.load(self.model_path)
        x = df[[col for col in self._feature_columns(df) if col in df.columns]]
        x = x.copy()
        x = x.fillna(x.median(numeric_only=True))

        proba = model.predict_proba(x)[:, 1]
        pred = model.predict(x)

        out = df.copy()
        out["predicao_ruptura"] = pred
        out["prob_ruptura"] = proba
        return out


if __name__ == "__main__":
    modelo = ModeloRuptura()
    resultado = modelo.train()
    print(resultado["metrics"])
