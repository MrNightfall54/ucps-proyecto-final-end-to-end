from decimal import Decimal, ROUND_HALF_UP

CENTIMOS = Decimal("0.01")

# separar para aplicar test

def calcular_monto_total(cantidad, precio_unitario):
    return (
        Decimal(cantidad) * Decimal(precio_unitario)
    ).quantize(CENTIMOS, rounding=ROUND_HALF_UP)


def calcular_igv(monto_total):
    return (
        Decimal(monto_total) * Decimal("0.18")
    ).quantize(CENTIMOS, rounding=ROUND_HALF_UP)