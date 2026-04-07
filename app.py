"""
Punto de Entrada del Dashboard GEIH
Usando diseño de UI moderno.
"""
import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="DASHBOARD DANE | GEIH Analytics", 
    page_icon="🇨🇴", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilado Minimalista y Corporativo (Sobrio)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Contenedores de Tarjetas KPI - Diseño Limpio */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700;
        color: #cbd5e1 !important; /* Gris claro corporativo */
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        color: #94a3b8 !important;
        font-weight: 500;
    }
    
    /* Efecto Hover Suave en todo Layout */
    div[data-testid="stBlock"] > div {
        transition: transform 0.2s ease, opacity 0.2s ease;
    }
    
    hr {
        border-color: #334155;
    }
    
    .status-warning {
        padding: 20px;
        background-color: rgba(234, 179, 8, 0.1);
        border-left: 4px solid #eab308;
        border-radius: 8px;
        color: #fef08a;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- Rutas Locales -----------------
RUTA_KPIS = "output/indicadores_mensuales.csv"
RUTA_RAMA_CIUDAD = "output/salarios_por_rama_ciudad.csv"

# ----------------- Funciones de Carga -----------------
@st.cache_data(ttl=60)
def load_data_base():
    data = {}
    if os.path.exists(RUTA_KPIS): data['kpis'] = pd.read_csv(RUTA_KPIS)
    if os.path.exists(RUTA_RAMA_CIUDAD): data['rama'] = pd.read_csv(RUTA_RAMA_CIUDAD)
    return data

@st.cache_data(ttl=60)
def load_data_avanzado(anio):
    data = {}
    if os.path.exists(f"output/ciudades_avanzado_resumen_{anio}.json"):
        import json
        with open(f"output/ciudades_avanzado_resumen_{anio}.json", "r", encoding="utf-8") as f:
            data['avanzado_json'] = json.load(f)
    if os.path.exists(f"output/ciudades_brecha_genero_{anio}.csv"):
        data['brecha'] = pd.read_csv(f"output/ciudades_brecha_genero_{anio}.csv")
    if os.path.exists(f"output/ciudades_costo_laboral_{anio}.csv"):
        data['costos'] = pd.read_csv(f"output/ciudades_costo_laboral_{anio}.csv")
    if os.path.exists(f"output/ciudades_formalidad_sectorial_{anio}.csv"):
        data['formalidad'] = pd.read_csv(f"output/ciudades_formalidad_sectorial_{anio}.csv")
    if os.path.exists(f"output/ciudades_calidad_empleo_{anio}.csv"):
        data['calidad'] = pd.read_csv(f"output/ciudades_calidad_empleo_{anio}.csv")
    if os.path.exists(f"output/ciudades_vulnerabilidad_{anio}.csv"):
        data['vulnerabilidad'] = pd.read_csv(f"output/ciudades_vulnerabilidad_{anio}.csv")
    if os.path.exists(f"output/ciudades_mincer_{anio}.csv"):
        data['mincer'] = pd.read_csv(f"output/ciudades_mincer_{anio}.csv")
    if os.path.exists(f"output/ciudades_rama_sexo_{anio}.csv"):
        data['ramasexo'] = pd.read_csv(f"output/ciudades_rama_sexo_{anio}.csv")
    return data

datos = load_data_base()

# ----------------- Header -----------------
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4b/Logo_del_DANE_%28Colombia%29.svg", width=120)
with col2:
    st.title("Inteligencia Laboral - GEIH Series")
    st.markdown("*Plataforma avanzada de análisis de microdatos (Mercado Laboral & Desarrollo Regional)*")

st.markdown("---")

if 'kpis' not in datos:
    st.markdown(
        "<div class='status-warning'><h3>⚠️ No se encontró la data procesada</h3><p>Para activar el dashboard debes ejecutar primero el pipeline de ingesta en la consola:<br><br><code>python src/01_pipeline_ingesta.py</code><br><code>python src/02_motor_calculo.py</code></p></div>", 
        unsafe_allow_html=True
    )
    st.stop()

# ----------------- Filtros Globales (Sidebar) -----------------
st.sidebar.markdown("## ⚙️ Filtros del Dashboard")
df_kpis = datos['kpis']

anios_disponibles = sorted(df_kpis['Año'].unique().tolist(), reverse=True)
selected_anio = st.sidebar.selectbox("Seleccione Año de Análisis", anios_disponibles)

# Filtrar meses disponibles para ese año
meses_disp_num = sorted(df_kpis[df_kpis['Año'] == selected_anio]['MES'].unique().tolist())
meses_disp = ["Anual (Consolidado Año)"] + meses_disp_num

# Map número a nombre mes
meses_nombres = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

format_func = lambda x: str(x) if isinstance(x, str) else f"{x} - {meses_nombres.get(x, '')}"
selected_mes_op = st.sidebar.selectbox("Seleccione Periodo", meses_disp, format_func=format_func)

# Logica: Si elige Anual, representamos el año con el último mes disponible (ej. Diciembre) ya que usamos metodologíá Año Móvil
if selected_mes_op == "Anual (Consolidado Año)":
    selected_mes = max(meses_disp_num) if meses_disp_num else 12
    etiqueta_periodo = "Anual"
else:
    selected_mes = selected_mes_op
    etiqueta_periodo = meses_nombres.get(selected_mes, str(selected_mes))

ciudades_disponibles = ["Todas (Panorama Nacional)"] + sorted(df_kpis[(df_kpis['Ciudad'] != "Todas (Panorama Nacional)")]['Ciudad'].unique().tolist())
selected_ciudad = st.sidebar.selectbox("Seleccione Ciudad Capital", ciudades_disponibles)

# ----------------- KPIs -----------------
# Cargar fila según filtros (Año, Mes, Ciudad)
df_fil_kpi = df_kpis[(df_kpis['Año'] == selected_anio) & (df_kpis['MES'] == selected_mes) & (df_kpis['Ciudad'] == selected_ciudad)]

if not df_fil_kpi.empty:
    row = df_fil_kpi.iloc[0]
    td_val, tgp_val, to_val = row['TD_%'], row['TGP_%'], row['TO_%']
    oc_m, des_m = row['Ocupados_M'], row['Desocupados_M']
else:
    td_val, tgp_val, to_val, oc_m, des_m = 0, 0, 0, 0, 0

# ----------------- Visualización Principal -----------------
main_tab1, main_tab2 = st.tabs(["📉 Dinámica Mensual & Geográfica", "🏦 Estructura Macro Avanzada (Nacional)"])

with main_tab1:
    titulo_kpi = "Panorama Nacional" if selected_ciudad == "Todas (Panorama Nacional)" else f"Panorama Local: {selected_ciudad}"
    st.subheader(f"{titulo_kpi} ({etiqueta_periodo} {selected_anio})")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label="Tasa de Desempleo (TD)", value=f"{td_val:.1f}%")
    c2.metric(label="Ocupados (Millones)", value=f"{oc_m:.2f}M")
    c3.metric(label="Tasa Global de Part (TGP)", value=f"{tgp_val:.1f}%")
    c4.metric(label="Desocupados (Millones)", value=f"{des_m:.2f}M")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tb1, tb2 = st.tabs(["🏙️ Comparativo Ciudades", "💼 Oportunidades Salariales por Industria"])
    
    with tb1:
        st.markdown("### Mercado Laboral por Ciudades Capitales")
        st.info("ℹ️ **Nota Metodológica:** Las cifras de tasas (TD, TO, TGP) y volúmenes para las ciudades reflejan el **Año Móvil** (promedio móvil de los últimos 12 meses finalizando en el mes seleccionado), de manera homóloga a los reportes oficiales del DANE.")
        # Todas las ciudades en ese mes excluyendo Nacional
        df_ciudades_mes = df_kpis[(df_kpis['Año'] == selected_anio) & (df_kpis['MES'] == selected_mes) & (df_kpis['Ciudad'] != "Todas (Panorama Nacional)")]
    
        if not df_ciudades_mes.empty:
            fig = px.bar(
                df_ciudades_mes.sort_values(by="TD_%", ascending=False).head(20), 
                x="Ciudad", y="TD_%", 
                color="TD_%", 
                color_continuous_scale="Blues_r",
                text="TD_%",
                title=f"Top Ciudades con mayor Tasa de Desempleo ({etiqueta_periodo} {selected_anio})"
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1',
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("Ver tabla de datos detallada (Estadísticas Ciudades)"):
                st.dataframe(df_ciudades_mes[['Ciudad', 'TD_%', 'TGP_%', 'TO_%', 'Ocupados_M']], use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de ciudades para este mes.")
            
    with tb2:
        st.markdown(f"### Retornos Salariales por Rama (Mediana)")
        if 'rama' in datos and not datos['rama'].empty:
            df_rama_anio_mes = datos['rama'][(datos['rama']['Año'] == selected_anio) & (datos['rama']['MES'] == selected_mes)]
            
            subtitulo = ""
            if selected_ciudad != "Todas (Panorama Nacional)":
                df_rama_plot = df_rama_anio_mes[df_rama_anio_mes['Ciudad'] == selected_ciudad]
                subtitulo = f"Sectores más rentables en {selected_ciudad}"
            else:
                # Nacional: mediana de todas las ciudades para el mes
                df_rama_plot = df_rama_anio_mes.groupby('Rama', as_index=False)[['Mediana', 'Mediana_SMMLV']].median()
                subtitulo = "Sectores más rentables a Nivel Nacional (Promedio Ciudades)"
                
            df_plot = df_rama_plot.sort_values("Mediana", ascending=True).tail(10) if not df_rama_plot.empty else pd.DataFrame()
            
            if not df_plot.empty:
                fig2 = px.bar(
                    df_plot, 
                    x="Mediana", y="Rama", orientation='h',
                    color="Mediana_SMMLV", 
                    color_continuous_scale="Greys",
                    title=f"{subtitulo} ({etiqueta_periodo} {selected_anio})"
                )
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1',
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No hay suficientes datos salariales capturados para esta selección.")

with main_tab2:
    titulo_adv = "Radiografía Estructural (Nivel Nacional)" if selected_ciudad == "Todas (Panorama Nacional)" else f"Radiografía Estructural ({selected_ciudad})"
    st.markdown(f"## {titulo_adv} - {selected_anio}")
    st.markdown("Estadísticas extraídas con rigor analítico desde el paquete unificado desglosadas por cobertura geográfica.")
    
    datos_adv_raw = load_data_avanzado(selected_anio)
    # Filtrar localmente por ciudad seleccionada
    datos_adv = {}
    for k, v in datos_adv_raw.items():
        if k == 'avanzado_json':
            # v es una lista de diccionarios, filtramos el correcto
            ciudad_d = next((item for item in v if item.get('Ciudad') == selected_ciudad), None)
            if ciudad_d:
                datos_adv[k] = ciudad_d
        elif isinstance(v, pd.DataFrame) and 'Ciudad' in v.columns:
            df_fil = v[v['Ciudad'] == selected_ciudad].copy()
            if not df_fil.empty:
                datos_adv[k] = df_fil

    # 1. Resumen Json (Gini, Jóvenes)
    if 'avanzado_json' in datos_adv:
        js = datos_adv['avanzado_json']
        col1, col2, col3 = st.columns(3)
        if 'Gini' in js:
            col1.metric("Coeficiente de Gini", f"{js['Gini']:.4f}")
        if 'Joven_TD_joven_%' in js:
            prec_dane = f" ({js.get('Precisión_DANE', '')})" if 'Precisión_DANE' in js else ""
            col2.metric(f"Tasa Desempleo Jóvenes{prec_dane}", f"{js['Joven_TD_joven_%']:.1f}%")
        if 'Joven_Ocupados_joven_M' in js:
            col3.metric("Ocupados Jóvenes (Millones)", f"{js['Joven_Ocupados_joven_M']:.2f}M")
            
    st.markdown("---")
    
    # 2. Matrices (Brecha, Costos, Formalidad, ICE, IVI, Mincer, Rama/Sexo)
    adv_tabs = st.tabs([
        "👫 Brecha de Género", 
        "🔖 Formalidad Sectorial", 
        "💰 Costos Laborales",
        "📈 Calidad (ICE)",
        "🛡️ Vulnerabilidad (IVI)",
        "📚 Retorno Educativo (Mincer)",
        "🚻 Rama / Sexo"
    ])
    adv_tab1, adv_tab2, adv_tab3, adv_tab4, adv_tab5, adv_tab6, adv_tab7 = adv_tabs
    
    with adv_tab1:
        st.subheader("Brecha de Género por Nivel Educativo")
        st.warning("**Nota Metodológica:** La brecha observada es un cálculo bruto que no utiliza Descomposición de Oaxaca-Blinder, por lo tanto no aísla el impacto de la segregación ocupacional (Occupational Sorting).")
        if 'brecha' in datos_adv:
            df_b = datos_adv['brecha']
            # Derretir datos para grafico agrupado
            df_b_melt = df_b.melt(id_vars=['Nivel', 'Brecha_%'], value_vars=['Hombres', 'Mujeres'], var_name='Género', value_name='Ingreso')
            
            fig_b = px.bar(
                df_b_melt, x="Nivel", y="Ingreso", color="Género",
                barmode="group",
                color_discrete_map={"Hombres": "#64748b", "Mujeres": "#cbd5e1"},
                title=f"Comparativa Salarial por Nivel Educativo ({selected_ciudad})",
                hover_data=["Brecha_%"]
            )
            fig_b.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1',
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_b, use_container_width=True)
            
            with st.expander("Ver tabla de datos detallada (Brecha)"):
                st.dataframe(df_b, use_container_width=True, hide_index=True)
        else:
            st.info("Datos de brecha no disponibles aún. Ejecute el motor unificado.")
            
    with adv_tab2:
        st.subheader("Formalidad (Afiliación a Salud y Pensión) y Precisión Muestral DANE")
        if 'formalidad' in datos_adv:
            df_form = datos_adv['formalidad'].sort_values("Afiliado_salud_%", ascending=False)
            
            # Gráfico Comparativo Salud vs Pensión
            if 'Cotiza_pension_%' in df_form.columns and 'Afiliado_salud_%' in df_form.columns:
                # Tomamos el TOP 15 para que no sea un gráfico inmenso
                df_form_top = df_form.head(15).copy()
                df_form_top_melt = df_form_top.melt(id_vars=['Rama'], value_vars=['Afiliado_salud_%', 'Cotiza_pension_%'], var_name='Cobertura', value_name='Porcentaje')
                
                fig_f = px.bar(
                    df_form_top_melt, x='Porcentaje', y='Rama', color='Cobertura',
                    orientation='h', barmode='group',
                    color_discrete_map={'Afiliado_salud_%': '#475569', 'Cotiza_pension_%': '#94a3b8'},
                    title=f"Brecha Salud vs Pensión por Sector (Top 15 - {selected_ciudad})"
                )
                fig_f.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1',
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_f, use_container_width=True)

            with st.expander("Ver tabla de datos detallada (Formalidad)"):
                st.dataframe(df_form, use_container_width=True, hide_index=True)
            
            # Gráfico con Intervalo de Confianza si existe 'CV_%'
            if 'CV_%' in df_form.columns and 'Cotiza_pension_%' in df_form.columns:
                st.markdown("#### Precisión de Estimación (% Pensionados por Industria)")
                st.info("**Nota Analítica:** El Coeficiente de Variación (CV%) es una aproximación. Al no aplicar factores de linealización de Taylor para el muestreo complejo GEIH, las penalidades reales de varianzas en dominios pequeños son mayores.")
                fig_cv = px.scatter(df_form, x="Cotiza_pension_%", y="CV_%", color="Clasificacion_Precision", hover_data=["Rama", "CV_%"], title=f"Dispersión y Riesgo Estadístico DANE ({selected_ciudad})")
                fig_cv.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1',
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_cv, use_container_width=True)
        else:
            st.info("Datos de formalidad no disponibles aún.")
            
    with adv_tab3:
        st.subheader("Costos Laborales Base (Mult. SMMLV)")
        if 'costos' in datos_adv:
            df_costos = datos_adv['costos'].sort_values("Costo_SMMLV", ascending=True)
            
            if not df_costos.empty:
                fig_c = px.bar(
                    df_costos, x="Costo_SMMLV", y="Rama", orientation='h',
                    color="Costo_SMMLV", color_continuous_scale="Greys",
                    title=f"Industrias más y menos costosas para contratar ({selected_ciudad})"
                )
                fig_c.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1',
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_c, use_container_width=True)
            
            df_c_t = df_costos.sort_values("Costo_SMMLV", ascending=False)
            with st.expander("Ver tabla de datos detallada (Costos)"):
                st.dataframe(df_c_t, use_container_width=True, hide_index=True)
        else:
            st.info("Datos de costos no disponibles aún.")

    with adv_tab4:
        st.subheader("Índice de Calidad del Empleo (ICE) por Rama")
        st.markdown("""
            El **ICE** es un indicador multidimensional que evalúa la calidad del puesto de trabajo basándose en:
            - **Ingreso**: Suficiencia del salario en términos de SMMLV.
            - **Estabilidad**: Tipo de contrato.
            - **Seguridad Social**: Afiliación a salud y pensión.
            - **Bienestar**: Jornada laboral adecuada.
        """)
        if 'calidad' in datos_adv:
            df_ice = datos_adv['calidad'].sort_values("ICE", ascending=True)
            if not df_ice.empty:
                fig_ice = px.bar(
                    df_ice, x="ICE", y="Rama", orientation='h',
                    color="ICE", color_continuous_scale="Blues",
                    title=f"Ranking de Calidad del Empleo por Sector ({selected_anio} - {selected_ciudad})"
                )
                fig_ice.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1',
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_ice, use_container_width=True)
            else:
                st.info("Sin registros ICE suficientes.")
        else:
            st.info("Datos de ICE no disponibles.")

    with adv_tab5:
        st.subheader("Índice de Vulnerabilidad Laboral (IVI)")
        st.markdown("""
            El **IVI** mide la probabilidad de que un trabajador pierda su fuente de ingresos o enfrente precariedad extrema.
            *Sectores con IVI > 30% se consideran de alto riesgo estructural.*
        """)
        if 'vulnerabilidad' in datos_adv:
            df_ivi = datos_adv['vulnerabilidad'].sort_values("IVI", ascending=True)
            fig_ivi = px.bar(
                df_ivi, x="IVI", y="Rama", orientation='h',
                color="IVI", color_continuous_scale="Greys",
                title=f"Grado de Vulnerabilidad por Sector ({selected_anio})"
            )
            fig_ivi.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1',
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_ivi, use_container_width=True)
        else:
            st.info("Datos de vulnerabilidad no disponibles.")

    with adv_tab6:
        st.subheader("Ecuación de Mincer: Retornos a la Educación")
        st.warning("**Caveat Econométrico:** Los coeficientes estimados vía MCO presentan Sesgo de Selección de Heckman al omitirse la población inactiva o desocupada en el cálculo. Los retornos reales podrían diferir estructuralmente.")
        st.markdown("""
            Análisis econométrico que estima cuánto aumenta el salario por cada año adicional de inversión en capital humano.
        """)
        if 'mincer' in datos_adv:
            m = datos_adv['mincer'].iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Retorno Educación", f"+{m['beta_educacion']:.1f}%", help="Incremento porcentual del salario por cada año de estudio")
            c2.metric("Retorno Experiencia", f"+{m['beta_exp']:.1f}%", help="Incremento por cada año de experiencia")
            c3.metric("Ajuste del Modelo (R²)", f"{m['R2']:.3f}")
            
            st.info(f"Modelo estimado sobre una muestra de {int(m['N']):,} registros de ocupados a nivel nacional.")
        else:
            st.info("Análisis de Mincer no disponible.")

    with adv_tab7:
        st.subheader("Distribución de Ocupados por Rama y Sexo")
        if 'ramasexo' in datos_adv:
            df_rs = datos_adv['ramasexo']
            # Melt para Plotly si el DF viene ancho
            if 'Hombre_M' in df_rs.columns and 'Mujer_M' in df_rs.columns:
                df_rs_plot = df_rs.melt(id_vars=['Rama'], value_vars=['Hombre_M', 'Mujer_M'], var_name='Sexo', value_name='Personas_M')
                fig_rs = px.bar(
                    df_rs_plot, x="Personas_M", y="Rama", color="Sexo",
                    title="Segregación Horizontal del Mercado Laboral",
                    barmode="group", color_discrete_map={'Hombre_M': '#475569', 'Mujer_M': '#cbd5e1'}
                )
                fig_rs.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1',
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_rs, use_container_width=True)
                
                with st.expander("Ver tabla de datos detallada (Distribución Rama/Sexo)"):
                    st.dataframe(df_rs, use_container_width=True, hide_index=True)
            else:
                with st.expander("Ver tabla de datos detallada (Distribución Rama/Sexo)"):
                    st.dataframe(df_rs, use_container_width=True, hide_index=True)
        else:
            st.info("Datos de distribución por rama/sexo no disponibles.")

st.markdown("---")
st.caption("Desarrollado sobre Python by Néstor Enrique Forero Herrera | `pip install geih-analisis`")
