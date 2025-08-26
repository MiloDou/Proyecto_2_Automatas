
COLORES = {
    # Fondo general de la app (carcasa/cuerpo)
    "background": "#F5F3EB",      # Beige suave
    "bezel": "#C1BFB6",           # Bisel metálico superior (opcional)
    # Pantalla (display)
    "display_bg": "#2A1E1A",      # Café oscuro casi negro
    "display_text": "#F08C3B",    # Naranja brillante
    # Botones
    "btn_clear_bg": "#E36B2C",    # Botón C (Clear)
    "btn_clear_text": "#FFFFFF",
    "btn_mem_bg": "#E87B32",      # Botones memoria (MC, M+, M-, MR)
    "btn_mem_text": "#FFFFFF",
    "btn_num_bg": "#555A5C",      # Botones numéricos (0-9) y punto
    "btn_num_text": "#FFFFFF",
    "btn_op_bg": "#3C3C3C",       # Botones de operación (+, -, ×, ÷, =)
    "btn_op_text": "#FFFFFF",
}

ESTILO_CONFIG = {
    # Pantalla principal (display)
    "CTkLabel_display": {
        "font": ("Consolas", 28, "bold"),
        "text_color": COLORES["display_text"],
        "bg_color": COLORES["display_bg"],
    },
    # Etiquetas generales
    "CTkLabel_title": {
        "font": ("Arial", 36, "bold"),
        "text_color": "#E36B2C",  # Naranja intenso para destacar el título
        "bg_color": "#F5F3EB",
    },
    "CTkLabel_body": {
        "font": ("Arial", 20, 'bold'),
        "text_color": "#3C3C3C",
    },
    # Entrada de texto
    "CTkEntry": {
        "font": ("Consolas", 28),
        "fg_color": COLORES["display_bg"],
        "text_color": COLORES["display_text"],
        "bg_color": COLORES["background"],
        "border_color": COLORES["bezel"],
        "border_width": 2,
    },
    # Botón C (Clear)
    "CTkButton_clear": {
        "font": ("Arial", 16, "bold"),
        "fg_color": COLORES["btn_clear_bg"],
        "text_color": COLORES["btn_clear_text"],
        "bg_color": COLORES["background"],
        "hover_color": "#F08C3B",
    },
    # Botones de memoria (MC, M+, M-, MR)
    "CTkButton_mem": {
        "font": ("Arial", 14, "bold"),
        "fg_color": COLORES["btn_mem_bg"],
        "text_color": COLORES["btn_mem_text"],
        "bg_color": COLORES["background"],
        "hover_color": "#F08C3B",
    },
    # Botones numéricos (0-9, .)
    "CTkButton_num": {
        "font": ("Arial", 16, "bold"),
        "fg_color": COLORES["btn_num_bg"],
        "text_color": COLORES["btn_num_text"],
        "bg_color": COLORES["background"],
        "hover_color": "#000000",
        
    },
    # Botones de operación (+, -, ×, ÷, =)
    "CTkButton_op": {
        "font": ("Arial", 16, "bold"),
        "fg_color": COLORES["btn_op_bg"],
        "text_color": COLORES["btn_op_text"],
        "bg_color": COLORES["background"],
        "hover_color": "#000000",
    },
    "CTkLabel_result": {
    "font": ("Consolas", 28, "bold"),
    "text_color": COLORES["display_text"],  # Naranja brillante
    "bg_color": COLORES["display_bg"],      # Café oscuro
    },

    # Marcos y frames
    "CTkFrame": {
        "fg_color": COLORES["bezel"],
        "bg_color": COLORES["background"],
    }
}