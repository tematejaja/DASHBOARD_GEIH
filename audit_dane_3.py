import importlib.util
import pandas as pd
import glob
import os
from geih import ConfigGEIH, ConsolidadorGEIH, PreparadorGEIH

spec = importlib.util.spec_from_file_location('motor', 'src/02_motor_calculo.py')
motor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(motor)

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

with open('audit_dane_results.md', 'w', encoding='utf-8') as f:
    f.write('# Auditoria DANE\n')
    for ciudad in df_all['Ciudad'].unique():
        if ciudad == 'Todas (Panorama Nacional)': continue
        f.write(f'\n## {ciudad}\n')
        g = df_all[df_all['Ciudad'] == ciudad].copy()
        g['TD_1m'] = (g['Desocupados_M'] / g['PEA_M']) * 100
        
        g['PEA_3m'] = g['PEA_M'].rolling(3, min_periods=3).sum() / 3
        g['Des_3m'] = g['Desocupados_M'].rolling(3, min_periods=3).sum() / 3
        g['TD_3m'] = (g['Des_3m'] / g['PEA_3m']) * 100
        
        g['PEA_12m'] = g['PEA_M'].rolling(12, min_periods=12).sum() / 12
        g['Des_12m'] = g['Desocupados_M'].rolling(12, min_periods=12).sum() / 12
        g['TD_12m'] = (g['Des_12m'] / g['PEA_12m']) * 100
        
        g_2025 = g[g['Año'] == 2025].sort_values('MES')
        f.write('MES | 1-Mes | Trim | Año Movil\n')
        f.write('--- | --- | --- | ---\n')
        for idx, row in g_2025.iterrows():
            m = int(row['MES'])
            if m <= 12:
                f.write(f"{m:02d} | {row['TD_1m']:5.2f} | {row['TD_3m']:5.2f} | {row['TD_12m']:5.2f}\n")
