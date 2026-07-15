import os
import argparse
import pandas as pd
import glob
import numpy as np
from geih import (
    ConfigGEIH, ConsolidadorGEIH, PreparadorGEIH,
    IndicadoresLaborales, AnalisisSalarios,
    BrechaGenero, IndicesCompuestos,
    CostoLaboral, FormalidadSectorial, FuerzaLaboralJoven,
    CalidadEmpleo, VulnerabilidadLaboral, EcuacionMincer, AnalisisRamaSexo
)
import json

try:
    from src.geografia_geih import asignar_dominio
except ModuleNotFoundError:  # Ejecucion directa: python src/02_motor_calculo.py
    from geografia_geih import asignar_dominio

VARIABLES_INFORMALIDAD_DANE = [
    'P6430', 'P3045S1', 'P3046', 'P3069', 'P6765', 'P3065', 'P3066',
    'P3067', 'P3067S1', 'P3067S2', 'P6775', 'P3068', 'P6100', 'P6110',
    'P6450', 'P6920', 'P6930', 'P6940', 'RAMA2D_R4', 'OFICIO_C8'
]


def clasificar_ocupacion_informal_dane(df, anio):
    """Clasifica ocupados con la sintaxis oficial DANE para GEIH marco 2018.

    Retorna ``True`` para ocupaci\u00f3n informal (EI=0 en el anexo DANE) y
    ``False`` para ocupaci\u00f3n formal (EI=1). La clasificaci\u00f3n aplica la
    l\u00f3gica publicada en las hojas ``C\u00f3digo_SAS`` de los anexos de empleo
    informal y seguridad social; no usa la cotizaci\u00f3n a pensi\u00f3n como proxy.
    """
    faltantes = [col for col in VARIABLES_INFORMALIDAD_DANE if col not in df.columns]
    if faltantes:
        raise ValueError(
            "No es posible calcular la informalidad con la metodolog\u00eda DANE. "
            f"Faltan variables requeridas: {', '.join(faltantes)}"
        )

    posicion = df['P6430']
    rama = df['RAMA2D_R4'].astype('string').str.zfill(2)
    oficio_num = pd.to_numeric(df['OFICIO_C8'], errors='coerce').round().astype('Int64')
    oficio_2d = oficio_num.astype('string').str.zfill(4).str[:2]
    oficio_directivo_profesional = oficio_2d.between('00', '20')
    tamanio_empresa = df['P3069']
    anio_renovacion_minimo = anio - 1

    # Sector informal: transcripci\u00f3n ordenada de las reglas 15-61 del
    # anexo DANE. Las condiciones se aplican solo a registros no clasificados,
    # equivalente a la cadena IF ... ELSE del c\u00f3digo SAS oficial.
    formal_sector = pd.Series(np.nan, index=df.index, dtype='float64')

    def asignar_formal(condicion, valor):
        formal_sector.loc[formal_sector.isna() & condicion.fillna(False)] = valor

    asignar_formal(posicion.eq(3), np.nan)
    asignar_formal(posicion.eq(6), 0)
    asignar_formal(rama.isin(['84', '99']), 1)
    asignar_formal(posicion.eq(8), 0)

    asalariado = posicion.isin([1, 7])
    asignar_formal(asalariado & df['P3045S1'].eq(1), 1)
    asignar_formal(asalariado & df['P3045S1'].isin([2, 9]) & df['P3046'].eq(1), 1)
    asignar_formal(asalariado & df['P3045S1'].isin([2, 9]) & df['P3046'].eq(2), 0)
    asignar_formal(asalariado & df['P3045S1'].isin([2, 9]) & df['P3046'].eq(9) & tamanio_empresa.ge(4), 1)
    asignar_formal(asalariado & df['P3045S1'].isin([2, 9]) & df['P3046'].eq(9) & tamanio_empresa.le(3), 0)

    independiente = posicion.isin([4, 5])
    sin_negocio = independiente & ~df['P6765'].eq(7)
    asignar_formal(sin_negocio & df['P3065'].eq(1), 1)
    asignar_formal(sin_negocio & df['P3065'].isin([2, 9]) & df['P3066'].eq(1), 1)
    asignar_formal(sin_negocio & df['P3065'].isin([2, 9]) & df['P3066'].eq(2), 0)
    asignar_formal(sin_negocio & posicion.eq(5) & df['P3065'].isin([2, 9]) & df['P3066'].eq(9) & tamanio_empresa.ge(4), 1)
    asignar_formal(sin_negocio & posicion.eq(5) & df['P3065'].isin([2, 9]) & df['P3066'].eq(9) & tamanio_empresa.le(3), 0)
    asignar_formal(sin_negocio & posicion.eq(4) & df['P3065'].isin([2, 9]) & df['P3066'].eq(9) & oficio_directivo_profesional, 1)
    asignar_formal(sin_negocio & posicion.eq(4) & df['P3065'].isin([2, 9]) & df['P3066'].eq(9) & ~oficio_directivo_profesional, 0)

    con_negocio = independiente & df['P6765'].eq(7)
    con_registro = con_negocio & df['P3067'].eq(1)
    asignar_formal(con_registro & df['P3067S1'].eq(1) & df['P3067S2'].ge(anio_renovacion_minimo), 1)
    asignar_formal(con_registro & df['P3067S1'].eq(1) & df['P3067S2'].lt(anio_renovacion_minimo), 0)
    asignar_formal(con_registro & df['P3067S1'].eq(2) & df['P6775'].eq(1), 1)
    asignar_formal(con_registro & df['P3067S1'].eq(2) & df['P6775'].eq(3) & oficio_directivo_profesional, 1)
    asignar_formal(con_registro & df['P3067S1'].eq(2) & df['P6775'].eq(3) & ~oficio_directivo_profesional, 0)
    asignar_formal(con_registro & df['P3067S1'].eq(2) & df['P6775'].eq(2), 0)
    asignar_formal(con_registro & posicion.eq(4) & df['P3067S1'].eq(2) & df['P6775'].eq(9) & oficio_directivo_profesional, 1)
    asignar_formal(con_registro & posicion.eq(4) & df['P3067S1'].eq(2) & df['P6775'].eq(9) & ~oficio_directivo_profesional, 0)
    asignar_formal(con_registro & posicion.eq(5) & df['P3067S1'].eq(2) & df['P6775'].eq(9) & tamanio_empresa.ge(4), 1)
    asignar_formal(con_registro & posicion.eq(5) & df['P3067S1'].eq(2) & df['P6775'].eq(9) & tamanio_empresa.le(3), 0)

    sin_registro = con_negocio & df['P3067'].eq(2)
    asignar_formal(sin_registro & df['P6775'].eq(1) & df['P3068'].eq(1), 1)
    asignar_formal(sin_registro & df['P6775'].eq(1) & df['P3068'].eq(2), 0)
    asignar_formal(sin_registro & df['P6775'].eq(3) & oficio_directivo_profesional, 1)
    asignar_formal(sin_registro & df['P6775'].eq(3) & ~oficio_directivo_profesional, 0)
    asignar_formal(sin_registro & df['P6775'].eq(1) & df['P3068'].isin([3, 9]), 0)
    asignar_formal(sin_registro & df['P6775'].eq(2), 0)
    asignar_formal(sin_registro & posicion.eq(5) & df['P6775'].eq(9) & tamanio_empresa.ge(4), 1)
    asignar_formal(sin_registro & posicion.eq(5) & df['P6775'].eq(9) & tamanio_empresa.le(3), 0)
    asignar_formal(sin_registro & posicion.eq(4) & df['P6775'].eq(9) & oficio_directivo_profesional, 1)
    asignar_formal(sin_registro & posicion.eq(4) & df['P6775'].eq(9) & ~oficio_directivo_profesional, 0)

    salud_formal = (
        posicion.isin([1, 3, 7])
        & ((df['P6100'].isin([1, 2]) & df['P6110'].isin([1, 2, 4]))
           | (df['P6100'].eq(9) & df['P6450'].eq(2))
           | (df['P6110'].eq(9) & df['P6450'].eq(2)))
    )
    pension_formal = (
        posicion.isin([1, 3, 7])
        & (df['P6920'].eq(3)
           | (df['P6920'].eq(1) & df['P6930'].isin([1, 2, 3]) & df['P6940'].isin([1, 3])))
    )

    ei_formal = pd.Series(np.nan, index=df.index, dtype='float64')
    ei_formal.loc[posicion.eq(2)] = 1
    ei_formal.loc[posicion.isin([6, 8])] = 0
    ei_formal.loc[independiente] = formal_sector.loc[independiente]
    ei_formal.loc[posicion.isin([1, 3, 7]) & salud_formal & pension_formal] = 1
    ei_formal.loc[posicion.isin([1, 3, 7]) & ei_formal.isna()] = 0
    ei_formal.loc[rama.isin(['84', '99']) & ~posicion.isin([6, 8])] = 1

    ocupados_sin_clasificar = df['OCI'].eq(1) & ei_formal.isna()
    if ocupados_sin_clasificar.any():
        raise ValueError(
            "La clasificaci\u00f3n DANE dej\u00f3 ocupados sin estado formal/informal: "
            f"{ocupados_sin_clasificar.sum():,} registros."
        )

    return ei_formal.eq(0)


