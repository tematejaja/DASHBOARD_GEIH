import importlib.util
import pandas as pd
import glob
import os
from geih import ConfigGEIH, ConsolidadorGEIH, PreparadorGEIH

spec = importlib.util.spec_from_file_location('motor', 'src/02_motor_calculo.py')
motor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(motor)

referencia = {
    'Bogotá D.C.':       [9.7, 9.6, 9.6, 9.4, 9.3, 9.1, 9.0, 8.8, 8.8, 8.6, 8.5, 8.2],
    'Medellín A.M.':     [8.4, 8.1, 7.9, 7.8, 7.5, 7.4, 7.4, 7.3, 7.2, 7.2, 7.3, 7.4],
    'Cali A.M.':         [11.0, 10.8, 10.5, 10.2, 9.9, 9.7, 9.5, 9.3, 9.2, 9.1, 9.0, 8.7],
    'Barranquilla A.M.': [11.0, 11.1, 10.9, 10.8, 10.6, 10.4, 10.3, 10.1, 10.1, 10.0, 9.9, 9.8],
    'Bucaramanga A.M.':  [8.8, 8.8, 8.7, 8.8, 8.8, 8.7, 8.5, 8.4, 8.5, 8.4, 8.4, 8.4]
}

lista = []
for f in glob.glob('GEIH/GEIH_*_Consolidado.parquet'):
    anio = int(os.path.basename(f).split('_')[1])
    df_crudo = ConsolidadorGEIH.cargar(f)
    mes_col = df_crudo['MES'].copy()
    
    cfg = ConfigGEIH(anio=anio, n_meses=12)
    prep = PreparadorGEIH(config=cfg)
    df_prep = prep.preparar_base(df_crudo)
    df_prep = prep.agregar_variables_derivadas(df_prep)
    df_prep['MES'] = mes_col
    kpi = motor.calcular_kpi_ciudades(df_prep, anio, 12)
    lista.append(kpi)

df_all = pd.concat(lista, ignore_index=True)
df_all['Fecha'] = pd.to_datetime(df_all['Año'].astype(str) + '-' + df_all['MES'].astype(str) + '-01')
df_all = df_all.sort_values(by=['Ciudad', 'Fecha'])

for ciudad, target_vals in referencia.items():
    print(f'\\n--- CIUDAD: {ciudad} ---')
    g = df_all[df_all['Ciudad'] == ciudad].copy()
    g['TD_1m'] = (g['Desocupados_M'] / g['PEA_M']) * 100
    
    g['PEA_3m'] = g['PEA_M'].rolling(3, min_periods=3).sum() / 3
    g['Des_3m'] = g['Desocupados_M'].rolling(3, min_periods=3).sum() / 3
    g['TD_3m'] = (g['Des_3m'] / g['PEA_3m']) * 100
    
    g['PEA_12m'] = g['PEA_M'].rolling(12, min_periods=12).sum() / 12
    g['Des_12m'] = g['Desocupados_M'].rolling(12, min_periods=12).sum() / 12
    g['TD_12m'] = (g['Des_12m'] / g['PEA_12m']) * 100
    
    g_2025 = g[g['Año'] == 2025].sort_values('MES')
    print('M    | DANE | 1-Mes | Trim. | Año M.')
    for idx, row in g_2025.iterrows():
        m = int(row['MES'])
        if m <= 12:
            dane_val = target_vals[m-1]
            td1 = row['TD_1m']
            td3 = row['TD_3m']
            td12 = row['TD_12m']
            print(f'{m:02d}   | {dane_val:4.1f} | {td1:5.2f} | {td3:5.2f} | {td12:5.2f}')
