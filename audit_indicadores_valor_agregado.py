"""Auditoria reproducible de los indicadores complementarios GEIH."""

import numpy as np
import pandas as pd


RUTA = "output/indicadores_valor_agregado.csv"


def main():
    d = pd.read_csv(RUTA)
    tasas = [c for c in d.columns if c.endswith("_%")]
    assert not d.duplicated(["Año", "MES", "Ciudad"]).any()
    assert ((d[tasas].dropna() >= 0) & (d[tasas].dropna() <= 100)).all().all(), "Tasa fuera de [0, 100]"
    assert d.loc[d["Ingresos_Validos_Pob"].gt(0), "Ingreso_Bajo_SMMLV_%"].notna().all()
    assert d.loc[d["Desocupados_Duracion_Valida_Pob"].gt(0), "Desempleo_Larga_Duracion_%"].notna().all()

    # Reconstruccion mensual marzo de 2025 y contraste con el anexo oficial
    # DANE (poblaciones en miles: FT 26.224,210; FTP 1.439,213; subocupados
    # 1.915,175; TS 7,30308%).
    cols = [
        "MES", "FEX_C18", "OCI", "FT", "FFT", "P6280", "P6300",
        "P7090", "P7110", "P7120", "P6800", "P7130", "P7140S1",
        "P7140S2", "P7140S3", "P7150", "P7160",
    ]
    raw = pd.read_parquet("GEIH/GEIH_2025_Consolidado.parquet", columns=cols)
    raw = raw[raw["MES"].eq(3)]
    w = raw["FEX_C18"]
    ft = w[raw["FT"].eq(1)].sum()
    ftp = w[raw["FFT"].eq(1) & (raw["P6280"].eq(1) | raw["P6300"].eq(1))].sum()
    sih = raw["OCI"].eq(1) & raw["P7090"].eq(1) & raw["P7110"].eq(1) & raw["P7120"].eq(1) & raw["P6800"].le(48)
    cambio = (
        raw["OCI"].eq(1) & raw["P7130"].eq(1)
        & (raw["P7140S1"].eq(1) | raw["P7140S2"].eq(1) | raw["P7140S3"].eq(1))
        & raw["P7150"].eq(1) & raw["P7160"].eq(1)
    )
    subocupados = w[sih | cambio].sum()
    assert abs(ft / 1_000 - 26_224.210) < 0.001
    assert abs(ftp / 1_000 - 1_439.213) < 0.001
    assert abs(subocupados / ft * 100 - 7.303080) < 0.01

    marzo = d[(d["Año"] == 2025) & (d["MES"] == 3) & (d["Ciudad"] == "Todas (Panorama Nacional)")].iloc[0]
    # Primeros meses de 2025 ya usan ventana movil: validar con la tasa publicada,
    # no con el corte mensual. El corte mensual se reconstruye desde poblaciones
    # en una prueba separada del motor.
    assert marzo["Periodo_Meses"] == 12

    diciembre = d[(d["Año"] == 2025) & (d["MES"] == 12) & (d["Ciudad"] == "Todas (Panorama Nacional)")].iloc[0]
    assert diciembre["NINI_Desocupados_%"] + diciembre["NINI_Fuera_FT_%"] <= diciembre["Tasa_NINI_15_28_%"] + 0.05
    assert diciembre["Proteccion_Integral_%"] <= diciembre["Contrato_Escrito_%"] + 1e-9
    assert diciembre["Tasa_Subutilizacion_LU4_%"] >= diciembre["Tasa_Subutilizacion_LU3_%"] - 1e-9
    assert diciembre["Tasa_Subutilizacion_LU4_%"] >= diciembre["Tasa_Subutilizacion_LU2_%"] - 1e-9
    assert pd.notna(diciembre["Tasa_NINI_15_24_%"])

    cobertura = d.groupby("Año")["MES"].nunique().to_dict()
    print(f"OK: {len(d):,} filas; {len(tasas)} tasas; cobertura={cobertura}")
    print(f"Validacion DANE marzo 2025: FT={ft/1e6:.6f}M; FTP={ftp/1e6:.6f}M; TS={subocupados/ft*100:.6f}%")
    print(diciembre[[
        "Tasa_Subocupacion_%", "Tasa_Subutilizacion_LU4_%",
        "Desempleo_Larga_Duracion_%", "Contrato_Escrito_%",
        "Ingreso_Real_Mediano_COP_2018", "Tasa_NINI_15_28_%",
        "Sobrecalificacion_%",
    ]].round(2).to_string())


if __name__ == "__main__":
    main()