def calcular_kpi_ciudades(df, anio, n_meses_config):
    # AREA identifica dominios autorrepresentados GEIH; no equivale siempre a
    # municipio ni a departamento. El registro territorial es independiente.
    
    # Optimización de memoria: copiar solo columnas necesarias
    cols_to_use = [c for c in ['AREA', 'MES', 'OCI', 'DSI', 'PET', 'FEX_ADJ', *VARIABLES_INFORMALIDAD_DANE] if c in df.columns]
    df_ciudades = df[cols_to_use].copy()
    df_ciudades['Ciudad'] = asignar_dominio(df_ciudades['AREA'])
    df_ciudades = df_ciudades.dropna(subset=['Ciudad'])
    
    if 'MES' not in df_ciudades.columns:
        df_ciudades['MES'] = 1 # Fallback

    df_ciudades['es_informal'] = clasificar_ocupacion_informal_dane(df_ciudades, anio).astype(int)

    # Al agrupar por mes individual, si FEX_ADJ fue dividido por n_meses para totales anuales,
    # debemos multiplicarlo de vuelta para obtener el volumen demográfico real de ESE mes concreto.
    pea = df_ciudades[df_ciudades['OCI'].eq(1) | df_ciudades['DSI'].eq(1)].groupby(['Ciudad', 'MES'])['FEX_ADJ'].sum() * n_meses_config
    desocupados = df_ciudades[df_ciudades['DSI'].eq(1)].groupby(['Ciudad', 'MES'])['FEX_ADJ'].sum() * n_meses_config
    ocupados = df_ciudades[df_ciudades['OCI'].eq(1)].groupby(['Ciudad', 'MES'])['FEX_ADJ'].sum() * n_meses_config
    pet = df_ciudades[df_ciudades['PET'].eq(1)].groupby(['Ciudad', 'MES'])['FEX_ADJ'].sum() * n_meses_config
    informales = df_ciudades[df_ciudades['OCI'].eq(1) & df_ciudades['es_informal'].eq(1)].groupby(['Ciudad', 'MES'])['FEX_ADJ'].sum() * n_meses_config
    
    res = pd.DataFrame({
        'PET_M': pet / 1000000,
        'Ocupados_M': ocupados / 1000000,
        'Desocupados_M': desocupados / 1000000,
        'PEA_M': pea / 1000000,
        'Informales_M': informales / 1000000
    }).fillna(0.0)
    
    res['TD_%'] = (res['Desocupados_M'] / res['PEA_M']) * 100
    res['TGP_%'] = (res['PEA_M'] / res['PET_M']) * 100
    res['TO_%'] = (res['Ocupados_M'] / res['PET_M']) * 100
    res['Tasa_Informalidad_%'] = (res['Informales_M'] / res['Ocupados_M']) * 100
    res['Año'] = anio
    
    return res.reset_index()

