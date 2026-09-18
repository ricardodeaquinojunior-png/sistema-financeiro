from datetime import datetime

def aplicar_mascara_data(event, var_texto):
    digitos = "".join(filter(str.isdigit, var_texto.get()))[:8]
    if len(digitos) > 4:
        formatado = f"{digitos[:2]}/{digitos[2:4]}/{digitos[4:]}"
    elif len(digitos) > 2:
        formatado = f"{digitos[:2]}/{digitos[2:]}"
    else:
        formatado = digitos
    var_texto.set(formatado)

def is_data_valida(valor):
    valor = valor.strip()
    if not valor:
        return True
    if len(valor) != 10:
        return False
    try:
        datetime.strptime(valor, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def aplicar_mascara_valor(event, var_texto):
    digitos = "".join(filter(str.isdigit, var_texto.get()))
    if not digitos:
        var_texto.set("0,00")
        return
    valor = float(digitos) / 100.0
    formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    var_texto.set(formatado)