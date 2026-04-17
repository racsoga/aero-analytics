import pandas as pd
import plotly.express as px
import streamlit as st
from src.config import DIAS_ORDEN, TRADUCCION_MESES

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
