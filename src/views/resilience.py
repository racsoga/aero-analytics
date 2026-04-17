import pandas as pd
import plotly.express as px
import streamlit as st

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
