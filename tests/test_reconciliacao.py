# tests/test_reconciliacao.py
import json
import os
import psycopg2
import pytest
from etl.transformacao import transformar_pedidos
from dotenv import load_dotenv

load_dotenv(".env", override=True)

def conectar():
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE", "verdejar"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST", "localhost"),
    )


def test_reconciliacao_origem_destino():
    with open("brutos/pedidos.json", encoding="utf-8") as f:
        brutos = json.load(f)
    tratados = transformar_pedidos(brutos)          # já sem repetidos
    contagem_origem = len(tratados)
    soma_origem = sum(p["valor_itens"] for p in tratados)

    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(valor_itens), 0) FROM pedidos")
    contagem_destino, soma_destino = cur.fetchone()
    con.close()

    assert contagem_destino == contagem_origem
    assert float(soma_destino) == pytest.approx(soma_origem, abs=0.01)


def test_soma_dos_meses_bate_com_soma_geral():     # teste de consulta
    con = conectar()
    cur = con.cursor()
    cur.execute("""SELECT COALESCE(SUM(total), 0) FROM (
                     SELECT SUM(valor_total) AS total
                     FROM pedidos GROUP BY DATE_TRUNC('month', data_pedido)) t""")
    soma_meses = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(valor_total), 0) FROM pedidos")
    soma_geral = cur.fetchone()[0]
    con.close()
    assert float(soma_meses) == pytest.approx(float(soma_geral), abs=0.01)