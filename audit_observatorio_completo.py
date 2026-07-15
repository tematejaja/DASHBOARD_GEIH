"""Auditoria integral de coherencia estadistica de todas las salidas visibles."""

from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd


ANIOS = range(2022, 2027)
CIUDAD_NACIONAL = "Todas (Panorama Nacional)"


def max_abs(s):
    return float(s.abs().max()) if len(s) else 0.0


def validar_rango(df, columnas, minimo=0, maximo=100):
    for col in columnas:
        validos = df[col].dropna()
        assert validos.between(minimo, maximo).all(), f"{col} fuera de [{minimo}, {maximo}]"


def main():
    resumen = {"estado": "APROBADO", "pruebas": {}, "advertencias": []}

    # Mercado laboral e informalidad
    kpi = pd.read_csv("output/indicadores_mensuales.csv")
    assert not kpi.duplicated(["Año", "MES", "Ciudad"]).any()
    assert not kpi.isna().any().any()
    validar_rango(kpi, ["TD_%", "TGP_%", "TO_%", "Tasa_Informalidad_%"])
    errores_kpi = {
        "TD": max_abs(kpi["TD_%"] - kpi["Desocupados_M"] / kpi["PEA_M"] * 100),
        "TGP": max_abs(kpi["TGP_%"] - kpi["PEA_M"] / kpi["PET_M"] * 100),
        "TO": max_abs(kpi["TO_%"] - kpi["Ocupados_M"] / kpi["PET_M"] * 100),
        "informalidad": max_abs(kpi["Tasa_Informalidad_%"] - kpi["Informales_M"] / kpi["Ocupados_M"] * 100),
    }
    assert max(errores_kpi.values()) < 1e-8
    assert (kpi["Ocupados_M"] + kpi["Desocupados_M"] - kpi["PEA_M"]).abs().max() < 1e-8
    resumen["pruebas"]["mercado_laboral"] = {"filas": len(kpi), "error_maximo_pp": errores_kpi}

    # Presion y calidad laboral
    va = pd.read_csv("output/indicadores_valor_agregado.csv")
    assert not va.duplicated(["Año", "MES", "Ciudad"]).any()
    tasas_va = [c for c in va if c.endswith("_%")]
    validar_rango(va, tasas_va)
    formulas_va = {
        "subocupacion": max_abs(va["Tasa_Subocupacion_%"] - va["Subocupados_Pob"] / va["FT_Pob"] * 100),
        "LU2": max_abs(va["Tasa_Subutilizacion_LU2_%"] - (va["SIH_Pob"] + va["Desocupados_Pob"]) / va["FT_Pob"] * 100),
        "LU3": max_abs(va["Tasa_Subutilizacion_LU3_%"] - (va["Desocupados_Pob"] + va["FTP_Pob"]) / (va["FT_Pob"] + va["FTP_Pob"]) * 100),
        "LU4": max_abs(va["Tasa_Subutilizacion_LU4_%"] - (va["SIH_Pob"] + va["Desocupados_Pob"] + va["FTP_Pob"]) / (va["FT_Pob"] + va["FTP_Pob"]) * 100),
        "NINI": max_abs(va["Tasa_NINI_15_28_%"] - va["NINI_Pob"] / va["Jovenes_15_28_Validos_Pob"] * 100),
        "NINI_15_24": max_abs(va["Tasa_NINI_15_24_%"] - va["NINI_15_24_Pob"] / va["Jovenes_15_24_Validos_Pob"] * 100),
        "sobrecalificacion": max_abs(va["Sobrecalificacion_%"] - va["Sobrecalificados_Pob"] / va["Sobrecalificacion_Validos_Pob"] * 100),
    }
    assert max(formulas_va.values()) < 1e-8
    assert ((va["NINI_Desocupados_Pob"] + va["NINI_Fuera_FT_Pob"] - va["NINI_Pob"]).abs() < 1e-6).all()
    assert (va["NINI_15_24_Pob"] <= va["NINI_Pob"] + 1e-6).all()
    ingreso_sin_den = va["Ingreso_Bajo_SMMLV_%"].isna()
    assert va.loc[ingreso_sin_den, "Ingresos_Validos_Pob"].eq(0).all()
    resumen["pruebas"]["presion_calidad"] = {
        "filas": len(va), "error_maximo_pp": formulas_va,
        "tasas_no_estimables_por_denominador_cero": int(ingreso_sin_den.sum()),
    }

    resultados_anuales = {}
    for anio in ANIOS:
        ciudad_json = pd.read_json(f"output/ciudades_avanzado_resumen_{anio}.json")
        assert not ciudad_json["Ciudad"].duplicated().any()
        validar_rango(ciudad_json, ["Gini"], 0, 1)
        validar_rango(ciudad_json, ["Joven_TD_joven_%"])
        assert (ciudad_json["Joven_Ocupados_joven_M"] <= ciudad_json["Joven_PEA_joven_M"] + 1e-9).all()

        calidad = pd.read_csv(f"output/ciudades_calidad_empleo_{anio}.csv")
        vulnerabilidad = pd.read_csv(f"output/ciudades_vulnerabilidad_{anio}.csv")
        formalidad = pd.read_csv(f"output/ciudades_formalidad_sectorial_{anio}.csv")
        costos = pd.read_csv(f"output/ciudades_costo_laboral_{anio}.csv")
        brecha = pd.read_csv(f"output/ciudades_brecha_genero_{anio}.csv")
        mincer = pd.read_csv(f"output/ciudades_mincer_{anio}.csv")
        rama_sexo = pd.read_csv(f"output/ciudades_rama_sexo_{anio}.csv")

        tablas_rama = [calidad, vulnerabilidad, formalidad, costos, rama_sexo]
        for tabla in tablas_rama:
            assert {"n_muestra", "poblacion_estimada"}.issubset(tabla.columns)
            assert tabla["n_muestra"].ge(30).all()
            assert tabla["poblacion_estimada"].ge(5_000).all()

        validar_rango(calidad, ["ICE"])
        validar_rango(vulnerabilidad, ["IVI"])
        validar_rango(formalidad, ["ICF", "Cotiza_pension_%", "Ingreso_SML_%", "Afiliado_salud_%"])
        error_icf = max_abs(formalidad["ICF"] - formalidad[["Cotiza_pension_%", "Ingreso_SML_%", "Afiliado_salud_%"]].mean(axis=1))
        assert error_icf <= 0.11

        error_costo = max_abs(costos["Costo_efectivo_COP"] - costos["Mediana_COP"] * 1.54)
        assert error_costo <= 1
        error_brecha = max_abs(brecha["Brecha_%"] - (brecha["Mujeres"] - brecha["Hombres"]) / brecha["Hombres"] * 100)
        assert error_brecha < 1e-8
        assert brecha[["n_hombres", "n_mujeres"]].ge(30).all().all()

        assert max_abs(rama_sexo["Total"] - rama_sexo["Hombres"] - rama_sexo["Mujeres"]) < 1e-6
        sumas_dist = rama_sexo.groupby("Ciudad")["Dist_%"].sum()
        assert sumas_dist.between(99, 101).all()

        estimables = mincer["N"].ge(100)
        assert mincer.loc[estimables, ["beta_educacion", "beta_exp", "R2"]].notna().all().all()
        assert mincer.loc[~estimables, ["beta_educacion", "beta_exp", "R2"]].isna().all().all()
        assert mincer.loc[estimables, "R2"].between(0, 1).all()

        resultados_anuales[str(anio)] = {
            "dominios": int(ciudad_json["Ciudad"].nunique()),
            "ramas_calidad": len(calidad),
            "ramas_formalidad": len(formalidad),
            "brechas_publicables": len(brecha),
            "mincer_no_estimable": int((~estimables).sum()),
            "error_icf_pp": error_icf,
            "error_costo_cop": error_costo,
            "error_brecha_pp": error_brecha,
        }

    resumen["pruebas"]["indicadores_estructurales"] = resultados_anuales

    with open("app.py", "r", encoding="utf-8") as f:
        texto_app = f.read().lower()
    frases_genericas = ["inteligencia analítica", "radiografía estructural", "alto riesgo"]
    presentes = [frase for frase in frases_genericas if frase in texto_app]
    assert not presentes, f"Persisten expresiones editoriales problemáticas: {presentes}"
    resumen["pruebas"]["redaccion"] = {"frases_genericas_detectadas": presentes}

    os.makedirs("output", exist_ok=True)
    with open("output/auditoria_observatorio_completo.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
