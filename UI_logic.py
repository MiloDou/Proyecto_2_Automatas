import logic

class UILogic:
    @staticmethod
    def normalizar(expr):
        return logic.normalizar(expr)

    @staticmethod
    def validar(expr):
        # Solo verifica que no esté vacía y que no tenga símbolos raros
        if not expr:
            return False, "Expresión vacía."
        try:
            logic.parsear(expr)
            return True, ""
        except Exception as e:
            return False, str(e)

    @staticmethod
    def simplificar_pasos(expr):
        final, pasos = logic.simplificar_expresion(expr)
        return pasos

    @staticmethod
    def simplificar_final(expr):
        final, pasos = logic.simplificar_expresion(expr)
        return final