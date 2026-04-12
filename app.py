"""
Tempo Pro - Aero Analytics Dashboard
Consolidated dashboard for analyzing Eurocontrol punctuality and traffic data.
"""

import os
import glob
from typing import Dict, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. CONFIGURACIÓN Y ESTÉTICA CORPORATIVA
# ==========================================
st.set_page_config(
    page_title="Tempo | Aero Analytics Pro",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-left: 5px solid #005c84;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-radius: 4px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: 600; }
    /* Enhance sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 2. CARGA DE DATOS MULTI-FUENTE
# ==========================================
@st.cache_data(show_spinner=False)
def scan_infrastructure() -> Tuple[Dict[str, str], Dict[str, str]]:
    """Scans the data directories to map available years to file paths."""
    punc_files = {
        os.path.basename(f).split("_")[-1].split(".")[0]: f
        for f in glob.glob("data/punctuality/apt_dly_*.csv.bz2")
    }
    traf_files = {
        os.path.basename(f).split("_")[-1].split(".")[0]: f
        for f in glob.glob("data/traffic/airport_traffic_*.csv")
    }
    return punc_files, traf_files


@st.cache_data(show_spinner=False)
def load_consolidated_data(year: str, punc_map: Dict[str, str]) -> pd.DataFrame:
    """Loads and preprocesses punctuality data for a specific year."""
    if year not in punc_map:
        st.error(f"Datos para el año {year} no encontrados.")
        return pd.DataFrame()

    try:
        df_p = pd.read_csv(punc_map[year], encoding="latin1")
        df_p["FLT_DATE"] = pd.to_datetime(df_p["FLT_DATE"])
        return df_p
    except Exception as e:
        st.error(f"Error al cargar los datos del año {year}: {str(e)}")
        return pd.DataFrame()


# ==========================================
# 3. LÓGICA DE NEGOCIO Y CONSTANTES
# ==========================================
DIAS_ORDEN = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ORDEN = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
TRADUCCION_MESES = dict(enumerate(MESES_ORDEN, start=1))

CAUSES_MAPPING = {
    "DLY_APT_ARR_W_1": "Clima",
    "DLY_APT_ARR_C_1": "ATC",
    "DLY_APT_ARR_G_1": "Infra",
    "DLY_APT_ARR_I_1": "Huelgas",
}

COLORS_MAPPING = {
    "Clima": "#0077b6",
    "ATC": "#fb8500",
    "Infra": "#2a9d8f",
    "Huelgas": "#e63946",
}


# ==========================================
# 4. DASHBOARD PRINCIPAL Y TABS
# ==========================================
def render_operations_tab(df_apt: pd.DataFrame, multiplier: int, unit_label: str):
    """Renders the Operations tab containing KPIs and area charts."""
    vuelos = df_apt["FLT_ARR_1"].sum()
    total_val = df_apt["DLY_APT_ARR_1"].sum() * multiplier

    c1, c2, c3 = st.columns(3)
    c1.metric("Volumen de Llegadas", f"{vuelos:,.0f}")
    c2.metric(f"Impacto Total ({unit_label})", f"{total_val:,.0f}")
    
    eficiencia = (total_val / vuelos) if vuelos > 0 else 0
    c3.metric("Eficiencia (media/vuelo)", f"{eficiencia:.2f} {unit_label}")

    # Prepare data for Area Chart
    df_plot = df_apt.copy()
    available_causes = [c for c in CAUSES_MAPPING.keys() if c in df_plot.columns]
    
    if not available_causes:
        st.info("No hay desglose de causas disponible para esta selección.")
        return

    plot_cols = []
    for col in available_causes:
        name = CAUSES_MAPPING[col]
        plot_cols.append(name)
        df_plot[name] = (df_plot[col] / df_plot["FLT_ARR_1"].replace(0, pd.NA)).fillna(0) * multiplier

    fig = px.area(
        df_plot,
        x="FLT_DATE",
        y=plot_cols,
        color_discrete_map=COLORS_MAPPING,
        labels={"value": f"Impacto ({unit_label})", "variable": "Causa"},
    )
    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1, title=""),
        margin=dict(t=0),
        xaxis_title="",
        yaxis_title=f"Impacto ({unit_label})",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_resilience_tab(df_apt: pd.DataFrame):
    """Renders the Resilience tab showing recovery after critical events."""
    st.subheader("Análisis de Resiliencia: El Día Después")
    st.markdown("Comparativa de recuperación tras eventos críticos (Días con >5 min/vuelo de retraso medio).")

    df_res = df_apt[df_apt["RETRASO_MEDIO"] > 5].copy()
    
    if df_res.empty:
        st.success("No se registraron eventos críticos (>5 min/vuelo) en este periodo.")
        return

    df_apt_dates = df_apt.set_index("FLT_DATE")
    res_list = []

    # Process up to 10 top events to avoid visual clutter
    for _, row in df_res.head(10).iterrows():
        current_date = row["FLT_DATE"]
        next_date = current_date + pd.Timedelta(days=1)
        
        next_val = 0.0
        if next_date in df_apt_dates.index:
            next_record = df_apt_dates.loc[next_date]
            if isinstance(next_record, pd.DataFrame):
                next_val = next_record["RETRASO_MEDIO"].mean()
            else:
                next_val = next_record["RETRASO_MEDIO"]

        res_list.append(
            {
                "Fecha Evento": current_date.strftime("%Y-%m-%d"),
                "Retraso Pico": row["RETRASO_MEDIO"],
                "Retraso Recuperación": next_val,
            }
        )

    df_res_plot = pd.DataFrame(res_list)
    fig_res = px.bar(
        df_res_plot,
        x="Fecha Evento",
        y=["Retraso Pico", "Retraso Recuperación"],
        barmode="group",
        labels={"value": "Minutos / Vuelo", "variable": "Métrica"},
        color_discrete_sequence=["#e63946", "#2a9d8f"],
    )
    fig_res.update_layout(
        legend=dict(orientation="h", y=1.1, title=""),
        xaxis_title="",
        yaxis_title="Retraso Medio (min)",
    )
    st.plotly_chart(fig_res, use_container_width=True)


def render_heatmaps_tab(df_apt: pd.DataFrame, unit_label: str):
    """Renders structural pattern heatmaps."""
    st.subheader("Patrones Estructurales")
    
    df_apt_hm = df_apt.copy()
    df_apt_hm["Mes_Num"] = df_apt_hm["FLT_DATE"].dt.month
    df_apt_hm["Día"] = df_apt_hm["FLT_DATE"].dt.dayofweek.map(dict(enumerate(DIAS_ORDEN)))

    if df_apt_hm.empty:
        st.info("No hay datos disponibles para el mapa de calor.")
        return

    pivot = df_apt_hm.pivot_table(
        index="Día", columns="Mes_Num", values="DLY_APT_ARR_1", aggfunc="mean"
    )
    
    pivot = pivot.reindex(DIAS_ORDEN)
    pivot.columns = [TRADUCCION_MESES.get(c, str(c)) for c in pivot.columns]

    fig_h = px.imshow(
        pivot,
        color_continuous_scale="YlOrRd",
        labels=dict(color=f"Retraso Total ({unit_label})", x="Mes", y="Día de la Semana"),
        aspect="auto"
    )
    fig_h.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig_h, use_container_width=True)


def render_historical_tab(sel_apt: str, punc_map: Dict[str, str]):
    """Renders the historical perspective tab."""
    st.subheader("Perspectiva Histórica (2014-2026)")
    
    # Use session state to persist the chart after the button is clicked
    if "hist_processed" not in st.session_state:
        st.session_state.hist_processed = False

    if st.button("🚀 Procesar Década Completa") or st.session_state.hist_processed:
        st.session_state.hist_processed = True
        
        with st.spinner("Analizando histórico..."):
            hist_data = []
            for y in sorted(punc_map.keys()):
                d = load_consolidated_data(y, punc_map)
                if d.empty:
                    continue
                d_apt = d[d["APT_ICAO"] == sel_apt]
                
                vuelos_sum = d_apt["FLT_ARR_1"].sum()
                minutos_sum = d_apt["DLY_APT_ARR_1"].sum()
                
                hist_data.append(
                    {
                        "Año": y,
                        "Vuelos": vuelos_sum,
                        "Minutos": minutos_sum,
                    }
                )

        if not hist_data:
            st.warning("No hay datos históricos disponibles.")
            return

        df_h = pd.DataFrame(hist_data)
        
        # Calculate efficiency safely
        df_h["Ratio Eficiencia"] = df_h["Minutos"] / df_h["Vuelos"].replace(0, pd.NA)
        df_h["Ratio Eficiencia"] = df_h["Ratio Eficiencia"].fillna(0)

        fig_hist = go.Figure()
        fig_hist.add_trace(
            go.Bar(
                x=df_h["Año"], 
                y=df_h["Vuelos"], 
                name="Volumen Vuelos", 
                marker_color="#adb5bd"
            )
        )
        fig_hist.add_trace(
            go.Scatter(
                x=df_h["Año"],
                y=df_h["Ratio Eficiencia"],
                name="Eficiencia (min/vuelo)",
                yaxis="y2",
                line=dict(color="#e63946", width=3),
                mode="lines+markers"
            )
        )
        
        fig_hist.update_layout(
            yaxis=dict(title="Volumen Vuelos"),
            yaxis2=dict(
                title="Eficiencia (min/vuelo)",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(orientation="h", y=1.1, title=""),
            margin=dict(t=0),
            hovermode="x unified"
        )
        st.plotly_chart(fig_hist, use_container_width=True)


def main():
    punc_map, _ = scan_infrastructure()

    if not punc_map:
        st.warning("⚠️ No se encontraron archivos de datos en 'data/punctuality/'.")
        return

    # --- SIDEBAR - CONTROL ESTRATÉGICO ---
    with st.sidebar:
        st.title("🚀 Tempo Pro")
        st.markdown("---")

        available_years = sorted(punc_map.keys(), reverse=True)
        sel_year = st.selectbox("📅 Año de Análisis", available_years)

        with st.spinner("Cargando datos..."):
            df_raw = load_consolidated_data(sel_year, punc_map)

        if df_raw.empty:
            st.stop()

        available_apts = sorted(df_raw["APT_ICAO"].unique())
        default_idx = available_apts.index("LEMD") if "LEMD" in available_apts else 0
        sel_apt = st.selectbox("📍 Aeropuerto ICAO", available_apts, index=default_idx)

        st.markdown("---")
        st.subheader("💰 Parámetros Económicos")
        view_mode = st.radio("Unidad de Medida", ["Minutos ATFM", "Impacto Económico (€)"])
        cost_per_min = st.slider("Coste/minuto (€)", 50, 200, 100)

    # --- PROCESAMIENTO DE DATOS ---
    df_apt = df_raw[df_raw["APT_ICAO"] == sel_apt].copy().sort_values("FLT_DATE")

    # Safe division para evitar división por 0 o Infs
    df_apt["RETRASO_MEDIO"] = df_apt["DLY_APT_ARR_1"] / df_apt["FLT_ARR_1"].replace(0, pd.NA)
    df_apt["RETRASO_MEDIO"] = df_apt["RETRASO_MEDIO"].fillna(0)

    multiplier = cost_per_min if view_mode == "Impacto Económico (€)" else 1
    unit_label = "€" if view_mode == "Impacto Económico (€)" else "min"

    # --- RENDERIZADO PRINCIPAL ---
    st.header(f"Performance Report: {sel_apt} | Ciclo {sel_year}")

    t1, t2, t3, t4 = st.tabs(["📊 Operaciones", "📉 Resiliencia", "🌡️ Heatmaps", "📜 Histórico"])

    with t1:
        render_operations_tab(df_apt, multiplier, unit_label)

    with t2:
        render_resilience_tab(df_apt)

    with t3:
        render_heatmaps_tab(df_apt, unit_label)

    with t4:
        render_historical_tab(sel_apt, punc_map)


if __name__ == "__main__":
    main()
