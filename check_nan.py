import pandas as pd
df = pd.read_csv('output/indicadores_mensuales.csv')

# Check all cities at Dec 2025
d = df[(df['Año']==2025) & (df['MES']==12)]
print("Dic 2025 - Todas las ciudades:")
for idx, row in d.iterrows():
    td = row['TD_%']
    to = row['TO_%']
    tgp = row['TGP_%']
    pet = row['PET_M']
    td_str = f"{td:.2f}" if pd.notna(td) else "NaN"
    to_str = f"{to:.2f}" if pd.notna(to) else "NaN"
    tgp_str = f"{tgp:.2f}" if pd.notna(tgp) else "NaN"
    pet_str = f"{pet:.4f}" if pd.notna(pet) else "NaN"
    print(f"  {row['Ciudad']:30s} TD={td_str:>6s}  TO={to_str:>6s}  TGP={tgp_str:>6s}  PET={pet_str}")

print()
# Check for NaN
nan_count = df[['TD_%','TO_%','TGP_%']].isna().sum()
print("Valores NaN totales:")
print(nan_count)
