#Colores utilizados en cada una de las partes de la aplicación
#Se utiliza para seguir con las buenas prácticas de diseño y mantener una paleta de colores 

COLORES = {
    "background": "#2c3e50",       # Fondo principal (Azul oscuro)
    "background_light": "#34495e", # Fondo de títulos (Azul más claro)
    "surface": "#ffffff",          # Superficies de paneles (Blanco)
    "primary_text": "#2c3e50",      # Texto principal sobre fondos claros
    "secondary_text": "#7f8c8d",    # Texto secundario o de ayuda
    "on_primary": "#ffffff",       # Texto sobre elementos de color
    "accent": "#3498db",           # Color de acento (ej. variables)
    "success": "#27ae60",          # Verde para éxito/validación
    "warning": "#f39c12",          # Naranja para advertencias
    "error": "#e74c3c",            # Rojo para errores
    "disabled": "#95a5a6",         # Color para elementos deshabilitados
    "border": "#bdc3c7",           # Color de bordes sutiles
    "table_header": "#34495e",     # Cabecera de la tabla
    "table_row_light": "#f8f9fa",   # Fila par de la tabla
    "table_row_dark": "#e9ecef",    # Fila impar de la tabla
}

# Fuentes
FUENTES = {
    "title": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 11),
    "button": ("Segoe UI", 11, "bold"),
    "component": ("Segoe UI", 12, "bold"),
    "table_header": ("Segoe UI", 12, "bold"),
    "table_body": ("Segoe UI", 11, "bold"),
}

#Configuración de Estilos 
ESTILO_CONFIG = {
    "button": {
        "fg": COLORES["on_primary"],
        "font": FUENTES["button"],
        "relief": "raised",
        "bd": 2,
        "cursor": "hand2",
        "pady": 8,
        "padx": 15,
    },
    "title_label": {
        "bg": COLORES["background_light"],
        "fg": COLORES["on_primary"],
        "font": FUENTES["title"],
        "pady": 15,
    },
}