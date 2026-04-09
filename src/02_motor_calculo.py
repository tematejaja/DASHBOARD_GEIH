import os
import argparse
import pandas as pd
import glob
from geih import (
    ConfigGEIH, ConsolidadorGEIH, PreparadorGEIH,
    IndicadoresLaborales, AnalisisSalarios,
    AREA_A_CIUDAD,
    BrechaGenero, IndicesCompuestos,
    CostoLaboral, FormalidadSectorial, FuerzaLaboralJoven,
    CalidadEmpleo, VulnerabilidadLaboral, EcuacionMincer, AnalisisRamaSexo
)
import json

def calcular_kpi_ciudades(df, anio, n_meses_config):
    # AREA en el dataset contiene códigos DANE de departamento (2 dígitos: '05', '11', etc.)
    # AREA_A_CIUDAD contiene códigos municipales de 5 dígitos ('05001' -> 'Medellín')
    # Para capitales: DPTO + '001' = código capital departamental
    DPTO_A_CAPITAL = {code[:2]: ciudad for code, ciudad in AREA_A_CIUDAD.items() if code[2:] == '001'}
    
    df_ciudades = df.copy()
    df_ciudades['Ciudad'] = df_ciudades['AREA'].astype(str).str.zfill(2).map(DPTO_A_CAPITAL)
    df_ciudades = df_ciudades.dropna(subset=['Ciudad'])
    
    if 'MES' not in df_ciudades.columns:
        df_ciudades['MES'] = 1 # Fallback

    # Al agrupar por mes individual, si FEX_ADJ fue dividido por n_meses para totales anuales,
    # debemos multiplicarlo de vuelta para obtener el volumen demográfico real de ESE mes concreto.
    pea = df_ciudades[df_ciudades['OCI'].eq(1) | df_ciudades['DSI'].eq(1)].groupby(['Ciudad', 'MES'])['FEX_ADJ'].sum() * n_meses_config
    desocupados = df_ciudades[df_ciudades['DSI'].eq(1)].groupby(['Ciudad', 'MES'])['FEX_ADJ'].sum() * n_meses_config
    ocupados = df_ciudades[df_ciudades['OCI'].eq(1)].groupby(['Ciudad', 'MES'])['FEX_ADJ'].sum() * n_meses_config
    pet = df_ciudades[df_ciudades['PET'].eq(1)].groupby(['Ciudad', 'MES'])['FEX_ADJ'].sum() * n_meses_config
    
    res = pd.DataFrame({
        'PET_M': pet / 1000000,
        'Ocupados_M': ocupados / 1000000,
        'Desocupados_M': desocupados / 1000000,
        'PEA_M': pea / 1000000
    })
    
    res['TD_%'] = (res['Desocupados_M'] / res['PEA_M']) * 100
    res['TGP_%'] = (res['PEA_M'] / res['PET_M']) * 100
    res['TO_%'] = (res['Ocupados_M'] / res['PET_M']) * 100
    res['Año'] = anio
    
    return res.reset_index()

def calcular_kpi_nacional(df, anio, n_meses_config):
    df_nacional = df.copy()
    if 'MES' not in df_nacional.columns:
        df_nacional['MES'] = 1 # Fallback
        
    pea = df_nacional[df_nacional['OCI'].eq(1) | df_nacional['DSI'].eq(1)].groupby('MES')['FEX_ADJ'].sum() * n_meses_config
    desocupados = df_nacional[df_nacional['DSI'].eq(1)].groupby('MES')['FEX_ADJ'].sum() * n_meses_config
    ocupados = df_nacional[df_nacional['OCI'].eq(1)].groupby('MES')['FEX_ADJ'].sum() * n_meses_config
    pet = df_nacional[df_nacional['PET'].eq(1)].groupby('MES')['FEX_ADJ'].sum() * n_meses_config
    
    res = pd.DataFrame({
        'PET_M': pet / 1000000,
        'Ocupados_M': ocupados / 1000000,
        'Desocupados_M': desocupados / 1000000,
        'PEA_M': pea / 1000000
    })
    
    res['TD_%'] = (res['Desocupados_M'] / res['PEA_M']) * 100
    res['TGP_%'] = (res['PEA_M'] / res['PET_M']) * 100
    res['TO_%'] = (res['Ocupados_M'] / res['PET_M']) * 100
    res['Año'] = anio
    res['Ciudad'] = "Todas (Panorama Nacional)"
    
    return res.reset_index()

