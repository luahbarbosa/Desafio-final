
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def carregar(produtos, clientes, pedidos):
    with psycopg.connect(
        dbname="verdejar",
        user="postgres",
        password=os.environ["DB_PASSWORD"],
        host="localhost",
        port=5433,
    ) as con:

        with con.cursor() as cur:

             # 1. Carregar produtos
            for produto in produtos:
                cur.execute("""
                    INSERT INTO produtos
                    (produto_id, nome, categoria, preco_base)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (produto_id) DO UPDATE SET
                        nome = EXCLUDED.nome,
                        categoria = EXCLUDED.categoria,
                        preco_base = EXCLUDED.preco_base
                """, (
                    produto["produto_id"],
                    produto["nome"],
                    produto["categoria"],
                    produto["preco_base"],
                ))

            # 2. Carregar clientes
            for cliente in clientes:
                cur.execute("""
                    INSERT INTO clientes
                    (id, nome, email, cidade, estado, cadastro_em)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        nome = EXCLUDED.nome,
                        email = EXCLUDED.email,
                        cidade = EXCLUDED.cidade,
                        estado = EXCLUDED.estado,
                        cadastro_em = EXCLUDED.cadastro_em
                """, (
                    cliente["id"],
                    cliente["nome"],
                    cliente["email"],
                    cliente["cidade"],
                    cliente["estado"],
                    cliente["cadastro_em"],
                ))

            # 3. Carregar pedidos e seus itens
            for pedido in pedidos:
                cur.execute("""
                    INSERT INTO pedidos
                    (id, cliente_id, data_pedido, status,
                    valor_total, valor_itens, divergente)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        cliente_id = EXCLUDED.cliente_id,
                        data_pedido = EXCLUDED.data_pedido,
                        status = EXCLUDED.status,
                        valor_total = EXCLUDED.valor_total,
                        valor_itens = EXCLUDED.valor_itens,
                        divergente = EXCLUDED.divergente
                """, (
                    pedido["id"],
                    pedido["cliente_id"],
                    pedido["data_pedido"],
                    pedido["status"],
                    pedido["valor_total"],
                    pedido["valor_itens"],
                    pedido["divergente"],
            ))

                # Remover itens antigos desse pedido
                cur.execute(
                    "DELETE FROM itens_pedido WHERE pedido_id = %s",
                    (pedido["id"],)
                )

                # Carregar os itens do pedido atual
                for linha, item in enumerate(pedido["itens"], start=1):
                    cur.execute("""
                        INSERT INTO itens_pedido
                        (pedido_id, linha, produto_id, quantidade, preco_unitario)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        pedido["id"],
                        linha,
                        item["produto_id"],
                        item["quantidade"],
                        item["preco_unitario"],
                 ))

    total_itens = sum(
    len(pedido["itens"]) for pedido in pedidos
    )

    print(
        f"carga: clientes={len(clientes)} "
        f"produtos={len(produtos)} "
        f"pedidos={len(pedidos)} "
        f"itens_pedido={total_itens}"
    )