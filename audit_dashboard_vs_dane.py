"""
AUDITORÍA EXHAUSTIVA: Lo que el dashboard MUESTRA vs DANE oficial.
Compara directamente el CSV que alimenta app.py contra la tabla de referencia.
"""
import pandas as pd
import numpy as np

# ============================================================
# 1. Cargar exactamente lo que el dashboard lee
# ============================================================
df = pd.read_csv('output/indicadores_mensuales.csv')
print(f"CSV cargado: {len(df)} filas, columnas: {df.columns.tolist()}")
print(f"Años: {sorted(df['Año'].unique())}")
print(f"Meses por año:")
for a in sorted(df['Año'].unique()):
    meses = sorted(df[df['Año']==a]['MES'].unique())
    print(f"  {a}: {len(meses)} meses -> {meses}")
print()

# ============================================================
# 2. Tabla DANE de referencia (proporcionada por el usuario)
# ============================================================
dane_ref = {
    'Bogotá D.C.':       [9.7, 9.6, 9.6, 9.4, 9.3, 9.1, 9.0, 8.8, 8.8, 8.6, 8.5, 8.2],
    'Medellín A.M.':     [8.4, 8.1, 7.9, 7.8, 7.5, 7.4, 7.4, 7.3, 7.2, 7.2, 7.3, 7.4],
    'Cali A.M.':         [11.0, 10.8, 10.5, 10.2, 9.9, 9.7, 9.5, 9.3, 9.2, 9.1, 9.0, 8.7],
    'Barranquilla A.M.': [11.0, 11.1, 10.9, 10.8, 10.6, 10.4, 10.3, 10.1, 10.1, 10.0, 9.9, 9.8],
    'Bucaramanga A.M.':  [8.8, 8.8, 8.7, 8.8, 8.8, 8.7, 8.5, 8.4, 8.5, 8.4, 8.4, 8.4],
    'Manizales A.M.':    [10.5, 10.4, 10.2, 10.0, 9.8, 9.6, 9.4, 9.2, 9.1, 9.0, 8.9, 8.8],
}

lines = []
lines.append("=" * 80)
lines.append("  AUDITORÍA: CSV del DASHBOARD vs DANE (Año Móvil 2025)")
lines.append("  Fuente: output/indicadores_mensuales.csv -> app.py")
lines.append("=" * 80)

total = 0
ok02 = 0
ok05 = 0
fail = 0
issues = []

for ciudad, vals_dane in dane_ref.items():
    lines.append(f"\n{'─'*60}")
    lines.append(f"  {ciudad}")
    lines.append(f"{'─'*60}")
    lines.append(f" Mes | DANE  | CSV   | Diff  | Estado")
    lines.append(f"─────┼───────┼───────┼───────┼────────")
    
    df_city = df[(df['Ciudad'] == ciudad) & (df['Año'] == 2025)].sort_values('MES')
    
    if df_city.empty:
        lines.append(f"  *** CIUDAD NO ENCONTRADA EN CSV ***")
        issues.append(f"Ciudad '{ciudad}' no existe en el CSV")
        continue
    
    for m in range(1, 13):
        dane_val = vals_dane[m-1]
        if dane_val is None:
            continue
            
        row = df_city[df_city['MES'] == m]
        if row.empty:
            lines.append(f"  {m:2d} | {dane_val:5.1f} |  N/A  |  N/A  | FALTA")
            issues.append(f"{ciudad} mes {m}: no existe en CSV")
            continue
        
        csv_val = row.iloc[0]['TD_%']
        if pd.isna(csv_val):
            lines.append(f"  {m:2d} | {dane_val:5.1f} |  NaN  |  N/A  | ERROR")
            issues.append(f"{ciudad} mes {m}: TD_% = NaN en CSV")
            continue
        
        diff = abs(dane_val - csv_val)
        total += 1
        
        if diff < 0.2:
            ok02 += 1
            ok05 += 1
            status = "✅ OK"
        elif diff < 0.5:
            ok05 += 1
            status = "⚠️ WARN"
        else:
            fail += 1
            status = "❌ FAIL"
            issues.append(f"{ciudad} mes {m}: DANE={dane_val}, CSV={csv_val:.2f}, diff={diff:.2f}")
        
        lines.append(f"  {m:2d} | {dane_val:5.1f} | {csv_val:5.2f} | {diff:5.2f} | {status}")

