"""
ANÁLISE DIAGNÓSTICA COMPLETA - CADERNO INTELIGENTE
Data Scientist Sênior + Analytics Engineer + Especialista em Supply Chain

Objetivo: Descobrir o problema real, impacto, dados relacionados, 
indicadores, justificativa de IA e oportunidade de solução.

Etapa: DIAGNÓSTICO TÉCNICO E DE NEGÓCIO
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

DATA_RAW = Path("../data/raw")

print("\n" + "="*100)
print(" DIAGNÓSTICO COMPLETO - CADERNO INTELIGENTE ".center(100, "="))
print("="*100)

# ============================================================================
# 1. INSPECIONAR REPOSITÓRIO
# ============================================================================

print("\n[1] INSPEÇÃO DO REPOSITÓRIO E ARQUIVOS DISPONÍVEIS")
print("-"*100)

arquivos_csv = sorted([f for f in DATA_RAW.glob("*.csv")])
print(f"Total de arquivos CSV encontrados: {len(arquivos_csv)}\n")

for arquivo in arquivos_csv:
    tamanho_kb = arquivo.stat().st_size / 1024
    print(f"  ✓ {arquivo.name:<35} {tamanho_kb:>10.1f} KB")

# ============================================================================
# 2. CARREGAR TODOS OS DADOS
# ============================================================================

print("\n[2] CARREGAMENTO DOS DADOS")
print("-"*100)

dados = {}
for arquivo in arquivos_csv:
    nome = arquivo.stem
    try:
        df = pd.read_csv(arquivo)
        dados[nome] = df
        print(f"✓ {nome:<30} {len(df):>8} linhas  {len(df.columns):>3} colunas")
    except Exception as e:
        print(f"✗ {nome:<30} ERRO: {e}")

# ============================================================================
# 3. CONTEXTO: LEIA-ME E DICIONÁRIO
# ============================================================================

print("\n[3] CONTEXTO DO NEGÓCIO - LEIA_ME.csv")
print("-"*100)

if 'LEIA_ME' in dados:
    df_leia_me = dados['LEIA_ME']
    print("\nInformações principais:")
    for idx, row in df_leia_me.iterrows():
        if pd.notna(row.iloc[0]):
            print(f"  {row.iloc[0]}: {row.iloc[1]}")
else:
    print("⚠ LEIA_ME não encontrado")

print("\n[4] DICIONÁRIO DE DADOS")
print("-"*100)

if 'Dicionario_Dados' in dados:
    df_dict = dados['Dicionario_Dados']
    print(f"\nTotal de campos documentados: {len(df_dict)}")
    print("\nCampos por tabela:")
    for tabela in df_dict['Aba'].unique():
        campos = df_dict[df_dict['Aba'] == tabela].shape[0]
        print(f"  {tabela:<25} {campos:>3} campos")
else:
    print("⚠ Dicionário não encontrado")

# ============================================================================
# 5. INVENTÁRIO DOS DADOS - TABELA RESUMIDA
# ============================================================================

print("\n[5] INVENTÁRIO COMPLETO DOS DADOS")
print("-"*100)

inventario = []
for nome, df in dados.items():
    # Período
    periodo = "A DETERMINAR"
    for col in df.columns:
        if 'mês' in col.lower() or 'data' in col.lower() or 'período' in col.lower():
            if df[col].dtype == 'object':
                periodo = f"{df[col].min()} a {df[col].max()}"
            break
    
    # Granularidade
    granularidade = "Ponto de vista"
    if 'SKU' in df.columns and 'Mês' in df.columns:
        granularidade = "Produto x Mês"
    elif 'SKU' in df.columns and 'Semana' in df.columns:
        granularidade = "Produto x Semana"
    elif 'SKU' in df.columns:
        granularidade = "Produto"
    elif 'Mês' in df.columns:
        granularidade = "Mensal"
    
    inventario.append({
        'Arquivo': nome,
        'Registros': len(df),
        'Colunas': len(df.columns),
        'Granularidade': granularidade,
        'Período': periodo,
        'Papel': 'A DETERMINAR'
    })

df_inventario = pd.DataFrame(inventario)
print(df_inventario.to_string(index=False))

print("\n[RESUMO]")
print(f"Total de tabelas: {len(dados)}")
print(f"Total de registros carregados: {sum(df.shape[0] for df in dados.values())}")

print("\n✓ Diagnóstico carregado. Aguardando análise detalhada...")
print("="*100 + "\n")
