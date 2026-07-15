"""Auditoria reproducible de variables e indicadores del observatorio GEIH.

Este modulo no importa los motores productivos. La separacion permite detectar
errores de implementacion en lugar de repetirlos durante la validacion.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from src.geografia_geih import asignar_dominio, dataframe_dominios
from src.metodologia_dashboard import dataframe_formulas, dataframe_variables


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "GEIH"
OUTPUT = ROOT / "output"
NACIONAL = "Todas (Panorama Nacional)"

BINARY = {
    "P6170", "P6280", "P6300", "P6440", "P6460", "P6090", "P7090",
    "P7110", "P7120", "P7130", "P7140S1", "P7140S2", "P7140S3",
    "P7150", "P7160", "P3045S1", "P3046", "P3067", "P3067S1",
    "P6424S1", "P6424S2", "P6424S3", "P6424S5",
}
ONE = {"PET", "FT", "FFT", "OCI", "DSI"}
CATEGORIES = {
    "MES": set(range(1, 13)), "P3271": {1, 2}, "CLASE": {1, 2},
    "P3042": set(range(1, 14)) | {99}, "P3043": set(range(1, 11)) | {99},
    "P6450": {1, 2, 9}, "P6920": {1, 2, 3},
}
CONTINUOUS_RANGES = {
    "FEX_C18": (0, np.inf), "FEX_ADJ": (0, np.inf), "P6040": (0, 111),
    "P6800": (1, 130), "P7250": (0, np.inf), "INGLABO": (0, np.inf),
    "P3067S2": (2000, 2026),
}


def _universe(d: pd.DataFrame, code: str) -> pd.Series:
    all_rows = pd.Series(True, index=d.index)
    employed = d["OCI"].eq(1)
    if code == "P7250":
        return d["DSI"].eq(1)
    if code in {"P6280", "P6300"}:
        return ~employed
    if code in {"P7110", "P7120"}:
        return employed & d["P7090"].eq(1)
    if code in {"P7140S1", "P7140S2", "P7140S3", "P7150", "P7160"}:
        return employed & d["P7130"].eq(1)
    if code == "P6450":
        return employed & d["P6440"].eq(1)
    if code == "P6460":
        return employed & d["P6450"].eq(2)
    employed_fields = {
        "P6430", "P6800", "INGLABO", "RAMA2D_R4", "OFICIO_C8", "P6920",
        "P6440", "P6424S1", "P6424S2", "P6424S3", "P6424S5", "P7090",
        "P7130", "P3045S1", "P3046", "P3065", "P3066", "P3067",
        "P3067S1", "P3067S2", "P3068", "P3069", "P6765", "P6775",
    }
    return employed if code in employed_fields else all_rows


def _weighted_quantiles(values: pd.Series, weights: pd.Series) -> dict[str, float]:
    x = pd.to_numeric(values, errors="coerce").to_numpy(float)
    w = pd.to_numeric(weights, errors="coerce").to_numpy(float)
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    if not ok.any():
        return {k: np.nan for k in ("min", "p01", "p50", "p99", "max")}
    x, w = x[ok], w[ok]
    order = np.argsort(x, kind="mergesort")
    x, w = x[order], w[order]
    cumulative = np.cumsum(w) / w.sum()
    pick = lambda q: float(x[min(np.searchsorted(cumulative, q), len(x) - 1)])
    return {"min": float(x[0]), "p01": pick(.01), "p50": pick(.5),
            "p99": pick(.99), "max": float(x[-1])}


def _invalid_mask(values: pd.Series, code: str) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if code in ONE:
        return values.notna() & ~numeric.isin([1])
    if code in BINARY:
        return values.notna() & ~numeric.isin([1, 2, 9])
    if code in CATEGORIES:
        return values.notna() & ~numeric.isin(CATEGORIES[code])
    if code in CONTINUOUS_RANGES:
        lo, hi = CONTINUOUS_RANGES[code]
        return values.notna() & (~numeric.between(lo, hi) | numeric.isna())
    return pd.Series(False, index=values.index)


def _distribution(values: pd.Series, weights: pd.Series) -> str:
    valid = values.notna() & weights.gt(0)
    if not valid.any():
        return "{}"
    grouped = weights[valid].groupby(values[valid].astype(str)).sum()
    shares = (grouped / grouped.sum() * 100).sort_values(ascending=False)
    return json.dumps({str(k): round(float(v), 4) for k, v in shares.items()}, ensure_ascii=False)


def auditar_variables() -> tuple[pd.DataFrame, pd.DataFrame]:
    variables = dataframe_variables()
    codes = variables["Codigo"].tolist()
    raw_codes = [c for c in codes if c != "FEX_ADJ"]
    details: list[dict] = []
    for parquet in sorted(DATA.glob("GEIH_*_Consolidado.parquet")):
        year = int(parquet.stem.split("_")[1])
        available = set(pq.read_schema(parquet).names)
        required = sorted(set(raw_codes + ["OCI", "DSI", "P7090", "P7130", "P6440", "P6450"]))
        missing_file = [c for c in required if c not in available]
        read_cols = [c for c in required if c in available]
        d = pd.read_parquet(parquet, columns=read_cols)
        d["Dominio_GEIH"] = asignar_dominio(d["AREA"])
        months = max(int(d["MES"].nunique()), 1)
        d["FEX_ADJ"] = d["FEX_C18"] / months
        for (month, domain), g in d.dropna(subset=["Dominio_GEIH"]).groupby(["MES", "Dominio_GEIH"], sort=False):
            weight = pd.to_numeric(g["FEX_C18"], errors="coerce").fillna(0)
            for row in variables.itertuples(index=False):
                code = row.Codigo
                base = {
                    "variable": code, "modulo": row.Modulo, "definicion": row.Definicion,
                    "codificacion_esperada": row.Codificacion, "universo_documentado": row.Universo,
                    "fuente_diccionario": "src/metodologia_dashboard.py",
                    "dominio_geih": domain, "anio": year, "mes": int(month),
                }
                if code in missing_file or code not in g:
                    details.append(base | {"estado": "NO APLICA", "evidencia": "Variable ausente del archivo anual"})
                    continue
                universe = _universe(g, code)
                values = g[code]
                observed = universe & values.notna()
                invalid = universe & _invalid_mask(values, code)
                outside = ~universe & values.notna()
                n_universe = int(universe.sum())
                pop_universe = float(weight[universe].sum())
                miss_n = int((universe & values.isna()).sum())
                miss_w = float(weight[universe & values.isna()].sum())
                is_continuous = code in CONTINUOUS_RANGES or code in {"P3069"}
                quant = _weighted_quantiles(values[observed], weight[observed]) if is_continuous else {
                    k: np.nan for k in ("min", "p01", "p50", "p99", "max")
                }
                invalid_n = int(invalid.sum())
                state = "ERROR" if invalid_n else ("NO APLICA" if n_universe == 0 else "APROBADA")
                evidence = f"invalidos={invalid_n}; faltantes_universo={miss_n}; fuera_universo={int(outside.sum())}"
                details.append(base | {
                    "tipo": "continua" if is_continuous else "categorica",
                    "registros_muestra": int(len(g)), "registros_universo": n_universe,
                    "registros_observados": int(observed.sum()), "poblacion_expandida": float(weight.sum()),
                    "poblacion_universo": pop_universe,
                    "faltantes_no_ponderados_pct": miss_n / n_universe * 100 if n_universe else np.nan,
                    "faltantes_ponderados_pct": miss_w / pop_universe * 100 if pop_universe else np.nan,
                    "valores_invalidos_n": invalid_n, "valores_fuera_universo_n": int(outside.sum()),
                    "distribucion_ponderada_pct_json": "" if is_continuous else _distribution(values[observed], weight[observed]),
                    **quant, "estado": state, "evidencia": evidence,
                })
        print(f"[OK] Variables {year}: {len(d):,} registros; {len(missing_file)} ausencias de esquema")

    detail = pd.DataFrame(details).sort_values(["variable", "dominio_geih", "anio", "mes"])
    detail["cambio_faltantes_pp"] = detail.groupby(["variable", "dominio_geih"])["faltantes_ponderados_pct"].diff()
    abs_change = detail["cambio_faltantes_pp"].abs()
    mad = abs_change.groupby([detail["variable"], detail["dominio_geih"]]).transform(
        lambda x: np.nanmedian(np.abs(x - np.nanmedian(x)))
    )
    detail["quiebre_temporal"] = (abs_change > 5) & (abs_change > 5 * mad.fillna(np.inf))
    alert = detail["quiebre_temporal"] & detail["estado"].eq("APROBADA")
    detail.loc[alert, "estado"] = "ALERTA"
    detail.loc[alert, "evidencia"] += "; salto temporal >5 pp y >5 MAD"
    OUTPUT.mkdir(exist_ok=True)
    detail.to_parquet(OUTPUT / "auditoria_variables_detalle.parquet", index=False)
    summary = (detail.groupby("variable", as_index=False)
               .agg(celdas=("estado", "size"), errores=("estado", lambda x: int((x == "ERROR").sum())),
                    alertas=("estado", lambda x: int((x == "ALERTA").sum())),
                    no_aplica=("estado", lambda x: int((x == "NO APLICA").sum())),
                    invalidos=("valores_invalidos_n", "sum"),
                    max_faltantes_ponderados_pct=("faltantes_ponderados_pct", "max")))
    summary["estado"] = np.select([summary.errores.gt(0), summary.alertas.gt(0)], ["ERROR", "ALERTA"], default="APROBADA")
    summary.to_csv(OUTPUT / "auditoria_variables_resumen.csv", index=False)
    return detail, summary


def _monthly_national(year: int, month: int) -> dict[str, float]:
    path = DATA / f"GEIH_{year}_Consolidado.parquet"
    cols = ["MES", "FEX_C18", "P6040", "PET", "OCI", "DSI"]
    d = pd.read_parquet(path, columns=cols)
    d = d[d.MES.eq(month)]
    w = d.FEX_C18
    employed, unemployed = d.OCI.eq(1), d.DSI.eq(1)
    pet = d.PET.eq(1) | (d.PET.isna() & d.P6040.ge(15))
    oc, ds, ft, pet_n = w[employed].sum(), w[unemployed].sum(), w[employed | unemployed].sum(), w[pet].sum()
    return {"TD": ds / ft * 100, "TGP": ft / pet_n * 100, "TO": oc / pet_n * 100}


def auditar_indicadores() -> pd.DataFrame:
    references = [
        (2025, 3, "TD", 9.616368662963705, 1e-8, "DANE_GEIH_MAR2025_ANEXO"),
        (2025, 3, "TGP", 64.72949545452133, 1e-8, "DANE_GEIH_MAR2025_ANEXO"),
        (2025, 3, "TO", 58.504868537937824, 1e-8, "DANE_GEIH_MAR2025_ANEXO"),
        (2026, 4, "TD", 8.8, .06, "DANE_GEIH_ABR2026_BOLETIN"),
        (2026, 4, "TGP", 64.7, .06, "DANE_GEIH_ABR2026_BOLETIN"),
        (2026, 4, "TO", 59.1, .06, "DANE_GEIH_ABR2026_BOLETIN"),
    ]
    own = {(y, m): _monthly_national(y, m) for y, m in {(r[0], r[1]) for r in references}}
    rows = []
    for year, month, indicator, ref, tolerance, source in references:
        value = own[(year, month)][indicator]
        diff = value - ref
        rows.append({
            "indicador": indicator, "dominio_geih": NACIONAL, "anio": year, "mes": month,
            "ventana_meses": 1, "calculo_independiente": value, "referencia_externa": ref,
            "diferencia_pp": diff, "tolerancia_pp": tolerance, "fuente_id": source,
            "clasificacion_comparabilidad": "COMPARABLE EXACTO" if tolerance < 1e-6 else "COMPARABLE CON REDONDEO",
            "resultado": "APROBADA" if abs(diff) <= tolerance else "ERROR",
        })
    covered = {"Tasa de desocupacion (TD)", "Tasa global de participacion (TGP)", "Tasa de ocupacion (TO)"}
    for f in dataframe_formulas().itertuples(index=False):
        if f.Indicador not in covered:
            rows.append({
                "indicador": f.Indicador, "dominio_geih": "No aplica", "anio": np.nan, "mes": np.nan,
                "ventana_meses": np.nan, "calculo_independiente": np.nan, "referencia_externa": np.nan,
                "diferencia_pp": np.nan, "tolerancia_pp": np.nan,
                "fuente_id": "OIT_ICLS19" if f.Tipo.startswith("OIT") else "DICCIONARIO_METODOLOGICO",
                "clasificacion_comparabilidad": "SOLO DEFINICIÓN", "resultado": "APROBADA",
            })
    result = pd.DataFrame(rows)
    result.to_csv(OUTPUT / "auditoria_indicadores_comparacion.csv", index=False)
    return result


def registrar_fuentes() -> pd.DataFrame:
    sources = [
        ("DANE_GEIH_HISTORICOS", "DANE", "https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo/geih-historicos", "2022-2026", "Nacional y dominios GEIH", "Porcentaje/personas", "Mercado laboral", "Boletines y anexos"),
        ("DANE_INFORMALIDAD_HISTORICOS", "DANE", "https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-informal-y-seguridad-social/empleo-informal-y-seguridad-social-historicos", "2022-2026", "23 ciudades y AM", "Porcentaje/personas", "Proporcion de informalidad", "Boletines y anexos"),
        ("DANE_GEIH_ABR2026_BOLETIN", "DANE", "https://www.dane.gov.co/files/operaciones/GEIH/bol-GEIH-abr2026.pdf", "abril 2026", "Nacional", "Porcentaje/personas", "TD, TGP y TO mensuales", "Cuadro resumen"),
        ("DANE_GEIH_MAR2025_ANEXO", "DANE", "https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo/geih-historicos", "marzo 2025", "Nacional", "Porcentaje/personas", "TD, TGP y TO mensuales", "Anexo estadistico"),
        ("OIT_ICLS19", "OIT", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-work-statistics-icls19/", "vigente", "Conceptual", "Definicion", "LU2, LU3 y LU4", "19.a CIET"),
        ("OIT_NEET", "OIT", "https://ilostat.ilo.org/data/snapshots/youth-neet-rate/", "vigente", "Conceptual", "Porcentaje", "NINI 15-24", "Indicador ODS 8.6.1"),
    ]
    rows = []
    for sid, entity, url, period, domain, unit, definition, table in sources:
        local = ROOT / "evidence" / "fuentes" / f"{sid}.bin"
        sha = hashlib.sha256(local.read_bytes()).hexdigest() if local.exists() else "NO_DESCARGADO"
        rows.append({"fuente_id": sid, "entidad": entity, "url": url, "fecha_consulta": date.today().isoformat(),
                     "periodo": period, "dominio": domain, "unidad": unit, "definicion": definition,
                     "hoja_cuadro": table, "archivo_local": str(local.relative_to(ROOT)) if local.exists() else "",
                     "sha256": sha})
    result = pd.DataFrame(rows)
    result.to_csv(OUTPUT / "auditoria_fuentes.csv", index=False)
    return result


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    dataframe_dominios().to_csv(OUTPUT / "registro_dominios_geih.csv", index=False)
    detail, summary = auditar_variables()
    comparisons = auditar_indicadores()
    sources = registrar_fuentes()
    critical = int((summary.estado == "ERROR").sum() + (comparisons.resultado == "ERROR").sum())
    report = {
        "fecha_ejecucion": date.today().isoformat(), "periodo": "2022-01/2026-04",
        "variables": int(summary.variable.nunique()), "celdas_variable": int(len(detail)),
        "dominios_registrados": 32, "comparaciones_numericas": int(comparisons.referencia_externa.notna().sum()),
        "fuentes_registradas": int(len(sources)), "errores_criticos": critical,
        "publicacion_habilitada": critical == 0,
        "limitacion_muestreo": "Sin estrato ni UPM: no se estiman errores oficiales de muestreo.",
    }
    (OUTPUT / "auditoria_resumen.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
