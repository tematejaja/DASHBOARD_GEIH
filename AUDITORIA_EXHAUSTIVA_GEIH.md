# Auditoría exhaustiva del Observatorio GEIH

**Corte auditado:** enero de 2022 a abril de 2026

**Unidad territorial:** dominio GEIH
**Fecha de ejecución:** 15 de julio de 2026

## Alcance y criterio estadístico

La revisión se ejecuta en dos capas independientes. La primera examina las 57
variables del diccionario por dominio, año y mes. La segunda reconstruye los
numeradores y denominadores de los indicadores sin importar funciones del motor
productivo. Esta separación evita aprobar una fórmula comparándola consigo misma.

Las estimaciones mensuales usan el factor original `FEX_C18`. `FEX_ADJ` se audita
como variable analítica derivada y solo se usa para combinar meses. Una tasa de
varios meses se obtiene como cociente de sumas ponderadas; nunca como promedio de
tasas mensuales. No se calculan errores oficiales de muestreo porque los
consolidados disponibles no contienen estrato ni UPM.

## Geografía

Se creó un registro territorial independiente del paquete `geih`, con código
`AREA`, nombre, tipo de dominio, municipios integrantes y vigencia. La corrección
crítica es:

- `AREA=41`: Neiva.
- `AREA=73`: Ibagué.

Las ausencias estructurales se conservan como ausencias, no como ceros. El
consolidado de 2022 contiene menos dominios representados que los años siguientes.
Las etiquetas visibles usan “dominio GEIH”, pues varios dominios son áreas
metropolitanas y no municipios individuales.

## Variables

`output/auditoria_variables_detalle.parquet` conserva, para cada celda, universo,
tamaño muestral, población expandida, faltantes ponderados y no ponderados,
violaciones de catálogo o rango, observaciones fuera del universo, distribución
ponderada o percentiles ponderados y evidencia del estado.

Los estados se interpretan así:

- `APROBADA`: no se detectaron violaciones de dominio o rango.
- `ALERTA`: cambio temporal superior simultáneamente a 5 puntos porcentuales y
  cinco desviaciones absolutas medianas. Requiere revisión, pero no prueba error.
- `ERROR`: valor incompatible con un catálogo o rango explícito.
- `NO APLICA`: universo vacío o variable no disponible en el archivo anual.

La presencia de un valor fuera del universo se reporta como evidencia y no se
convierte automáticamente en error: los saltos del cuestionario y la codificación
de “no informa” deben interpretarse con el diccionario del periodo.

## Indicadores

Se corrigió la clasificación de subutilización conforme a la 19.ª CIET:

- LU2 = `(SIH + DS) / FT`.
- LU3 = `(DS + FTP) / (FT + FTP)`.
- LU4 = `(SIH + DS + FTP) / (FT + FTP)`.

El tablero conserva NINI 15–28 como adaptación nacional y añade NINI 15–24 como
estándar de comparación OIT. Las etiquetas impiden tratarlos como indicadores
idénticos. La duración mediana usa exclusivamente desocupados con `P7250` válido;
el desempleo de larga duración aplica el umbral de 52 semanas.

La informalidad conserva la decisión completa del marco 2018 para rutas de
asalariados e independientes. Sus pruebas sintéticas verifican ambas rutas y no
reducen el indicador a afiliación pensional o tamaño del establecimiento.

## Contraste externo

Solo se comparan celdas con igual definición, territorio y ventana. Las cifras
nacionales mensuales se contrastan contra publicaciones mensuales; las ciudades
solo pueden contrastarse contra anexos de trimestre móvil mediante una
recomputación de tres meses. La ventana principal de doce meses del tablero no se
compara con publicaciones mensuales o trimestrales.

La tolerancia es media unidad del último decimal publicado más 0,01 puntos
porcentuales. Cada comparación conserva fuente, periodo, unidad, territorio y
huella SHA-256 cuando la descarga automatizada fue posible. Las páginas de OIT
que bloquearon la descarga automatizada se registran como fuente conceptual, sin
inventar una copia local ni una cifra comparable.

## Clasificación metodológica

Los indicadores se distinguen expresamente entre oficiales DANE, estándares OIT,
adaptaciones, indicadores analíticos, índices propios, modelos descriptivos y
simulaciones. ICE, IVI e ICF no se presentan como estadísticas oficiales. La
ecuación de Mincer es descriptiva y el costo laboral ampliado depende del supuesto
fijo de 54 %, por lo que ninguno constituye una estimación causal u oficial.

## Archivos reproducibles

- `output/registro_dominios_geih.csv`
- `output/auditoria_variables_resumen.csv`
- `output/auditoria_variables_detalle.parquet`
- `output/auditoria_indicadores_comparacion.csv`
- `output/auditoria_fuentes.csv`
- `output/auditoria_resumen.json`

## Limitaciones

La falta de variables de diseño impide reproducir errores estándar y coeficientes
de variación oficiales. Un resultado `SIN COMPARABLE` o `SOLO DEFINICIÓN` no se
considera aprobado por contraste numérico: queda validado únicamente por universo,
fórmula, ponderación, identidades internas y estándar conceptual. No se imputan
referencias públicas ausentes.
