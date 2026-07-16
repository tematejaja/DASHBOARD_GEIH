# Auditoría de gráficas, leyendas y movimiento

Fecha de validación: 16 de julio de 2026.

## Alcance y método

Se revisaron las 14 figuras del dashboard mediante inspección del código, contratos de los CSV, render real de Streamlit y medición del DOM en escritorio y celular. La revisión comprobó presencia, título, ejes, leyenda, rótulos recortados, recursos rotos, excepciones y desbordamiento horizontal. Los datos no se contrastaron contra cifras externas en esta intervención porque el objetivo fue exclusivamente de presentación; sí se verificaron las identidades internas necesarias para dibujar las figuras.

## Resultados por figura

| Sección | Figura | Hallazgo | Corrección y estado |
| --- | --- | --- | --- |
| Mercado laboral | Tasa de desocupación por dominio | Sin fallo de datos; escala de color redundante | Escala visual sin barra redundante, eje explícito y tooltip conservado. Aprobada. |
| Mercado laboral | Ingreso mediano por rama | Ramas largas y nombre técnico de la escala | Rótulos envueltos, escala redundante retirada y eje en COP. Aprobada. |
| Mercado laboral | Tasas laborales | Leyenda mostraba `TD_%`, `TGP_%` y `TO_%` | Leyenda reemplazada por los nombres completos de las tres tasas. Aprobada. |
| Mercado laboral | Personas ocupadas | Eje vertical heredaba el nombre de columna | Ejes `Periodo` y `Personas ocupadas (millones)`. Aprobada. |
| Mercado laboral | Personas desocupadas | Eje vertical heredaba el nombre de columna | Ejes `Periodo` y `Personas desocupadas (millones)`. Aprobada. |
| Calidad del empleo | Escala de subutilización | Margen no especializado | Eje porcentual explícito, altura y margen para cinco categorías. Aprobada. |
| Calidad del empleo | Cobertura contractual | Categorías densas | Etiquetas rotadas moderadamente y eje de cobertura explícito. Aprobada. |
| Calidad del empleo | Composición NINI | Margen izquierdo genérico | Margen para categorías y eje `Porcentaje de jóvenes (%)`. Aprobada. |
| Estructura anual | Brecha por nivel educativo | Título impreciso, tooltip decía promedio aunque el motor calcula mediana, categorías solapadas | Título y tooltip corregidos a mediana, niveles envueltos y leyenda visible. Aprobada. |
| Estructura anual | Ocupados por rama y sexo | No se dibujaba: esperaba columnas inexistentes `Hombre_M`, `Mujer_M` y `Rama` | Se usa el esquema real `RAMA`, `Hombres`, `Mujeres`, `Total`; se valida la identidad y se convierte a millones. Aprobada. |
| Estructura anual | Índice de Calidad del Empleo | Título interno `undefined` y ramas fuera del contenedor | Título fantasma eliminado, rótulos envueltos, eje ICE y escala redundante retirada. Aprobada. |
| Estructura anual | Índice de Vulnerabilidad Laboral | Título interno `undefined` y ramas fuera del contenedor | Título fantasma eliminado, rótulos envueltos y eje 0–100. Aprobada. |
| Estructura anual | Salud y pensión | Título interno `undefined` | Título fantasma eliminado, leyenda Salud/Pensión contenida y eje porcentual. Aprobada. |
| Estructura anual | Costo laboral simulado | Título interno `undefined`, rótulos largos y escala técnica | Título fantasma eliminado, rótulos envueltos, eje en SMMLV y tooltip marcado como simulación. Aprobada. |

## Control del gráfico por sexo

Los archivos 2022–2026 contienen entre 24 y 29 dominios y no presentan duplicados por dominio, rama y año. Para todas las filas se verificó:

- valores no negativos;
- ausencia de faltantes en las columnas utilizadas;
- `Hombres + Mujeres = Total`, con error máximo observado de `4,66e-10` personas por redondeo numérico;
- conversión a millones después de validar la identidad;
- conservación del nombre íntegro de la rama en el tooltip.

## Revisión de movimiento

Se aplicaron los criterios de `emilkowalski/skills`, instalado globalmente en Codex desde el commit `6bf24434f7730ad169077756cf9c7cd7bd675fc6`. Los seis archivos `SKILL.md` instalados coinciden byte a byte con ese commit.

| Before | After | Why |
| --- | --- | --- |
| Cambio instantáneo entre paneles | Entrada de `180ms`, `translateY(4px)` y opacidad con `cubic-bezier(0.23, 1, 0.32, 1)` | Ayuda a seguir el cambio de estado sin retrasar la consulta. |
| Botones sin respuesta física uniforme | `scale(0.97)` durante la presión, `120ms` con la misma curva | Confirma inmediatamente que el control recibió la acción. |
| Controles Plotly con opacidad fija | Cambio de opacidad de `140ms` y presión de `120ms` | Mejora la localización y el feedback sin mover los datos. |
| Movimiento idéntico para todas las preferencias | Con movimiento reducido se elimina el desplazamiento y se conserva un fundido de `120ms` | Mantiene orientación sin imponer movimiento espacial. |

### Candidatos rechazados

- Animar barras, líneas o áreas al cargar: rechazado porque son datos funcionales que deben compararse sin movimiento decorativo.
- Escalonar la entrada de KPI: rechazado porque se repetiría con cada recálculo de filtros.
- Elevar tarjetas KPI al pasar el cursor: rechazado porque las tarjetas no son controles interactivos.
- Añadir movimiento continuo o seguimiento del puntero: rechazado por distracción y ausencia de propósito estadístico.

## Validación final

- 14 de 14 figuras renderizadas en sus estados correspondientes.
- 0 títulos `undefined` visibles.
- 0 rótulos de eje fuera del contenedor en las seis figuras estructurales.
- 0 leyendas fuera del contenedor.
- 0 excepciones de Streamlit.
- 0 desbordamiento horizontal a 390 px y 1366 px.
- 8 pruebas unitarias aprobadas, incluidas tres nuevas para la transformación por rama y sexo.
