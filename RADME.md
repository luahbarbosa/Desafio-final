
## 1. Sobre o projeto

ETL da Verdejar, uma loja virtual fictícia de hortifrúti (Fellowship OCT26 AI-Driven Data Engineering, Sprint 2). O projeto extrai clientes e pedidos de uma API local e produtos de um arquivo CSV, trata seis problemas de qualidade de dados (A1 a A6), carrega tudo em um banco PostgreSQL e prova, com testes e reconciliação, que a carga está completa e correta. Todos os dados são sintéticos.

### Escolhas técnicas

| Item | Escolha |
|---|---|
| Banco de dados | Caminho A: PostgreSQL instalado localmente, porta **5433**, banco `verdejar` |
| Biblioteca de conexão | `psycopg`, instalada com `pip install "psycopg[binary]"` |
| Leitura do `.env` | `python-dotenv` |
| Extração HTTP | `requests` |
| Testes | `pytest` |
| Python | 3.14, ambiente virtual em `.venv` |

### Estrutura

```
desafio-final/
  README.md
  COMO_USEI_IA.md
  CONTRATO_DE_DADOS.md
  consultas_validacao.sql
  requirements.txt
  insumos/   (api_verdejar.py, gerar_dados.py, schema.sql, schema_sqlite.sql, dados/)
  etl/       (extracao.py, transformacao.py, carga.py, main.py)
  tests/     (test_transformacao.py, test_reconciliacao.py)
  brutos/    (dados extraídos, fora do Git)
```

### Como executar

Os comandos são para o Git Bash no Windows e rodam na raiz do projeto.

1. Ambiente Python:
   ```bash
   python -m venv .venv
   ./.venv/Scripts/python.exe -m pip install -r requirements.txt
   ```
2. Banco de dados (PostgreSQL local):
   ```bash
   psql -U postgres -p 5433 -c "CREATE DATABASE verdejar;"
   psql -U postgres -p 5433 -d verdejar -f insumos/schema.sql
   ```
3. Senha: A senha esta no `.env` na raiz com a linha `DB_PASSWORD=sua_senha`. O `.env` está no `.gitignore` e nunca é versionado.
4. API, em um terminal separado que fica aberto:
   ```bash
   cd insumos
   python api_verdejar.py

6. Colocar Senha:
   ```bash
   export DB_PASSWORD=luana

5. ETL completo (extração, transformação, carga e reconciliação):
   ```bash
   ./.venv/Scripts/python.exe -m etl.main
   ```
6. Testes:
   ```bash
   ./.venv/Scripts/python.exe -m pytest
   ```

## 2. Extração dos dados

- A função `extrair_rota` consome uma rota paginada da API (`page` e `page_size`), verifica o status HTTP de cada resposta e percorre as páginas até `total_pages`.
- A API aceita `page_size` de até 50. Resultado: 20 páginas de clientes (1000 registros) e 102 páginas de pedidos (5100 registros brutos, incluindo os repetidos).
- Erro de conexão e status diferente de 200 geram mensagem clara, sem interromper o programa com erro não tratado. Se a extração vier vazia, o ETL encerra com a mensagem "confira se a API esta rodando".
- Os produtos são lidos de `insumos/dados/produtos.csv` com `csv.DictReader` (12 registros).
- Os dados brutos são gravados em `brutos/` (JSON) antes de qualquer transformação, para permitir reprocessar sem chamar a API de novo.

## 3. Transformação dos dados

Cada armadilha é tratada em uma função pequena, que recebe um registro e devolve um registro novo, sem alterar o original. As regras campo a campo estão em `CONTRATO_DE_DADOS.md`.

| Código | Problema | Tratamento | Função |
|---|---|---|---|
| A1 | E-mail ausente | Cliente mantido, e-mail gravado como nulo, contagem impressa | `tratar_email` |
| A2 | Estado em maiúsculas e minúsculas | Padronizado para maiúsculas | `padronizar_estado` |
| A3 | Data em `AAAA-MM-DD` e `DD/MM/AAAA` | Convertida para `AAAA-MM-DD` (DATE no banco). Data inválida levanta `ValueError` | `padronizar_data` |
| A4 | Valor como número ou texto com vírgula | Convertido para número com duas casas decimais | `transformar_valor_pedido` |
| A5 | Pedidos repetidos entre páginas | Deduplicação pelo `id` (com um `set`), mantendo a primeira ocorrência | `remover_repetidos` |
| A6 | `valor_total` diferente da soma dos itens | `valor_itens` calculado como soma de quantidade vezes preço unitário. `divergente` é verdadeiro quando a diferença passa de R$ 0,01 | `calcular_divergencia` |

Contadores impressos pela transformação:

```
transformacao: emails_nulos=81 estados_padronizados=151
transformacao: pedidos_unicos=5000 repetidos_descartados=100
transformacao: datas_convertidas=5000 valores_convertidos=5000
divergentes: 238 pedidos com valor_total diferente da soma dos itens
```

