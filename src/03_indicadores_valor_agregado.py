"""Indicadores complementarios de subutilizacion y calidad laboral GEIH.

Las tasas se calculan con FEX_C18 y, desde el duodecimo periodo disponible,
corresponden a una ventana movil de 12 meses. Los primeros once periodos son
estimaciones mensuales. Se conservan numeradores y denominadores expandidos
para que cada resultado sea auditable.
"""

from __future__ import annotations

import argparse
import glob
import os
from collections import defaultdict

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from geih import AREA_A_CIUDAD, ConfigGEIH


CIUDAD_NACIONAL = "Todas (Panorama Nacional)"

VARIABLES = [
    "MES", "AREA", "FEX_C18", "P6040", "P6170", "OCI", "DSI", "FT", "FFT",
    "P6280", "P6300", "P7090", "P7110", "P7120", "P7130", "P7140S1",
    "P7140S2", "P7140S3", "P7150", "P7160", "P6800", "P7250", "P6430",
    "P6440", "P6450", "P6460", "P6424S1", "P6424S2", "P6424S3",
    "P6424S5", "P6920", "P3042", "OFICIO_C8", "INGLABO",
]

IPC_DIC_2018_100 = {
    2022: [113.26, 115.11, 116.26, 117.71, 118.70, 119.31, 120.27, 121.50, 122.63, 123.51, 124.46, 126.03],
    2023: [128.27, 130.40, 131.77, 132.80, 133.38, 133.78, 134.45, 135.39, 136.11, 136.45, 137.09, 137.72],
    2024: [138.98, 140.49, 141.48, 142.32, 142.92, 143.38, 143.67, 143.67, 144.02, 143.83, 144.22, 144.88],
    2025: [146.24, 147.90, 148.68, 149.66, 150.14, 150.30, 150.71, 150.99, 151.48, 151.76, 151.87, 152.27],
    2026: [154.07, 155.73, 156.94, 158.17, 158.91, 159.53],
}


def _capitales_por_area() -> dict[str, str]:
    return {
        codigo[:2]: ciudad
        for codigo, ciudad in AREA_A_CIUDAD.items()
        if len(codigo) == 5 and codigo[2:] == "001"
    }


def _suma_peso(df: pd.DataFrame, condicion: pd.Series) -> float:
    return float(df.loc[condicion.fillna(False), "FEX_C18"].sum())


def _mediana_ponderada(valores: np.ndarray, pesos: np.ndarray) -> float:
    validos = np.isfinite(valores) & np.isfinite(pesos) & (pesos > 0)
    if not validos.any():
        return np.nan
    valores = valores[validos]
    pesos = pesos[validos]
    orden = np.argsort(valores, kind="mergesort")
    valores = valores[orden]
    pesos = pesos[orden]
    return float(valores[np.searchsorted(np.cumsum(pesos), pesos.sum() / 2, side="left")])


def _nivel_educativo_cualificacion(p3042: pd.Series) -> pd.Series:
    """Aproxima niveles CINE a los cuatro niveles de cualificacion CIUO-08."""
    return p3042.map({
        1: 1, 2: 1, 3: 1,
        4: 2, 5: 2, 6: 2, 7: 2,
        8: 3, 9: 3,
        10: 4, 11: 4, 12: 4, 13: 4,
    }).astype("Float64")


def _nivel_ocupacion_ciuo(oficio: pd.Series) -> pd.Series:
    codigo = pd.to_numeric(oficio, errors="coerce").round().astype("Int64").astype("string").str.zfill(4)
    mayor = pd.to_numeric(codigo.str[0], errors="coerce")
    submayor = pd.to_numeric(codigo.str[:2], errors="coerce")
    nivel = pd.Series(np.nan, index=oficio.index, dtype="float64")
    nivel.loc[mayor.eq(1)] = 4
    nivel.loc[submayor.eq(14)] = 3
    nivel.loc[mayor.eq(2)] = 4
    nivel.loc[mayor.eq(3)] = 3
    nivel.loc[mayor.between(4, 8)] = 2
    nivel.loc[mayor.eq(9)] = 1
    return nivel


