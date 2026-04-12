import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
AEROPUERTO = 'LEMD'
ARCHIVO = 'data/punctuality/apt_dly_2026.csv.bz2'

# ==========================================
# 2. EXTRACCIÓN Y LIMPIEZA
# ==========================================
columnas_clave = [
    'FLT_DATE', 'APT_ICAO', 'FLT_ARR_1', 
    'DLY_APT_ARR_1', 'DLY_APT_ARR_W_1', 
    'DLY_APT_ARR_C_1', 'DLY_APT_ARR_G_1', 'DLY_APT_ARR_I_1'
]

df = pd.read_csv(ARCHIVO, usecols=columnas_clave, encoding='latin1')
df_apt = df[df['APT_ICAO'] == AEROPUERTO].copy()
df_apt['FLT_DATE'] = pd.to_datetime(df_apt['FLT_DATE']).dt.date
df_apt = df_apt.sort_values('FLT_DATE')

# ==========================================
# 3. TRANSFORMACIÓN A KPIs
# ==========================================
df_apt['W (Clima)'] = df_apt['DLY_APT_ARR_W_1'] / df_apt['FLT_ARR_1']
df_apt['C (ATC/Espacio Aéreo)'] = df_apt['DLY_APT_ARR_C_1'] / df_apt['FLT_ARR_1']
df_apt['G (Capacidad Aeropuerto)'] = df_apt['DLY_APT_ARR_G_1'] / df_apt['FLT_ARR_1']
df_apt['I (Huelgas)'] = df_apt['DLY_APT_ARR_I_1'] / df_apt['FLT_ARR_1']
df_apt['RETRASO_TOTAL_MEDIO'] = df_apt['DLY_APT_ARR_1'] / df_apt['FLT_ARR_1']

df_apt = df_apt.fillna(0)

# --- NUEVO: EXTRACCIÓN DE INSIGHTS (TOP 5 PEORES DÍAS) ---
print(f"\n--- TOP 5 DÍAS MÁS CRÍTICOS EN {AEROPUERTO} ---")
peores_dias = df_apt.sort_values('RETRASO_TOTAL_MEDIO', ascending=False).head(5)

for index, fila in peores_dias.iterrows():
    fecha = fila['FLT_DATE']
    retraso = fila['RETRASO_TOTAL_MEDIO']
    
    # Buscamos cuál fue la causa principal ese día
    causas_dia = {
        'Clima': fila['W (Clima)'],
        'ATC': fila['C (ATC/Espacio Aéreo)'],
        'Infraestructura': fila['G (Capacidad Aeropuerto)'],
        'Huelgas': fila['I (Huelgas)']
    }
    causa_principal = max(causas_dia, key=causas_dia.get)
    
    print(f"📅 Fecha: {fecha} | ⏱️ Retraso Medio: {retraso:.1f} min/vuelo | 🚨 Causa Principal: {causa_principal}")
print("---------------------------------------------------\n")

df_apt.set_index('FLT_DATE', inplace=True)

# ==========================================
# 4. VISUALIZACIÓN AVANZADA
# ==========================================
sns.set_theme(style="whitegrid")
causas = ['W (Clima)', 'C (ATC/Espacio Aéreo)', 'G (Capacidad Aeropuerto)', 'I (Huelgas)']
colores = ['#4A90E2', '#F5A623', '#7ED321', '#D0021B']

# Creamos la figura
fig, ax = plt.subplots(figsize=(14, 6))

df_apt[causas].plot.area(
    stacked=True, color=colores, alpha=0.85, linewidth=0, ax=ax
)

plt.title(f'Disección de Retrasos ATFM por Causa - {AEROPUERTO} (Llegadas)', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Fecha de Operación', fontsize=12, labelpad=10)
plt.ylabel('Minutos de retraso medio por vuelo', fontsize=12, labelpad=10)

# --- NUEVO: LIMPIEZA DEL EJE X (FECHAS) ---
# Forzamos a que muestre solo el primer día de cada mes
ax.xaxis.set_major_locator(mdates.MonthLocator())
# Formateamos para que ponga "Ene 2026", "Feb 2026", etc.
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=0, ha='center') # Quitamos la rotación, ahora caben rectos

plt.legend(title='Causa Principal', loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()

nombre_imagen = f'diseccion_capacidad_{AEROPUERTO}.png'
plt.savefig(f'outputs/img/heatmap_{AEROPUERTO}.png')
plt.show()