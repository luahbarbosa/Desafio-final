import os

import psycopg
from dotenv import load_dotenv


def conectar():
    load_dotenv()
    return psycopg.connect(
        dbname="verdejar",
        user="postgres",
        password=os.environ["DB_PASSWORD"],
        host="localhost",
        port=5433,
    )


def carregar(produtos, clientes, pedidos):
    with conectar() as con:
        with con.cursor() as cur:

            # 1. Produtos
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

            # 2. Clientes
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

            # 3. Pedidos e seus itens
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

                # Remove os itens antigos deste pedido (evita duplicar na reexecucao)
                cur.execute(
                    "DELETE FROM itens_pedido WHERE pedido_id = %s",
                    (pedido["id"],),
                )

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

    total_itens = sum(len(pedido["itens"]) for pedido in pedidos)

    print(
        f"carga: clientes={len(clientes)} "
        f"produtos={len(produtos)} "
        f"pedidos={len(pedidos)} "
        f"itens_pedido={total_itens}"
    )


def reconciliar(pedidos):
    with conectar() as con:
        with con.cursor() as cur:
            cur.execute("SELECT COALESCE(SUM(valor_itens), 0) FROM pedidos")
            soma_destino = float(cur.fetchone()[0])

    soma_origem = round(sum(p["valor_itens"] for p in pedidos), 2)
    diferenca = abs(soma_origem - soma_destino)

    print(
        f"reconciliacao: soma_valor_itens_origem={soma_origem:.2f} "
        f"soma_valor_itens_destino={soma_destino:.2f} diferenca={diferenca:.2f}"
    )