lines.append(f"\n{'='*80}")
lines.append(f"  RESUMEN GLOBAL:")
lines.append(f"    Total tests:           {total}")
lines.append(f"    ✅ OK   (diff < 0.2):   {ok02}/{total} ({ok02/total*100:.0f}%)" if total else "")
lines.append(f"    ⚠️  WARN (diff < 0.5):  {ok05}/{total} ({ok05/total*100:.0f}%)" if total else "")
lines.append(f"    ❌ FAIL (diff >= 0.5):  {fail}/{total}" if total else "")
lines.append(f"{'='*80}")

if issues:
    lines.append(f"\n  PROBLEMAS DETECTADOS:")
    for iss in issues:
        lines.append(f"    ⚠ {iss}")

# ============================================================
# 3. Verificar coherencia interna: TD = Des/PEA * 100
# ============================================================
lines.append(f"\n{'='*80}")
lines.append(f"  VERIFICACIÓN DE COHERENCIA INTERNA")
lines.append(f"{'='*80}")

df_2025 = df[(df['Año']==2025) & (df['Ciudad'] != 'Todas (Panorama Nacional)')]
inconsistencias = 0
for idx, row in df_2025.iterrows():
    if pd.notna(row['PEA_M']) and row['PEA_M'] > 0 and pd.notna(row['TD_%']):
        td_recalc = (row['Desocupados_M'] / row['PEA_M']) * 100
        diff_interna = abs(td_recalc - row['TD_%'])
        if diff_interna > 0.01:
            inconsistencias += 1
            if inconsistencias <= 5:
                lines.append(f"  {row['Ciudad']} M{int(row['MES'])}: TD_csv={row['TD_%']:.2f} vs recalc={td_recalc:.2f} (diff={diff_interna:.4f})")

if inconsistencias == 0:
    lines.append(f"  ✅ Todas las TD son coherentes con Des/PEA * 100")
else:
    lines.append(f"  ⚠ {inconsistencias} filas con TD inconsistente (primeras 5 mostradas arriba)")

# ============================================================
# 4. Verificar que el gráfico de barras usa los mismos datos
# ============================================================
lines.append(f"\n{'='*80}")
lines.append(f"  DATOS QUE VE EL GRÁFICO DE BARRAS (Dic 2025)")
lines.append(f"  (app.py línea 168-184: filtra Año+MES+Ciudad!=Nacional)")
lines.append(f"{'='*80}")

df_graf = df[(df['Año']==2025) & (df['MES']==12) & (df['Ciudad'] != 'Todas (Panorama Nacional)')].sort_values('TD_%', ascending=False)
lines.append(f" {'Ciudad':30s} | {'TD_%':>6s} | {'TO_%':>6s} | {'TGP_%':>6s}")
lines.append(f" {'─'*30}─┼────────┼────────┼────────")
for idx, row in df_graf.iterrows():
    td = f"{row['TD_%']:.2f}" if pd.notna(row['TD_%']) else "NaN"
    to = f"{row['TO_%']:.2f}" if pd.notna(row['TO_%']) else "NaN"
    tgp = f"{row['TGP_%']:.2f}" if pd.notna(row['TGP_%']) else "NaN"
    lines.append(f" {row['Ciudad']:30s} | {td:>6s} | {to:>6s} | {tgp:>6s}")

result = '\n'.join(lines)
with open('audit_dashboard_results.txt', 'w', encoding='utf-8') as f:
    f.write(result)
print(result)