def _preparar_indicadores(df: pd.DataFrame, anio: int) -> pd.DataFrame:
    d = df.copy()
    d["Ciudad"] = d["AREA"].astype("string").str.strip().str.zfill(2).map(_capitales_por_area())
    # En algunos archivos 2025-2026 FT viene vacio para registros DSI=1.
    # La identidad oficial y el motor principal usan FT = OCI union DSI.
    d["ft_analitica"] = d["OCI"].eq(1) | d["DSI"].eq(1)

    # Subocupacion objetiva DANE: insuficiencia de horas o deseo de cambiar
    # para mejorar capacidades, ingresos o jornada, con gestion y disponibilidad.
    d["sih"] = (
        d["OCI"].eq(1) & d["P7090"].eq(1) & d["P7110"].eq(1)
        & d["P7120"].eq(1) & d["P6800"].le(48)
    )
    cambio_objetivo = (
        d["OCI"].eq(1) & d["P7130"].eq(1)
        & (d["P7140S1"].eq(1) | d["P7140S2"].eq(1) | d["P7140S3"].eq(1))
        & d["P7150"].eq(1) & d["P7160"].eq(1)
    )
    d["subocupado"] = d["sih"] | cambio_objetivo
    d["ftp"] = d["FFT"].eq(1) & (d["P6280"].eq(1) | d["P6300"].eq(1))

    d["duracion_valida"] = d["DSI"].eq(1) & d["P7250"].ge(0)
    d["desempleo_larga_duracion"] = d["duracion_valida"] & d["P7250"].ge(52)

    asalariado = d["OCI"].eq(1) & d["P6430"].isin([1, 2, 3, 7])
    contrato_escrito = asalariado & d["P6440"].eq(1) & d["P6450"].eq(2)
    prestaciones = asalariado & np.logical_and.reduce([
        d["P6424S1"].eq(1), d["P6424S2"].eq(1),
        d["P6424S3"].eq(1), d["P6424S5"].eq(1),
    ])
    cotiza_pension = d["OCI"].eq(1) & d["P6920"].eq(1)
    d["asalariado"] = asalariado
    d["contrato_escrito"] = contrato_escrito
    d["contrato_indefinido"] = contrato_escrito & d["P6460"].eq(1)
    d["prestaciones_completas"] = prestaciones
    d["cotiza_pension"] = cotiza_pension
    d["proteccion_integral"] = contrato_escrito & prestaciones & cotiza_pension

    joven = d["P6040"].between(15, 28) & d["P6170"].isin([1, 2])
    d["joven_valido"] = joven
    d["nini"] = joven & ~d["OCI"].eq(1) & d["P6170"].eq(2)
    d["nini_desocupado"] = d["nini"] & d["DSI"].eq(1)
    d["nini_fuera_ft"] = d["nini"] & ~d["ft_analitica"]

    nivel_educ = _nivel_educativo_cualificacion(d["P3042"])
    nivel_ocup = _nivel_ocupacion_ciuo(d["OFICIO_C8"])
    d["sobrecalif_valido"] = d["OCI"].eq(1) & nivel_educ.notna() & nivel_ocup.notna()
    d["sobrecalificado"] = d["sobrecalif_valido"] & nivel_educ.gt(nivel_ocup)

    smmlv = ConfigGEIH(anio=anio, n_meses=int(d["MES"].nunique())).smmlv
    d["ingreso_valido"] = d["OCI"].eq(1) & d["INGLABO"].gt(0)
    d["ingreso_bajo_smmlv"] = d["ingreso_valido"] & d["INGLABO"].lt(smmlv)
    return d


