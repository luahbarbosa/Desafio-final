# CONTRATO DE DADOS — VERDEJAR

Este documento define a estrutura das tabelas de destino do projeto Verdejar, incluindo os campos, tipos de dados, obrigatoriedade e regras de transformação aplicadas durante o processo de ETL (Extração, Transformação e Carga).

O banco de dados escolhido é o PostgreSQL, utilizando o esquema disponibilizado pelo instrutor no arquivo schema.sql.

---

## 1. Convenções Gerais

* **Banco de dados:**  PostgreSQL.
* **Encoding:** UTF-8.
* **Nomenclatura:**  nomes de tabelas e colunas em letras minúsculas.
* **Valores nulos**  campos definidos como NOT NULL são obrigatórios. Campos sem essa restrição podem receber valores nulos.
* **Valores monetários:** utilizar duas casas decimais.
* **Datas:** armazenar no tipo DATE do PostgreSQL.
* **Integridade referencial:** respeitar as chaves estrangeiras definidas no esquema do banco.

---

## 2. Tabelas de Destino

### 2.1. Tabela clientes

**Descrição:** armazena os dados cadastrais dos clientes.

**Chave Primária (PK):** `id`  

| Campo | Tipo | Admite Nulo? | Regra de Transformação |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Não | Manter o identificador original do cliente. Deve ser único. |
| `nome` | `TEXT` | Não | Manter o nome, removendo espaços desnecessários nas extremidades.|
| `email` | `TEXT` | Sim | Preservar o cliente mesmo quando o e-mail estiver ausente. Nesse caso, gravar NULL (A1). |
| `cidade` | `TEXT` | Não | Remover espaços desnecessários nas extremidades. |
| `estado` | `CHAR(2)` | Não | Padronizar a sigla do estado para letras maiúsculas (A2). |
| `cadastro_em` | `DATE` | Não | Converter para o tipo DATE do PostgreSQL, respeitando o formato de data da origem. |

---

### 2.2. Tabela produtos

**Descrição:** armazena o catálogo de produtos fornecido pelo arquivo produtos.csv  

**Chave Primária (PK):** `produto_id`  

| Campo | Tipo | Admite Nulo? | Regra de Transformação.  |
| :--- | :--- | :--- | :--- |
| `produto_id` | `INTEGER` | Não | Utilizar o identificador do produto presente no CSV. |
| `nome` | `TEXT` | Não | Manter o nome do produto, removendo espaços desnecessários nas extremidades. |
| `categoria` | `TEXT` | Não | Manter a categoria informada no CSV, removendo espaços desnecessários. |
| `preco_base` | `NUMERIC(10,2)` | Não |Converter para valor numérico com duas casas decimais. |

---

### 2.3. Tabela pedidos

**Descrição:** armazena os pedidos realizados pelos clientes, incluindo os valores totais e a identificação de possíveis divergências.

**Chave Primária (PK):** `id`

**Chaves Estrangeiras (FK):** `cliente_id`, que referenciando `clientes(id)`  

| Campo | Tipo | Admite Nulo? | Regra de Transformação |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Não | Manter o identificador original do pedido. Remover pedidos duplicados pelo mesmo ID, mantendo a primeira ocorrência (A5). |
| `cliente_id` | `INTEGER` | Não | Manter o identificador do cliente relacionado ao pedido, respeitando a chave estrangeira. |
| `data_pedido` | `DATE` | Não | Converter os formatos AAAA-MM-DD e DD/MM/AAAA para o tipo DATE do PostgreSQL (A3). |
| `status` | `TEXT` | Não | Preservar o status informado na origem. |
| `valor_total` | `NUMERIC(12,2)` | Não | Converter valores numéricos e textos com vírgula decimal para números com duas casas decimais (A4). |
| `valor_itens` | `NUMERIC(12,2)` | Não | Calcular pela soma de quantidade * preco_unitario de todos os itens do pedido (A6). |
| `divergente` | `BOOLEAN` | Não | Marcar como TRUE quando a diferença absoluta entre valor_total e valor_itens for maior que R$ 0,01. Caso contrário, marcar como FALSE (A6). |


---

## 2.4 Tabela itens_pedido

**Descrição:**  armazena os produtos e suas respectivas quantidades e preços dentro de cada pedido.

- **Chaves primárias (PK):** composta pelos campos `pedido_id` e `linha`, que juntos identificam unicamente cada item de um pedido.

- **Chave primária composta:** na tabela `itens_pedido`, é formada pelos campos `pedido_id` e `linha`.

- **Chaves estrangeiras (FK):**
  - `pedidos.cliente_id` referencia `clientes.id`.
  - `itens_pedido.pedido_id` referencia `pedidos.id`.
  - `itens_pedido.produto_id` referencia `produtos.produto_id`.

| Campo | Tipo | Admite Nulo? | Regra de Transformação  |
| :--- | :--- | :--- | :--- |
| `pedido_id` | `INTEGER` | Não | Identificar o pedido ao qual o item pertence. |
| `linha` | `INTEGER` | Não | Manter o número da linha do item dentro do pedido. |
| `produto_id` | `INTEGER` | Não | Identificar o produto correspondente no catálogo. |
| `quantidade` | `INTEGER` | Não | Converter para número inteiro, preservando a quantidade informada na origem. |
| `preco_unitario` | `NUMERIC(10,2)` | Não | Converter para valor numérico com duas casas decimais. |



---

## 3. Regras de transformação — Armadilhas A1 a A6

| Código | Problema identificado | Regra aplicada | 
| :--- | :--- | :--- | 
| A1 | Clientes com e-mail ausente. | Manter o cliente e gravar o e-mail como NULL. Contabilizar os e-mails nulos. |
| A2 | Estados com letras maiúsculas e minúsculas. | Padronizar todas as siglas de estado para maiúsculas. |
| A3 | Datas de pedidos em formatos diferentes. | Converter os formatos AAAA-MM-DD e DD/MM/AAAA para DATE.|
| A4 | Valores totais como números ou textos com vírgula decimal. | Converter todos os valores para números com duas casas decimais. |
| A5 | Pedidos repetidos em páginas diferentes da API.|  Remover duplicados pelo campo id, mantendo a primeira ocorrência. |
| A6 | Divergência entre o valor total e a soma dos itens. | Calcular valor_itens, comparar com valor_total e preencher divergente conforme a diferença. |


---

## 4. Regras de integridade e qualidade

* Cada cliente deve possuir um identificador único.
* Cada produto deve possuir um identificador único.
* Cada pedido deve possuir um identificador único.
* A combinação de pedido_id e linha deve ser única em itens_pedido.
* Todo pedido deve estar relacionado a um cliente existente.
* Todo item de pedido deve estar relacionado a um pedido e a um produto existentes.
* Pedidos repetidos não devem ser carregados mais de uma vez.
* A execução do ETL novamente não deve duplicar os registros já carregados.
* Os valores de valor_itens e valor_total devem ser armazenados separadamente para permitir a conferência das divergências.



---

## 5. Histórico de Alterações

| Versão | Data | Descrição da Alteração |
| :--- | :--- | :--- |
| `1.0` | 2026-11-23 | Criação inicial do contrato de dados com base no esquema PostgreSQL fornecido para o desafio Verdejar. |

