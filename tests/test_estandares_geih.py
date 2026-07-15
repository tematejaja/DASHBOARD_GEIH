from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.geografia_geih import AREA_A_DOMINIO, asignar_dominio


ROOT = Path(__file__).resolve().parents[1]


def cargar_modulo(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(modulo)
    return modulo


valor = cargar_modulo("indicadores_valor_agregado", ROOT / "src" / "03_indicadores_valor_agregado.py")
motor = cargar_modulo("motor_calculo", ROOT / "src" / "02_motor_calculo.py")


class TestGeografia(unittest.TestCase):
    def test_codigos_neiva_ibague(self):
        self.assertEqual(AREA_A_DOMINIO["41"], "Neiva")
        self.assertEqual(AREA_A_DOMINIO["73"], "Ibagué")
        self.assertEqual(len(AREA_A_DOMINIO), 32)

    def test_normalizacion_no_inventa_faltantes(self):
        resultado = asignar_dominio(pd.Series([41, "73", " 05 ", None, ""]))
        self.assertEqual(resultado.iloc[0], "Neiva")
        self.assertEqual(resultado.iloc[1], "Ibagué")
        self.assertEqual(resultado.iloc[2], "Medellín A.M.")
        self.assertTrue(pd.isna(resultado.iloc[3]))
        self.assertTrue(pd.isna(resultado.iloc[4]))


class TestEstandaresInternacionales(unittest.TestCase):
    def test_lu2_lu3_lu4(self):
        tasas = valor.calcular_tasas_subutilizacion(ft=100, ds=10, sih=5, ftp=20)
        self.assertAlmostEqual(tasas["LU2"], 15.0)
        self.assertAlmostEqual(tasas["LU3"], 25.0)
        self.assertAlmostEqual(tasas["LU4"], 35 / 120 * 100)

    def test_nini_oit_y_adaptacion_nacional(self):
        d = pd.DataFrame({col: [0, 0, 0] for col in valor.VARIABLES})
        d["AREA"] = [11, 11, 11]
        d["MES"] = 1
        d["FEX_C18"] = 1.0
        d["P6040"] = [24, 25, 28]
        d["P6170"] = 2
        d["OCI"] = 0
        d["DSI"] = 0
        d["FFT"] = 1
        preparado = valor._preparar_indicadores(d, 2025)
        self.assertEqual(preparado["nini_15_24"].tolist(), [True, False, False])
        self.assertEqual(preparado["nini"].tolist(), [True, True, True])


class TestInformalidad(unittest.TestCase):
    def _base(self, n=5):
        columnas = set(motor.VARIABLES_INFORMALIDAD_DANE) | {"OCI"}
        d = pd.DataFrame({col: np.zeros(n) for col in columnas})
        d["OCI"] = 1
        d["RAMA2D_R4"] = 10
        d["OFICIO_C8"] = 110
        d["P3069"] = 5
        return d

    def test_rutas_basicas_formal_informal(self):
        d = self._base()
        d["P6430"] = [2, 6, 1, 1, 4]

        d.loc[2, ["P3045S1", "P6100", "P6110", "P6920", "P6930", "P6940"]] = [1, 1, 1, 1, 1, 1]
        d.loc[3, ["P3045S1", "P3046", "P6100", "P6110", "P6920"]] = [2, 2, 3, 3, 2]
        d.loc[4, ["P6765", "P3065"]] = [0, 1]

        informal = motor.clasificar_ocupacion_informal_dane(d, 2025)
        self.assertEqual(informal.tolist(), [False, True, False, True, False])


if __name__ == "__main__":
    unittest.main()
