"""
Tempo Pro - Aero Analytics Dashboard
Consolidated dashboard for analyzing Eurocontrol punctuality and traffic data.
"""

import pandas as pd
import streamlit as st

from src.data_loader import scan_infrastructure, load_consolidated_data
from src.views.operations import render_operations_tab
from src.views.resilience import render_resilience_tab
from src.views.heatmaps import render_heatmaps_tab
from src.views.historical import render_historical_tab

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
# 2. DASHBOARD PRINCIPAL Y ORQUESTACIÓN
# ==========================================
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