def calcular_salarios_ciudades(df, anio, config):
    DPTO_A_CAPITAL = {code[:2]: ciudad for code, ciudad in AREA_A_CIUDAD.items() if code[2:] == '001'}
    
    df_ciudades = df.copy()
    df_ciudades['Ciudad'] = df_ciudades['AREA'].astype(str).str.zfill(2).map(DPTO_A_CAPITAL)
    df_ciudades = df_ciudades.dropna(subset=['Ciudad'])
    
    if 'MES' not in df_ciudades.columns:
        df_ciudades['MES'] = 1
        
    list_salarios = []
    
    for (ciudad, mes), df_c in df_ciudades.groupby(['Ciudad', 'MES']):
        if len(df_c[df_c['INGLABO'] > 0]) > 50:
            sal = AnalisisSalarios(config=config).por_rama(df_c).reset_index()
            if sal.columns[0] != 'Rama' and 'Rama' not in sal.columns:
                sal.rename(columns={sal.columns[0]: 'Rama'}, inplace=True)
            sal['Ciudad'] = ciudad
            sal['MES'] = mes
            sal['Año'] = anio
            list_salarios.append(sal)
            
    if list_salarios:
        return pd.concat(list_salarios, ignore_index=True)
    return pd.DataFrame()

from geih import evaluar_proporcion

