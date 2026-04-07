import pandas as pd
import numpy as np
import statsmodels.api as sm
from geih import ConsolidadorGEIH, PreparadorGEIH, ConfigGEIH

print("Iniciando auditoria del modelo de Mincer...")
ruta_base = "GEIH"
config = ConfigGEIH(anio=2025, n_meses=12)

# Usamos el consolidado 2025
geih = ConsolidadorGEIH.cargar("GEIH_2025_Consolidado.parquet")
df = PreparadorGEIH(config=config).preparar_base(geih)
df = PreparadorGEIH(config=config).agregar_variables_derivadas(df)

# Filtrar población aplicable a mincer: Ocupados con ingreso mayor a cero
df_m = df[(df['OCI'] == 1) & (df['INGLABO'] > 0)].copy()

# Años de educación (Años aprobados = P3042 modificado o P3043)
# Vamos a extraer los años de educacion y edad como proxy
# En geih-analisis probablemente hacen: log(INGLABO) ~ educacion + experiencia (edad - educacion - 6)
df_m['ln_w'] = np.log(df_m['INGLABO'])

# Necesitamos definir educacion. En el DANE, P3042A (años aprobados). P3042 es nivel...
# Veamos qué columnas tiene df_m relacionadas a educacion
cols = df_m.columns.tolist()
if 'P3042A' not in cols: print("No P3042A. Usaremos EDUC_AÑOS si existe")

# Asumamos que geih_analisis usa una edad o educacion especifica
if 'P6040' in cols:
    df_m['edad'] = df_m['P6040']
else:
    df_m['edad'] = 30 # default si no hay

# Vamos a ver qué variables tiene df_m que sirvan.
print("Variables utiles Mincer encontradas:", [c for c in cols if c in ['P6040', 'P3042A', 'P3042', 'EDUC_AÑOS', 'P3271', 'SEXO', 'P3271', 'Cotiza_pension']])

# Extraer el codigo de la clase original EcuacionMincer de GEIH para ver qué hace
import inspect
from geih import EcuacionMincer
print("\n--- CODIGO ORIGINAL EcuacionMincer ---")
print(inspect.getsource(EcuacionMincer.estimar))

