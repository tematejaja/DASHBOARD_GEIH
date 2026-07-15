"""Catalogo auditable de variables y formulas del dashboard GEIH."""

from __future__ import annotations

import pandas as pd


VARIABLES_DASHBOARD = [
    # Identificacion, geografia y ponderacion
    ("Identificacion", "MES", "Mes de recoleccion", "1 a 12", "Todos", "Periodo de las series"),
    ("Geografia", "AREA", "Dominio de cabecera urbana", "Codigo de area; vacio fuera del dominio", "Todos", "Capitales y areas metropolitanas"),
    ("Geografia", "DPTO", "Departamento", "Codigo DANE de dos digitos", "Todos", "Control geografico"),
    ("Geografia", "CLASE", "Clase geografica", "1 cabecera; 2 centro poblado/rural disperso", "Todos", "Analisis urbano-rural"),
    ("Ponderacion", "FEX_C18", "Factor de expansion CNPV 2018", "Peso mensual original DANE", "Todos", "Totales y estimaciones ponderadas"),
    ("Ponderacion", "FEX_ADJ", "Factor analitico ajustado", "FEX_C18 / numero de meses del consolidado", "Derivada", "Promedios de periodos multimensuales"),

    # Caracteristicas generales y educacion
    ("Demografia", "P3271", "Sexo al nacer", "1 hombre; 2 mujer", "Todos", "Brechas y desagregaciones"),
    ("Demografia", "P6040", "Edad en anos cumplidos", "Valor continuo", "Todos", "PET, jovenes y experiencia potencial"),
    ("Educacion", "P3042", "Mayor nivel educativo alcanzado", "1-13; 99 no informa", "Todos", "Nivel agrupado, anos educativos y sobrecalificacion"),
    ("Educacion", "P3043", "Mayor titulo o diploma recibido", "1-10; 99 no informa", "Todos", "Control educativo complementario"),
    ("Educacion", "P6170", "Asistencia actual a educacion formal", "1 si; 2 no", "Personas elegibles", "Indicador NINI"),

    # Estado laboral derivado por DANE
    ("Estado laboral", "PET", "Poblacion en edad de trabajar", "1 si; faltantes se completan con P6040 >= 15", "Poblacion total", "Denominador TGP y TO"),
    ("Estado laboral", "FT", "Fuerza de trabajo publicada en microdatos", "1 si; el analisis armoniza FT*=OCI union DSI", "PET", "Control de consistencia"),
    ("Estado laboral", "FFT", "Fuera de la fuerza de trabajo", "1 si", "PET", "Fuerza de trabajo potencial y NINI"),
    ("Estado laboral", "OCI", "Poblacion ocupada", "1 si", "PET", "Numerador TO y universos de calidad"),
    ("Estado laboral", "DSI", "Poblacion desocupada", "1 si", "PET", "Numerador TD y duracion"),
    ("Estado laboral", "P6280", "Busqueda reciente de trabajo", "1 si; 2 no", "No ocupados", "Fuerza de trabajo potencial"),
    ("Estado laboral", "P6300", "Deseo de trabajar", "1 si; 2 no", "No ocupados", "Fuerza de trabajo potencial"),
    ("Estado laboral", "P7250", "Semanas buscando trabajo", "Numero de semanas", "Desocupados", "Duracion y desempleo de larga duracion"),

    # Empleo, ingreso y clasificaciones
    ("Empleo", "P6430", "Posicion ocupacional", "Categorias DANE", "Ocupados", "Asalariados, independientes e informalidad"),
    ("Empleo", "P6800", "Horas que trabaja normalmente por semana", "1 a 130", "Ocupados", "Jornada, ICE, IVI y subocupacion"),
    ("Ingreso", "INGLABO", "Ingreso laboral mensual armonizado", "COP; faltante si no observable", "Ocupados", "Salarios, Gini, Mincer e ingreso real"),
    ("Actividad", "RAMA2D_R4", "Rama CIIU Rev. 4 A.C. a dos digitos", "Codigo de actividad", "Ocupados", "Sectores y clasificacion de informalidad"),
    ("Ocupacion", "OFICIO_C8", "Ocupacion CIUO-08 a cuatro digitos", "Codigo ocupacional", "Ocupados", "Informalidad y sobrecalificacion"),

    # Seguridad social, contrato y prestaciones
    ("Proteccion", "P6090", "Afiliacion al sistema de salud", "1 si", "Personas elegibles", "ICE, ICF e IVI"),
    ("Proteccion", "P6100", "Regimen de afiliacion en salud", "Categorias DANE", "Afiliados", "Clasificador oficial de informalidad"),
    ("Proteccion", "P6110", "Condicion o pagador de afiliacion en salud", "Categorias DANE", "Afiliados", "Clasificador oficial de informalidad"),
    ("Proteccion", "P6920", "Cotizacion actual a pension", "1 cotiza; 2 no; 3 pensionado", "Ocupados", "Formalidad, ICE, IVI y proteccion"),
    ("Proteccion", "P6930", "Tipo de fondo de pensiones", "Categorias DANE", "Cotizantes/pensionados", "Clasificador oficial de informalidad"),
    ("Proteccion", "P6940", "Quien paga la cotizacion pensional", "Categorias DANE", "Cotizantes", "Clasificador oficial de informalidad"),
    ("Contrato", "P6440", "Tiene contrato de trabajo", "1 si; 2 no", "Ocupados", "Calidad contractual"),
    ("Contrato", "P6450", "Forma del contrato", "1 verbal; 2 escrito; 9 no informa", "Con contrato", "Contrato escrito e informalidad"),
    ("Contrato", "P6460", "Duracion del contrato escrito", "1 indefinido; 2 fijo", "Contrato escrito", "Contrato indefinido"),
    ("Prestaciones", "P6424S1", "Vacaciones con sueldo", "1 si; 2 no", "Con contrato", "Prestaciones completas"),
    ("Prestaciones", "P6424S2", "Prima de navidad", "1 si; 2 no", "Con contrato", "Prestaciones completas"),
    ("Prestaciones", "P6424S3", "Derecho a cesantias", "1 si; 2 no", "Con contrato", "Prestaciones completas"),
    ("Prestaciones", "P6424S5", "Licencia por enfermedad pagada", "1 si; 2 no", "Con contrato", "Prestaciones completas"),

    # Subocupacion y fuerza de trabajo potencial
    ("Subocupacion", "P7090", "Desea trabajar mas horas", "1 si; 2 no", "Ocupados", "Insuficiencia de horas"),
    ("Subocupacion", "P7110", "Hizo diligencias para trabajar mas horas", "1 si; 2 no", "Desea mas horas", "Subocupacion objetiva"),
    ("Subocupacion", "P7120", "Disponibilidad para trabajar mas horas", "1 si; 2 no", "Desea mas horas", "Subocupacion objetiva"),
    ("Subocupacion", "P7130", "Desea cambiar de trabajo", "1 si; 2 no", "Ocupados", "Condiciones de empleo inadecuado"),
    ("Subocupacion", "P7140S1", "Cambiar para usar mejor capacidades", "1 si; 2 no", "Desea cambiar", "Subocupacion por competencias"),
    ("Subocupacion", "P7140S2", "Cambiar para mejorar ingresos", "1 si; 2 no", "Desea cambiar", "Subocupacion por ingresos"),
    ("Subocupacion", "P7140S3", "Cambiar para trabajar menos horas", "1 si; 2 no", "Desea cambiar", "Condicion laboral inadecuada"),
    ("Subocupacion", "P7150", "Hizo diligencias para cambiar de trabajo", "1 si; 2 no", "Desea cambiar", "Subocupacion objetiva"),
    ("Subocupacion", "P7160", "Disponibilidad para iniciar otro trabajo", "1 si; 2 no", "Desea cambiar", "Subocupacion objetiva"),

    # Insumos del algoritmo oficial de informalidad DANE marco 2018
    ("Informalidad", "P3045S1", "Registro de la empresa en Camara de Comercio", "1 si; 2 no; 9 no informa", "Asalariados", "Sector formal/informal"),
    ("Informalidad", "P3046", "Oficina de contabilidad o contador", "1 si; 2 no; 9 no informa", "Asalariados", "Sector formal/informal"),
    ("Informalidad", "P3065", "Registro mercantil del negocio", "Categorias DANE", "Independientes", "Sector formal/informal"),
    ("Informalidad", "P3066", "Seguimiento al registro mercantil", "Categorias DANE", "Independientes", "Sector formal/informal"),
    ("Informalidad", "P3067", "Registro del negocio ante Camara de Comercio", "1 si; 2 no", "Independientes con negocio", "Sector formal/informal"),
    ("Informalidad", "P3067S1", "Renovacion del registro mercantil", "1 si; 2 no", "Negocio registrado", "Sector formal/informal"),
    ("Informalidad", "P3067S2", "Ultimo ano de renovacion", "Ano", "Registro renovado", "Vigencia del registro"),
    ("Informalidad", "P3068", "Separacion contable negocio-hogar", "Categorias DANE", "Independientes", "Sector formal/informal"),
    ("Informalidad", "P3069", "Tamano de la empresa o negocio", "Numero/categoria de personas", "Ocupados", "Sector formal/informal"),
    ("Informalidad", "P6765", "Caracteristica operativa del negocio independiente", "Categorias DANE", "Independientes", "Ruta del clasificador DANE"),
    ("Informalidad", "P6775", "Contabilidad o libro de operaciones", "Categorias DANE", "Independientes", "Sector formal/informal"),
]


