"""Auditoria automatica del diccionario y las identidades de calculo GEIH."""

from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from src.metodologia_dashboard import dataframe_formulas, dataframe_variables


ANIOS = [2022, 2023, 2024, 2025, 2026]
DERIVADAS = {"FEX_ADJ"}


def _max_error(estimado, esperado):
    valido = esperado.notna() & esperado.ne(0)
    return float((estimado[valido] - esperado[valido]).abs().max()) if valido.any() else 0.0


def main():
    variables = dataframe_variables()
    formulas = dataframe_formulas()
    assert not variables["Codigo"].duplicated().any(), "Codigos duplicados en el diccionario"
    assert not formulas["Indicador"].duplicated().any(), "Indicadores duplicados en formulas"

    codigos = set(variables["Codigo"])
    legacy_incorrectos = {"P6020", "P6210", "P6210S1", "FEX_C_2011", "ING_LAB", "RAMA2D_R12"}
    assert not codigos.intersection(legacy_incorrectos), "Persisten codigos del marco anterior"

    requeridas = codigos - DERIVADAS
    cobertura = {}
    identidades = {}
    for anio in ANIOS:
        ruta = f"GEIH/GEIH_{anio}_Consolidado.parquet"
        esquema = set(pq.read_schema(ruta).names)
        faltantes = sorted(requeridas - esquema)
        cobertura[str(anio)] = {"requeridas": len(requeridas), "faltantes": faltantes}
        assert not faltantes, f"{anio}: faltan variables documentadas: {faltantes}"

        d = pd.read_parquet(ruta, columns=["MES", "FEX_C18", "P6040", "PET", "FT", "FFT", "OCI", "DSI"])
        ft_logica = d["OCI"].eq(1) | d["DSI"].eq(1)
        pet_analitica = d["PET"].eq(1) | (d["PET"].isna() & d["P6040"].ge(15))
        errores_ft_crudo = int((d["FT"].eq(1) != ft_logica).sum())
        pet_faltante_reparada = int((d["PET"].isna() & d["P6040"].ge(15)).sum())
        ft_fuera_pet = int((ft_logica & ~pet_analitica).sum())
        solapamiento = int((d["OCI"].eq(1) & d["DSI"].eq(1)).sum())
        identidades[str(anio)] = {
            "FT_cruda_distinta_OCI_o_DSI": errores_ft_crudo,
            "PET_faltantes_reparados_con_edad": pet_faltante_reparada,
            "FT_analitica_fuera_PET_analitica": ft_fuera_pet,
            "OCI_y_DSI_simultaneos": solapamiento,
        }
        assert ft_fuera_pet == 0 and solapamiento == 0

    kpi = pd.read_csv("output/indicadores_mensuales.csv")
    errores_kpi = {
        "TD_pp": float((kpi["Desocupados_M"] / kpi["PEA_M"] * 100 - kpi["TD_%"]).abs().max()),
        "TGP_pp": float((kpi["PEA_M"] / kpi["PET_M"] * 100 - kpi["TGP_%"]).abs().max()),
        "TO_pp": float((kpi["Ocupados_M"] / kpi["PET_M"] * 100 - kpi["TO_%"]).abs().max()),
        "Informalidad_pp": float((kpi["Informales_M"] / kpi["Ocupados_M"] * 100 - kpi["Tasa_Informalidad_%"]).abs().max()),
    }
    assert max(errores_kpi.values()) < 1e-9

    valor = pd.read_csv("output/indicadores_valor_agregado.csv")
    reconstrucciones = {
        "Subocupacion_pp": valor["Subocupados_Pob"] / valor["FT_Pob"] * 100,
        "LU3_pp": (valor["SIH_Pob"] + valor["Desocupados_Pob"]) / valor["FT_Pob"] * 100,
        "LU4_pp": (valor["SIH_Pob"] + valor["Desocupados_Pob"] + valor["FTP_Pob"]) / (valor["FT_Pob"] + valor["FTP_Pob"]) * 100,
        "NINI_pp": valor["NINI_Pob"] / valor["Jovenes_15_28_Validos_Pob"] * 100,
        "Sobrecalificacion_pp": valor["Sobrecalificados_Pob"] / valor["Sobrecalificacion_Validos_Pob"] * 100,
    }
    columnas = {
        "Subocupacion_pp": "Tasa_Subocupacion_%", "LU3_pp": "Tasa_Subutilizacion_LU3_%",
        "LU4_pp": "Tasa_Subutilizacion_LU4_%", "NINI_pp": "Tasa_NINI_15_28_%",
        "Sobrecalificacion_pp": "Sobrecalificacion_%",
    }
    errores_valor = {k: _max_error(v, valor[columnas[k]]) for k, v in reconstrucciones.items()}
    assert max(errores_valor.values()) < 1e-9

    raw = pd.read_parquet("GEIH/GEIH_2025_Consolidado.parquet", columns=["MES", "FEX_C18", "P6040", "FT", "OCI", "DSI", "PET"])
    marzo = raw[raw["MES"].eq(3)]
    w = marzo["FEX_C18"]
    ft_marzo = marzo["OCI"].eq(1) | marzo["DSI"].eq(1)
    pet_marzo = marzo["PET"].eq(1) | (marzo["PET"].isna() & marzo["P6040"].ge(15))
    pob = {
        "FT_M": float(w[ft_marzo].sum() / 1e6),
        "OC_M": float(w[marzo["OCI"].eq(1)].sum() / 1e6),
        "DS_M": float(w[marzo["DSI"].eq(1)].sum() / 1e6),
        "PET_M": float(w[pet_marzo].sum() / 1e6),
    }
    pob["TD_%"] = pob["DS_M"] / pob["FT_M"] * 100
    pob["TGP_%"] = pob["FT_M"] / pob["PET_M"] * 100
    pob["TO_%"] = pob["OC_M"] / pob["PET_M"] * 100
    referencias = {"TD_%": 9.616368662963705, "TGP_%": 64.72949545452133, "TO_%": 58.504868537937824}
    diferencias = {k: abs(pob[k] - v) for k, v in referencias.items()}
    assert max(diferencias.values()) < 0.1

    resultado = {
        "estado": "APROBADO",
        "variables_documentadas": int(len(variables)),
        "indicadores_documentados": int(len(formulas)),
        "cobertura_por_anio": cobertura,
        "identidades_por_anio": identidades,
        "error_maximo_formulas_kpi_pp": errores_kpi,
        "error_maximo_formulas_valor_agregado_pp": errores_valor,
        "validacion_dane_marzo_2025": {"calculado": pob, "referencia": referencias, "diferencia_pp": diferencias},
        "nota_precision": "Los CV del tablero son aproximaciones MAS con DEFF fijo; no errores oficiales del diseno GEIH.",
    }
    os.makedirs("output", exist_ok=True)
    with open("output/auditoria_diccionario_logica.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
