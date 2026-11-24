# Desafio Final - Verdejar

## 1. Sobre o projeto

## 2. Extração dos dados

## 3. Transformação dos dados

## 4. Carga dos dados

### Estratégia de carga e idempotência

A carga dos dados foi realizada respeitando a ordem das chaves estrangeiras:

1. Produtos;
2. Clientes;
3. Pedidos;
4. Itens_pedido.

Para garantir a idempotência, foi utilizada a estratégia de atualização de registros existentes por meio de `ON CONFLICT DO UPDATE` nas tabelas produtos, clientes e pedidos.

Na tabela `itens_pedido`, os itens anteriores de cada pedido são removidos antes da inserção dos novos itens.

Dessa forma, a execução repetida do ETL com os mesmos dados não gera duplicações e mantém as contagens das tabelas.

## 5. Testes e reconciliação

## 6. Consultas SQL

## 7. Evidências de execução