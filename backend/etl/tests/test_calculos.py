import unittest
from decimal import Decimal

from calculos import calcular_monto_total, calcular_igv


class TestCalculos(unittest.TestCase):

    def test_monto_normal(self):
        resultado = calcular_monto_total(3, "15.90")
        self.assertEqual(resultado, Decimal("47.70"))

    def test_monto_minimo(self):
        resultado = calcular_monto_total(1, "0.01")
        self.assertEqual(resultado, Decimal("0.01"))

    def test_monto_redondeo(self):
        resultado = calcular_monto_total(1, "10.005")
        self.assertEqual(resultado, Decimal("10.01"))

    def test_igv_normal(self):
        resultado = calcular_igv("200.00")
        self.assertEqual(resultado, Decimal("36.00"))

    def test_igv_minimo(self):
        resultado = calcular_igv("0.01")
        self.assertEqual(resultado, Decimal("0.00"))

    def test_igv_redondeo(self):
        resultado = calcular_igv("0.25")
        self.assertEqual(resultado, Decimal("0.05"))


if __name__ == "__main__":
    unittest.main()