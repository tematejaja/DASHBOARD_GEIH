import pandas as pd
import numpy as np

def run_audit():
    ruta = "output/indicadores_mensuales.csv"
    print(f"--- Iniciando Auditoría Municipal: {ruta} ---")
    
    try:
        df = pd.read_csv(ruta)
    except FileNotFoundError:
        print("Error: No se encontró el archivo de indicadores.")
        return

    # 1. Verificación Algebraica: PEA = OC + DS
    df['PEA_Calc'] = df['Ocupados_M'] + df['Desocupados_M']
    df['Err_PEA'] = np.abs(df['PEA_Calc'] - df['PEA_M'])
    
    # 2. Verificación de Tasas
    df['TD_Calc'] = (df['Desocupados_M'] / df['PEA_M'] * 100).fillna(0)
    df['TGP_Calc'] = (df['PEA_M'] / df['PET_M'] * 100).fillna(0)
    df['TO_Calc'] = (df['Ocupados_M'] / df['PET_M'] * 100).fillna(0)
    
    df['Err_TD'] = np.abs(df['TD_Calc'] - df['TD_%'])
    df['Err_TGP'] = np.abs(df['TGP_Calc'] - df['TGP_%'])
    df['Err_TO'] = np.abs(df['TO_Calc'] - df['TO_%'])

    # Tolerar pequeñas diferencias por redondeo
    tol = 0.05 
    
    inconsistencias = df[
        (df['Err_PEA'] > 0.01) | 
        (df['Err_TD'] > tol) | 
        (df['Err_TGP'] > tol) | 
        (df['Err_TO'] > tol)
    ]

    print(f"Total registros auditados: {len(df)}")
    print(f"Inconsistencias algebraicas detectadas: {len(inconsistencias)}")
    
    if len(inconsistencias) > 0:
        print("\nDetalle de algunas inconsistencias (Tolerancia > 0.05%):")
        print(inconsistencias[['Año', 'MES', 'Ciudad', 'Err_PEA', 'Err_TD']].head(10))

    # 3. Detección de Municipios de Baja Precisión (DANE)
    # Como no tenemos CV en este CSV, usamos PEA_M < 0.03 (menos de 30 mil personas) como proxy de riesgo
    riesgo = df[df['PEA_M'] < 0.03] # Menos de 30 mil personas en el dominio
    print(f"\nRegistros con riesgo de baja precisión (Muestra pequeña): {len(riesgo)}")
    print(riesgo['Ciudad'].unique())

if __name__ == "__main__":
    run_audit()
