from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


class PipelineDados:
    """
    Fase 1 do MVP Caderno Inteligente.

    Objetivo:
    - carregar os CSVs do projeto;
    - preservar arquivos originais;
    - normalizar colunas e tipos;
    - tratar datas e ausentes;
    - salvar versão processada em data/processed/.
    """

    def __init__(self, root_dir: str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self.data_raw_dir = self.root / "data" / "raw"
        self.data_processed_dir = self.root / "data" / "processed"
        self.source_candidates = [self.root, self.data_raw_dir]

    def list_csv_files(self) -> List[Path]:
        files: List[Path] = []
        seen: set[Path] = set()

        for base_dir in self.source_candidates:
            if not base_dir.exists():
                continue
            for path in sorted(base_dir.glob("*.csv")):
                if path not in seen:
                    seen.add(path)
                    files.append(path)
        return files

    def ensure_directories(self) -> None:
        self.data_raw_dir.mkdir(parents=True, exist_ok=True)
        self.data_processed_dir.mkdir(parents=True, exist_ok=True)

    def copy_raw_if_needed(self) -> None:
        csv_files = [
            p for p in self.root.glob("*.csv") if p.name not in {"LEIA_ME.csv", "Dicionario_Dados.csv"}
        ]

        for csv_file in csv_files:
            target = self.data_raw_dir / csv_file.name
            if not target.exists():
                target.write_bytes(csv_file.read_bytes())
                logging.info(f"Arquivo copiado para data/raw: {csv_file.name}")

    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        new_columns = []
        for col in df.columns:
            col_str = str(col).strip()
            col_str = col_str.replace(" ", "_")
            col_str = col_str.replace("-", "_")
            col_str = col_str.replace("/", "_")
            col_str = col_str.lower()
            new_columns.append(col_str)
        df.columns = new_columns
        return df

    def standardize_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in df.columns:
            if "data" in col or "mes" in col or "vigencia" in col or "semana" in col:
                if df[col].dtype == "object":
                    df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    def remove_metadata_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if df.empty:
            return df

        mask = df.iloc[:, 0].astype(str).str.contains(
            "CADERNO INTELIGENTE|DADOS FICTÍCIOS|Orientações de uso",
            case=False,
            na=False,
        )
        df = df[~mask]
        return df

    def clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in df.columns:
            if df[col].dtype == "object":
                numeric_like = df[col].map(
                    lambda x: (
                        str(x).replace(".", "").replace(",", ".")
                        if isinstance(x, str)
                        and x.replace(".", "").replace(",", "").replace("-", "").replace(" ", "").replace("%", "").replace("R$", "").strip()
                        else x
                    )
                )
                try:
                    numeric = pd.to_numeric(numeric_like, errors="coerce")
                    if numeric.notna().sum() > 0 and numeric.notna().sum() >= max(1, len(df) * 0.4):
                        df[col] = numeric
                except Exception:
                    pass
        return df

    def validate_schema(self, df: pd.DataFrame, expected_columns: Iterable[str] | None = None) -> pd.DataFrame:
        if expected_columns is not None:
            missing = [c for c in expected_columns if c not in df.columns]
            if missing:
                raise ValueError(f"Colunas esperadas ausentes: {missing}")
        return df

    def normalize_file(self, path: Path) -> pd.DataFrame:
        df = pd.read_csv(
            path,
            encoding="utf-8",
            engine="python",
            na_values=["", "NA", "N/A", "nan", "null", "—", "-"],
        )
        df = self.remove_metadata_rows(df)
        df = self.normalize_column_names(df)
        df = self.clean_numeric_columns(df)
        df = self.standardize_date_columns(df)
        df = df.drop_duplicates()
        return df

    def process_all(self) -> dict[str, pd.DataFrame]:
        self.ensure_directories()
        self.copy_raw_if_needed()

        processed: dict[str, pd.DataFrame] = {}

        for path in self.list_csv_files():
            if path.name in {"LEIA_ME.csv", "Dicionario_Dados.csv"}:
                continue

            try:
                df = self.normalize_file(path)
                processed[path.stem] = df
                final_path = self.data_processed_dir / f"{path.stem}_processado.csv"
                df.to_csv(final_path, index=False)
                logging.info(f"Processado: {path.stem} -> {final_path}")
            except Exception as exc:
                logging.warning(f"Falha ao processar {path.name}: {exc}")

        return processed

    def run(self) -> dict[str, pd.DataFrame]:
        return self.process_all()


if __name__ == "__main__":
    pipeline = PipelineDados()
    dfs = pipeline.run()
    print(f"Arquivos processados: {len(dfs)}")
    for name in sorted(dfs):
        print(f"- {name}: {dfs[name].shape[0]} linhas / {dfs[name].shape[1]} colunas")