def calcular_kpi_nacional(df, anio, n_meses_config):
    # Optimización de memoria: copiar solo columnas necesarias
    cols_to_use = [c for c in ['MES', 'OCI', 'DSI', 'PET', 'FEX_ADJ', *VARIABLES_INFORMALIDAD_DANE] if c in df.columns]
    df_nacional = df[cols_to_use].copy()
    if 'MES' not in df_nacional.columns:
        df_nacional['MES'] = 1 # Fallback

    df_nacional['es_informal'] = clasificar_ocupacion_informal_dane(df_nacional, anio).astype(int)

    pea = df_nacional[df_nacional['OCI'].eq(1) | df_nacional['DSI'].eq(1)].groupby('MES')['FEX_ADJ'].sum() * n_meses_config
    desocupados = df_nacional[df_nacional['DSI'].eq(1)].groupby('MES')['FEX_ADJ'].sum() * n_meses_config
    ocupados = df_nacional[df_nacional['OCI'].eq(1)].groupby('MES')['FEX_ADJ'].sum() * n_meses_config
    pet = df_nacional[df_nacional['PET'].eq(1)].groupby('MES')['FEX_ADJ'].sum() * n_meses_config
    informales = df_nacional[df_nacional['OCI'].eq(1) & df_nacional['es_informal'].eq(1)].groupby('MES')['FEX_ADJ'].sum() * n_meses_config
    
    res = pd.DataFrame({
        'PET_M': pet / 1000000,
        'Ocupados_M': ocupados / 1000000,
        'Desocupados_M': desocupados / 1000000,
        'PEA_M': pea / 1000000,
        'Informales_M': informales / 1000000
    }).fillna(0.0)
    
    res['TD_%'] = (res['Desocupados_M'] / res['PEA_M']) * 100
    res['TGP_%'] = (res['PEA_M'] / res['PET_M']) * 100
    res['TO_%'] = (res['Ocupados_M'] / res['PET_M']) * 100
    res['Tasa_Informalidad_%'] = (res['Informales_M'] / res['Ocupados_M']) * 100
    res['Año'] = anio
    res['Ciudad'] = "Todas (Panorama Nacional)"
    
    return res.reset_index()

