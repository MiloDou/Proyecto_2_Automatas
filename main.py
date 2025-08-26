import customtkinter as ctk
from theme import COLORES, ESTILO_CONFIG
from UI_logic import UILogic

class BooleanSimplifierApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simplificador de Expresiones Booleanas")
        self.geometry("750x600")
        ctk.set_appearance_mode("light")
        self.configure(bg_color=COLORES["background"])

        # Título
        self.title_label = ctk.CTkLabel(self, text="Simplificador de Expresiones Booleanas", **ESTILO_CONFIG["CTkLabel_title"])
        self.title_label.pack(pady=(10, 5), fill="x")

        # Entrada
        self.input_frame = ctk.CTkFrame(self, **ESTILO_CONFIG["CTkFrame"])
        self.input_frame.pack(pady=10, padx=30, fill="x")
        self.input_label = ctk.CTkLabel(self.input_frame, text="Expresión:", **ESTILO_CONFIG["CTkLabel_body"])
        self.input_label.pack(side="left", padx=10)
        self.input_entry = ctk.CTkEntry(self.input_frame, width=800,height=90, **ESTILO_CONFIG["CTkEntry"])
        self.input_entry.pack(side="left", padx=10)
        self.input_entry.bind("<Return>", lambda e: self.simplify_step_by_step())

# ...existing code...

        # Teclado de botones para ingresar símbolos
        self.keyboard_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.keyboard_frame.pack(pady=5)
        symbols = [
            ['A', 'B', 'C', 'D', 'E', 'F'],
            ['+', '*', '!', '(', ')', '0', '1'],
            ['←', 'Limpiar']
        ]
        for row in symbols:
            row_frame = ctk.CTkFrame(self.keyboard_frame, fg_color="transparent")
            row_frame.pack(pady=2)
            for sym in row:
                # Selecciona el estilo según el tipo de botón
                if sym in ['A', 'B', 'C', 'D', 'E', 'F', '0', '1']:
                    estilo = ESTILO_CONFIG["CTkButton_num"]
                elif sym in ['+', '*', '!', '(', ')']:
                    estilo = ESTILO_CONFIG["CTkButton_op"]
                elif sym == 'Limpiar':
                    estilo = ESTILO_CONFIG["CTkButton_clear"]
                else:  # ←
                    estilo = ESTILO_CONFIG["CTkButton_mem"]
                btn = ctk.CTkButton(
                    row_frame, text=sym, width=55, height=42,
                    command=lambda s=sym: self.insert_symbol(s),
                    **estilo
                )
                btn.pack(side="left", padx=4)

        # Botones de acción
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10)
        self.btn_simplify = ctk.CTkButton(self.button_frame, text="Simplificar paso a paso", command=self.simplify_step_by_step, **ESTILO_CONFIG["CTkButton_op"])
        self.btn_simplify.pack(side="left", padx=15)
        self.btn_result = ctk.CTkButton(self.button_frame, text="Mostrar resultado final", command=self.show_final_result, **ESTILO_CONFIG["CTkButton_op"])
        self.btn_result.pack(side="left", padx=15)
        self.btn_exit = ctk.CTkButton(self.button_frame, text="Salir", command=self.quit, **ESTILO_CONFIG["CTkButton_clear"])
        self.btn_exit.pack(side="left", padx=15)



        # Área de resultados
        self.result_frame = ctk.CTkFrame(self, **ESTILO_CONFIG["CTkFrame"])
        self.result_frame.pack(pady=15, padx=30, fill="both", expand=True)
        self.result_text = ctk.CTkTextbox(self.result_frame, font=ESTILO_CONFIG["CTkLabel_body"]["font"], wrap="word", height=300)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.result_text.configure(state="disabled")

    def insert_symbol(self, symbol):
        if symbol == 'Limpiar':
            self.input_entry.delete(0, "end")
        elif symbol == '←':
            current = self.input_entry.get()
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, current[:-1])
        else:
            self.input_entry.insert("end", symbol)

    def simplify_step_by_step(self):
        expr = self.input_entry.get()
        expr = UILogic.normalizar(expr)
        valid, msg = UILogic.validar(expr)
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        if not valid:
            self.result_text.insert("end", f"Error: {msg}\n")
            self.result_text.configure(state="disabled")
            return
        pasos = UILogic.simplificar_pasos(expr)
        if not pasos:
            self.result_text.insert("end", "No se realizaron simplificaciones.\n")
        else:
            for antes, ley, despues, nota in pasos:
                self.result_text.insert("end", f"{antes}  --[{ley}]→  {despues}\n")
        self.result_text.configure(state="disabled")

    def show_final_result(self):
        expr = self.input_entry.get()
        expr = UILogic.normalizar(expr)
        valid, msg = UILogic.validar(expr)
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        if not valid:
            self.result_text.insert("end", f"Error: {msg}\n")
            self.result_text.configure(state="disabled")
            return
        final = UILogic.simplificar_final(expr)
        self.result_text.insert("end", f"Expresión simplificada: {final}\n")
        self.result_text.configure(state="disabled")

if __name__ == "__main__":
    app = BooleanSimplifierApp()
    app.mainloop()