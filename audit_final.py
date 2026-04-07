import importlib.util
import pandas as pd
import glob
import os
from geih import ConfigGEIH, ConsolidadorGEIH, PreparadorGEIH

spec = importlib.util.spec_from_file_location('motor', 'src/02_motor_calculo.py')
motor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(motor)

# Mapping exacto: nombre interno -> (nombre DANE display, valores referencia)
referencia = {
    'Bogotá D.C.':       [9.7, 9.6, 9.6, 9.4, 9.3, 9.1, 9.0, 8.8, 8.8, 8.6, 8.5, 8.2],
    'Medellín A.M.':     [8.4, 8.1, 7.9, 7.8, 7.5, 7.4, 7.4, 7.3, 7.2, 7.2, 7.3, 7.4],
    'Cali A.M.':         [11.0, 10.8, 10.5, 10.2, 9.9, 9.7, 9.5, 9.3, 9.2, 9.1, 9.0, 8.7],
    'Barranquilla A.M.': [11.0, 11.1, 10.9, 10.8, 10.6, 10.4, 10.3, 10.1, 10.1, 10.0, 9.9, 9.8],
    'Bucaramanga A.M.':  [8.8, 8.8, 8.7, 8.8, 8.8, 8.7, 8.5, 8.4, 8.5, 8.4, 8.4, 8.4],
    'Manizales A.M.':    [10.5, None, None, None, None, None, None, None, None, None, None, None],
}

lista = []
for f in sorted(glob.glob('GEIH/GEIH_*_Consolidado.parquet')):
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

lines = []
lines.append("=" * 70)
lines.append("   AUDITORIA: DASHBOARD vs DANE (Año Movil 2025)")
lines.append("=" * 70)

total_tests = 0
passed_02 = 0
passed_05 = 0

for ciudad, target_vals in referencia.items():
    if ciudad not in df_all['Ciudad'].unique():
        lines.append(f"[!] NO encontrada: {ciudad}")
        continue

    lines.append(f"")
    lines.append(f"--- {ciudad} ---")
    lines.append(f" Mes |  DANE |  Calc |  Diff | Estado")
    lines.append(f"-----+-------+-------+-------+--------")

    g = df_all[df_all['Ciudad'] == ciudad].copy()
    g['PEA_12m'] = g['PEA_M'].rolling(12, min_periods=12).sum() / 12
    g['Des_12m'] = g['Desocupados_M'].rolling(12, min_periods=12).sum() / 12
    g['TD_12m'] = (g['Des_12m'] / g['PEA_12m']) * 100

    g_2025 = g[g['Año'] == 2025].sort_values('MES')
    for idx, row in g_2025.iterrows():
        m = int(row['MES'])
        if m <= 12 and target_vals[m-1] is not None:
            dane_val = target_vals[m-1]
            calc_val = row['TD_12m']
            if pd.isna(calc_val):
                lines.append(f"  {m:2d} | {dane_val:5.1f} |   NaN |   N/A | SKIP")
                continue
            diff = abs(dane_val - calc_val)
            total_tests += 1
            if diff < 0.2:
                passed_02 += 1
                passed_05 += 1
                status = 'OK'
            elif diff < 0.5:
                passed_05 += 1
                status = 'WARN'
            else:
                status = 'FAIL'
            lines.append(f"  {m:2d} | {dane_val:5.1f} | {calc_val:5.2f} | {diff:5.2f} | {status}")

lines.append(f"")
lines.append(f"{'='*70}")
lines.append(f"  RESUMEN:")
lines.append(f"    Tests totales:       {total_tests}")
lines.append(f"    OK   (diff < 0.2pp): {passed_02}/{total_tests}")
lines.append(f"    WARN (diff < 0.5pp): {passed_05}/{total_tests}")
lines.append(f"    FAIL (diff >= 0.5):  {total_tests - passed_05}/{total_tests}")
lines.append(f"{'='*70}")

result = '\n'.join(lines)
with open('audit_results.txt', 'w', encoding='utf-8') as fout:
    fout.write(result)
print(result)