def calcular_salarios_ciudades(df, anio, config):
    
    df_ciudades = df.copy()
    df_ciudades['Ciudad'] = asignar_dominio(df_ciudades['AREA'])
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


def soporte_muestral_ramas(group):
    """Resume muestra y poblacion expandida por rama."""
    ocupados = group[(group['OCI'].eq(1)) & group['RAMA'].notna()]
    return ocupados.groupby('RAMA').agg(
        n_muestra=('FEX_ADJ', 'size'),
        poblacion=('FEX_ADJ', 'sum'),
    )


def ramas_con_soporte_muestral(group, n_minimo=30, poblacion_minima=5_000):
    """Retorna ramas con soporte basico para resultados descriptivos."""
    soporte = soporte_muestral_ramas(group)
    return set(soporte[
        soporte['n_muestra'].ge(n_minimo)
        & soporte['poblacion'].ge(poblacion_minima)
    ].index)


def agregar_soporte(tabla, soporte, columna='Rama'):
    """Agrega evidencia de soporte muestral a una tabla por rama."""
    tabla = tabla.copy()
    tabla['n_muestra'] = tabla[columna].map(soporte['n_muestra'])
    tabla['poblacion_estimada'] = tabla[columna].map(soporte['poblacion'])
    return tabla

def calcular_estadisticas_ciudades_avanzadas(df, anio, config, ruta_output):
    print(f"[*] Computando Componente Avanzado por Ciudades ({anio})...")
    
    df_c = df.copy()
    df_c['Ciudad'] = asignar_dominio(df_c['AREA'])
    
    # Optimización extrema de memoria: Evitar concat de dataframes masivos que causa ArrayMemoryError.
    # En su lugar, creamos una lista de tuplas (nombre, DataFrame) para iterar directamente.
    ciudades_groups = list(df_c.dropna(subset=['Ciudad']).groupby('Ciudad'))
    grupos_de_calculo = [("Todas (Panorama Nacional)", df)] + ciudades_groups
    
    resumen_jovenes = []
    lista_brecha = []
    lista_costos = []
    lista_formalidad = []
    lista_calidad = []
    lista_vulnerabilidad = []
    lista_mincer = []
    lista_ramasexo = []
    
    for ciudad, group in grupos_de_calculo:
        soporte_ramas = soporte_muestral_ramas(group)
        ramas_validas = ramas_con_soporte_muestral(group)
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
            form = form[form['Rama'].isin(ramas_validas)].copy()
            form = agregar_soporte(form, soporte_ramas)
            
            if 'Cotiza_pension_%' in form.columns:
                cvs, clases = [], []
                for idx, row in form.iterrows():
                    prop = row['Cotiza_pension_%'] / 100.0
                    ocupados_rama = group[(group['OCI'].eq(1)) & (group['RAMA'] == row['Rama'])]
                    prec = evaluar_proporcion(
                        prop, len(ocupados_rama), ocupados_rama['FEX_ADJ'].sum() or 1,
                        str(row.get('Rama', ciudad))
                    )
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
            costos = costos[costos['Rama'].isin(ramas_validas)].copy()
            costos = agregar_soporte(costos, soporte_ramas)
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
            cal = cal[cal['Rama'].isin(ramas_validas)].copy()
            cal = agregar_soporte(cal, soporte_ramas)
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
            vuln = vuln[vuln['Rama'].isin(ramas_validas)].copy()
            vuln = agregar_soporte(vuln, soporte_ramas)
            vuln['Ciudad'] = ciudad
            vuln['Año'] = anio
            lista_vulnerabilidad.append(vuln)
        except Exception:
            pass
            
        # --- Brecha Genero ---
        try:
            brecha = BrechaGenero().calcular(group).reset_index()
            brecha.columns.name = None
            base_brecha = group[
                group['OCI'].eq(1) & group['INGLABO'].gt(0)
                & group['NIVEL_GRUPO'].notna() & group['P3271'].isin([1, 2])
            ]
            conteos_brecha = base_brecha.groupby(['NIVEL_GRUPO', 'P3271']).size().unstack(fill_value=0)
            for sexo in [1, 2]:
                if sexo not in conteos_brecha.columns:
                    conteos_brecha[sexo] = 0
            niveles_validos = set(conteos_brecha[
                conteos_brecha[1].ge(30) & conteos_brecha[2].ge(30)
            ].index)
            brecha = brecha[brecha['Nivel'].isin(niveles_validos)].copy()
            brecha['n_hombres'] = brecha['Nivel'].map(conteos_brecha[1])
            brecha['n_mujeres'] = brecha['Nivel'].map(conteos_brecha[2])
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
            rama_col = 'RAMA' if 'RAMA' in ramas.columns else 'Rama'
            ramas = ramas[ramas[rama_col].isin(ramas_validas)].copy()
            ramas = agregar_soporte(ramas, soporte_ramas, columna=rama_col)
            # Las participaciones deben usar como denominador únicamente las ramas
            # que superan el umbral de publicación en esta ciudad y periodo.
            ramas['Total'] = ramas['Hombres'] + ramas['Mujeres']
            total_publicable = ramas['Total'].sum()
            total_hombres = ramas['Hombres'].sum()
            total_mujeres = ramas['Mujeres'].sum()
            ramas['Dist_%'] = ramas['Total'].div(total_publicable).mul(100) if total_publicable else 0
            ramas['Dist_H_%'] = ramas['Hombres'].div(total_hombres).mul(100) if total_hombres else 0
            ramas['Dist_M_%'] = ramas['Mujeres'].div(total_mujeres).mul(100) if total_mujeres else 0
            for columna in ['Hombres', 'Mujeres', 'Total']:
                ramas[f'{columna}_miles'] = ramas[columna] / 1_000
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
        g['PEA_M_movil'] = g['PEA_M'].fillna(0).rolling(window=12, min_periods=12).sum() / 12
        g['Desocupados_M_movil'] = g['Desocupados_M'].fillna(0).rolling(window=12, min_periods=12).sum() / 12
        g['Ocupados_M_movil'] = g['Ocupados_M'].fillna(0).rolling(window=12, min_periods=12).sum() / 12
        g['PET_M_movil'] = g['PET_M'].fillna(0).rolling(window=12, min_periods=12).sum() / 12
        g['Informales_M_movil'] = g['Informales_M'].fillna(0).rolling(window=12, min_periods=12).sum() / 12 if 'Informales_M' in g.columns else None

        # Recalcular las tasas en base a los promedios móviles
        g['TD_%_movil'] = (g['Desocupados_M_movil'] / g['PEA_M_movil']) * 100
        g['TO_%_movil'] = (g['Ocupados_M_movil'] / g['PET_M_movil']) * 100
        g['TGP_%_movil'] = (g['PEA_M_movil'] / g['PET_M_movil']) * 100
        if 'Informales_M_movil' in g.columns and g['Informales_M_movil'] is not None:
            g['Tasa_Informalidad_%_movil'] = (g['Informales_M_movil'] / g['Ocupados_M_movil']) * 100
        else:
            g['Tasa_Informalidad_%_movil'] = np.nan

        list_movil.append(g)
        
    df_movil = pd.concat(list_movil, ignore_index=True)
    
    # Rellenar con los valores mensuales originales si no hay suficientes datos (primeros 11 meses)
    # y aplicar la calibración del Año Móvil donde sí la haya.
    df_movil['TD_%'] = df_movil['TD_%_movil'].fillna(df_movil['TD_%'])
    df_movil['TO_%'] = df_movil['TO_%_movil'].fillna(df_movil['TO_%'])
    df_movil['TGP_%'] = df_movil['TGP_%_movil'].fillna(df_movil['TGP_%'])
    if 'Tasa_Informalidad_%_movil' in df_movil.columns:
        df_movil['Tasa_Informalidad_%'] = df_movil['Tasa_Informalidad_%_movil'].fillna(df_movil['Tasa_Informalidad_%'])
    
    # Actualizar ABS también para que coincida
    df_movil['PEA_M'] = df_movil['PEA_M_movil'].fillna(df_movil['PEA_M'])
    df_movil['Desocupados_M'] = df_movil['Desocupados_M_movil'].fillna(df_movil['Desocupados_M'])
    df_movil['Ocupados_M'] = df_movil['Ocupados_M_movil'].fillna(df_movil['Ocupados_M'])
    df_movil['PET_M'] = df_movil['PET_M_movil'].fillna(df_movil['PET_M'])
    if 'Informales_M_movil' in df_movil.columns:
        df_movil['Informales_M'] = df_movil['Informales_M_movil'].fillna(df_movil['Informales_M'])
    
    drop_cols = ['PEA_M_movil', 'Desocupados_M_movil', 'Ocupados_M_movil', 'PET_M_movil', 'TD_%_movil', 'TO_%_movil', 'TGP_%_movil']
    if 'Informales_M_movil' in df_movil.columns:
        drop_cols.append('Informales_M_movil')
    if 'Tasa_Informalidad_%_movil' in df_movil.columns:
        drop_cols.append('Tasa_Informalidad_%_movil')
        
    df_movil = df_movil.drop(columns=drop_cols)
    
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
        
        # Optimización masiva de carga de memoria (WLS / Parquet):
        # Leer únicamente las columnas que serán utilizadas en el cálculo para evitar ArrayMemoryError
        import pyarrow.parquet as pq
        parquet_schema = pq.read_schema(parquet_path)
        all_parquet_cols = parquet_schema.names
        
        columnas_a_cargar = [c for c in all_parquet_cols if (
            c in VARIABLES_INFORMALIDAD_DANE
            or any(p in c.upper() for p in [
                'OCI', 'DSI', 'PET', 'FEX', 'MES', 'AREA', 'ING', 'ANOS', 'P6', 'P3',
                'DPTO', 'FT', 'RAMA', 'CIIU', 'SEXO', 'EDUC', 'COTIZA', 'FORMAL', 'INFORMAL',
                'NIVEL'
            ])
        )]
        
        print(f"   [i] Cargando {len(columnas_a_cargar)} de {len(all_parquet_cols)} columnas del Parquet...")
        geih_crudos = pd.read_parquet(parquet_path, columns=columnas_a_cargar)
        
        n_meses_datos = geih_crudos['MES'].nunique() if 'MES' in geih_crudos.columns else 12
        print(f"   [i] Meses detectados en el Parquet: {n_meses_datos}")
        config = ConfigGEIH(anio=anio, n_meses=n_meses_datos)
        
        mes_col = geih_crudos['MES'].copy() if 'MES' in geih_crudos.columns else None
        
        prep = PreparadorGEIH(config=config)
        df = prep.preparar_base(geih_crudos)
        df = prep.agregar_variables_derivadas(df)

        # PreparadorGEIH conserva solo su esquema analítico. Estas variables se
        # reincorporan para reproducir literalmente la clasificación oficial.
        for columna in VARIABLES_INFORMALIDAD_DANE:
            if columna in geih_crudos.columns:
                df[columna] = geih_crudos[columna].to_numpy(copy=False)
        
        if mes_col is not None:
            df['MES'] = mes_col
        else:
            df['MES'] = 1
            
        # -------------------------------------------------------------------
        # OPTIMIZACIÓN DE MEMORIA: Las columnas ya vienen filtradas desde la carga del Parquet
        # -------------------------------------------------------------------
        
        # -------------------------------------------------------------------
        # FIX: Derivar PET desde P6040 (edad) si PET viene como NaN del CSV
        # GEIH marco 2018: PET = 1 si edad >= 15 años. Solo se completan
        # faltantes; los valores observados del archivo se conservan.
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