CONTEOS = {
    "FT": lambda d: d["ft_analitica"],
    "Desocupados": lambda d: d["DSI"].eq(1),
    "Ocupados": lambda d: d["OCI"].eq(1),
    "SIH": lambda d: d["sih"],
    "Subocupados": lambda d: d["subocupado"],
    "FTP": lambda d: d["ftp"],
    "Desocupados_Duracion_Valida": lambda d: d["duracion_valida"],
    "Desocupados_52_Semanas": lambda d: d["desempleo_larga_duracion"],
    "Asalariados": lambda d: d["asalariado"],
    "Contrato_Escrito": lambda d: d["contrato_escrito"],
    "Contrato_Indefinido": lambda d: d["contrato_indefinido"],
    "Prestaciones_Completas": lambda d: d["prestaciones_completas"],
    "Cotizantes_Pension": lambda d: d["cotiza_pension"],
    "Proteccion_Integral": lambda d: d["proteccion_integral"],
    "Jovenes_15_28_Validos": lambda d: d["joven_valido"],
    "NINI": lambda d: d["nini"],
    "NINI_Desocupados": lambda d: d["nini_desocupado"],
    "NINI_Fuera_FT": lambda d: d["nini_fuera_ft"],
    "Sobrecalificacion_Validos": lambda d: d["sobrecalif_valido"],
    "Sobrecalificados": lambda d: d["sobrecalificado"],
    "Ingresos_Validos": lambda d: d["ingreso_valido"],
    "Ingresos_Bajo_SMMLV": lambda d: d["ingreso_bajo_smmlv"],
}


def _resumir_dominio(d: pd.DataFrame, ciudad: str, anio: int) -> tuple[list[dict], dict, dict]:
    filas: list[dict] = []
    ingresos: dict = {}
    duraciones: dict = {}
    for mes, m in d.groupby("MES", sort=True):
        fila = {"Año": anio, "MES": int(mes), "Ciudad": ciudad}
        for nombre, condicion in CONTEOS.items():
            fila[nombre] = _suma_peso(m, condicion(m))
        filas.append(fila)

        mask_ing = m["ingreso_valido"]
        ipc = IPC_DIC_2018_100[anio][int(mes) - 1]
        ingresos[(ciudad, anio, int(mes))] = (
            m.loc[mask_ing, "INGLABO"].to_numpy(float) / (ipc / 100),
            m.loc[mask_ing, "FEX_C18"].to_numpy(float),
        )
        mask_dur = m["duracion_valida"]
        duraciones[(ciudad, anio, int(mes))] = (
            m.loc[mask_dur, "P7250"].to_numpy(float),
            m.loc[mask_dur, "FEX_C18"].to_numpy(float),
        )
    return filas, ingresos, duraciones


def _tasa(numerador: float, denominador: float) -> float:
    return numerador / denominador * 100 if denominador > 0 else np.nan


