"""
Punto de Entrada del Dashboard GEIH
Observatorio del Mercado Laboral Colombiano
"""
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from src.metodologia_dashboard import dataframe_formulas, dataframe_variables

st.set_page_config(
    page_title="Observatorio GEIH | Mercado Laboral", 
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="auto"
)

# ─── Sistema de Diseño Corporativo ───
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #14b8a6;
        --primary-light: #5eead4;
        --primary-subtle: rgba(20, 184, 166, 0.09);
        --accent: #fbbf24;
        --bg-dark: #111315;
        --bg-surface: #191c1f;
        --bg-card: #1d2124;
        --text-main: #f4f4f3;
        --text-secondary: #c6c8c9;
        --text-muted: #92979a;
        --border: rgba(255, 255, 255, 0.12);
        --border-hover: rgba(94, 234, 212, 0.55);
        --shadow: 0 2px 10px rgba(0, 0, 0, 0.18);
        --radius: 6px;
        --transition: all 0.2s ease;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── Card System ── */
    .glass-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem 1.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 0.75rem;
        transition: var(--transition);
    }
    
    .glass-card:hover {
        border-color: var(--border-hover);
        box-shadow: var(--shadow);
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
        letter-spacing: 0;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-main);
        line-height: 1.1;
        font-variant-numeric: tabular-nums;
    }

    /* ── Tab Navigation ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: transparent;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0;
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 44px;
        white-space: normal;
        word-break: normal;
        overflow-wrap: normal;
        background-color: transparent;
        border-radius: 0;
        color: var(--text-muted);
        border: none;
        border-bottom: 2px solid transparent;
        padding: 8px 20px;
        font-weight: 500;
        font-size: 0.875rem;
        letter-spacing: 0;
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

    .stSelectbox [data-baseweb="select"] > div,
    .stCheckbox label {
        min-height: 44px;
    }

    [data-testid="stMetricValue"], [role="gridcell"] {
        font-variant-numeric: tabular-nums;
    }

    /* ── Section Dividers ── */
    .section-divider {
        height: 1px;
        background: var(--border);
        margin: 1.5rem 0;
    }

    h1, h2, h3, h4, p, label, button {
        letter-spacing: 0 !important;
    }

    [data-testid="stAppViewContainer"] h1 {
        font-size: 2.25rem;
        line-height: 1.15;
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

    /* ── Responsive Design (Mobile) ── */
    @media (max-width: 768px) {
        html, body, [data-testid="stAppViewContainer"] {
            max-width: 100%;
            overflow-x: hidden;
        }
        .block-container {
            padding: 1.25rem 1rem 3rem;
        }
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
            gap: 0.75rem;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 1 1 100%;
            min-width: 0;
            width: 100%;
        }
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            scrollbar-width: thin;
        }
        .glass-card {
            padding: 1rem;
        }
        .kpi-value {
            font-size: 1.5rem;
        }
        .header-text h1 {
            font-size: 1.35rem;
        }
        .header-text p {
            font-size: 0.8rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 7px;
            font-size: 0.78rem;
            min-height: 44px;
        }
        .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
        }
        [data-testid="stAppViewContainer"] h1 {
            font-size: 2rem;
        }
        [data-testid="stAppViewContainer"] h2 {
            font-size: 1.6rem;
        }
        [data-testid="stAppViewContainer"] h3 {
            font-size: 1.25rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

def apply_plotly_style(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#e7e5e4", size=12),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        margin=dict(l=20, r=20, t=50, b=20),
        colorway=["#14b8a6", "#fbbf24", "#60a5fa", "#f472b6", "#a3e635"],
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
RUTA_VALOR_AGREGADO = "output/indicadores_valor_agregado.csv"
CIUDAD_NACIONAL = "Todas (Panorama Nacional)"
DATA_VERSION = "geih-audit-2026-07-15"

# ─── Funciones de Carga ───
@st.cache_data(ttl=3600)
def load_data_base(version: str):
    data = {}
    if os.path.exists(RUTA_KPIS): data['kpis'] = pd.read_csv(RUTA_KPIS)
    if os.path.exists(RUTA_RAMA_CIUDAD): data['rama'] = pd.read_csv(RUTA_RAMA_CIUDAD)
    if os.path.exists(RUTA_VALOR_AGREGADO): data['valor_agregado'] = pd.read_csv(RUTA_VALOR_AGREGADO)
    if os.path.exists("output/auditoria_diccionario_logica.json"):
        import json
        with open("output/auditoria_diccionario_logica.json", "r", encoding="utf-8") as f:
            data['auditoria_metodologia'] = json.load(f)
    return data

@st.cache_data(ttl=3600)
def load_data_avanzado(anio, version: str):
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

datos = load_data_base(DATA_VERSION)

# ─── Header ───
st.title("Pulso Laboral: Observatorio GEIH")
st.caption("Cifras de empleo, ingresos y condiciones laborales construidas con los microdatos de la GEIH, marco 2018.")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

if 'kpis' not in datos:
    st.markdown(
        "<div class='status-warning'><strong>Datos no disponibles</strong>No se encontraron las salidas estadísticas del observatorio.</div>",
        unsafe_allow_html=True
    )
    st.stop()

# ─── Filtros (Sidebar) ───
st.sidebar.markdown("## Filtros de Análisis")
df_kpis = datos['kpis']

anios_disponibles = sorted(df_kpis['Año'].unique().tolist(), reverse=True)
selected_anio = st.sidebar.selectbox("Año de análisis", anios_disponibles)

meses_disp_num = sorted(df_kpis[df_kpis['Año'] == selected_anio]['MES'].unique().tolist())
OPCION_MOVIL = "Últimos 12 meses"
meses_disp = [OPCION_MOVIL] + meses_disp_num

meses_nombres = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

format_func = lambda x: str(x) if isinstance(x, str) else f"{x} — {meses_nombres.get(x, '')}"
selected_mes_op = st.sidebar.selectbox("Periodo", meses_disp, format_func=format_func)

if selected_mes_op == OPCION_MOVIL:
    selected_mes = max(meses_disp_num) if meses_disp_num else 12
    etiqueta_periodo = f"12 meses a {str(meses_nombres.get(selected_mes, selected_mes)).lower()}"
else:
    selected_mes = selected_mes_op
    etiqueta_periodo = str(meses_nombres.get(selected_mes, selected_mes)).lower()

ultimo_mes_anio = max(meses_disp_num) if meses_disp_num else 12
cobertura_estructura = (
    f"enero–{meses_nombres.get(ultimo_mes_anio, ultimo_mes_anio).lower()} de {selected_anio}"
    if ultimo_mes_anio < 12 else f"enero–diciembre de {selected_anio}"
)

ciudades_disponibles = ["Todas (Panorama Nacional)"] + sorted(df_kpis[(df_kpis['Ciudad'] != "Todas (Panorama Nacional)")]['Ciudad'].unique().tolist())
selected_ciudad = st.sidebar.selectbox("Dominio GEIH", ciudades_disponibles)

# Capa de Seguridad Estadística
st.sidebar.markdown("---")
st.sidebar.markdown("### Precisión Muestral")
ver_ciudades_riesgo = st.sidebar.checkbox("Incluir ciudades con baja precisión", value=False, 
                                          help="Incluye dominios con menor tamaño muestral. La clasificación es preventiva y no sustituye errores oficiales del diseño GEIH.")

CIUDADES_RIESGO = ["Inírida", "Leticia", "Mitú", "Mocoa", "Puerto Carreño", "San Andrés", "San José del Guaviare"]

# ─── KPIs ───
df_fil_kpi = df_kpis[(df_kpis['Año'] == selected_anio) & (df_kpis['MES'] == selected_mes) & (df_kpis['Ciudad'] == selected_ciudad)]

if not df_fil_kpi.empty:
    row = df_fil_kpi.iloc[0]
    td_val, tgp_val, to_val = row['TD_%'], row['TGP_%'], row['TO_%']
    oc_m, des_m = row['Ocupados_M'], row['Desocupados_M']
else:
    td_val, tgp_val, to_val, oc_m, des_m = 0, 0, 0, 0, 0

# ─── Alerta Global de Precisión Muestral ───
if selected_ciudad in CIUDADES_RIESGO:
    st.markdown(f"""
        <div class="status-warning" style="margin-bottom: 20px;">
            <strong>Precaución por tamaño muestral</strong>
            <b>{selected_ciudad}</b> pertenece al grupo de dominios pequeños del tablero.
            Los indicadores son estimaciones exploratorias: no se dispone aquí de estrato y conglomerado
            para reproducir el error de muestreo oficial del DANE.
        </div>
    """, unsafe_allow_html=True)

# ─── Navegación Principal ───
main_tab1, main_tab_presion, main_tab2, main_tab3 = st.tabs([
    "Mercado",
    "Presión",
    "Macro",
    "Método"
])

with main_tab1:
    titulo_kpi = "Panorama Nacional" if selected_ciudad == "Todas (Panorama Nacional)" else f"Panorama: {selected_ciudad}"
    st.subheader(f"{titulo_kpi} · {etiqueta_periodo} {selected_anio}")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi("Tasa de desocupación", f"{td_val:.1f}%")
    with c2: render_kpi("Ocupados", f"{oc_m:.2f} M")
    with c3: render_kpi("Tasa Global de Participación", f"{tgp_val:.1f}%")
    with c4: render_kpi("Desocupados", f"{des_m:.2f} M")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    tb1, tb2, tb3 = st.tabs(["Ciudades", "Ingresos por rama", "Evolución"])
    
    with tb1:
        st.markdown("#### Mercado laboral por dominios GEIH")
        st.info("Las cifras corresponden a los últimos 12 meses disponibles. Las tasas se calculan con sumas expandidas, no como promedios mensuales.")
        
        df_ciudades_mes = df_kpis[(df_kpis['Año'] == selected_anio) & (df_kpis['MES'] == selected_mes) & (df_kpis['Ciudad'] != "Todas (Panorama Nacional)")]
        df_nacional_mes = df_kpis[(df_kpis['Año'] == selected_anio) & (df_kpis['MES'] == selected_mes) & (df_kpis['Ciudad'] == "Todas (Panorama Nacional)")]
    
        if not df_ciudades_mes.empty:
            df_plot_ranking = df_ciudades_mes.copy()
            if not ver_ciudades_riesgo:
                df_plot_ranking = df_plot_ranking[~df_plot_ranking['Ciudad'].isin(CIUDADES_RIESGO)]

            fig = px.bar(
                df_plot_ranking.sort_values(by="TD_%", ascending=False).head(20), 
                x="Ciudad", y="TD_%", 
                color="TD_%", 
                color_continuous_scale="Viridis",
                text="TD_%",
                title=f"Ciudades con mayor tasa de desocupación — {etiqueta_periodo} {selected_anio}"
            )
            fig.update_traces(hovertemplate='<b>%{x}</b><br>Tasa de desocupación: %{y:.1f}%<extra></extra>')
            apply_plotly_style(fig)
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            
            st.plotly_chart(fig, width="stretch")
            
            if not ver_ciudades_riesgo:
                st.caption(f"Se han excluido {len(CIUDADES_RIESGO)} ciudades con baja precisión muestral. Active el filtro en el panel lateral para incluirlas.")

            with st.expander("Ver tabla de datos — Estadísticas por ciudad"):
                # La referencia nacional permite interpretar cada ciudad frente al total país.
                df_tabla_comparativa = pd.concat([df_nacional_mes, df_ciudades_mes], ignore_index=True)
                df_tabla_comparativa['Dominio'] = df_tabla_comparativa['Ciudad'].replace(
                    {'Todas (Panorama Nacional)': 'Total nacional'}
                )
                df_tabla_comparativa['_orden'] = df_tabla_comparativa['Dominio'].ne('Total nacional').astype(int)
                df_tabla_comparativa = df_tabla_comparativa.sort_values(['_orden', 'Dominio'])

                comparativo_config = {
                    'Dominio': 'Dominio geográfico',
                    'TD_%': st.column_config.NumberColumn('Tasa de desocupación (%)', format='%.1f%%'),
                    'TGP_%': st.column_config.NumberColumn('Tasa global de participación (%)', format='%.1f%%'),
                    'TO_%': st.column_config.NumberColumn('Tasa de ocupación (%)', format='%.1f%%'),
                    'Tasa_Informalidad_%': st.column_config.NumberColumn(
                        'Proporción de ocupados informales (%)',
                        help='Ocupados clasificados como informales según la metodología DANE GEIH marco 2018, sobre el total de ocupados.',
                        format='%.1f%%'
                    ),
                    'Informales_M': st.column_config.NumberColumn('Ocupados informales (millones)', format='%.2f M'),
                    'Ocupados_M': st.column_config.NumberColumn('Población ocupada total (millones)', format='%.2f M')
                }
                cols_to_show = ['Dominio', 'TD_%', 'TGP_%', 'TO_%', 'Tasa_Informalidad_%', 'Informales_M', 'Ocupados_M']

                st.dataframe(
                    df_tabla_comparativa[cols_to_show],
                    column_config=comparativo_config,
                    width="stretch",
                    hide_index=True
                )
        else:
            st.info("No hay datos de ciudades para este periodo.")
            
    with tb2:
        st.markdown("#### Ingreso laboral mediano por rama")
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
                    color_continuous_scale="Viridis",
                    title=f"{subtitulo} — {etiqueta_periodo} {selected_anio}",
                    hover_data=["Mediana_SMMLV"]
                )
                fig2.update_traces(hovertemplate='<b>%{y}</b><br>Salario Mediano: $%{x:,.0f}<br>Eq. Salario Mínimo: %{customdata[0]:.2f} SMMLV<extra></extra>')
                apply_plotly_style(fig2)
                st.plotly_chart(fig2, width="stretch")
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
                title="Tasas laborales — últimos 12 meses",
                markers=True, line_shape='spline'
            )
            fig_tasas.update_traces(hovertemplate='<b>%{x|%B %Y}</b><br>Tasa: %{y:.1f}%<extra></extra>')
            apply_plotly_style(fig_tasas)
            st.plotly_chart(fig_tasas, width="stretch")
            
            # Volúmenes
            col1, col2 = st.columns(2)
            with col1:
                fig_oc = px.area(
                    df_hist, x='Fecha', y='Ocupados_M',
                    title="Ocupados (Millones)",
                    color_discrete_sequence=["#14b8a6"]
                )
                fig_oc.update_traces(hovertemplate='<b>%{x|%B %Y}</b><br>Ocupados: %{y:.2f} Millones<extra></extra>')
                apply_plotly_style(fig_oc)
                st.plotly_chart(fig_oc, width="stretch")
            
            with col2:
                fig_des = px.area(
                    df_hist, x='Fecha', y='Desocupados_M',
                    title="Desocupados (Millones)",
                    color_discrete_sequence=["#fbbf24"]
                )
                fig_des.update_traces(hovertemplate='<b>%{x|%B %Y}</b><br>Desocupados: %{y:.2f} Millones<extra></extra>')
                apply_plotly_style(fig_des)
                st.plotly_chart(fig_des, width="stretch")

            with st.expander("Ver tabla de datos históricos"):
                cols_hist = ['Año', 'MES', 'TD_%', 'TGP_%', 'TO_%']
                if 'Tasa_Informalidad_%' in df_hist.columns:
                    cols_hist.append('Tasa_Informalidad_%')
                cols_hist.extend(['Ocupados_M', 'Desocupados_M'])
                
                hist_config = {
                    'Año': 'Año',
                    'MES': 'Mes',
                    'TD_%': st.column_config.NumberColumn('Tasa de desocupación', format='%.1f%%'),
                    'TGP_%': st.column_config.NumberColumn('TGP', format='%.1f%%'),
                    'TO_%': st.column_config.NumberColumn('TO', format='%.1f%%'),
                    'Tasa_Informalidad_%': st.column_config.NumberColumn('Tasa de Informalidad', format='%.1f%%'),
                    'Ocupados_M': st.column_config.NumberColumn('Ocupados (Millones)', format='%.2f M'),
                    'Desocupados_M': st.column_config.NumberColumn('Desocupados (Millones)', format='%.2f M')
                }
                st.dataframe(
                    df_hist[cols_hist].sort_values(['Año', 'MES'], ascending=False),
                    column_config=hist_config,
                    width="stretch",
                    hide_index=True
                )
        else:
            st.info("No hay datos históricos disponibles para esta ciudad.")