FORMULAS_DASHBOARD = [
    ("Oficial DANE", "Tasa de desocupacion (TD)", "PET clasificada en FT", "DS", "FT*=OCI union DSI", "DS / FT* x 100", "OCI, DSI, FEX_C18", "Movil 12 meses"),
    ("Oficial DANE", "Tasa global de participacion (TGP)", "Poblacion en edad de trabajar armonizada", "FT*=OCI union DSI", "PET*", "FT* / PET* x 100", "OCI, DSI, PET, P6040, FEX_C18", "Movil 12 meses"),
    ("Oficial DANE", "Tasa de ocupacion (TO)", "Poblacion en edad de trabajar", "OC", "PET", "OC / PET x 100", "OCI, PET, FEX_C18", "Movil 12 meses"),
    ("Oficial DANE", "Proporcion de ocupacion informal", "Poblacion ocupada", "Ocupados informales EI=0", "OC", "Informales / OC x 100", "P6430 y 20 insumos del algoritmo EI", "Movil 12 meses"),
    ("Oficial DANE", "Tasa de subocupacion", "Fuerza de trabajo", "PS", "FT", "PS / FT x 100", "P7090-P7160, P6800", "Movil 12 meses"),
    ("OIT", "LU2: desocupacion e insuficiencia de horas", "Fuerza de trabajo", "SIH + DS", "FT", "(SIH + DS) / FT x 100", "P7090, P7110, P7120, P6800, DSI", "Movil 12 meses"),
    ("OIT", "LU3: desocupacion y fuerza potencial", "Fuerza de trabajo ampliada", "DS + FTP", "FT + FTP", "(DS + FTP) / (FT + FTP) x 100", "FT, FFT, P6280, P6300, DSI", "Movil 12 meses"),
    ("OIT/DANE", "LU4: subutilizacion amplia", "FT mas fuerza potencial", "SIH + DS + FTP", "FT + FTP", "(SIH + DS + FTP) / (FT + FTP) x 100", "FT, FFT, P6280, P6300 y SIH", "Movil 12 meses"),
    ("Analitico", "Desempleo de larga duracion", "Desocupados con duracion observada", "P7250 >= 52 semanas", "P7250 valido", "Numerador / denominador x 100", "DSI, P7250", "Movil 12 meses"),
    ("Analitico", "Contrato escrito", "Asalariados P6430 in 1,2,3,7", "P6440=1 y P6450=2", "Asalariados", "Numerador / denominador x 100", "P6430, P6440, P6450", "Movil 12 meses"),
    ("Analitico", "Proteccion integral", "Asalariados P6430 in 1,2,3,7", "Contrato escrito + pension + 4 prestaciones", "Asalariados", "Numerador / denominador x 100", "P6450, P6920, P6424S1/S2/S3/S5", "Movil 12 meses"),
    ("Analitico", "Ingreso real mediano", "Ocupados con INGLABO > 0", "Mediana ponderada", "No aplica", "Mediana ponderada de INGLABO/(IPC/100)", "INGLABO, FEX_C18, IPC DANE", "Movil 12 meses"),
    ("Analitico", "Ingreso inferior a 1 SMMLV", "Ocupados con INGLABO > 0", "INGLABO < SMMLV", "Ingreso observado positivo", "Numerador / denominador x 100", "INGLABO, SMMLV, FEX_C18", "Movil 12 meses"),
    ("OIT adaptado", "NINI 15-28", "Jovenes 15-28 con asistencia valida", "No OCI y P6170=2", "Jovenes validos", "Numerador / denominador x 100", "P6040, OCI, P6170", "Movil 12 meses"),
    ("OIT", "NINI 15-24", "Jovenes 15-24 con asistencia valida", "No OCI y P6170=2", "Jovenes validos", "Numerador / denominador x 100", "P6040, OCI, P6170", "Movil 12 meses"),
    ("OIT normativo", "Sobrecalificacion educativa", "Ocupados con educacion y CIUO validas", "Nivel CINE superior al requerido por CIUO-08", "Ocupados clasificables", "Numerador / denominador x 100", "P3042, OFICIO_C8, OCI", "Movil 12 meses"),
    ("Analitico", "Gini de ingreso laboral", "Ocupados con INGLABO > 0", "Area entre Lorenz e igualdad", "No aplica", "Gini ponderado por FEX_ADJ", "INGLABO, OCI, FEX_ADJ", "Ano calendario/disponible"),
    ("Analitico", "Brecha salarial por educacion", "Ocupados con ingreso positivo", "Mediana mujeres - mediana hombres", "Mediana hombres", "(M-H)/H x 100", "P3271, P3042, INGLABO, FEX_ADJ", "Ano calendario/disponible"),
    ("Indice propio", "ICE", "Ocupados", "Puntaje individual ponderado", "Ocupados", "30% pension + 25% salud + 25% horas 20-48 + 20% ingreso >= SMMLV", "P6920, P6090, P6800, INGLABO", "Ano calendario/disponible"),
    ("Indice propio", "IVI", "Ocupados por rama", "Promedio de cuatro tasas de riesgo", "Ocupados de la rama", "Media: cuenta propia sin pension, sobrejornada, ingreso bajo, sin salud/pension", "P6430, P6920, P6090, P6800, INGLABO", "Ano calendario/disponible"),
    ("Indice propio", "ICF sectorial", "Ocupados por rama", "Promedio de tres coberturas", "Ocupados de la rama", "Media: pension, salud e ingreso >= SMMLV", "P6920, P6090, INGLABO", "Ano calendario/disponible"),
    ("Modelo descriptivo", "Ecuacion de Mincer", "Ocupados con ingreso positivo", "log(INGLABO)", "No aplica", "WLS: ln(w)=b0+b1 educ+b2 exp+b3 exp2", "P3042->ANOS_EDUC, P6040, INGLABO, FEX_ADJ", "Ano calendario/disponible"),
    ("Simulacion", "Costo laboral ampliado", "Ocupados con ingreso positivo por rama", "Mediana salarial x 1.54", "No aplica", "Supuesto fijo de carga adicional del 54%", "INGLABO, RAMA2D_R4, FEX_ADJ", "Ano calendario/disponible"),
]


def dataframe_variables() -> pd.DataFrame:
    return pd.DataFrame(VARIABLES_DASHBOARD, columns=["Modulo", "Codigo", "Definicion", "Codificacion", "Universo", "Uso en el tablero"])


def dataframe_formulas() -> pd.DataFrame:
    return pd.DataFrame(FORMULAS_DASHBOARD, columns=["Tipo", "Indicador", "Universo", "Numerador", "Denominador", "Formula", "Variables", "Periodo"])
