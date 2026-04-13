# ✈️ Aero Analytics

Plataforma interactiva en desarrollo diseñada para analizar datos operativos de Eurocontrol, evaluar cuellos de botella y monetizar el impacto de los retrasos ATFM en la red aeroportuaria.

## Guidelines Generales

Para poner en marcha el proyecto en un entorno local, sigue estas directrices generales:

1. **Entorno de Desarrollo:**
   Se recomienda encarecidamente utilizar un entorno virtual (venv) de Python para aislar las dependencias del proyecto.

2. **Instalación de Dependencias:**
   El dashboard requiere la instalación de librerías de análisis de datos y visualización web (principalmente `pandas`, `streamlit` y `plotly`). Asegúrate de instalarlas a través de tu gestor de paquetes (`pip`):
   ```bash
   pip install pandas streamlit plotly
   ```

3. **Ejecución del Dashboard:**
   La interfaz gráfica no se ejecuta como un script tradicional de Python. Debes lanzarla utilizando el motor de Streamlit desde tu terminal:
   ```bash
   streamlit run app.py
   ```

4. **Gestión de Datos:**
   La herramienta se alimenta de datos masivos crudos (archivos `.csv.bz2` de puntualidad y `.csv` de tráfico). Estos archivos no se incluyen en el repositorio por su tamaño y deben ser descargados y almacenados localmente para que el motor de datos los procese en las carpetas `data/punctuality` y `data/traffic`.

## Aviso Legal / Disclaimer

Esta aplicación utiliza datos públicos proporcionados por Eurocontrol. Los cálculos económicos, métricas de resiliencia y análisis generados son estimaciones con fines analíticos y de investigación. Este proyecto no está afiliado, patrocinado ni respaldado oficialmente por Eurocontrol. Asegúrate de cumplir con los términos de uso de los datos originales de Eurocontrol si planeas utilizarlos con fines comerciales.