def _aplicar_ventanas(conteos: pd.DataFrame, ingresos: dict, duraciones: dict) -> pd.DataFrame:
    salida = []
    for ciudad, grupo in conteos.groupby("Ciudad", sort=False):
        grupo = grupo.sort_values(["Año", "MES"]).reset_index(drop=True)
        for i, fila in grupo.iterrows():
            inicio = i - 11 if i >= 11 else i
            ventana = grupo.iloc[inicio:i + 1]
            acumulado = ventana[list(CONTEOS)].sum()
            out = fila[["Año", "MES", "Ciudad"]].to_dict()
            out["Periodo_Meses"] = int(len(ventana))
            out.update({f"{k}_Pob": float(v) for k, v in acumulado.items()})

            out["Tasa_Subocupacion_%"] = _tasa(acumulado.Subocupados, acumulado.FT)
            out["Tasa_Insuficiencia_Horas_%"] = _tasa(acumulado.SIH, acumulado.FT)
            out["Tasa_Subutilizacion_LU3_%"] = _tasa(acumulado.SIH + acumulado.Desocupados, acumulado.FT)
            out["Tasa_Subutilizacion_LU4_%"] = _tasa(
                acumulado.SIH + acumulado.Desocupados + acumulado.FTP,
                acumulado.FT + acumulado.FTP,
            )
            out["Desempleo_Larga_Duracion_%"] = _tasa(acumulado.Desocupados_52_Semanas, acumulado.Desocupados_Duracion_Valida)
            out["Contrato_Escrito_%"] = _tasa(acumulado.Contrato_Escrito, acumulado.Asalariados)
            out["Contrato_Indefinido_%"] = _tasa(acumulado.Contrato_Indefinido, acumulado.Contrato_Escrito)
            out["Prestaciones_Completas_%"] = _tasa(acumulado.Prestaciones_Completas, acumulado.Asalariados)
            out["Cotiza_Pension_%"] = _tasa(acumulado.Cotizantes_Pension, acumulado.Ocupados)
            out["Proteccion_Integral_%"] = _tasa(acumulado.Proteccion_Integral, acumulado.Asalariados)
            out["Tasa_NINI_15_28_%"] = _tasa(acumulado.NINI, acumulado.Jovenes_15_28_Validos)
            out["NINI_Desocupados_%"] = _tasa(acumulado.NINI_Desocupados, acumulado.Jovenes_15_28_Validos)
            out["NINI_Fuera_FT_%"] = _tasa(acumulado.NINI_Fuera_FT, acumulado.Jovenes_15_28_Validos)
            out["Sobrecalificacion_%"] = _tasa(acumulado.Sobrecalificados, acumulado.Sobrecalificacion_Validos)
            out["Ingreso_Bajo_SMMLV_%"] = _tasa(acumulado.Ingresos_Bajo_SMMLV, acumulado.Ingresos_Validos)

            claves = [(ciudad, int(r["Año"]), int(r["MES"])) for _, r in ventana.iterrows()]
            vals_i = [ingresos[k][0] for k in claves if k in ingresos and len(ingresos[k][0])]
            pes_i = [ingresos[k][1] for k in claves if k in ingresos and len(ingresos[k][1])]
            out["Ingreso_Real_Mediano_COP_2018"] = _mediana_ponderada(np.concatenate(vals_i), np.concatenate(pes_i)) if vals_i else np.nan
            vals_d = [duraciones[k][0] for k in claves if k in duraciones and len(duraciones[k][0])]
            pes_d = [duraciones[k][1] for k in claves if k in duraciones and len(duraciones[k][1])]
            out["Duracion_Desempleo_Mediana_Semanas"] = _mediana_ponderada(np.concatenate(vals_d), np.concatenate(pes_d)) if vals_d else np.nan
            salida.append(out)
    return pd.DataFrame(salida)


def generar_indicadores(ruta_data: str = "GEIH", ruta_output: str = "output") -> pd.DataFrame:
    filas = []
    ingresos = {}
    duraciones = {}
    for parquet_path in sorted(glob.glob(os.path.join(ruta_data, "GEIH_*_Consolidado.parquet"))):
        anio = int(os.path.basename(parquet_path).split("_")[1])
        disponibles = set(pq.read_schema(parquet_path).names)
        faltantes = sorted(set(VARIABLES) - disponibles)
        if faltantes:
            raise ValueError(f"{parquet_path}: faltan variables requeridas: {', '.join(faltantes)}")
        print(f"[*] Indicadores de valor agregado {anio}")
        d = _preparar_indicadores(pd.read_parquet(parquet_path, columns=VARIABLES), anio)

        f, ing, dur = _resumir_dominio(d, CIUDAD_NACIONAL, anio)
        filas.extend(f); ingresos.update(ing); duraciones.update(dur)
        for ciudad, ciudad_df in d.dropna(subset=["Ciudad"]).groupby("Ciudad"):
            f, ing, dur = _resumir_dominio(ciudad_df, ciudad, anio)
            filas.extend(f); ingresos.update(ing); duraciones.update(dur)

    resultado = _aplicar_ventanas(pd.DataFrame(filas), ingresos, duraciones)
    os.makedirs(ruta_output, exist_ok=True)
    destino = os.path.join(ruta_output, "indicadores_valor_agregado.csv")
    resultado.to_csv(destino, index=False)
    print(f"[OK] {len(resultado):,} filas guardadas en {destino}")
    return resultado


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="GEIH")
    parser.add_argument("--output", default="output")
    args = parser.parse_args()
    generar_indicadores(args.data, args.output)
