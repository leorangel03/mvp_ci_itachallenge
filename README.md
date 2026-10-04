# Prototipo IA Dados

Protótipo de solução baseada em dados e IA com foco em análise incremental, validação de hipóteses e documentação clara das etapas de desenvolvimento.

## Objetivo do projeto

Organizar uma base reprodutível para desenvolver um protótipo de solução orientada por dados e IA, com foco em:

- análise dos dados disponíveis;
- avaliação da qualidade dos dados;
- definição da hipótese de solução;
- desenvolvimento incremental do protótipo;
- testes, validação e documentação.

## Problema a ser investigado

O problema de negócio específico ainda será definido após a análise do contexto do repositório e dos dados disponíveis. Nesta etapa, o projeto está em fase de diagnóstico e preparação.

Status: A DEFINIR

## Etapa atual

A etapa atual é de estruturação e diagnóstico inicial do repositório.

- dados identificados e catalogados;
- documentação de contexto disponível;
- estrutura do projeto organizada para desenvolvimento incremental;
- hipótese de solução e MVP ainda em validação.

## Como executar o projeto

1. Clone o repositório.
2. Crie um ambiente virtual.
3. Instale as dependências listadas em `requirements.txt`.
4. Mantenha os dados brutos em `data/raw/` sem alteração.
5. Use `data/processed/` para dados derivados.
6. Realize análises em notebooks e scripts em `src/`.
7. Registre decisões e conclusões em `docs/`.

Exemplo:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Estrutura das pastas

```text
.
├── README.md
├── .gitignore
├── requirements.txt
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
├── docs/
│   ├── desafio.md
│   ├── diagnostico_dados.md
│   ├── hipotese_solucao.md
│   ├── planejamento_prototipo.md
│   └── relatorio_semana_2.md
├── notebooks/
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   └── utils/
├── tests/
├── config/
└── .github/   # opcional
```

## Tecnologias previstas

A tecnologia final ainda será validada com base nos dados e no problema que se definir. Para esta fase inicial, a base considerada é:

- Python
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- Jupyter Notebook
- pytest
- Git/GitHub

## Próximos passos

- validar qualidade e integridade dos dados;
- mapear relações entre as bases de vendas, estoque, produção e forecast;
- identificar o problema principal a resolver;
- definir a hipótese de solução e o papel da IA;
- estabelecer baseline e métricas;
- iniciar o desenvolvimento do MVP de forma incremental;
- registrar cada decisão em documentação.

## Observações importantes

- Os arquivos CSV originais devem ser tratados como dados brutos e preservados.
- Qualquer transformação deve ser documentada antes de execução.
- Informações ainda não confirmadas devem ser marcadas como `A DEFINIR` ou `A VALIDAR`.
- Nesta etapa não foi escolhida uma arquitetura final nem um modelo de IA definitivo.
