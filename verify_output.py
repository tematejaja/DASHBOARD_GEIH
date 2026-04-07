import pandas as pd

df = pd.read_csv('output/indicadores_mensuales.csv')

print('=== Verificacion del archivo indicadores_mensuales.csv ===')
for anio in sorted(df['Año'].unique()):
    meses = sorted(df[df['Año'] == anio]['MES'].unique())
    print(f'{anio}: {len(meses)} meses -> {meses}')

print()

# Bogota Enero 2025
row = df[(df['Año']==2025) & (df['MES']==1) & (df['Ciudad']=='Bogotá D.C.')]
if not row.empty:
    r = row.iloc[0]
    print(f"Bogota Ene 2025: TD={r['TD_%']:.2f}% (DANE=9.7)")

# Nacional Enero 2025
row_n = df[(df['Año']==2025) & (df['MES']==1) & (df['Ciudad']=='Todas (Panorama Nacional)')]
if not row_n.empty:
    r = row_n.iloc[0]
    print(f"Nacional Ene 2025: TD={r['TD_%']:.2f}%")

print()
print("=== Ciudades principales Dic 2025 ===")
ciudades_check = ['Bogotá D.C.', 'Medellín A.M.', 'Cali A.M.', 'Barranquilla A.M.', 'Bucaramanga A.M.']
for c in ciudades_check:
    row = df[(df['Año']==2025) & (df['MES']==12) & (df['Ciudad']==c)]
    if not row.empty:
        r = row.iloc[0]
        print(f"  {c}: TD={r['TD_%']:.2f}%  TO={r['TO_%']:.2f}%  TGP={r['TGP_%']:.2f}%")
