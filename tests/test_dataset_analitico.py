from pathlib import Path

from src.data.01_pipeline_dados import PipelineDados
from src.data.02_dataset_analitico import DatasetAnalitico


def test_pipeline_creates_processed_dir():
    pipeline = PipelineDados()
    pipeline.ensure_directories()
    assert Path("data/processed").exists()


def test_pipeline_processes_csv_files():
    pipeline = PipelineDados()
    dfs = pipeline.run()
    assert isinstance(dfs, dict)
    assert len(dfs) > 0


def test_dataset_analitico_is_built():
    dataset = DatasetAnalitico()
    df = dataset.build()
    assert not df.empty
    assert "sku" in df.columns
    assert "mes" in df.columns
    assert "risco_ruptura_hipotese" in df.columns
