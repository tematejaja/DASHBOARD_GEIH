import unittest

import pandas as pd

from src.visualizacion_dashboard import prepare_rama_sexo, wrap_label


class TestVisualizacionRamaSexo(unittest.TestCase):
    def test_esquema_actual_convierte_a_millones_sin_alterar_totales(self):
        source = pd.DataFrame(
            {
                "RAMA": ["Servicios profesionales", "Comercio"],
                "Hombres": [1_200_000.0, 800_000.0],
                "Mujeres": [800_000.0, 700_000.0],
                "Total": [2_000_000.0, 1_500_000.0],
            }
        )
        result = prepare_rama_sexo(source, top_n=2)
        totals = result.groupby("Rama")["Personas_M"].sum().to_dict()
        self.assertEqual(totals, {"Comercio": 1.5, "Servicios profesionales": 2.0})
        self.assertEqual(set(result["Sexo"]), {"Hombres", "Mujeres"})

    def test_rechaza_identidad_poblacional_inconsistente(self):
        source = pd.DataFrame(
            {"RAMA": ["Comercio"], "Hombres": [10], "Mujeres": [5], "Total": [20]}
        )
        with self.assertRaisesRegex(ValueError, "no reproducen el total"):
            prepare_rama_sexo(source)

    def test_envuelve_sin_abreviar(self):
        label = "Actividades profesionales cientificas y tecnicas"
        wrapped = wrap_label(label, width=20)
        self.assertIn("<br>", wrapped)
        self.assertEqual(wrapped.replace("<br>", " "), label)


if __name__ == "__main__":
    unittest.main()
