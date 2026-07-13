# Auditoria integral del Observatorio GEIH

Fecha de cierre: 12 de julio de 2026

## Alcance

La revision cubrio los indicadores nacionales y territoriales del mercado laboral, presion y calidad del empleo, ingresos, juventud e indicadores estructurales. Tambien se revisaron el diccionario de variables, las formulas, los archivos de salida, la redaccion y el comportamiento de la interfaz en pantallas pequenas.

## Resultado estadistico

- Se validaron 1.545 combinaciones de ciudad, ano y mes en los resultados principales.
- Las identidades de desocupacion, participacion, ocupacion e informalidad presentan errores inferiores a 0,000000000002 puntos porcentuales, atribuibles al redondeo de punto flotante.
- Los resultados nacionales de marzo de 2025 reproducen las tasas del anexo oficial del DANE: TD 9,6164 %, TGP 64,7295 % y TO 58,5049 %.
- La fuerza de trabajo analitica se armonizo como la union de personas ocupadas y desocupadas. Esto corrige inconsistencias de la variable entregada en algunos archivos de 2025 y 2026 sin alterar la clasificacion laboral observada.
- Se comprobaron las formulas de subocupacion, LU3, LU4, NINI y sobrecalificacion. Sus errores maximos son inferiores a 0,00000000000002 puntos porcentuales.
- Cuatro resultados de ingreso inferior a un salario minimo no son estimables porque el denominador de personas con ingreso positivo observado es cero. Se conservan como faltantes y no como ceros.

## Controles de publicacion

- Los cuadros sectoriales solo publican ramas con al menos 30 observaciones y una poblacion expandida minima de 5.000 personas por ciudad y periodo.
- Las brechas por sexo solo se muestran cuando existen al menos 30 hombres y 30 mujeres en la categoria educativa comparada.
- Las distribuciones por rama y sexo se recalculan despues del filtro de publicacion, por lo que vuelven a sumar 100 % dentro de cada ciudad.
- La ecuacion de Mincer se oculta cuando no alcanza 100 observaciones o cuando sus coeficientes no son estimables.
- Los coeficientes de variacion son aproximaciones bajo muestreo aleatorio simple con un efecto de diseno fijo. No se presentan como errores oficiales del diseno muestral de la GEIH.

## Interpretacion

- La informalidad conserva la definicion operativa GEIH marco 2018 aplicada a la poblacion ocupada.
- Los indicadores de cobertura sectorial describen afiliacion a salud, cotizacion a pension e ingreso frente al salario minimo; no se rotulan como tasa oficial de informalidad.
- El indice de calidad del empleo y el indice de vulnerabilidad son medidas comparativas propias. No se les asignan umbrales oficiales ni se interpretan como relaciones causales.
- El costo laboral es una simulacion equivalente al 154 % del ingreso laboral mediano. No representa un costo observado en los microdatos.
- Las brechas y la ecuacion de ingresos son asociaciones descriptivas. No controlan seleccion laboral, endogeneidad ni diferencias no observadas.
- Los indicadores estructurales de 2026 corresponden a enero-abril y se identifican expresamente como cobertura parcial.

## Redaccion y diseno

- Se reemplazaron expresiones promocionales y genericas por lenguaje estadistico directo.
- Los encabezados distinguen tasa, proporcion, poblacion, unidad monetaria, periodo y dominio geografico.
- La interfaz usa una paleta sobria y variada, sin efectos decorativos que compitan con la lectura.
- Los controles tactiles tienen una altura minima de 44 px. En pantallas de hasta 768 px las columnas se apilan, las graficas ocupan el ancho disponible y las pestanas se desplazan sin generar desbordamiento horizontal de toda la pagina.
- El panel lateral usa apertura automatica: permanece disponible en escritorio y no bloquea la vista inicial en celular.

## Evidencia automatizada

- `output/auditoria_observatorio_completo.json`: consistencia de resultados, rangos, formulas y soportes muestrales.
- `output/auditoria_diccionario_logica.json`: cobertura de variables, identidades laborales y comparacion oficial.
- `audit_indicadores_valor_agregado.py`: validacion de 15 tasas, denominadores y cobertura temporal.
- Prueba de aplicacion Streamlit: 14 pestanas y 12 metricas cargadas, sin excepciones de ejecucion.

## Limites que deben conservarse visibles

Los resultados territoriales no reemplazan los anexos oficiales del DANE. Antes de usar una cifra para inferencia, debe revisarse su soporte muestral y, cuando corresponda, calcular la varianza con estratos, unidades primarias de muestreo y factores finales de expansion. Los indicadores propios sirven para comparacion descriptiva dentro del observatorio y deben mantenerse diferenciados de las tasas oficiales.