def calcular_estadisticas_ciudades_avanzadas(df, anio, config, ruta_output):
    print(f"[*] Computando Componente Avanzado por Ciudades ({anio})...")
    
    DPTO_A_CAPITAL = {code[:2]: ciudad for code, ciudad in AREA_A_CIUDAD.items() if code[2:] == '001'}
    df_c = df.copy()
    df_c['Ciudad'] = df_c['AREA'].astype(str).str.zfill(2).map(DPTO_A_CAPITAL)
    
    df_nacional = df.copy()
    df_nacional['Ciudad'] = "Todas (Panorama Nacional)"
    
    df_all = pd.concat([df_nacional, df_c.dropna(subset=['Ciudad'])], ignore_index=True)
    
    resumen_jovenes = []
    lista_brecha = []
    lista_costos = []
    lista_formalidad = []
    lista_calidad = []
    lista_vulnerabilidad = []
    lista_mincer = []
    lista_ramasexo = []
    
    for ciudad, group in df_all.groupby('Ciudad'):
        # --- Gini & Jovenes ---
        try:
            gini_val = IndicesCompuestos(config=config).gini(group)
            jovenes = FuerzaLaboralJoven(config=config).calcular(group)
            
            row_jv = {'Año': anio, 'Ciudad': ciudad, 'Gini': round(float(gini_val), 4)}
            if isinstance(jovenes, dict):
                for k, v in jovenes.items():
                    row_jv[f"Joven_{k}"] = round(float(v), 2)
            
            # Evaluación Varianza (Desempleo Juvenil)
            if 'TD_joven_%' in jovenes:
                prop_joven = jovenes['TD_joven_%'] / 100.0
                joven_pea = group[(group['P6040'] >= 15) & (group['P6040'] <= 28) & ((group['OCI'] == 1) | (group['DSI'] == 1))]
                prec_joven = evaluar_proporcion(prop_joven, len(joven_pea), joven_pea['FEX_ADJ'].sum() or 1, ciudad)
                row_jv['CV_TD_joven_%'] = prec_joven.cv_pct
                row_jv['Precisión_DANE'] = prec_joven.clasificacion
                
            resumen_jovenes.append(row_jv)
        except Exception:
            pass
            
        # --- Formalidad Sectorial ---
        try:
            form = FormalidadSectorial(config=config).calcular(group).reset_index()
            if 'Rama' not in form.columns and len(form.columns) > 0:
                form.rename(columns={form.columns[0]: 'Rama'}, inplace=True)
            
            if 'Cotiza_pension_%' in form.columns:
                cvs, clases = [], []
                ocupados = group[group['OCI']==1]
                for idx, row in form.iterrows():
                    prop = row['Cotiza_pension_%'] / 100.0
                    # Calculamos el muestreo con la proporcion reportada en la rama
                    prec = evaluar_proporcion(prop, len(ocupados), ocupados['FEX_ADJ'].sum() or 1, str(row.get('Rama', ciudad)))
                    cvs.append(prec.cv_pct)
                    clases.append(prec.clasificacion)
                form['CV_%'] = cvs
                form['Clasificacion_Precision'] = clases
                
            form['Ciudad'] = ciudad
            form['Año'] = anio
            lista_formalidad.append(form)
        except Exception:
            pass
            
        # --- Costos Laborales ---
        try:
            costos = CostoLaboral(config=config).calcular(group).reset_index()
            if 'Rama' not in costos.columns and len(costos.columns) > 0:
                costos.rename(columns={costos.columns[0]: 'Rama'}, inplace=True)
            costos['Ciudad'] = ciudad
            costos['Año'] = anio
            lista_costos.append(costos)
        except Exception:
            pass
            
        # --- Calidad del Empleo ---
        try:
            cal = CalidadEmpleo(config=config).calcular_por_rama(group).reset_index()
            if 'Rama' not in cal.columns and len(cal.columns) > 0:
                cal.rename(columns={cal.columns[0]: 'Rama'}, inplace=True)
            cal['Ciudad'] = ciudad
            cal['Año'] = anio
            lista_calidad.append(cal)
        except Exception:
            pass
            
        # --- Vulnerabilidad ---
        try:
            vuln = VulnerabilidadLaboral(config=config).calcular(group).reset_index()
            if 'Rama' not in vuln.columns and len(vuln.columns) > 0:
                vuln.rename(columns={vuln.columns[0]: 'Rama'}, inplace=True)
            vuln['Ciudad'] = ciudad
            vuln['Año'] = anio
            lista_vulnerabilidad.append(vuln)
        except Exception:
            pass
            
        # --- Brecha Genero ---
        try:
            brecha = BrechaGenero().calcular(group).reset_index()
            brecha.columns.name = None
            brecha['Ciudad'] = ciudad
            brecha['Año'] = anio
            lista_brecha.append(brecha)
        except Exception:
            pass
            
        # --- Ecuacion Mincer ---
        try:
            dict_mincer = EcuacionMincer().estimar(group)
            df_mincer = dict_mincer if isinstance(dict_mincer, pd.DataFrame) else pd.DataFrame([dict_mincer])
            df_mincer['Ciudad'] = ciudad
            df_mincer['Año'] = anio
            lista_mincer.append(df_mincer)
        except Exception:
            pass
            
        # --- Rama Sexo ---
        try:
            ramas = AnalisisRamaSexo().calcular(group).reset_index()
            if 'RAMA' not in ramas.columns and len(ramas.columns) > 0:
                ramas.rename(columns={ramas.columns[0]: 'RAMA'}, inplace=True)
            ramas['Ciudad'] = ciudad
            ramas['Año'] = anio
            lista_ramasexo.append(ramas)
        except Exception:
            pass

    print("[*] Consolidando resultados de ciudades y exportando CSVs/JSONs ...")
    if resumen_jovenes: pd.DataFrame(resumen_jovenes).to_json(os.path.join(ruta_output, f"ciudades_avanzado_resumen_{anio}.json"), orient='records', force_ascii=False, indent=4)
    if lista_brecha: pd.concat(lista_brecha, ignore_index=True).to_csv(os.path.join(ruta_output, f"ciudades_brecha_genero_{anio}.csv"), index=False)
    if lista_costos: pd.concat(lista_costos, ignore_index=True).to_csv(os.path.join(ruta_output, f"ciudades_costo_laboral_{anio}.csv"), index=False)
    if lista_formalidad: pd.concat(lista_formalidad, ignore_index=True).to_csv(os.path.join(ruta_output, f"ciudades_formalidad_sectorial_{anio}.csv"), index=False)
    if lista_calidad: pd.concat(lista_calidad, ignore_index=True).to_csv(os.path.join(ruta_output, f"ciudades_calidad_empleo_{anio}.csv"), index=False)
    if lista_vulnerabilidad: pd.concat(lista_vulnerabilidad, ignore_index=True).to_csv(os.path.join(ruta_output, f"ciudades_vulnerabilidad_{anio}.csv"), index=False)
    if lista_mincer: pd.concat(lista_mincer, ignore_index=True).to_csv(os.path.join(ruta_output, f"ciudades_mincer_{anio}.csv"), index=False)
    if lista_ramasexo: pd.concat(lista_ramasexo, ignore_index=True).to_csv(os.path.join(ruta_output, f"ciudades_rama_sexo_{anio}.csv"), index=False)

