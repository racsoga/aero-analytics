import os
import glob
from typing import Dict, Tuple
import pandas as pd
import streamlit as st

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