with main_tab_presion:
    st.markdown("## Presión y calidad laboral")

    if 'valor_agregado' not in datos:
        st.info("Los indicadores de presión y calidad no están disponibles para esta versión de los datos.")
    else:
        df_valor = datos['valor_agregado']
        valor_sel = df_valor[
            (df_valor['Año'] == selected_anio)
            & (df_valor['MES'] == selected_mes)
            & (df_valor['Ciudad'] == selected_ciudad)
        ]

        if valor_sel.empty:
            st.info("No hay resultados disponibles para esta selección.")
        else:
            v = valor_sel.iloc[0]
            meses_ventana = int(v['Periodo_Meses'])
            alcance = "ventana móvil de 12 meses" if meses_ventana == 12 else "estimación mensual"
            dominio = "Total nacional" if selected_ciudad == "Todas (Panorama Nacional)" else selected_ciudad
            mes_caption = str(meses_nombres.get(selected_mes, selected_mes)).lower()
            st.caption(f"{dominio} · {mes_caption} {selected_anio} · {alcance}")

            def pct(valor):
                return f"{valor:.1f}%" if pd.notna(valor) else "No estimable"

            def cop(valor):
                return f"${valor:,.0f}" if pd.notna(valor) else "No estimable"

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                render_kpi("Tasa de subocupación", pct(v['Tasa_Subocupacion_%']))
            with k2:
                render_kpi("Subutilización amplia (LU4)", pct(v['Tasa_Subutilizacion_LU4_%']))
            with k3:
                render_kpi("Desempleo de larga duración", pct(v['Desempleo_Larga_Duracion_%']))
            with k4:
                render_kpi("Jóvenes NINI (15–28)", pct(v['Tasa_NINI_15_28_%']))

            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            p1, p2, p3 = st.tabs(["Presión", "Contratos e ingresos", "Jóvenes"])

            with p1:
                presion = pd.DataFrame({
                    'Indicador': [
                        'Insuficiencia de horas',
                        'Subocupación objetiva',
                        'LU2: desocupación + horas',
                        'LU3: desocupación + fuerza potencial',
                        'LU4: presión laboral amplia',
                    ],
                    'Porcentaje': [
                        v['Tasa_Insuficiencia_Horas_%'],
                        v['Tasa_Subocupacion_%'],
                        v['Tasa_Subutilizacion_LU2_%'],
                        v['Tasa_Subutilizacion_LU3_%'],
                        v['Tasa_Subutilizacion_LU4_%'],
                    ],
                })
                fig_presion = px.bar(
                    presion, x='Porcentaje', y='Indicador', orientation='h',
                    color='Indicador',
                    color_discrete_sequence=['#60a5fa', '#14b8a6', '#a3e635', '#fbbf24', '#f87171'],
                    title="Escala de subutilización de la fuerza de trabajo",
                )
                fig_presion.update_traces(hovertemplate='<b>%{y}</b><br>%{x:.1f}%<extra></extra>')
                fig_presion.update_layout(showlegend=False)
                apply_plotly_style(fig_presion)
                st.plotly_chart(fig_presion, width="stretch")

                d1, d2 = st.columns(2)
                with d1:
                    st.metric("Duración mediana de búsqueda", f"{v['Duracion_Desempleo_Mediana_Semanas']:.0f} semanas")
                with d2:
                    st.metric("Desocupados con 52 semanas o más", pct(v['Desempleo_Larga_Duracion_%']))
                st.caption("La duración se calcula entre personas desocupadas con semanas de búsqueda observadas.")

            with p2:
                q1, q2, q3 = st.columns(3)
                with q1:
                    st.metric("Asalariados con contrato escrito", pct(v['Contrato_Escrito_%']))
                with q2:
                    st.metric("Ocupados que cotizan a pensión", pct(v['Cotiza_Pension_%']))
                with q3:
                    st.metric("Protección laboral integral", pct(v['Proteccion_Integral_%']))

                calidad = pd.DataFrame({
                    'Indicador': ['Contrato escrito', 'Contrato indefinido', 'Prestaciones completas', 'Protección integral'],
                    'Porcentaje': [
                        v['Contrato_Escrito_%'], v['Contrato_Indefinido_%'],
                        v['Prestaciones_Completas_%'], v['Proteccion_Integral_%'],
                    ],
                })
                fig_calidad = px.bar(
                    calidad, x='Indicador', y='Porcentaje', color='Indicador',
                    color_discrete_sequence=['#14b8a6', '#60a5fa', '#a3e635', '#fbbf24'],
                    title="Cobertura contractual y de protección social",
                )
                fig_calidad.update_traces(hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>')
                fig_calidad.update_layout(showlegend=False)
                apply_plotly_style(fig_calidad)
                st.plotly_chart(fig_calidad, width="stretch")

                i1, i2 = st.columns(2)
                with i1:
                    st.metric("Ingreso laboral real mediano", cop(v['Ingreso_Real_Mediano_COP_2018']))
                    st.caption("Pesos constantes de diciembre de 2018; ingreso laboral positivo.")
                with i2:
                    st.metric("Ingreso inferior a 1 SMMLV", pct(v['Ingreso_Bajo_SMMLV_%']))
                    st.caption("Entre ocupados con ingreso laboral positivo observado.")

            with p3:
                y1, y2 = st.columns(2)
                with y1:
                    st.metric("Tasa NINI de 15 a 28 años", pct(v['Tasa_NINI_15_28_%']))
                    nini_componentes = pd.DataFrame({
                        'Componente': ['NINI desocupados', 'NINI fuera de la fuerza laboral'],
                        'Porcentaje': [v['NINI_Desocupados_%'], v['NINI_Fuera_FT_%']],
                    })
                    fig_nini = px.bar(
                        nini_componentes, x='Porcentaje', y='Componente', orientation='h',
                        color='Componente', color_discrete_sequence=['#14b8a6', '#fbbf24'],
                        title="Composición de la tasa NINI",
                    )
                    fig_nini.update_traces(hovertemplate='<b>%{y}</b><br>%{x:.1f}% de jóvenes<extra></extra>')
                    fig_nini.update_layout(showlegend=False)
                    apply_plotly_style(fig_nini)
                    st.plotly_chart(fig_nini, width="stretch")
                with y2:
                    st.metric("Tasa NINI OIT de 15 a 24 años", pct(v['Tasa_NINI_15_24_%']))
                    st.caption("La medida 15–24 permite comparación internacional; la medida 15–28 conserva la adaptación nacional.")
                    st.metric("Ocupados con sobrecalificación", pct(v['Sobrecalificacion_%']))
                    st.caption("Nivel educativo superior al requerimiento normativo de la ocupación CIUO-08.")
                    st.info(
                        "Este indicador mide desajuste educativo, no habilidades efectivas. "
                        "Excluye fuerzas armadas y registros sin nivel educativo u ocupación clasificable."
                    )

            st.markdown("### Comparativo territorial")
            tabla_valor = df_valor[
                (df_valor['Año'] == selected_anio) & (df_valor['MES'] == selected_mes)
            ].copy()
            if not ver_ciudades_riesgo:
                tabla_valor = tabla_valor[~tabla_valor['Ciudad'].isin(CIUDADES_RIESGO)]
            tabla_valor['Dominio'] = tabla_valor['Ciudad'].replace({CIUDAD_NACIONAL: 'Total nacional'})
            tabla_valor['_orden'] = tabla_valor['Dominio'].ne('Total nacional').astype(int)
            tabla_valor = tabla_valor.sort_values(['_orden', 'Tasa_Subutilizacion_LU4_%'], ascending=[True, False])

            columnas_valor = [
                'Dominio', 'Tasa_Subocupacion_%', 'Tasa_Subutilizacion_LU4_%',
                'Desempleo_Larga_Duracion_%', 'Contrato_Escrito_%',
                'Proteccion_Integral_%', 'Tasa_NINI_15_28_%', 'Tasa_NINI_15_24_%', 'Sobrecalificacion_%',
            ]
            st.dataframe(
                tabla_valor[columnas_valor],
                column_config={
                    'Dominio': st.column_config.TextColumn('Dominio', width='medium'),
                    'Tasa_Subocupacion_%': st.column_config.NumberColumn('Subocup. (%)', format='%.1f%%', width='small'),
                    'Tasa_Subutilizacion_LU4_%': st.column_config.NumberColumn('LU4 (%)', format='%.1f%%', width='small'),
                    'Desempleo_Larga_Duracion_%': st.column_config.NumberColumn('Desemp. ≥52 sem. (%)', format='%.1f%%', width='small'),
                    'Contrato_Escrito_%': st.column_config.NumberColumn('Contrato escrito (%)', format='%.1f%%', width='small'),
                    'Proteccion_Integral_%': st.column_config.NumberColumn('Protección integral (%)', format='%.1f%%', width='small'),
                    'Tasa_NINI_15_28_%': st.column_config.NumberColumn('NINI 15–28 (%)', format='%.1f%%', width='small'),
                    'Tasa_NINI_15_24_%': st.column_config.NumberColumn('NINI 15–24, estándar OIT (%)', format='%.1f%%', width='small'),
                    'Sobrecalificacion_%': st.column_config.NumberColumn('Sobrecalif. (%)', format='%.1f%%', width='small'),
                },
                width="stretch",
                hide_index=True,
            )

            with st.expander("Definiciones y universos estadísticos"):
                st.markdown(
                    "**LU2:** insuficiencia de horas + desocupación sobre la fuerza de trabajo.  \n"
                    "**LU3:** desocupación + fuerza de trabajo potencial sobre la fuerza de trabajo ampliada.  \n"
                    "**LU4:** insuficiencia de horas + desocupación + fuerza de trabajo potencial, "
                    "sobre fuerza de trabajo + fuerza de trabajo potencial.  \n"
                    "**Protección integral:** contrato escrito, cotización pensional y prestaciones completas entre asalariados.  \n"
                    "**NINI:** jóvenes de 15 a 28 años no ocupados y que no asisten a educación formal.  \n"
                    "**Sobrecalificación:** comparación normativa CINE–CIUO-08 entre ocupados con información válida."
                )

with main_tab2:
    titulo_adv = "Indicadores estructurales — Nacional" if selected_ciudad == "Todas (Panorama Nacional)" else f"Indicadores estructurales — {selected_ciudad}"
    st.markdown(f"## {titulo_adv} · {selected_anio}")
    st.caption(
        f"Resultados agregados para {cobertura_estructura}. No cambian con el selector mensual. "
        "Las ramas requieren al menos 30 registros y 5.000 personas expandidas."
    )

    datos_adv_raw = load_data_avanzado(selected_anio, DATA_VERSION)
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
    
    # ─── Sección 1: Desigualdades y Brechas ───
    st.markdown("### Ingresos y participación por sexo")
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        st.subheader("Brecha de Género por Nivel Educativo")
        st.caption("Diferencia descriptiva entre medianas. No controla por ocupación, experiencia ni horas trabajadas.")
        if 'brecha' in datos_adv:
            df_b = datos_adv['brecha']
            df_b_melt = df_b.melt(id_vars=['Nivel', 'Brecha_%'], value_vars=['Hombres', 'Mujeres'], var_name='Género', value_name='Ingreso')
            fig_b = px.bar(
                df_b_melt, x="Nivel", y="Ingreso", color="Género",
                barmode="group",
                color_discrete_map={"Hombres": "#14b8a6", "Mujeres": "#f472b6"},
                title=f"Salarial por Nivel Educativo",
                hover_data=["Brecha_%"]
            )
            fig_b.update_traces(hovertemplate='<b>Nivel: %{x}</b><br>Género: %{data.name}<br>Ingreso Promedio: $%{y:,.0f}<br>Brecha del Nivel: %{customdata[0]:.1f}%<extra></extra>')
            apply_plotly_style(fig_b)
            st.plotly_chart(fig_b, width="stretch")
            
            with st.expander("Ver tabla de datos — Brecha salarial"):
                st.dataframe(df_b, width="stretch", hide_index=True)
        else:
            st.info("Datos de brecha no disponibles.")
            
    with c_b2:
        st.subheader("Distribución de Ocupados por Rama y Sexo")
        st.caption("Población ocupada por rama y sexo, en millones de personas.")
        if 'ramasexo' in datos_adv:
            df_rs = datos_adv['ramasexo']
            if 'Hombre_M' in df_rs.columns and 'Mujer_M' in df_rs.columns:
                df_rs_plot = df_rs.melt(id_vars=['Rama'], value_vars=['Hombre_M', 'Mujer_M'], var_name='Sexo', value_name='Personas_M')
                df_rs_plot['Género'] = df_rs_plot['Sexo'].replace({'Hombre_M': 'Hombres', 'Mujer_M': 'Mujeres'})
                fig_rs = px.bar(
                    df_rs_plot, x="Personas_M", y="Rama", color="Género",
                    barmode="group", color_discrete_map={'Hombres': '#14b8a6', 'Mujeres': '#f472b6'}
                )
                fig_rs.update_traces(hovertemplate='<b>Sector: %{y}</b><br>Género: %{data.name}<br>Volumen: %{x:.2f} M ocupados<extra></extra>')
                apply_plotly_style(fig_rs)
                st.plotly_chart(fig_rs, width="stretch")

                with st.expander("Ver tabla de datos — Distribución por sexo"):
                    st.dataframe(df_rs, width="stretch", hide_index=True)
        else:
            st.info("Datos no disponibles.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ─── Sección 2: Calidad y Vulnerabilidad ───
    st.markdown("### Condiciones del empleo")
    c_c1, c_c2 = st.columns(2)
    with c_c1:
        st.subheader("Índice de Calidad del Empleo (ICE)")
        st.caption("Pensión (30%), salud (25%), jornada usual de 20–48 horas (25%) e ingreso ≥ SMMLV (20%). Índice analítico propio.")
        if 'calidad' in datos_adv:
            df_ice = datos_adv['calidad'].sort_values("ICE", ascending=True)
            if not df_ice.empty:
                fig_ice = px.bar(
                    df_ice.tail(15), x="ICE", y="Rama", orientation='h',
                    color="ICE", color_continuous_scale="Viridis",
                )
                fig_ice.update_traces(hovertemplate='<b>%{y}</b><br>Puntaje ICE: %{x:.1f} / 100<extra></extra>')
                apply_plotly_style(fig_ice)
                st.plotly_chart(fig_ice, width="stretch")
            else:
                st.info("Registros insuficientes.")
        else:
            st.info("Datos no disponibles.")

    with c_c2:
        st.subheader("Índice de Vulnerabilidad Laboral (IVI)")
        st.caption("Promedio de cuatro señales de riesgo laboral. Es un índice comparativo propio, sin umbral oficial.")
        if 'vulnerabilidad' in datos_adv:
            df_ivi = datos_adv['vulnerabilidad'].sort_values("IVI", ascending=True)
            fig_ivi = px.bar(
                df_ivi.tail(15), x="IVI", y="Rama", orientation='h',
                color="IVI", color_continuous_scale="OrRd",
            )
            fig_ivi.update_traces(hovertemplate='<b>%{y}</b><br>Nivel de Vulnerabilidad: %{x:.1f}%<extra></extra>')
            apply_plotly_style(fig_ivi)
            st.plotly_chart(fig_ivi, width="stretch")
        else:
            st.info("Datos de vulnerabilidad no disponibles.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ─── Sección 3: Formalidad, Costos y Retornos ───
    st.markdown("### Protección social e ingresos")
    c_f1, c_f2 = st.columns(2)
    
    with c_f1:
        st.subheader("Cobertura de salud y pensión")
        if 'formalidad' in datos_adv:
            df_form = datos_adv['formalidad'].sort_values("Afiliado_salud_%", ascending=False)
            if 'Cotiza_pension_%' in df_form.columns and 'Afiliado_salud_%' in df_form.columns:
                df_form_top = df_form.head(10).copy()
                df_form_top_melt = df_form_top.melt(id_vars=['Rama'], value_vars=['Afiliado_salud_%', 'Cotiza_pension_%'], var_name='Cobertura', value_name='Porcentaje')
                df_form_top_melt['Tipo'] = df_form_top_melt['Cobertura'].replace({'Afiliado_salud_%': 'Salud', 'Cotiza_pension_%': 'Pensión'})
                
                fig_f = px.bar(
                    df_form_top_melt, x='Porcentaje', y='Rama', color='Tipo',
                    orientation='h', barmode='group',
                    color_discrete_map={'Salud': '#14b8a6', 'Pensión': '#fbbf24'}
                )
                fig_f.update_traces(hovertemplate='<b>Sector: %{y}</b><br>Cobertura (%{data.name}): %{x:.1f}%<extra></extra>')
                apply_plotly_style(fig_f)
                st.plotly_chart(fig_f, width="stretch")
                
                with st.expander("Ver tabla de datos — Formalidad"):
                    st.dataframe(df_form, width="stretch", hide_index=True)
        else:
            st.info("Datos no disponibles.")

    with c_f2:
        st.subheader("Simulación de costo laboral ampliado")
        st.caption("Mediana salarial sectorial multiplicada por 1,54. Es un supuesto fijo, no un costo observado en la GEIH.")
        if 'costos' in datos_adv:
            df_costos = datos_adv['costos'].sort_values("Costo_SMMLV", ascending=True)
            if not df_costos.empty:
                fig_c = px.bar(
                    df_costos.tail(10), x="Costo_SMMLV", y="Rama", orientation='h',
                    color="Costo_SMMLV", color_continuous_scale="Cividis"
                )
                fig_c.update_traces(hovertemplate='<b>%{y}</b><br>Costo Promedio: %{x:.2f} SMMLVs<extra></extra>')
                apply_plotly_style(fig_c)
                st.plotly_chart(fig_c, width="stretch")

                with st.expander("Ver tabla de datos — Costos laborales"):
                    st.dataframe(df_costos.sort_values("Costo_SMMLV", ascending=False), width="stretch", hide_index=True)
        else:
            st.info("Datos no disponibles.")

    # ─── Ecuación de Mincer ───
    st.markdown("#### Ecuación de Mincer — Asociación entre educación e ingreso")
    st.warning("Modelo descriptivo WLS condicionado a ocupados con ingreso positivo. No identifica un efecto causal y no implementa corrección de Heckman.")
    if 'mincer' in datos_adv:
        m = datos_adv['mincer'].iloc[0]
        if pd.notna(m.get('beta_educacion')) and int(m.get('N', 0)) >= 100:
            col1, col2, col3 = st.columns(3)
            with col1: render_kpi("Coef. educación (aprox.)", f"{m['beta_educacion']:.1f}%")
            with col2: render_kpi("Coef. experiencia (aprox.)", f"{m['beta_exp']:.1f}%")
            with col3: render_kpi("Ajuste del modelo (R²)", f"{m['R2']:.3f}")
            st.caption(f"Estimación log-lineal sobre {int(m['N']):,} registros ocupados con ingreso positivo.")
        else:
            st.info("La muestra disponible no alcanza los 100 registros válidos exigidos para mostrar el modelo.")
    else:
        st.info("Análisis de Mincer no disponible.")

# ─── Pestaña: Diccionario y Metodología ───
with main_tab3:
    st.markdown("## Diccionario y lógica de cálculo")
    st.caption("Trazabilidad entre microdatos GEIH marco 2018, transformaciones analíticas, fórmulas y salidas del observatorio.")

    variables_doc = dataframe_variables()
    formulas_doc = dataframe_formulas()
    inner_tab1, inner_tab2, inner_tab3, inner_tab4 = st.tabs([
        "Variables", "Oficiales", "Analíticos", "Validación"
    ])

    with inner_tab1:
        st.markdown("### Catálogo de variables utilizadas")
        st.caption(f"{len(variables_doc)} variables directas o derivadas presentes en los motores activos.")
        modulos = sorted(variables_doc['Modulo'].unique())
        modulos_sel = st.multiselect("Módulos", modulos, default=modulos)
        tabla_variables = variables_doc[variables_doc['Modulo'].isin(modulos_sel)]
        st.dataframe(
            tabla_variables,
            column_config={
                'Modulo': st.column_config.TextColumn('Módulo', width='small'),
                'Codigo': st.column_config.TextColumn('Código GEIH', width='small'),
                'Definicion': st.column_config.TextColumn('Definición', width='large'),
                'Codificacion': st.column_config.TextColumn('Codificación / tratamiento', width='large'),
                'Universo': st.column_config.TextColumn('Universo', width='medium'),
                'Uso en el tablero': st.column_config.TextColumn('Uso', width='large'),
            },
            hide_index=True,
            width="stretch",
            height=520,
        )
        st.info(
            "Armonizaciones verificadas: FT* = OCI ∪ DSI cuando FT está vacío; "
            "PET faltante se completa únicamente con edad ≥ 15. FEX_ADJ es una variable analítica, no un campo original del DANE."
        )

    with inner_tab2:
        st.markdown("### Indicadores alineados con DANE/OIT")
        oficiales = formulas_doc[formulas_doc['Tipo'].isin(['Oficial DANE', 'OIT/DANE', 'OIT adaptado', 'OIT normativo'])]
        st.dataframe(oficiales, hide_index=True, width="stretch", height=455)
        st.latex(r"TD=\frac{DS}{FT^*}\times100\qquad TGP=\frac{FT^*}{PET^*}\times100\qquad TO=\frac{OC}{PET^*}\times100")
        st.latex(r"LU2=\frac{SIH+DS}{FT^*}\times100")
        st.latex(r"LU3=\frac{DS+FTP}{FT^*+FTP}\times100")
        st.latex(r"LU4=\frac{SIH+DS+FTP}{FT^*+FTP}\times100")
        st.warning(
            "La informalidad no se aproxima por pensión. Se aplica la secuencia EI del DANE marco 2018 con posición ocupacional, "
            "registro mercantil, contabilidad, tamaño, salud y pensión."
        )
        st.markdown("#### Secuencia de procesamiento")
        st.markdown("""
        El motor de cálculo (`src/02_motor_calculo.py`) ejecuta la siguiente secuencia:

        **1. Limpieza y Armonización**  
        Se unifican los archivos mensuales, se convierten tipos y se estandariza la rama CIIU Rev. 4. No se imputan ingresos faltantes.

        **2. Expansión Poblacional**  
        Se aplica `FEX_ADJ = FEX_C18 / n`, donde `n` es el número de meses consolidados (12 en años completos; 4 en el corte 2026 disponible).

        **3. Construcción de los últimos 12 meses**
        Desde diciembre de 2022 las cifras se consolidan en ventanas de 12 meses. Enero–noviembre de 2022 permanecen mensuales:
        """)
        st.latex(r"TD = \frac{\sum_{t-11}^{t} \text{Desocupados}_i}{\sum_{t-11}^{t} \text{FT}^{*}_i} \times 100")
        st.markdown("""
        **4. Estimación Econométrica (Mincer)**  
        Regresión descriptiva ponderada (WLS) entre ocupados con ingreso positivo. El coeficiente no identifica un efecto causal.
        """)
        st.latex(r"\ln(w_i) = \beta_0 + \beta_1 \text{Educ}_i + \beta_2 \text{Exp}_i + \beta_3 \text{Exp}_i^2 + \epsilon_i")
        st.markdown("""
        **5. Índices Compuestos (ICE / IVI)**  
        ICE, IVI e ICF son promedios ponderados de indicadores binarios o tasas. Son índices propios, no estadísticas oficiales DANE.

        **6. Coeficiente de Gini**  
        Calculado sobre la curva de Lorenz del ingreso laboral expandido:
        """)
        st.latex(r"G = 1 - \sum_{i=1}^{n} (X_i - X_{i-1})(Y_i + Y_{i-1})")

    with inner_tab3:
        st.markdown("### Indicadores analíticos propios")
        analiticos = formulas_doc[~formulas_doc['Tipo'].isin(['Oficial DANE', 'OIT/DANE', 'OIT adaptado', 'OIT normativo'])]
        st.dataframe(analiticos, hide_index=True, width="stretch", height=510)
        st.markdown("#### Glosario e interpretación")
        st.markdown("""
        | Término | Definición |
        |---|---|
        | **PET** | Población en Edad de Trabajar (15+ años). |
        | **FT analítica** | Unión de ocupados y desocupados; corrige vacíos de FT en algunos cortes. |
        | **FFT** | Personas en edad de trabajar que están fuera de la fuerza de trabajo. |
        | **Subocupación** | Ocupados con insuficiencia de horas o condiciones inadecuadas, con gestión y disponibilidad según la definición aplicada. |
        | **Informalidad** | Clasificación EI del DANE marco 2018; integra sector, registro, contabilidad y protección social. |
        | **Gini** | 0.0 = igualdad perfecta; 1.0 = desigualdad máxima. |
        | **ICE** | Índice de Calidad del Empleo (0–100). |
        | **IVI** | Índice analítico de Vulnerabilidad Laboral; no tiene umbral oficial DANE. |
        | **FEX_ADJ** | Variable analítica: FEX_C18 dividido por los meses consolidados. |
        | **Año móvil** | Cociente de sumas expandidas de 12 meses consecutivos; no promedio simple de tasas. |
        """)
        
        st.markdown("---")
        st.markdown("#### Clasificación operativa de precisión")
        st.latex(r"CV(\hat{p}) = \frac{SE(\hat{p})}{\hat{p}} \times 100")
        st.markdown("""
        | Nivel | Rango CV | Interpretación |
        |---|---|---|
        | **Alta** | CV ≤ 7% | Referencia operativa del tablero. |
        | **Aceptable** | 7% < CV ≤ 15% | Interpretar con cautela. |
        | **Baja** | 15% < CV ≤ 20% | Solo uso exploratorio. |
        | **No confiable** | CV > 20% | No usar para conclusiones. |
        """)
        st.warning(
            "Estos CV son aproximaciones bajo muestreo aleatorio simple con DEFF=2,5. "
            "No reproducen la varianza oficial del diseño complejo GEIH."
        )

    with inner_tab4:
        st.markdown("### Estado de la auditoría reproducible")
        auditoria = datos.get('auditoria_metodologia')
        if auditoria:
            a1, a2, a3 = st.columns(3)
            with a1: st.metric("Estado", auditoria.get('estado', 'Sin estado'))
            with a2: st.metric("Variables verificadas", auditoria.get('variables_documentadas', 0))
            with a3: st.metric("Indicadores trazados", auditoria.get('indicadores_documentados', 0))
            validacion = auditoria.get('validacion_dane_marzo_2025', {})
            calculado = validacion.get('calculado', {})
            referencia = validacion.get('referencia', {})
            if calculado and referencia:
                tabla_validacion = pd.DataFrame([
                    {'Indicador': k, 'Calculado (%)': calculado.get(k), 'DANE (%)': v,
                     'Diferencia (p.p.)': validacion.get('diferencia_pp', {}).get(k)}
                    for k, v in referencia.items()
                ])
                st.dataframe(
                    tabla_validacion,
                    column_config={
                        'Calculado (%)': st.column_config.NumberColumn('Calculado (%)', format='%.4f'),
                        'DANE (%)': st.column_config.NumberColumn('DANE (%)', format='%.4f'),
                        'Diferencia (p.p.)': st.column_config.NumberColumn('Diferencia (p.p.)', format='%.6f'),
                    },
                    hide_index=True,
                    width="stretch",
                )
            st.caption(auditoria.get('nota_precision', ''))
        else:
            st.warning("La evidencia de validación no está disponible en esta versión de los datos.")

        st.markdown("#### Reglas de lectura")
        st.markdown(
            "- Las tasas se reconstruyen con numeradores y denominadores expandidos; no se promedian porcentajes.\n"
            "- Ingresos, Gini y Mincer condicionan a ingreso laboral positivo observado.\n"
            "- Mincer es descriptivo; ICE, IVI e ICF son índices propios; el costo ampliado es una simulación.\n"
            "- Las ciudades pequeñas requieren errores oficiales del diseño antes de publicar inferencias."
        )

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.caption("Elaborado por Nicolás Álvarez, economista. Fuente: DANE, Gran Encuesta Integrada de Hogares.")
