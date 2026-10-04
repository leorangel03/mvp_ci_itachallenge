# Diagnóstico inicial dos dados

## Contexto

Este repositório contém uma base de dados fictícia organizada para um cenário de análise operacional, comercial e de planejamento. A documentação disponível indica que a base foi criada como material de desafio e que os dados são fictícios.

## Arquivos identificados

### Dados

- `Produtos.csv`
- `Vendas_24m.csv`
- `Historico_Estoque.csv`
- `Estoque_Atual.csv`
- `Carteira_Pedidos.csv`
- `Ordens_Producao.csv`
- `Capacidade_Producao.csv`
- `Capacidade_Semanal.csv`
- `Sell_In.csv`
- `Sell_Out.csv`
- `Forecast_Comercial.csv`
- `Parceiros_Canais.csv`
- `Lead_Times.csv`
- `Precos_Produtos.csv`
- `Calendario_Eventos.csv`
- `Indicadores_Atuais.csv`

### Documentação

- `LEIA_ME.csv`
- `Dicionario_Dados.csv`
- `README.md`

## Classificação inicial das informações

### Dados de produto e catálogo

- `Produtos.csv` reúne SKU, família, status, lead time, lote mínimo, estoque atual, cobertura e métricas de demanda.
- `Precos_Produtos.csv` contém informação de preço por vigência.
- `Lead_Times.csv` indica tempo de produção/disponibilidade por SKU e família.

### Dados de demanda e vendas

- `Vendas_24m.csv` registra histórico de unidades faturadas e faturamento por mês, SKU e canal/cliente.
- `Sell_In.csv` e `Sell_Out.csv` trazem movimentos de expedição e venda ao consumidor final, com diferentes coberturas e granularidades.
- `Forecast_Comercial.csv` contém previsões mensais de unidades para out/26, nov/26 e dez/26.

### Dados de estoque, produção e capacidade

- `Estoque_Atual.csv` mostra posição atual de estoque por SKU.
- `Historico_Estoque.csv` registra histórico mensal de estoque.
- `Carteira_Pedidos.csv` indica pedidos confirmados com datas prometidas.
- `Ordens_Producao.csv` lista ordens planejadas, em produção e liberadas.
- `Capacidade_Producao.csv` e `Capacidade_Semanal.csv` trazem capacidade por linha e ocupação semanal.

### Dados de parceiros e contexto comercial

- `Parceiros_Canais.csv` informa região, UF, cidade, canal e cobertura de sell-out.
- `Calendario_Eventos.csv` traz eventos/ campanhas e impacto esperado.
- `Indicadores_Atuais.csv` reúne indicadores operacionais do cenário fictício.

## Observações sobre qualidade inicial

- A base parece combinar dados observados, estimados e previstos.
- Há diferenca de granularidade entre tabelas, o que exige cuidado na integração.
- O dicionário de dados confirma que algumas variáveis são estimadas ou simuladas.
- A cobertura de sell-out é parcial, com ausência de registro representando dado não disponível e não necessariamente venda zero.
- Existem SKUs repetidos em nomes similares, diferenciados por coleção/versão e descrição completa, o que exige atenção na chave de integração.

## Conclusões preliminares

- O repositório já possui uma base sólida para análise exploratória.
- O conjunto de dados é suficientemente rico para estudar demanda, estoque, produção e previsão.
- Ainda não foi definida a pergunta de negócio principal nem a métrica de sucesso do protótipo.
- A definição da hipótese e do MVP depende da análise das relações entre as tabelas.

## Decisões tomadas

- Os arquivos originais devem ser preservados como dados brutos.
- Antes de qualquer transformação, o objetivo e a justificativa devem ser registrados.
- Mudanças em dados devem ser feitas em fluxo controlado e documentado.

## Pendências

- problema de negócio específico: A DEFINIR
- hipótese de solução: A DEFINIR
- papel da IA no fluxo: A DEFINIR
- baseline e métricas: A DEFINIR
- arquitetura e modelo: A DEFINIR
