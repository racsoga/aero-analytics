from typing import Dict
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.data_loader import load_consolidated_data

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
