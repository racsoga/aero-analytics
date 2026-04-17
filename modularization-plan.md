# Plan de Arquitectura Modular: Eurocontrol Analyzer Pro

## 1. Objetivo y Motivación
Dado que el proyecto crecerá para explotar en profundidad la gran cantidad de datos disponibles de Eurocontrol (retrasos de aerolíneas, rutas, tráfico en espacio aéreo, etc.), mantener todo el código en un único archivo `app.py` se volverá insostenible. El objetivo de este plan es refactorizar la aplicación actual en una arquitectura modular de componentes. 

## 2. Nueva Estructura de Directorios

Se propone crear la siguiente jerarquía bajo un nuevo directorio `src/` (Source):

```text
eurocontrol_analyzer/
├── data/
├── scripts/
├── src/
│   ├── __init__.py
│   ├── config.py         # Constantes, configuraciones estéticas y mapeos de datos (meses, causas)
│   ├── data_loader.py    # Funciones pesadas con @st.cache_data para escanear y cargar CSVs
│   └── views/            # Módulos independientes por cada pestaña del dashboard
│       ├── __init__.py
│       ├── operations.py
│       ├── resilience.py
│       ├── heatmaps.py
│       └── historical.py
├── app.py                # Punto de entrada (main). Solo orquesta y llama a los módulos.
└── requirements.txt
```

## 3. Pasos de Implementación

### Fase 1: Creación del Core (`src/`)
1. **`src/config.py`**: Migrar las constantes de `app.py` (`DIAS_ORDEN`, `MESES_ORDEN`, `TRADUCCION_MESES`, `CAUSES_MAPPING`, `COLORS_MAPPING`).
2. **`src/data_loader.py`**: Migrar las funciones `scan_infrastructure()` y `load_consolidated_data()`. Mantener el uso intensivo de `st.cache_data`.

### Fase 2: Modularización de Vistas (`src/views/`)
1. **`operations.py`**: Migrar la función `render_operations_tab()`.
2. **`resilience.py`**: Migrar la función `render_resilience_tab()`.
3. **`heatmaps.py`**: Migrar la función `render_heatmaps_tab()`.
4. **`historical.py`**: Migrar la función `render_historical_tab()`.

### Fase 3: Refactorización del Main (`app.py`)
1. Limpiar `app.py` eliminando todo el código migrado.
2. Importar los módulos desde `src`.
3. Mantener exclusivamente la configuración de la página (`st.set_page_config`), la lógica del **Sidebar** y el orquestador principal (`st.tabs` llamando a las funciones de las vistas).

## 4. Beneficios de esta Arquitectura
- **Escalabilidad:** Añadir una nueva pestaña de datos de tráfico o rendimiento en ruta (En-route) será tan fácil como crear un archivo nuevo en `views/` y añadir una línea en `app.py`.
- **Trabajo en equipo:** Facilita el desarrollo simultáneo sin conflictos en GitHub.
- **Rendimiento:** Permite separar claramente la lógica pesada de datos (`data_loader.py`) de la interfaz de usuario.
- **Mantenimiento:** Facilita la localización de errores.

## 5. Verificación
- Ejecutar `streamlit run app.py` y confirmar que la aplicación arranca sin errores y las cuatro pestañas originales mantienen la misma funcionalidad visual e interactiva.