def calcular_ventanas_moviles(df_kpis):
    """
    Toma el DataFrame consolidado de métricas mensuales absolutas
    y calcula el 'Año Móvil' (promedio móvil de los últimos 12 meses)
    replicando la metodología oficial del DANE para publicación de cifras.
    """
    df = df_kpis.copy()
    
    # Asegurar el orden cronológico estricto: Año, MES
    df = df.sort_values(by=['Ciudad', 'Año', 'MES'])
    
    list_movil = []
    # Agrupar por dominio geográfico (cada ciudad o Nacional)
    for ciudad, group in df.groupby('Ciudad'):
        g = group.copy()
        
        # Calcular sumas móviles de 12 meses para volúmenes absolutos
        g['PEA_M_movil'] = g['PEA_M'].rolling(window=12, min_periods=12).sum() / 12
        g['Desocupados_M_movil'] = g['Desocupados_M'].rolling(window=12, min_periods=12).sum() / 12
        g['Ocupados_M_movil'] = g['Ocupados_M'].rolling(window=12, min_periods=12).sum() / 12
        g['PET_M_movil'] = g['PET_M'].rolling(window=12, min_periods=12).sum() / 12
        
        # Recalcular las tasas en base a los promedios móviles
        g['TD_%_movil'] = (g['Desocupados_M_movil'] / g['PEA_M_movil']) * 100
        g['TO_%_movil'] = (g['Ocupados_M_movil'] / g['PET_M_movil']) * 100
        g['TGP_%_movil'] = (g['PEA_M_movil'] / g['PET_M_movil']) * 100
        
        list_movil.append(g)
        
    df_movil = pd.concat(list_movil, ignore_index=True)
    
    # Rellenar con los valores mensuales originales si no hay suficientes datos (primeros 11 meses)
    # y aplicar la calibración del Año Móvil donde sí la haya.
    df_movil['TD_%'] = df_movil['TD_%_movil'].fillna(df_movil['TD_%'])
    df_movil['TO_%'] = df_movil['TO_%_movil'].fillna(df_movil['TO_%'])
    df_movil['TGP_%'] = df_movil['TGP_%_movil'].fillna(df_movil['TGP_%'])
    
    # Actualizar ABS también para que coincida
    df_movil['PEA_M'] = df_movil['PEA_M_movil'].fillna(df_movil['PEA_M'])
    df_movil['Desocupados_M'] = df_movil['Desocupados_M_movil'].fillna(df_movil['Desocupados_M'])
    df_movil['Ocupados_M'] = df_movil['Ocupados_M_movil'].fillna(df_movil['Ocupados_M'])
    df_movil['PET_M'] = df_movil['PET_M_movil'].fillna(df_movil['PET_M'])
    
    df_movil = df_movil.drop(columns=['PEA_M_movil', 'Desocupados_M_movil', 'Ocupados_M_movil', 'PET_M_movil', 'TD_%_movil', 'TO_%_movil', 'TGP_%_movil'])
    
    return df_movil

