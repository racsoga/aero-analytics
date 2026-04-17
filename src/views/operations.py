import pandas as pd
import plotly.express as px
import streamlit as st
from src.config import CAUSES_MAPPING, COLORS_MAPPING

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
