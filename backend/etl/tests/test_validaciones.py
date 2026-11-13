import unittest
from decimal import Decimal

from validaciones import (
    limpiar_texto,
    normalizar_categoria,
    limpiar_precio,
    limpiar_entero,
)


class TestValidaciones(unittest.TestCase):

    def test_limpiar_espacios(self):
        self.assertEqual(
            limpiar_texto("  Laptop         Gamer  "),
            "Laptop Gamer"
        )

    def test_categoria_mayusculas(self):
        self.assertEqual(
            normalizar_categoria("ROPA"),
            "Ropa"
        )

    def test_categoria_mayusculas(self):
            self.assertEqual(
                normalizar_categoria("HOgar"),
                "Hogar"
            )

    def test_categoria_tilde(self):
        self.assertEqual(
            normalizar_categoria("Tecnología"),
            "Tecnología"
        )

    def test_categoria_invalida(self):
        self.assertIsNone(
            normalizar_categoria("Alimentos")
        )

    def test_precio_soles(self):
        self.assertEqual(
            limpiar_precio("S/ 150.50"),
            Decimal("150.50")
        )

    def test_precio_coma_decimal(self):
        self.assertEqual(
            limpiar_precio("150,50"),
            Decimal("150.50")
        )

    def test_precio_negativo(self):
        self.assertIsNone(
            limpiar_precio("-50")
        )

    def test_precio_invalido(self):
        self.assertIsNone(
            limpiar_precio("abc")
        )

    def test_entero_valido(self):
        self.assertEqual(
            limpiar_entero("15"),
            15
        )

    def test_entero_decimal(self):
        self.assertIsNone(
            limpiar_entero("15.5")
        )

    def test_entero_texto(self):
        self.assertIsNone(
            limpiar_entero("abc")
        )


    def test_precio_formato_europeo(self):
        self.assertEqual(
            limpiar_precio("1.250,50"),
            Decimal("1250.50")
        )

    def test_precio_formato_americano(self):
        self.assertEqual(
            limpiar_precio("1,250.50"),
            Decimal("1250.50")
        )

    def test_precio_miles_con_coma(self):
        self.assertEqual(
            limpiar_precio("1,250"),
            Decimal("1250.00")
        )

    def test_precio_sin_separadores(self):
        self.assertEqual(
            limpiar_precio("1500"),
            Decimal("1500.00")
        )

    def test_precio_cero(self):
        self.assertIsNone(
            limpiar_precio("0")
        )

    def test_precio_nan(self):
        self.assertIsNone(
            limpiar_precio("NaN")
        )

    def test_precio_infinito(self):
        self.assertIsNone(
            limpiar_precio("Infinity")
        )

    def test_precio_vacio(self):
        self.assertIsNone(
            limpiar_precio("")
        )

    def test_precio_redondeo(self):
        self.assertEqual(
            limpiar_precio("10.005"),
            Decimal("10.01")
        )

    def test_precio_moneda_pen(self):
        self.assertEqual(
            limpiar_precio("PEN 150.50"),
            Decimal("150.50")
        )

    def test_entero_negativo(self):
        self.assertEqual(
            limpiar_entero("-5"),
            -5
        )

    def test_entero_con_signo_positivo(self):
        self.assertEqual(
            limpiar_entero("+10"),
            10
        )

    def test_categoria_con_espacios(self):
        self.assertEqual(
            normalizar_categoria("  TECNOLOGÍA  "),
            "Tecnología"
        )

if __name__ == "__main__":
    unittest.main()