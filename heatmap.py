import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
AEROPUERTO = 'LEMD' # Cambia al que estés usando
ARCHIVO = 'data/punctuality/apt_dly_2026.csv.bz2'

# ==========================================
# 2. EXTRACCIÓN Y LIMPIEZA
# ==========================================
df = pd.read_csv(ARCHIVO, usecols=['FLT_DATE', 'APT_ICAO', 'FLT_ARR_1', 'DLY_APT_ARR_1'], encoding='latin1')
df_apt = df[df['APT_ICAO'] == AEROPUERTO].copy()

# Calculamos el retraso total medio por vuelo
df_apt['RETRASO_MEDIO'] = df_apt['DLY_APT_ARR_1'] / df_apt['FLT_ARR_1']
df_apt = df_apt.fillna(0)

# ==========================================
# 3. INGENIERÍA DE CARACTERÍSTICAS (Fechas)
# ==========================================
# Convertimos a formato fecha para extraer el día y el mes
df_apt['FECHA'] = pd.to_datetime(df_apt['FLT_DATE'])
df_apt['NUM_MES'] = df_apt['FECHA'].dt.month
df_apt['NUM_DIA'] = df_apt['FECHA'].dt.dayofweek # 0=Lunes, 6=Domingo

# Diccionarios para traducir los números a texto
meses = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 
         7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
dias = {0: '1-Lunes', 1: '2-Martes', 2: '3-Miércoles', 3: '4-Jueves', 
        4: '5-Viernes', 5: '6-Sábado', 6: '7-Domingo'}

df_apt['MES'] = df_apt['NUM_MES'].map(meses)
df_apt['DIA'] = df_apt['NUM_DIA'].map(dias)

# ==========================================
# 4. CREACIÓN DE LA MATRIZ PARA EL HEATMAP
# ==========================================
# Pivotamos la tabla: Filas = Días, Columnas = Meses, Valores = Media de Retraso
matriz = df_apt.pivot_table(
    values='RETRASO_MEDIO', 
    index='DIA', 
    columns='NUM_MES', # Usamos el número para que se ordenen cronológicamente
    aggfunc='mean'
)

# Limpiamos los nombres para que se vean bien en el gráfico
matriz.columns = [meses[m] for m in matriz.columns]
matriz.index = [d.split('-')[1] for d in matriz.index] # Quitamos el número del día

# ==========================================
# 5. VISUALIZACIÓN ESTRATÉGICA
# ==========================================
plt.figure(figsize=(10, 6))

# Dibujamos el mapa de calor (YlOrRd = de Amarillo a Rojo intenso)
sns.heatmap(
    matriz, 
    annot=True,          # Escribe el número exacto en la celda
    fmt=".1f",           # Solo un decimal
    cmap='YlOrRd',       # Paleta de colores semáforo
    linewidths=1,        # Líneas de separación
    cbar_kws={'label': 'Minutos de retraso medio / vuelo'}
)

plt.title(f'Patrón Estructural de Retrasos - {AEROPUERTO}\n(Media de min/vuelo por día de la semana y mes)', 
          fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Mes del Año', fontsize=12)
plt.ylabel('Día de la Semana', fontsize=12)
plt.yticks(rotation=0)

plt.tight_layout()
plt.savefig(f'outputs/img/heatmap_{AEROPUERTO}.png')
plt.show()