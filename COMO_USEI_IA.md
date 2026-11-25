# Como usei IA

Como ainda não domino completamente o assunto, recorri à IA quando surgiram erros ou quando tive dificuldade para desenvolver algumas partes do código. Utilizei a ferramenta como apoio para entender os problemas e construir soluções, mas sempre procurando ler, compreender e comparar as sugestões com o que o desafio solicitava, além de testar se realmente funcionavam.

Ferramentas usadas: Claude (conversa no chat, para explicar o desafio, sugerir funções e revisar meu código) e GitHub Copilot (no editor).

## Sugestões aceitas

1. Estrutura do main.py (integrar extração, transformação e carga)

* Trecho pedido: como estruturar a execução do ETL, porque eu não entendia como ligar as etapas.
* Por que aceitei: a ordem proposta (extração, transformação, carga, reconciliação) é a mesma que o desafio descreve, e a extração vazia interrompe o programa com mensagem clara.
* Como validei: rodei o ETL duas vezes seguidas e as duas saídas saíram idênticas, com diferenca=0.00 na reconciliação.

2. remover_repetidos com um set de ids vistos (armadilha A5)

* Trecho pedido: uma função para descartar pedidos repetidos mantendo a primeira ocorrência.
* Por que aceitei: a minha primeira versão percorria a lista inteira para cada pedido, o que é lento com 5100 pedidos. O set consulta cada id de uma vez e preserva a ordem.
* Como validei: a saída mostrou pedidos_unicos=5000 repetidos_descartados=100, e há testes automatizados com repetido de valor diferente (mantém o primeiro) e lista vazia.

3. Divergência com tolerância de um centavo (armadilha A6)

* Trecho pedido: revisão da minha função de divergência, que comparava os valores com !=.
* Por que aceitei: comparar números decimais com igualdade exata dá falso positivo. O desafio pede divergente quando a diferença é maior que um centavo, e valor_itens precisa ser calculado a partir dos itens, não lido pronto.
* Como validei: conferi à mão o pedido 1 (3 x 4,30 + 5 x 15,86 + 4 x 9,66 = 130,84, contra 125,84 informado) e o banco tem 238 pedidos divergentes, o mesmo número do contador do ETL.


## Sugestões rejeitadas

1. Mudanças do GitHub Copilot na arquitetura medalhão

Estava tentando implementar uma arquitetura medalhão, mas tive dificuldade para organizar e mover os arquivos. Pedi ajuda ao GitHub Copilot para ajustar a estrutura como eu queria, porém ele começou a modificar partes do código que eu não pretendia alterar. Por isso, rejeitei as mudanças para preservar a organização e o funcionamento que eu já havia desenvolvido.

2. Limpar as tabelas antes da carga como estratégia de idempotência

* O que foi proposto: apagar as tabelas (na ordem inversa das chaves estrangeiras) antes de inserir, como a forma mais simples de não duplicar.
* Por que rejeitei: preferi atualizar os registros existentes com INSERT ... ON CONFLICT DO UPDATE, sem esvaziar as tabelas. Assim a carga pode ser repetida sem apagar o que já está no banco.
* O que fiz no lugar e como validei: upsert em produtos, clientes e pedidos, e remoção e reinserção dos itens de cada pedido. Rodei o ETL duas vezes e a contagem no banco ficou 1000 | 12 | 5000 | 12455 nas duas.

3. Biblioteca psycopg2 para conectar ao PostgreSQL

* O que foi proposto: usar psycopg2 no ETL e nos testes.
* Por que rejeitei: usei psycopg (versão 3) no carga.py. Manter duas bibliotecas no mesmo projeto confundia a explicação, então o teste de reconciliação passou a reutilizar a função conectar do próprio ETL.
* Como validei: o pytest passou com a conexão única (16 testes aprovados).

## Falhas e retrabalho

1. Chave errada no código de extração proposto pela IA

função de extração sugerida lia a lista de registros em corpo["dados"], mas a API devolve a lista em items. A IA tinha avisado que o nome era uma suposição. Descobri o nome real ao olhar a resposta de /clientes no Thunder Client e corrigi para items. Depois disso, a extração trouxe 1000 clientes e 5100 pedidos, como esperado.

2. API procurando os arquivos na pasta errada

Durante o desenvolvimento, tive dificuldade para executar a API. Inicialmente, o problema era que ela procurava os arquivos JSON na pasta errada. Consegui resolver informando o caminho correto com o comando:

bash
`python insumos/api_verdejar.py --dados insumos/dados'

3. Conteúdo do extracao.py apagado

Outra dificuldade aconteceu quando, sem perceber, apaguei o conteúdo do arquivo extracao.py e comecei a colocar a lógica de extração diretamente no main.py. Quando tentei executar o projeto, não consegui realizar a extração corretamente.

Pedi ajuda à IA para identificar o problema e percebi que havia organizado os arquivos de forma incorreta. Como já tinha enviado a versão anterior ao GitHub, recuperei o código de extracao.py por lá, criei novamente o main.py e organizei o código nos arquivos correspondentes.

Esse processo gerou retrabalho, mas me ajudou a entender melhor a responsabilidade de cada arquivo e a importância de manter a organização do projeto.
