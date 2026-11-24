
import csv
import json
import os

from .extracao import extrair_rota
from .transformacao import transformar_clientes, transformar_pedidos
from .carga import carregar


def salvar_bruto(nome, dados):
    os.makedirs("brutos", exist_ok=True)

    with open(f"brutos/{nome}.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False)


def main():
    # 1) Extração
    clientes_brutos = extrair_rota("clientes")
    pedidos_brutos = extrair_rota("pedidos")

    if not clientes_brutos or not pedidos_brutos:
        raise SystemExit("Extração vazia: confira se a API está rodando")

    # Leitura dos produtos CSV
    with open(
        "insumos/dados/produtos.csv",
        encoding="utf-8",
        newline=""
    ) as f:
        produtos = list(csv.DictReader(f))

    print(f"extração: produtos registros={len(produtos)}")

    # Salvar dados brutos
    salvar_bruto("clientes", clientes_brutos)
    salvar_bruto("pedidos", pedidos_brutos)
    salvar_bruto("produtos", produtos)

    # 2) Transformação
    clientes = transformar_clientes(clientes_brutos)
    pedidos = transformar_pedidos(pedidos_brutos)

    # 3) Carga
    carregar(produtos, clientes, pedidos)


if __name__ == "__main__":
    main()
