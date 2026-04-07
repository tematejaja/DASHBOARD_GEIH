"""
AUDITORIA EXHAUSTIVA FINAL - Que ve el usuario en el Dashboard?
Simula EXACTAMENTE la logica de app.py para cada combinacion de anno/mes/ciudad
y compara con la tabla oficial de referencia DANE.
"""
import pandas as pd, numpy as np

df = pd.read_csv('output/indicadores_mensuales.csv')

dane = {
    'Bogota D.C.':       [9.7, 9.6, 9.6, 9.4, 9.3, 9.1, 9.0, 8.8, 8.8, 8.6, 8.5, 8.2],
    'Medellin A.M.':     [8.4, 8.1, 7.9, 7.8, 7.5, 7.4, 7.4, 7.3, 7.2, 7.2, 7.3, 7.4],
    'Cali A.M.':         [11.0, 10.8, 10.5, 10.2, 9.9, 9.7, 9.5, 9.3, 9.2, 9.1, 9.0, 8.7],
    'Barranquilla A.M.': [11.0, 11.1, 10.9, 10.8, 10.6, 10.4, 10.3, 10.1, 10.1, 10.0, 9.9, 9.8],
    'Bucaramanga A.M.':  [8.8, 8.8, 8.7, 8.8, 8.8, 8.7, 8.5, 8.4, 8.5, 8.4, 8.4, 8.4],
    'Manizales A.M.':    [10.5, 10.4, 10.2, 10.0, 9.8, 9.6, 9.4, 9.2, 9.1, 9.0, 8.9, 8.8],
}

# Map accented names from CSV to our keys
city_map = {}
for csv_city in df['Ciudad'].unique():
    for key in dane:
        if key.replace('a D.C.','a D.C.').lower() in csv_city.lower() or csv_city.lower().startswith(key[:5].lower()):
            city_map[key] = csv_city
            break

# Better mapping
city_map = {}
csv_cities = df['Ciudad'].unique().tolist()
for key in dane:
    for cc in csv_cities:
        # normalize: remove accents conceptually
        if key[:6].lower().replace('o','o') == cc[:6].lower().replace('\u00f3','o').replace('\u00e1','a').replace('\u00e9','e').replace('\u00ed','i').replace('\u00fa','u'):
            city_map[key] = cc
            break

print("City mapping:")
for k, v in city_map.items():
    print(f"  {k} -> {v}")

out = []
out.append("="*90)
out.append("  AUDITORIA: QUE VE EL USUARIO EN EL DASHBOARD?")
out.append("="*90)

grand_ok = 0
grand_warn = 0
grand_fail = 0
grand_total = 0

visual_mismatches = []

for ciudad_key, vals in dane.items():
    csv_city = city_map.get(ciudad_key, ciudad_key)
    df_c = df[(df['Ciudad']==csv_city) & (df['Ano']==2025)].sort_values('MES') if 'Ano' in df.columns else df[(df['Ciudad']==csv_city) & (df['Ano']==2025)].sort_values('MES') if 'Ano' in df.columns else pd.DataFrame()
    
    # Try both column names
    year_col = 'Ano' if 'Ano' in df.columns else 'Año' if 'Año' in df.columns else None
    if year_col is None:
        print("ERROR: No year column found!")
        break
    
    df_c = df[(df['Ciudad']==csv_city) & (df[year_col]==2025)].sort_values('MES')
    
    out.append(f"\n  {csv_city}:")
    out.append(f"  {'Mes':>3s}  {'DANE':>6s}  {'CSV_raw':>8s}  {'Graf(.1f)':>9s}  {'Diff':>6s}  {'Veredicto':>10s}  {'Visual?'}")
    
    for m in range(1, 13):
        dane_v = vals[m-1]
        row = df_c[df_c['MES']==m]
        if row.empty:
            out.append(f"  {m:3d}  {dane_v:6.1f}  {'FALTA':>8s}  {'':>9s}  {'':>6s}  {'NO DATA':>10s}")
            continue
        
        csv_v = row.iloc[0]['TD_%']
        if pd.isna(csv_v):
            out.append(f"  {m:3d}  {dane_v:6.1f}  {'NaN':>8s}  {'':>9s}  {'':>6s}  {'NaN':>10s}")
            continue
        
        diff = abs(dane_v - csv_v)
        grand_total += 1
        
        if diff < 0.2:
            v = "OK"
            grand_ok += 1
        elif diff < 0.5:
            v = "WARN"
            grand_warn += 1
        else:
            v = "FAIL"
            grand_fail += 1
        
        # Visual check: what the bar chart label shows (.1f) vs DANE (.1f)
        graf_rounded = round(csv_v, 1)
        vis = "=" if graf_rounded == dane_v else f"DIFF({dane_v}->{graf_rounded})"
        if graf_rounded != dane_v:
            visual_mismatches.append((csv_city, m, dane_v, graf_rounded, diff))
        
        out.append(f"  {m:3d}  {dane_v:6.1f}  {csv_v:8.2f}  {graf_rounded:9.1f}  {diff:6.2f}  {v:>10s}  {vis}")

