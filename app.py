"""
Punto de Entrada del Dashboard GEIH
Observatorio del Mercado Laboral Colombiano
"""
import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Observatorio GEIH | Mercado Laboral", 
    page_icon="https://upload.wikimedia.org/wikipedia/commons/4/4b/Logo_del_DANE_%28Colombia%29.svg", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Sistema de Diseño Corporativo ───
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-subtle: rgba(37, 99, 235, 0.08);
        --accent: #0ea5e9;
        --bg-dark: #0f172a;
        --bg-surface: #1e293b;
        --bg-card: rgba(30, 41, 59, 0.65);
        --text-main: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border: rgba(255, 255, 255, 0.08);
        --border-hover: rgba(37, 99, 235, 0.35);
        --shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
        --radius: 12px;
        --transition: all 0.2s ease;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── Card System ── */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem 1.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 0.75rem;
        transition: var(--transition);
    }
    
    .glass-card:hover {
        border-color: var(--border-hover);
        transform: translateY(-1px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    }

    /* ── KPI Metrics ── */
    .kpi-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.35rem;
    }
    
    .kpi-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-main);
        line-height: 1.1;
    }

    /* ── Tab Navigation ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: transparent;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: var(--text-muted);
        border: none;
        border-bottom: 2px solid transparent;
        padding: 8px 20px;
        font-weight: 500;
        font-size: 0.875rem;
    }

    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: var(--primary-light) !important;
        border-bottom: 2px solid var(--primary) !important;
        font-weight: 600;
    }

    /* ── Alerts & Warnings ── */
    .status-warning {
        padding: 20px 24px;
        background: rgba(234, 179, 8, 0.04);
        border: 1px solid rgba(234, 179, 8, 0.15);
        border-left: 4px solid #eab308;
        border-radius: var(--radius);
        color: #fef08a;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    .status-warning strong {
        display: block;
        margin-bottom: 6px;
        font-size: 0.95rem;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-dark);
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    /* ── Section Dividers ── */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 1.5rem 0;
    }

    /* ── Header ── */
    .dashboard-header {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding-bottom: 1rem;
    }

    .header-text h1 {
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
        color: var(--text-main);
    }

    .header-text p {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0.5rem 0 0 0;
        line-height: 1.6;
        max-width: 800px;
    }

    /* ── Expander refinement ── */
    .streamlit-expanderHeader {
        font-size: 0.875rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

def apply_plotly_style(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#e2e8f0", size=12),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        margin=dict(l=20, r=20, t=50, b=20),
        colorway=["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"],
        legend=dict(font=dict(size=11))
    )
    return fig

def render_kpi(label, value):
    st.markdown(f"""
        <div class="glass-card">
            <div class="kpi-container">
                <span class="kpi-label">{label}</span>
                <span class="kpi-value">{value}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ─── Rutas ───
RUTA_KPIS = "output/indicadores_mensuales.csv"
RUTA_RAMA_CIUDAD = "output/salarios_por_rama_ciudad.csv"

# ─── Funciones de Carga ───
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

# ─── Header ───
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4b/Logo_del_DANE_%28Colombia%29.svg", width=100)
with col2:
    st.title("Pulso Laboral: Observatorio GEIH")
    st.caption("Plataforma de inteligencia analítica sobre microdatos de la Gran Encuesta Integrada de Hogares (GEIH), alineada con los estándares metodológicos del DANE — Marco 2018.")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

if 'kpis' not in datos:
    st.markdown(
        "<div class='status-warning'><strong>Datos no disponibles</strong>Para activar el dashboard ejecute el pipeline de ingesta:<br><br><code>python src/01_pipeline_ingesta.py</code><br><code>python src/02_motor_calculo.py</code></div>", 
        unsafe_allow_html=True
    )
    st.stop()

# ─── Filtros (Sidebar) ───
st.sidebar.markdown("## Filtros de Análisis")
df_kpis = datos['kpis']

anios_disponibles = sorted(df_kpis['Año'].unique().tolist(), reverse=True)
selected_anio = st.sidebar.selectbox("Año de análisis", anios_disponibles)

meses_disp_num = sorted(df_kpis[df_kpis['Año'] == selected_anio]['MES'].unique().tolist())
meses_disp = ["Anual (Consolidado Año)"] + meses_disp_num

meses_nombres = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

format_func = lambda x: str(x) if isinstance(x, str) else f"{x} — {meses_nombres.get(x, '')}"
selected_mes_op = st.sidebar.selectbox("Periodo", meses_disp, format_func=format_func)

if selected_mes_op == "Anual (Consolidado Año)":
    selected_mes = max(meses_disp_num) if meses_disp_num else 12
    etiqueta_periodo = "Anual"
else:
    selected_mes = selected_mes_op
    etiqueta_periodo = meses_nombres.get(selected_mes, str(selected_mes))

ciudades_disponibles = ["Todas (Panorama Nacional)"] + sorted(df_kpis[(df_kpis['Ciudad'] != "Todas (Panorama Nacional)")]['Ciudad'].unique().tolist())
selected_ciudad = st.sidebar.selectbox("Ciudad capital", ciudades_disponibles)

# Capa de Seguridad Estadística
st.sidebar.markdown("---")
st.sidebar.markdown("### Precisión Muestral")
ver_ciudades_riesgo = st.sidebar.checkbox("Incluir ciudades con baja precisión", value=False, 
                                          help="Muestra municipios de la Amazonía, Orinoquía y San Andrés cuya muestra es insuficiente para estimaciones estables.")

CIUDADES_RIESGO = ["Inírida", "Leticia", "Mitú", "Mocoa", "Puerto Carreño", "San Andrés", "San José del Guaviare"]

# ─── KPIs ───
df_fil_kpi = df_kpis[(df_kpis['Año'] == selected_anio) & (df_kpis['MES'] == selected_mes) & (df_kpis['Ciudad'] == selected_ciudad)]

if not df_fil_kpi.empty:
    row = df_fil_kpi.iloc[0]
    td_val, tgp_val, to_val = row['TD_%'], row['TGP_%'], row['TO_%']
    oc_m, des_m = row['Ocupados_M'], row['Desocupados_M']
else:
    td_val, tgp_val, to_val, oc_m, des_m = 0, 0, 0, 0, 0

# ─── Navegación Principal ───
main_tab1, main_tab2, main_tab3 = st.tabs([
    "Dinámica Mensual y Geográfica", 
    "Estructura Macro Avanzada", 
    "Diccionario y Metodología"
])

with main_tab1:
    titulo_kpi = "Panorama Nacional" if selected_ciudad == "Todas (Panorama Nacional)" else f"Panorama: {selected_ciudad}"
    st.subheader(f"{titulo_kpi} · {etiqueta_periodo} {selected_anio}")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi("Tasa de Desempleo (TD)", f"{td_val:.1f}%")
    with c2: render_kpi("Ocupados", f"{oc_m:.2f} M")
    with c3: render_kpi("Tasa Global de Participación", f"{tgp_val:.1f}%")
    with c4: render_kpi("Desocupados", f"{des_m:.2f} M")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    tb1, tb2, tb3 = st.tabs(["Comparativo Ciudades", "Retornos Salariales", "Evolución Temporal"])
    
    with tb1:
        st.markdown("#### Mercado Laboral por Ciudades Capitales")
        st.info("**Nota metodológica:** Las cifras reflejan el Año Móvil (ventana de 12 meses), homólogo a los reportes oficiales del DANE.")
        
        # Aviso de confiabilidad
        if selected_ciudad in CIUDADES_RIESGO:
            st.markdown(f"""
                <div class="status-warning">
                    <strong>Clasificación: No confiable</strong>
                    La muestra para <b>{selected_ciudad}</b> es insuficiente (PEA expandida < 30,000). 
                    El error estándar supera el umbral de publicación del DANE. Utilice estas cifras únicamente como referencia direccional.
                </div>
            """, unsafe_allow_html=True)

        df_ciudades_mes = df_kpis[(df_kpis['Año'] == selected_anio) & (df_kpis['MES'] == selected_mes) & (df_kpis['Ciudad'] != "Todas (Panorama Nacional)")]
    
        if not df_ciudades_mes.empty:
            df_plot_ranking = df_ciudades_mes.copy()
            if not ver_ciudades_riesgo:
                df_plot_ranking = df_plot_ranking[~df_plot_ranking['Ciudad'].isin(CIUDADES_RIESGO)]

            fig = px.bar(
                df_plot_ranking.sort_values(by="TD_%", ascending=False).head(20), 
                x="Ciudad", y="TD_%", 
                color="TD_%", 
                color_continuous_scale="Blues_r",
                text="TD_%",
                title=f"Ciudades con mayor Tasa de Desempleo — {etiqueta_periodo} {selected_anio}"
            )
            apply_plotly_style(fig)
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            
            st.plotly_chart(fig, use_container_width=True)
            
            if not ver_ciudades_riesgo:
                st.caption(f"Se han excluido {len(CIUDADES_RIESGO)} ciudades con baja precisión muestral. Active el filtro en el panel lateral para incluirlas.")

            with st.expander("Ver tabla de datos — Estadísticas por ciudad"):
                st.dataframe(df_ciudades_mes[['Ciudad', 'TD_%', 'TGP_%', 'TO_%', 'Ocupados_M']], use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de ciudades para este periodo.")
            
    with tb2:
        st.markdown(f"#### Retornos Salariales por Rama de Actividad (Mediana)")
        if 'rama' in datos and not datos['rama'].empty:
            df_rama_anio_mes = datos['rama'][(datos['rama']['Año'] == selected_anio) & (datos['rama']['MES'] == selected_mes)]
            
            subtitulo = ""
            if selected_ciudad != "Todas (Panorama Nacional)":
                df_rama_plot = df_rama_anio_mes[df_rama_anio_mes['Ciudad'] == selected_ciudad]
                subtitulo = f"Sectores con mayor remuneración — {selected_ciudad}"
            else:
                df_rama_plot = df_rama_anio_mes.groupby('Rama', as_index=False)[['Mediana', 'Mediana_SMMLV']].median()
                subtitulo = "Sectores con mayor remuneración — Nivel Nacional"
                
            df_plot = df_rama_plot.sort_values("Mediana", ascending=True).tail(10) if not df_rama_plot.empty else pd.DataFrame()
            
            if not df_plot.empty:
                fig2 = px.bar(
                    df_plot, 
                    x="Mediana", y="Rama", orientation='h',
                    color="Mediana_SMMLV", 
                    color_continuous_scale="Blues",
                    title=f"{subtitulo} — {etiqueta_periodo} {selected_anio}"
                )
                apply_plotly_style(fig2)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No hay suficientes datos salariales para esta selección.")

    with tb3:
        st.markdown(f"#### Evolución Histórica — {selected_ciudad}")
        
        df_hist = df_kpis[df_kpis['Ciudad'] == selected_ciudad].copy()
        
        if not df_hist.empty:
            df_hist['Fecha'] = pd.to_datetime(df_hist[['Año', 'MES']].rename(columns={'Año': 'year', 'MES': 'month'}).assign(day=1))
            df_hist = df_hist.sort_values('Fecha')
            
            # Serie de tasas
            df_tasas = df_hist.melt(id_vars=['Fecha'], value_vars=['TD_%', 'TGP_%', 'TO_%'], 
                                   var_name='Indicador', value_name='Porcentaje')
            
            fig_tasas = px.line(
                df_tasas, x='Fecha', y='Porcentaje', color='Indicador',
                title="Evolución de Tasas Laborales (Año Móvil)",
                markers=True, line_shape='spline'
            )
            apply_plotly_style(fig_tasas)
            st.plotly_chart(fig_tasas, use_container_width=True)
            
            # Volúmenes
            col1, col2 = st.columns(2)
            with col1:
                fig_oc = px.area(
                    df_hist, x='Fecha', y='Ocupados_M',
                    title="Ocupados (Millones)",
                    color_discrete_sequence=["#2563eb"]
                )
                apply_plotly_style(fig_oc)
                st.plotly_chart(fig_oc, use_container_width=True)
            
            with col2:
                fig_des = px.area(
                    df_hist, x='Fecha', y='Desocupados_M',
                    title="Desocupados (Millones)",
                    color_discrete_sequence=["#60a5fa"]
                )
                apply_plotly_style(fig_des)
                st.plotly_chart(fig_des, use_container_width=True)
                
            with st.expander("Ver tabla de datos históricos"):
                st.dataframe(df_hist[['Año', 'MES', 'TD_%', 'TGP_%', 'TO_%', 'Ocupados_M', 'Desocupados_M']].sort_values(['Año', 'MES'], ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos históricos disponibles para esta ciudad.")

with main_tab2:
    titulo_adv = "Radiografía Estructural — Nacional" if selected_ciudad == "Todas (Panorama Nacional)" else f"Radiografía Estructural — {selected_ciudad}"
    st.markdown(f"## {titulo_adv} · {selected_anio}")
    st.caption("Indicadores avanzados extraídos del paquete unificado de análisis, desglosados por cobertura geográfica.")
    
    datos_adv_raw = load_data_avanzado(selected_anio)
    datos_adv = {}
    for k, v in datos_adv_raw.items():
        if k == 'avanzado_json':
            ciudad_d = next((item for item in v if item.get('Ciudad') == selected_ciudad), None)
            if ciudad_d:
                datos_adv[k] = ciudad_d
        elif isinstance(v, pd.DataFrame) and 'Ciudad' in v.columns:
            df_fil = v[v['Ciudad'] == selected_ciudad].copy()
            if not df_fil.empty:
                datos_adv[k] = df_fil

    # KPIs Avanzados
    if 'avanzado_json' in datos_adv:
        js = datos_adv['avanzado_json']
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'Gini' in js:
                render_kpi("Coeficiente de Gini", f"{js['Gini']:.4f}")
        with col2:
            if 'Joven_TD_joven_%' in js:
                prec_dane = f" ({js.get('Precisión_DANE', '')})" if 'Precisión_DANE' in js else ""
                render_kpi(f"TD Jóvenes{prec_dane}", f"{js['Joven_TD_joven_%']:.1f}%")
        with col3:
            if 'Joven_Ocupados_joven_M' in js:
                render_kpi("Ocupados Jóvenes", f"{js['Joven_Ocupados_joven_M']:.2f} M")
            
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Sub-tabs
    adv_tabs = st.tabs([
        "Brecha de Género", 
        "Formalidad Sectorial", 
        "Costos Laborales",
        "Calidad del Empleo (ICE)",
        "Vulnerabilidad (IVI)",
        "Retorno Educativo (Mincer)",
        "Composición por Sexo"
    ])
    adv_tab1, adv_tab2, adv_tab3, adv_tab4, adv_tab5, adv_tab6, adv_tab7 = adv_tabs
    
    with adv_tab1:
        st.subheader("Brecha de Género por Nivel Educativo")
        st.warning("**Nota metodológica:** La brecha observada es un cálculo bruto que no aplica Descomposición de Oaxaca-Blinder, por lo tanto no aísla el efecto de la segregación ocupacional.")
        if 'brecha' in datos_adv:
            df_b = datos_adv['brecha']
            df_b_melt = df_b.melt(id_vars=['Nivel', 'Brecha_%'], value_vars=['Hombres', 'Mujeres'], var_name='Género', value_name='Ingreso')
            
            fig_b = px.bar(
                df_b_melt, x="Nivel", y="Ingreso", color="Género",
                barmode="group",
                color_discrete_map={"Hombres": "#2563eb", "Mujeres": "#60a5fa"},
                title=f"Comparativa Salarial por Nivel Educativo — {selected_ciudad}",
                hover_data=["Brecha_%"]
            )
            apply_plotly_style(fig_b)
            st.plotly_chart(fig_b, use_container_width=True)
            
            with st.expander("Ver tabla de datos — Brecha salarial"):
                st.dataframe(df_b, use_container_width=True, hide_index=True)
        else:
            st.info("Datos de brecha no disponibles. Ejecute el motor de cálculo.")
            
    with adv_tab2:
        st.subheader("Formalidad: Afiliación a Salud y Pensión")
        if 'formalidad' in datos_adv:
            df_form = datos_adv['formalidad'].sort_values("Afiliado_salud_%", ascending=False)
            
            if 'Cotiza_pension_%' in df_form.columns and 'Afiliado_salud_%' in df_form.columns:
                df_form_top = df_form.head(15).copy()
                df_form_top_melt = df_form_top.melt(id_vars=['Rama'], value_vars=['Afiliado_salud_%', 'Cotiza_pension_%'], var_name='Cobertura', value_name='Porcentaje')
                
                fig_f = px.bar(
                    df_form_top_melt, x='Porcentaje', y='Rama', color='Cobertura',
                    orientation='h', barmode='group',
                    color_discrete_map={'Afiliado_salud_%': '#2563eb', 'Cotiza_pension_%': '#60a5fa'},
                    title="Cobertura Salud vs. Pensión — Top 15 sectores"
                )
                apply_plotly_style(fig_f)
                st.plotly_chart(fig_f, use_container_width=True)

            with st.expander("Ver tabla de datos — Formalidad"):
                st.dataframe(df_form, use_container_width=True, hide_index=True)
            
            if 'CV_%' in df_form.columns and 'Cotiza_pension_%' in df_form.columns:
                st.markdown("#### Precisión de Estimación por Industria")
                st.info("**Nota analítica:** El CV% es una aproximación. Sin linealización de Taylor para el muestreo complejo GEIH, las varianzas reales en dominios pequeños son mayores.")
                fig_cv = px.scatter(df_form, x="Cotiza_pension_%", y="CV_%", 
                                   color="Clasificacion_Precision", hover_data=["Rama", "CV_%"],
                                   title="Dispersión y Riesgo Estadístico")
                apply_plotly_style(fig_cv)
                st.plotly_chart(fig_cv, use_container_width=True)
        else:
            st.info("Datos de formalidad no disponibles.")
            
    with adv_tab3:
        st.subheader("Costos Laborales por Sector (Múlt. SMMLV)")
        if 'costos' in datos_adv:
            df_costos = datos_adv['costos'].sort_values("Costo_SMMLV", ascending=True)
            
            if not df_costos.empty:
                fig_c = px.bar(
                    df_costos, x="Costo_SMMLV", y="Rama", orientation='h',
                    color="Costo_SMMLV", color_continuous_scale="Blues",
                    title="Intensidad de Costos Laborales por Sector"
                )
                apply_plotly_style(fig_c)
                st.plotly_chart(fig_c, use_container_width=True)
            
            with st.expander("Ver tabla de datos — Costos laborales"):
                st.dataframe(df_costos.sort_values("Costo_SMMLV", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("Datos de costos no disponibles.")

    with adv_tab4:
        st.subheader("Índice de Calidad del Empleo (ICE)")
        st.markdown("""
            Indicador multidimensional (0–100) que evalúa la calidad del puesto de trabajo:
            **Ingreso** (30%) · **Estabilidad** (25%) · **Seguridad Social** (25%) · **Bienestar** (20%)
        """)
        if 'calidad' in datos_adv:
            df_ice = datos_adv['calidad'].sort_values("ICE", ascending=True)
            if not df_ice.empty:
                fig_ice = px.bar(
                    df_ice, x="ICE", y="Rama", orientation='h',
                    color="ICE", color_continuous_scale="Blues",
                    title=f"Ranking de Calidad del Empleo — {selected_anio}"
                )
                apply_plotly_style(fig_ice)
                st.plotly_chart(fig_ice, use_container_width=True)
            else:
                st.info("Registros ICE insuficientes.")
        else:
            st.info("Datos de ICE no disponibles.")

    with adv_tab5:
        st.subheader("Índice de Vulnerabilidad Laboral (IVI)")
        st.markdown("Mide el riesgo de precariedad extrema. Sectores con IVI > 30% se consideran de **alto riesgo estructural**.")
        if 'vulnerabilidad' in datos_adv:
            df_ivi = datos_adv['vulnerabilidad'].sort_values("IVI", ascending=True)
            fig_ivi = px.bar(
                df_ivi, x="IVI", y="Rama", orientation='h',
                color="IVI", color_continuous_scale="OrRd",
                title="Vulnerabilidad por Rama de Actividad"
            )
            apply_plotly_style(fig_ivi)
            st.plotly_chart(fig_ivi, use_container_width=True)
        else:
            st.info("Datos de vulnerabilidad no disponibles.")

    with adv_tab6:
        st.subheader("Ecuación de Mincer — Retornos a la Educación")
        st.warning("**Caveat econométrico:** Los coeficientes estimados vía MCO presentan Sesgo de Selección de Heckman al omitir la población inactiva. Los retornos reales podrían diferir estructuralmente.")
        st.markdown("Estimación del retorno salarial por cada año adicional de inversión en capital humano.")
        if 'mincer' in datos_adv:
            m = datos_adv['mincer'].iloc[0]
            col1, col2, col3 = st.columns(3)
            with col1: render_kpi("Retorno Educación", f"+{m['beta_educacion']:.1f}%")
            with col2: render_kpi("Retorno Experiencia", f"+{m['beta_exp']:.1f}%")
            with col3: render_kpi("Ajuste del Modelo (R²)", f"{m['R2']:.3f}")
            
            st.caption(f"Modelo estimado sobre una muestra de {int(m['N']):,} registros.")
        else:
            st.info("Análisis de Mincer no disponible.")

    with adv_tab7:
        st.subheader("Distribución de Ocupados por Rama y Sexo")
        if 'ramasexo' in datos_adv:
            df_rs = datos_adv['ramasexo']
            if 'Hombre_M' in df_rs.columns and 'Mujer_M' in df_rs.columns:
                df_rs_plot = df_rs.melt(id_vars=['Rama'], value_vars=['Hombre_M', 'Mujer_M'], var_name='Sexo', value_name='Personas_M')
                fig_rs = px.bar(
                    df_rs_plot, x="Personas_M", y="Rama", color="Sexo",
                    title="Segregación Horizontal del Mercado Laboral",
                    barmode="group", color_discrete_map={'Hombre_M': '#2563eb', 'Mujer_M': '#60a5fa'}
                )
                apply_plotly_style(fig_rs)
                st.plotly_chart(fig_rs, use_container_width=True)
                
                with st.expander("Ver tabla de datos — Distribución por sexo"):
                    st.dataframe(df_rs, use_container_width=True, hide_index=True)
            else:
                with st.expander("Ver tabla de datos — Distribución por sexo"):
                    st.dataframe(df_rs, use_container_width=True, hide_index=True)
        else:
            st.info("Datos de distribución por rama/sexo no disponibles.")

# ─── Pestaña: Diccionario y Metodología ───
with main_tab3:
    st.markdown("## Diccionario de Variables y Manual Metodológico")
    st.caption("Documentación técnica del observatorio: mapeo de variables, lógica algorítmica y glosario de términos.")

    inner_tab1, inner_tab2, inner_tab3 = st.tabs(["Diccionario de Variables", "Lógica de Cálculo", "Glosario y Umbrales"])

    with inner_tab1:
        st.markdown("#### Mapeo de Variables: DANE (GEIH) → Dashboard")
        st.info("Variables estructurales extraídas de los módulos de Vivienda, Hogares, Personas y Fuerza de Trabajo.")
        
        mapping_data = {
            "Variable Dashboard": [
                "Edad", "Sexo", "Nivel Educativo", "Factor de Expansión", 
                "Ocupado", "Desocupado", "PEA", "PET", 
                "Ingreso Laboral", "Horas Trabajadas", "Rama de Actividad"
            ],
            "Variable DANE (GEIH)": [
                "P6040", "P6020", "P6210 / P6210S1", "FEX_C_2011 / FEX_ADJ",
                "OCI", "DSI", "FT (Fuerza de Trabajo)", "PET (Edad >= 15)",
                "P6426 / ING_LAB", "P6800", "RAMA2D_R12"
            ],
            "Descripción": [
                "Edad cronológica del encuestado.",
                "Género del individuo (1: Hombre, 2: Mujer).",
                "Nivel más alto de estudios alcanzado.",
                "Peso estadístico para representar la población total.",
                "Condición de ocupación según definición OIT.",
                "Condición de desempleo abierto.",
                "Población Económicamente Activa = Ocupados + Desocupados.",
                "Población en Edad de Trabajar (Marco 2018: 15+ años).",
                "Ingreso monetario por actividad principal.",
                "Horas efectivamente laboradas en la semana de referencia.",
                "Clasificación CIIU Rev. 4 Adaptada para Colombia."
            ]
        }
        st.table(pd.DataFrame(mapping_data))

    with inner_tab2:
        st.markdown("#### Metodología de Procesamiento")
        st.markdown("""
        El motor de cálculo (`src/02_motor_calculo.py`) ejecuta la siguiente secuencia:

        **1. Limpieza y Armonización**  
        Se unifican los archivos mensuales del DANE, corrigiendo atípicos en ingresos y estandarizando ramas de actividad (CIIU Rev. 4).

        **2. Expansión Poblacional**  
        Se aplica el factor $FEX\\_ADJ$ a cada registro. Para el cálculo anual, se divide por 12 para evitar sobreestimación del volumen demográfico.

        **3. Construcción del Año Móvil**  
        Las cifras se consolidan en una ventana deslizante de 12 meses. Fórmula de la Tasa de Desempleo:
        """)
        st.latex(r"TD = \frac{\sum_{t-11}^{t} \text{Desocupados}_i}{\sum_{t-11}^{t} \text{PEA}_i} \times 100")
        st.markdown("""
        **4. Estimación Econométrica (Mincer)**  
        Regresión ponderada (WLS) para estimar retornos a la educación. Se excluyen observaciones con ingresos nulos o negativos.
        """)
        st.latex(r"\ln(w_i) = \beta_0 + \beta_1 \text{Educ}_i + \beta_2 \text{Exp}_i + \beta_3 \text{Exp}_i^2 + \epsilon_i")
        st.markdown("""
        **5. Índices Compuestos (ICE / IVI)**  
        Se normalizan las variables de formalidad, ingreso y estabilidad en una escala de 0 a 100 para generar rankings sectoriales.

        **6. Coeficiente de Gini**  
        Calculado sobre la curva de Lorenz del ingreso laboral expandido:
        """)
        st.latex(r"G = 1 - \sum_{i=1}^{n} (X_i - X_{i-1})(Y_i + Y_{i-1})")

    with inner_tab3:
        st.markdown("#### Glosario de Términos")
        st.markdown("""
        | Término | Definición |
        |---|---|
        | **PET** | Población en Edad de Trabajar (15+ años). |
        | **PEA** | Fuerza de trabajo: Ocupados + Desocupados. |
        | **Inactivos** | Personas en edad de trabajar que no buscan ni tienen empleo. |
        | **Subempleo** | Ocupados que desean y están disponibles para trabajar más horas. |
        | **Informalidad** | Ocupados sin afiliación a seguridad social vinculada a su empleo. |
        | **Gini** | 0.0 = igualdad perfecta; 1.0 = desigualdad máxima. |
        | **ICE** | Índice de Calidad del Empleo (0–100). |
        | **IVI** | Índice de Vulnerabilidad Laboral. > 30% = alto riesgo. |
        | **FEX_ADJ** | Factor de expansión ajustado por el DANE. |
        | **Año Móvil** | Agregación de 12 meses consecutivos para suavizar estacionalidad. |
        """)
        
        st.markdown("---")
        st.markdown("#### Niveles de Precisión Muestral (DANE)")
        st.latex(r"CV(\hat{p}) = \frac{SE(\hat{p})}{\hat{p}} \times 100")
        st.markdown("""
        | Nivel | Rango CV | Interpretación |
        |---|---|---|
        | **Alta precisión** | CV ≤ 7% | Cifra publicable sin restricciones. |
        | **Aceptable** | 7% < CV ≤ 15% | Publicable con nota metodológica. |
        | **Baja precisión** | 15% < CV ≤ 20% | Usar con precaución. |
        | **No confiable** | CV > 20% | No publicable por falta de representatividad. |
        """)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.caption("Desarrollado por Nicolás Álvarez, Economista.")
