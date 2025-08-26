import customtkinter as ctk
from theme import COLORES, ESTILO_CONFIG
import re

# Leyes implementadas (nombre, función de aplicación)
BOOLEAN_LAWS = [
    ("Ley de Idempotencia", lambda e: re.sub(r'(\b\w+\b)\s*\+\s*\1', r'\1', e)),
    ("Ley de Idempotencia", lambda e: re.sub(r'(\b\w+\b)\s*\*\s*\1', r'\1', e)),
    ("Ley del Complemento", lambda e: re.sub(r'(\b\w+\b)\s*\+\s*!\1', '1', e)),
    ("Ley del Complemento", lambda e: re.sub(r'(\b\w+\b)\s*\*\s*!\1', '0', e)),
    ("Ley del Neutro", lambda e: re.sub(r'(\b\w+\b)\s*\+\s*0', r'\1', e)),
    ("Ley del Neutro", lambda e: re.sub(r'(\b\w+\b)\s*\*\s*1', r'\1', e)),
    ("Ley del Anulador", lambda e: re.sub(r'(\b\w+\b)\s*\*\s*0', '0', e)),
    ("Ley del Dominio", lambda e: re.sub(r'(\b\w+\b)\s*\+\s*1', '1', e)),
    ("Ley de Doble Negación", lambda e: re.sub(r'!!(\b\w+\b)', r'\1', e)),
]

# Normalización de símbolos
def normalize(expr):
    expr = expr.replace(' ', '')
    expr = expr.replace('·', '*').replace('∧', '*').replace('^', '*')
    expr = expr.replace('+', '+').replace('∨', '+')
    expr = expr.replace('¬', '!').replace('~', '!')
    expr = expr.replace('(', '(').replace(')', ')')
    return expr

# Validación sintáctica básica
def validate(expr):
    if not expr:
        return False, "Expresión vacía."
    if not re.fullmatch(r'[A-Za-z01!+*()]+', expr):
        return False, "Símbolos inválidos."
    stack = []
    for c in expr:
        if c == '(':
            stack.append(c)
        elif c == ')':
            if not stack:
                return False, "Paréntesis desbalanceados."
            stack.pop()
    if stack:
        return False, "Paréntesis desbalanceados."
    return True, ""

# Simplificación paso a paso
def simplify(expr):
    pasos = []
    expr = normalize(expr)
    expr = expr.upper()
    cambios = True
    while cambios:
        cambios = False
        for nombre, ley in BOOLEAN_LAWS:
            nuevo = ley(expr)
            if nuevo != expr:
                pasos.append((expr, nombre, nuevo))
                expr = nuevo
                cambios = True
                break
    return pasos, expr

class BooleanSimplifierApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simplificador de Expresiones Booleanas")
        self.geometry("700x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(bg_color=COLORES["background"])

        # Título
        self.title_label = ctk.CTkLabel(self, text="Simplificador de Expresiones Booleanas", **ESTILO_CONFIG["CTkLabel_title"])
        self.title_label.pack(pady=10, fill="x")

        # Entrada
        self.input_frame = ctk.CTkFrame(self, **ESTILO_CONFIG["CTkFrame"])
        self.input_frame.pack(pady=10, padx=20, fill="x")
        self.input_label = ctk.CTkLabel(self.input_frame, text="Expresión:", **ESTILO_CONFIG["CTkLabel_body"])
        self.input_label.pack(side="left", padx=10)
        self.input_entry = ctk.CTkEntry(self.input_frame, width=350, **ESTILO_CONFIG["CTkEntry"])
        self.input_entry.pack(side="left", padx=10)
        self.input_entry.bind("<Return>", lambda e: self.simplify_step_by_step())

        # Botones
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=5)
        self.btn_simplify = ctk.CTkButton(self.button_frame, text="Simplificar paso a paso", command=self.simplify_step_by_step, **ESTILO_CONFIG["CTkButton"])
        self.btn_simplify.pack(side="left", padx=10)
        self.btn_result = ctk.CTkButton(self.button_frame, text="Mostrar resultado final", command=self.show_final_result, **ESTILO_CONFIG["CTkButton"])
        self.btn_result.pack(side="left", padx=10)
        self.btn_exit = ctk.CTkButton(self.button_frame, text="Salir", command=self.quit, **ESTILO_CONFIG["CTkButton"])
        self.btn_exit.pack(side="left", padx=10)

        # Área de resultados
        self.result_frame = ctk.CTkFrame(self, **ESTILO_CONFIG["CTkFrame"])
        self.result_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.result_text = ctk.CTkTextbox(self.result_frame, font=ESTILO_CONFIG["CTkLabel_body"]["font"], wrap="word", height=250)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.result_text.configure(state="disabled")

    def simplify_step_by_step(self):
        expr = self.input_entry.get()
        expr = normalize(expr)
        valid, msg = validate(expr)
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        if not valid:
            self.result_text.insert("end", f"Error: {msg}\n")
            self.result_text.configure(state="disabled")
            return
        pasos, _ = simplify(expr)
        if not pasos:
            self.result_text.insert("end", "No se realizaron simplificaciones.\n")
        else:
            for antes, ley, despues in pasos:
                self.result_text.insert("end", f"{antes}  --[{ley}]→  {despues}\n")
        self.result_text.configure(state="disabled")

    def show_final_result(self):
        expr = self.input_entry.get()
        expr = normalize(expr)
        valid, msg = validate(expr)
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        if not valid:
            self.result_text.insert("end", f"Error: {msg}\n")
            self.result_text.configure(state="disabled")
            return
        pasos, final = simplify(expr)
        if pasos:
            self.result_text.insert("end", f"Expresión simplificada: {final}\n")
        else:
            self.result_text.insert("end", f"Expresión ya simplificada: {final}\n")
        self.result_text.configure(state="disabled")
