from datetime import datetime



def tratar_email(cliente):  #A1
    novo = dict(cliente)
    email = novo.get("email")
    if email is None or str(email).strip() == "":
        novo["email"] = None
    else:
        novo["email"] = str(email).strip()
    return novo



def padronizar_estado(sigla):  #A2
    if sigla:
        return sigla.upper()
    return sigla



def padronizar_data(data):  #A3
    if not data:
        return None
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(data, formato).strftime("%Y-%m-%d")
        except ValueError:
            pass
    raise ValueError(f"data invalida: {data}")



def transformar_valor_pedido(valor):  #A4
    if valor is None:
        return None
    if isinstance(valor, str):
        valor = valor.replace(",", ".")
    return round(float(valor), 2)



def remover_repetidos(pedidos):  #A5
    vistos = set()
    unicos = []
    for pedido in pedidos:
        if pedido["id"] not in vistos:
            vistos.add(pedido["id"])
            unicos.append(pedido)
    repetidos = len(pedidos) - len(unicos)
    print(f"transformacao: pedidos_unicos={len(unicos)} repetidos_descartados={repetidos}")
    return unicos



def calcular_divergencia(pedido):  #A6
    novo = dict(pedido)
    novo["valor_total"] = transformar_valor_pedido(pedido["valor_total"])
    novo["valor_itens"] = round(
        sum(i["quantidade"] * i["preco_unitario"] for i in pedido["itens"]), 2
    )
    novo["divergente"] = abs(novo["valor_total"] - novo["valor_itens"]) > 0.01
    return novo


# Aplicação 
def transformar_clientes(clientes):
    tratados = []
    emails_nulos = 0
    estados_padronizados = 0
    for c in clientes:
        t = tratar_email(c)
        if t["email"] is None:
            emails_nulos += 1

        estado_original = t["estado"]
        t["estado"] = padronizar_estado(estado_original)
        if t["estado"] != estado_original:
            estados_padronizados += 1

        tratados.append(t)
    print(f"transformacao: emails_nulos={emails_nulos} estados_padronizados={estados_padronizados}")
    return tratados


def transformar_pedidos(pedidos):
    unicos = remover_repetidos(pedidos)

    tratados = []
    datas_convertidas = 0
    valores_convertidos = 0
    divergentes = 0

    for p in unicos:
        novo = dict(p)
        novo["data_pedido"] = padronizar_data(p["data_pedido"])
        datas_convertidas += 1
        novo = calcular_divergencia(novo)
        valores_convertidos += 1
        if novo["divergente"]:
            divergentes += 1
        tratados.append(novo)

    print(f"transformacao: datas_convertidas={datas_convertidas} valores_convertidos={valores_convertidos}")
    print(f"divergentes: {divergentes} pedidos com valor_total diferente da soma dos itens")
    return tratados