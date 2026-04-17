DIAS_ORDEN = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ORDEN = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
TRADUCCION_MESES = dict(enumerate(MESES_ORDEN, start=1))

CAUSES_MAPPING = {
    "DLY_APT_ARR_W_1": "Clima",
    "DLY_APT_ARR_C_1": "ATC",
    "DLY_APT_ARR_G_1": "Infra",
    "DLY_APT_ARR_I_1": "Huelgas",
}

COLORS_MAPPING = {
    "Clima": "#0077b6",
    "ATC": "#fb8500",
    "Infra": "#2a9d8f",
    "Huelgas": "#e63946",
}
