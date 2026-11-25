import pytest
from etl.transformacao import (
    padronizar_data,
    transformar_valor_pedido,
    remover_repetidos,
)

from etl.transformacao import tratar_email, padronizar_estado, calcular_divergencia

# ---------- A3: data ----------
def test_padronizar_data():
    assert padronizar_data("24/11/2026") == "2026-11-24"


def test_data_dia_antes_do_mes():
    # 01/02 é 1º de fevereiro (dd/mm), não 2 de janeiro
    assert padronizar_data("01/02/2026") == "2026-02-01"


def test_data_ano_bissexto():
    assert padronizar_data("29/02/2024") == "2024-02-29"


def test_data_invalida_levanta_erro():
    # Especificação: data impossível não passa em silêncio
    with pytest.raises(ValueError):
        padronizar_data("31/02/2026")


# ---------- A4: valor com vírgula ----------
def test_transformar_valor_com_virgula():
    assert transformar_valor_pedido("125,84") == pytest.approx(125.84)


@pytest.mark.parametrize("entrada, esperado", [
    ("0,5", 0.5),
    ("100", 100.0),
])
def test_transformar_valor_variacoes(entrada, esperado):
    assert transformar_valor_pedido(entrada) == pytest.approx(esperado)


# ---------- A5: pedidos repetidos ----------
def test_remover_pedidos_repetidos():
    pedidos = [
        {"id": 1, "valor_total": 100},
        {"id": 2, "valor_total": 200},
        {"id": 1, "valor_total": 100},
    ]
    assert remover_repetidos(pedidos) == [
        {"id": 1, "valor_total": 100},
        {"id": 2, "valor_total": 200},
    ]


def test_sem_repetidos_nao_altera():
    pedidos = [{"id": 1, "valor_total": 10}, {"id": 2, "valor_total": 20}]
    assert remover_repetidos(pedidos) == pedidos


def test_lista_vazia():
    assert remover_repetidos([]) == []


def test_repetido_mantem_primeira_ocorrencia_e_ordem():
    pedidos = [
        {"id": 2, "valor_total": 200},
        {"id": 1, "valor_total": 100},
        {"id": 2, "valor_total": 999},  # repetido com valor diferente
    ]
    assert remover_repetidos(pedidos) == [
        {"id": 2, "valor_total": 200},
        {"id": 1, "valor_total": 100},
    ]


def test_email_vazio_vira_nulo():                      # A1
    assert tratar_email({"id": 1, "email": "  "})["email"] is None

def test_estado_minusculo_vira_maiusculo():            # A2
    assert padronizar_estado("rs") == "RS"

def test_pedido_divergente():                          # A6
    pedido = {"valor_total": "125,84",
              "itens": [{"quantidade": 3, "preco_unitario": 4.3},
                        {"quantidade": 5, "preco_unitario": 15.86},
                        {"quantidade": 4, "preco_unitario": 9.66}]}
    r = calcular_divergencia(pedido)
    assert r["valor_itens"] == pytest.approx(130.84)
    assert r["divergente"] is True