def generar_datos_dashboard(ruta_data="GEIH", ruta_output="output"):
    parquet_files = glob.glob(os.path.join(ruta_data, "GEIH_*_Consolidado.parquet"))
    
    if not parquet_files:
        print(f"[!] Error: No se encuentran archivos consolidados en {ruta_data}.")
        return
        
    os.makedirs(ruta_output, exist_ok=True)
    
    all_kpis = []
    all_salarios = []
    
    for parquet_path in parquet_files:
        filename = os.path.basename(parquet_path)
        try:
            anio = int(filename.split('_')[1])
        except Exception:
            continue
            
        print(f"[*] Iniciando Motor Analítico para el año: {anio}")
        config = ConfigGEIH(anio=anio, n_meses=12)
        
        geih_crudos = ConsolidadorGEIH.cargar(parquet_path)
        mes_col = geih_crudos['MES'].copy() if 'MES' in geih_crudos.columns else None
        
        prep = PreparadorGEIH(config=config)
        df = prep.preparar_base(geih_crudos)
        df = prep.agregar_variables_derivadas(df)
        
        if mes_col is not None:
            df['MES'] = mes_col
        else:
            df['MES'] = 1
        
        # -------------------------------------------------------------------
        # FIX: Derivar PET desde P6040 (edad) si PET viene como NaN del CSV
        # Definición DANE: PET = 1 si edad >= 12 años
        # -------------------------------------------------------------------
        if 'PET' in df.columns and df['PET'].isna().any() and 'P6040' in df.columns:
            mask_nan_pet = df['PET'].isna()
            n_fixed = mask_nan_pet.sum()
            df.loc[mask_nan_pet, 'PET'] = (df.loc[mask_nan_pet, 'P6040'] >= 15).astype(int)
            if n_fixed > 0:
                print(f"   ⚠️ PET derivada desde P6040 (edad >= 15) para {n_fixed:,} registros con PET=NaN")
        
        print(f"[*] Calculando Indicadores Macro y Ciudades ({anio})...")
        kpi_macro = calcular_kpi_nacional(df, anio, config.n_meses)
        kpi_ciudades = calcular_kpi_ciudades(df, anio, config.n_meses)
        
        all_kpis.append(kpi_macro)
        all_kpis.append(kpi_ciudades)
        
        print(f"[*] Analizando Mercado Salarial ({anio})...")
        df_salarios = calcular_salarios_ciudades(df, anio, config)
        all_salarios.append(df_salarios)
        
        # Generar estadisticas avanzadas (Gini, Jovenes, Costos, Formalidad, Brecha Genero)
        calcular_estadisticas_ciudades_avanzadas(df, anio, config, ruta_output)

    print("\n[*] Exportando DataFrames Consolidados...")
    df_all_kpis_raw = pd.concat(all_kpis, ignore_index=True)
    
    # -------------------------------------------------------------------
    # APLICACIÓN DE CALIBRACIÓN: CÁLCULO DE AÑO MÓVIL
    # -------------------------------------------------------------------
    print("[*] Aplicando calibración oficial DANE (Ventanas Móviles 12 meses)...")
    df_all_kpis_movil = calcular_ventanas_moviles(df_all_kpis_raw)
    
    df_all_kpis_movil.to_csv(os.path.join(ruta_output, "indicadores_mensuales.csv"), index=False)
    
    if all_salarios and len(all_salarios) > 0 and len(all_salarios[0]) > 0:
        pd.concat(all_salarios, ignore_index=True).to_csv(os.path.join(ruta_output, "salarios_por_rama_ciudad.csv"), index=False)

    print(f"[✅] Proceso completado. Archivos guardados en: {ruta_output}/")

if __name__ == "__main__":
    generar_datos_dashboard()