out.append(f"\n  RESUMEN:")
out.append(f"    Total={grand_total}  OK={grand_ok}  WARN={grand_warn}  FAIL={grand_fail}")
if grand_total > 0:
    out.append(f"    Precision <0.2pp: {grand_ok/grand_total*100:.0f}%  |  <0.5pp: {(grand_ok+grand_warn)/grand_total*100:.0f}%")

out.append(f"\n  DESAJUSTES VISUALES (grafico muestra .1f != DANE .1f):")
if visual_mismatches:
    for city, m, d, g, diff in visual_mismatches:
        out.append(f"    {city} M{m}: DANE={d} vs Grafico={g} (diff={diff:.2f})")
else:
    out.append(f"    Ninguno - todos coinciden visualmente")

# VERIFICACION 2: KPIs Nacional
out.append(f"\n{'='*90}")
out.append(f"  KPI CARDS (Nacional Dic 2025)")
out.append(f"{'='*90}")
year_col = [c for c in df.columns if c in ['Ano','Año']][0]
row_nac = df[(df[year_col]==2025) & (df['MES']==12) & (df['Ciudad']=='Todas (Panorama Nacional)')]
if not row_nac.empty:
    r = row_nac.iloc[0]
    out.append(f"  TD:  {r['TD_%']:.1f}%")
    out.append(f"  TGP: {r['TGP_%']:.1f}%" if pd.notna(r['TGP_%']) else "  TGP: NaN")
    out.append(f"  TO:  {r['TO_%']:.1f}%" if pd.notna(r['TO_%']) else "  TO: NaN")
    out.append(f"  Ocupados: {r['Ocupados_M']:.2f}M")
    out.append(f"  Desocupados: {r['Desocupados_M']:.2f}M")

# VERIFICACION 3: Coherencia interna
out.append(f"\n{'='*90}")
out.append(f"  COHERENCIA INTERNA: TD = Des/PEA * 100")
out.append(f"{'='*90}")
issues = 0
for idx, row in df.iterrows():
    if pd.notna(row['PEA_M']) and row['PEA_M'] > 0 and pd.notna(row['TD_%']):
        recalc = (row['Desocupados_M'] / row['PEA_M']) * 100
        diff = abs(recalc - row['TD_%'])
        if diff > 0.5:
            issues += 1
            if issues <= 10:
                out.append(f"  X: {row['Ciudad']} {int(row[year_col])} M{int(row['MES'])}: CSV={row['TD_%']:.2f} vs recalc={recalc:.2f}")
if issues == 0:
    out.append(f"  OK: 100% coherente (diff < 0.5)")
else:
    out.append(f"  WARN: {issues} filas incoherentes")

# VERIFICACION 4: Completitud meses
out.append(f"\n{'='*90}")
out.append(f"  MESES DISPONIBLES")
out.append(f"{'='*90}")
for yr in [2024, 2025]:
    nac = df[(df[year_col]==yr) & (df['Ciudad']=='Todas (Panorama Nacional)')].sort_values('MES')
    meses = nac['MES'].tolist()
    na_td = nac['TD_%'].isna().sum()
    na_to = nac['TO_%'].isna().sum()
    out.append(f"  {yr}: {len(meses)} meses {meses}  NaN: TD={na_td} TO={na_to}")

result = '\n'.join(out)
with open('audit_exhaustivo_results.txt', 'w', encoding='utf-8') as f:
    f.write(result)
print(result)
