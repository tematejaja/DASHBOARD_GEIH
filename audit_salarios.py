import pandas as pd

print("=== SALARIOS POR RAMA Y CIUDAD (output/salarios_por_rama_ciudad.csv) ===")
try:
    df_sal = pd.read_csv("output/salarios_por_rama_ciudad.csv")
    # Mostrar estadisticas a nivel nacional (sumarizando las ciudades o viendo si hay algo consolidado)
    print("Columnas:", df_sal.columns.tolist())
    print(df_sal.head(10))
    
    # Veamos Medellín en Diciembre 2025
    df_med_dec = df_sal[(df_sal['Ciudad'] == 'Medellín') & (df_sal['MES'] == 12) & (df_sal['Año'] == 2025)]
    print("\nMedellín Diciembre 2025:")
    print(df_med_dec)
    
except Exception as e:
    print("Error:", e)

print("\n=== COSTO LABORAL NACIONAL (output/nacional_costo_laboral_2025.csv) ===")
try:
    df_costo = pd.read_csv("output/nacional_costo_laboral_2025.csv")
    print("Columnas:", df_costo.columns.tolist())
    print(df_costo.head(10))
except Exception as e:
    print("Error:", e)

print("\n=== MINCER NACIONAL (output/nacional_mincer_2025.csv) ===")
try:
    df_mincer = pd.read_csv("output/nacional_mincer_2025.csv")
    print("Columnas:", df_mincer.columns.tolist())
    print(df_mincer)
except Exception as e:
    print("Error:", e)
