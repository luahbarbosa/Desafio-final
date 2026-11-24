import csv
import json
import os
import requests

BASE = "http://127.0.0.1:8000"


def extrair_rota(rota, page_size=50):
    registros = []
    pagina = 1
    total_paginas = None

    while total_paginas is None or pagina <= total_paginas:
        try:
            resp = requests.get(
                f"{BASE}/{rota}",
                params={"page": pagina, "page_size": page_size},
                timeout=10,
            )
        except requests.exceptions.ConnectionError:
            print(f"erro: sem conexao com a API em {BASE}")
            return registros

        if resp.status_code != 200:
            print(f"erro: {rota} pagina={pagina} status={resp.status_code}")
            break

        corpo = resp.json()
        if total_paginas is None:
            total_paginas = corpo["total_pages"]

        registros.extend(corpo["items"])
        pagina += 1

    print(f"extracao: {rota} paginas={total_paginas} registros={len(registros)}")
    return registros


if __name__ == "__main__":
    os.makedirs("brutos", exist_ok=True)
    for rota in ("clientes", "pedidos"):
        dados = extrair_rota(rota)
        with open(f"brutos/{rota}.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)

    with open("insumos/dados/produtos.csv", encoding="utf-8", newline="") as f:
        produtos = list(csv.DictReader(f))
    with open("brutos/produtos.json", "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False)
    print(f"extracao: produtos registros={len(produtos)}")