Observação: `datas_convertidas` e `valores_convertidos` contam todos os pedidos processados, e não apenas os que mudaram de formato. `estados_padronizados` conta somente os que mudaram (por exemplo, `mg` para `MG`).

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

Detalhes adicionais:

- Todas as inserções usam parâmetros (`%s`), nunca SQL montado por concatenação de texto.
- A carga roda em uma única transação, confirmada ao final.
- Limitação conhecida: se um registro deixasse de existir na origem, ele não seria removido do destino. Para este desafio, com dados fixos (seed 2026), isso não ocorre.

## 5. Testes e reconciliação

São 16 testes com `pytest`:

- **Transformação (14 testes):** cobrem as armadilhas A1 a A6. Em A3, formato brasileiro, dia antes do mês, ano bissexto e data inválida. Em A4, vírgula decimal, valor sem decimais e valor numérico. Em A5, repetidos, ordem, primeira ocorrência e lista vazia. Em A6, pedido divergente.
- **Reconciliação (2 testes):** comparam, após a carga, a contagem de pedidos únicos da origem com a da tabela `pedidos`, e a soma de `valor_itens` da origem com a do destino, com tolerância de um centavo. O segundo é o teste de consulta: a soma dos totais mensais bate com a soma geral.

Decisão registrada: o formato com ponto de milhar (por exemplo `1.234,56`) não é tratado nem testado, porque os dados fornecidos só trazem vírgula decimal.

O ETL também imprime a reconciliação ao final de cada execução:

```
reconciliacao: soma_valor_itens_origem=311228.75 soma_valor_itens_destino=311228.75 diferenca=0.00
```

Saída do pytest:

```
======================= 16 passed in 1.16s =======================
```

## 6. Consultas SQL

As três consultas estão em `consultas_validacao.sql` e foram executadas com:

```bash
psql -U postgres -p 5433 -d verdejar -f consultas_validacao.sql
```

**(a) Total de vendas por mês**

```
    mes     | total_vendas
------------+--------------
 2026-01-01 |     30449.02
 2026-02-01 |     33923.86
 2026-03-01 |     30678.70
 2026-04-01 |     31253.96
 2026-05-01 |     30890.02
 2026-06-01 |     31627.73
 2026-07-01 |     32796.17
 2026-08-01 |     29328.04
 2026-09-01 |     29995.71
 2026-10-01 |     31104.54
(10 rows)
```

Teste de consulta: a soma dos 10 meses (312047.75) bate com a soma geral de `valor_total` da tabela `pedidos` (`test_soma_dos_meses_bate_com_soma_geral`, aprovado).

**(b) Quantidade de pedidos por estado**

```
 estado | qtd_pedidos
--------+-------------
 RS     |        1543
 SC     |        1127
 PR     |         974
 SP     |         880
 MG     |         476
(5 rows)
```

A soma (1543 + 1127 + 974 + 880 + 476) é 5000, igual ao total de pedidos carregados. Todos os estados estão em maiúsculas, o que confirma a A2 no banco.

**(c) Pedidos divergentes**

A consulta retorna 238 linhas, o mesmo número do contador `divergentes` da transformação. Primeiras linhas:

```
  id  | valor_total | valor_itens
------+-------------+-------------
    1 |      125.84 |      130.84
   51 |       26.58 |       23.58
   71 |      144.35 |      134.35
   81 |       -1.84 |        3.16
  106 |       47.78 |       44.78
```

O pedido 1 foi conferido à mão: 3 x 4,30 + 5 x 15,86 + 4 x 9,66 = 130,84, contra 125,84 informado. O pedido 81 tem `valor_total` negativo. Isso não é uma das seis armadilhas declaradas. O ETL o carregou e marcou como divergente, sem alterar o dado de origem.

## 7. Evidências de execução

### Duas execuções seguidas do ETL (idempotência)

Execução 1:

```
extracao: clientes paginas=20 registros=1000
extracao: pedidos paginas=102 registros=5100
extracao: produtos registros=12
transformacao: emails_nulos=81 estados_padronizados=151
transformacao: pedidos_unicos=5000 repetidos_descartados=100
transformacao: datas_convertidas=5000 valores_convertidos=5000
divergentes: 238 pedidos com valor_total diferente da soma dos itens
carga: clientes=1000 produtos=12 pedidos=5000 itens_pedido=12455
reconciliacao: soma_valor_itens_origem=311228.75 soma_valor_itens_destino=311228.75 diferenca=0.00
```

Execução 2: saída idêntica à da execução 1, linha por linha.

### Contagem no banco após as duas execuções

```
  c   | p  |  pe  |   i
------+----+------+-------
 1000 | 12 | 5000 | 12455
```

### Pedidos divergentes no banco

```
 count
-------
   238
```

## 8. Registro de uso de IA

O registro completo (sugestões aceitas, rejeitadas, falhas e retrabalho) está em `COMO_USEI_IA.md`.
