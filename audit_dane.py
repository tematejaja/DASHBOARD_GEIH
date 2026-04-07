import pandas as pd
import numpy as np

# Datos proporcionados por el usuario
referencia = {
    'Bogotá D.C.':       [9.7, 9.6, 9.6, 9.4, 9.3, 9.1, 9.0, 8.8, 8.8, 8.6, 8.5, 8.2],
    'Medellín A.M.':     [8.4, 8.1, 7.9, 7.8, 7.5, 7.4, 7.4, 7.3, 7.2, 7.2, 7.3, 7.4],
    'Cali A.M.':         [11.0, 10.8, 10.5, 10.2, 9.9, 9.7, 9.5, 9.3, 9.2, 9.1, 9.0, 8.7],
    'Barranquilla A.M.': [11.0, 11.1, 10.9, 10.8, 10.6, 10.4, 10.3, 10.1, 10.1, 10.0, 9.9, 9.8],
    'Bucaramanga A.M.':  [8.8, 8.8, 8.7, 8.8, 8.8, 8.7, 8.5, 8.4, 8.5, 8.4, 8.4, 8.4]
}

# Cargar nuestra base cruda (sin ventanas) suponiendo que el archivo original se mantenía en all_kpis
# Pero output/indicadores_mensuales.csv tiene ya los datos absolutos mensuales originales porque
# los rellenamos con fillna. ¡Espera! Mi script previo (calcular_ventanas_moviles) reemplazó PEA_M y Desocupados_M
# por sus promedios móviles si existían 12 periodos!
# OUCH. Eso significa que 'indicadores_mensuales.csv' ya no tiene los ABSOLUTOS de 1 mes puro para calcular trimestre.
# Debemos regenerar los datos limpios en memoria o desde logs reales.

# Para simplificar, leemos de los parquet generados.
# ¡Este es el proceso de auditoría profunda!
print("====== AUDITORÍA PROFUNDA DE CIFRAS GEIH vs REFERENCIA ======")
print("Leyendo Parquets de 2024 y 2025 para obtener valores limpios del mes...")
from geih import ConfigGEIH, ConsolidadorGEIH, PreparadorGEIH

def get_kpis_base():
    import glob
    import os
    from src.02_motor_calculo import calcular_kpi_ciudades
    archivos = glob.glob('GEIH/GEIH_*_Consolidado.parquet')
    lista = []
    for f in archivos:
        anio = int(os.path.basename(f).split('_')[1])
        df_crudo = ConsolidadorGEIH.cargar(f)
        mes_col = df_crudo['MES'].copy()
        
        cfg = ConfigGEIH(anio=anio, n_meses=12)
        prep = PreparadorGEIH(config=cfg)
        df_prep = prep.preparar_base(df_crudo)
        df_prep = prep.agregar_variables_derivadas(df_prep)
        df_prep['MES'] = mes_col
        # calcular_kpi_ciudades original NO calcula móvil, da puramente el mes (escalado x12).
        # Multiplicamos / sumamos, da el mes exacto normalizado.
        kpi = calcular_kpi_ciudades(df_prep, anio, 12)
        lista.append(kpi)
    
    return pd.concat(lista, ignore_index=True)

df_all = get_kpis_base()

# Asegurar orden
df_all['Fecha'] = pd.to_datetime(df_all['Año'].astype(str) + '-' + df_all['MES'].astype(str) + '-01')
df_all = df_all.sort_values(by=['Ciudad', 'Fecha'])

for ciudad, target_vals in referencia.items():
    print(f"\n--- CIUDAD: {ciudad} ---")
    g = df_all[df_all['Ciudad'] == ciudad].copy()
    
    # 1 MES
    g['TD_1m'] = (g['Desocupados_M'] / g['PEA_M']) * 100
    
    # Trimestre Móvil (3 m)
    g['PEA_3m'] = g['PEA_M'].rolling(3).sum() / 3
    g['Des_3m'] = g['Desocupados_M'].rolling(3).sum() / 3
    g['TD_3m'] = (g['Des_3m'] / g['PEA_3m']) * 100
    
    # Año Móvil (12 m)
    g['PEA_12m'] = g['PEA_M'].rolling(12).sum() / 12
    g['Des_12m'] = g['Desocupados_M'].rolling(12).sum() / 12
    g['TD_12m'] = (g['Des_12m'] / g['PEA_12m']) * 100
    
    g_2025 = g[g['Año'] == 2025].sort_values('MES')
    
    print("M    | DANE | 1-Mes | Trim. | Año M.")
    print("---------------------------------------")
    for idx, row in g_2025.iterrows():
        m = int(row['MES'])
        if m <= 12:
            dane_val = target_vals[m-1]
            td1 = row['TD_1m']
            td3 = row['TD_3m']
            td12 = row['TD_12m']
            print(f"{m:02d}   | {dane_val:4.1f} | {td1:5.2f} | {td3:5.2f} | {td12:5.2f}")
