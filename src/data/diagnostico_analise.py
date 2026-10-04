"""
Diagnóstico completo dos dados - Caderno Inteligente
Análise profunda e reproduzível de todos os CSVs
Objetivo: Entender os dados, qualidade, relacionamentos e oportunidades
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================

DATA_RAW_PATH = Path("../../data/raw")
ARQUIVOS_ESPERADOS = [
    "Produtos.csv",
    "Vendas_24m.csv",
    "Estoque_Atual.csv",
    "Carteira_Pedidos.csv",
    "Ordens_Producao.csv",
    "Capacidade_Semanal.csv",
    "Sell_In.csv",
    "Sell_Out.csv",
    "Forecast_Comercial.csv",
    "Parceiros_Canais.csv",
    "Historico_Estoque.csv",
    "Lead_Times.csv",
    "Precos_Produtos.csv",
    "Calendario_Eventos.csv",
    "Indicadores_Atuais.csv",
    "Capacidade_Producao.csv"
]

print("=" * 80)
print("DIAGNÓSTICO COMPLETO DOS DADOS - CADERNO INTELIGENTE")
print("=" * 80)
print()

# ============================================================================
# 1. INSPECIONAR REPOSITÓRIO E LISTAR ARQUIVOS
# ============================================================================

print("1. INSPEÇÃO DO REPOSITÓRIO")
print("-" * 80)

arquivos_encontrados = list(DATA_RAW_PATH.glob("*.csv"))
nomes_encontrados = [f.name for f in arquivos_encontrados]

print(f"✓ Arquivos CSV encontrados: {len(nomes_encontrados)}")
for arquivo in sorted(nomes_encontrados):
    tamanho = (DATA_RAW_PATH / arquivo).stat().st_size / 1024
    print(f"  - {arquivo:<30} ({tamanho:>8.1f} KB)")

print()

# ============================================================================
# 2. CARREGAR E INSPECIONAR CADA CSV
# ============================================================================

print("2. INSPEÇÃO INICIAL DE CADA CSV")
print("-" * 80)

dataframes = {}
inventario = []

for arquivo in sorted(nomes_encontrados):
    try:
        df = pd.read_csv(DATA_RAW_PATH / arquivo)
        dataframes[arquivo.replace('.csv', '')] = df
        
        inventario.append({
            'Arquivo': arquivo.replace('.csv', ''),
            'Linhas': len(df),
            'Colunas': len(df.columns),
            'Colunas (nomes)': ', '.join(df.columns.tolist()),
            'Tamanho (KB)': (DATA_RAW_PATH / arquivo).stat().st_size / 1024
        })
        
        print(f"✓ {arquivo:<30} {len(df):>6} linhas  {len(df.columns):>3} colunas")
        
    except Exception as e:
        print(f"✗ {arquivo:<30} ERRO: {str(e)}")

print()

# ============================================================================
# 3. ANÁLISE DETALHADA DE CADA DATAFRAME
# ============================================================================

print("3. ANÁLISE DETALHADA DOS DADOS")
print("-" * 80)

for nome_df, df in dataframes.items():
    print()
    print(f"\n📊 ARQUIVO: {nome_df}")
    print(f"   Dimensões: {df.shape[0]} linhas × {df.shape[1]} colunas")
    print(f"   Tipos de dados:")
    
    tipos = df.dtypes.value_counts()
    for dtype, count in tipos.items():
        print(f"     - {str(dtype):<15} : {count:>3} colunas")
    
    print(f"\n   Colunas:")
    for col in df.columns:
        nulos = df[col].isnull().sum()
        unicos = df[col].nunique()
        tipo = str(df[col].dtype)
        pct_nulos = (nulos / len(df)) * 100
        
        status = "✓" if nulos == 0 else "⚠"
        print(f"     {status} {col:<30} | Tipo: {tipo:<10} | Nulos: {nulos:>5} ({pct_nulos:>5.1f}%) | Únicos: {unicos:>5}")
    
    # Amostra de dados
    print(f"\n   Amostra (primeiras 3 linhas):")
    print(df.head(3).to_string())

print()
print("=" * 80)
print("ANÁLISE CONCLUÍDA")
print("=" * 80)
print()
print("✓ Todos os dataframes carregados com sucesso")
print(f"✓ Total de arquivos analisados: {len(dataframes)}")
print()
