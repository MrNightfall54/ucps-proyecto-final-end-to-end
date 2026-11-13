import re
import unicodedata
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


CATEGORIAS = {
    "electro": "Electro",
    "ropa": "Ropa",
    "hogar": "Hogar",
    "tecnologia": "Tecnología",
    "calzado": "Calzado",
}

CENTIMOS = Decimal("0.01")


def limpiar_texto(valor):
    return " ".join(str(valor).strip().split())


def normalizar_categoria(valor):
    texto = limpiar_texto(valor).lower()

    texto = "".join(
        c for c in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(c)
    )

    return CATEGORIAS.get(texto)


def limpiar_precio(valor):
    texto = limpiar_texto(valor)

    texto = re.sub(
        r"(?i)(s/|pen|soles|\$)",
        "",
        texto
    ).replace(" ", "")

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")

    elif "," in texto:
        partes = texto.split(",")

        if len(partes) == 2 and len(partes[1]) <= 2:
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")

    try:
        numero = Decimal(texto)

        if not numero.is_finite():
            return None

        numero = numero.quantize(
            CENTIMOS,
            rounding=ROUND_HALF_UP
        )

        return numero if numero > 0 else None

    except (InvalidOperation, ValueError):
        return None


def limpiar_entero(valor):
    texto = limpiar_texto(valor)

    if not re.fullmatch(r"[+-]?\d+", texto):
        return None

    return int(texto)