import pandas as pd

file_path = 'data/punctuality/apt_dly_2026.csv.bz2'

# Añadimos el encoding para que no se atragante con caracteres europeos
df = pd.read_csv(file_path, nrows=3, encoding='latin1')

# Imprimimos el resultado
print(df.to_csv(index=False))