import re

# Clases para el AST
class Const:
    def __init__(self, v):
        self.v = int(v)
    def __repr__(self):
        return str(self.v)

class Var:
    def __init__(self, nombre):
        self.nombre = nombre.upper()
    def __repr__(self):
        return self.nombre

class Not:
    def __init__(self, x):
        self.x = x
    def __repr__(self):
        # Paréntesis solo si es necesario
        if isinstance(self.x, (And, Or)):
            return f"({self.x})'"
        return f"{self.x}'"

class And:
    def __init__(self, cosas):
        self.cosas = tuple(cosas)
    def __repr__(self):
        return "*".join(str(c) for c in self.cosas)

class Or:
    def __init__(self, cosas):
        self.cosas = tuple(cosas)
    def __repr__(self):
        return "+".join(str(c) for c in self.cosas)

# Normalizador de símbolos
simbolos = {
    "∨": "+", "|": "+", "+": "+",
    "·": "*", "∙": "*", "∧": "*", "&": "*", "*": "*",
    "¬": "'", "~": "'", "!": "'",
}

def normalizar(txt):
    for k, v in simbolos.items():
        txt = txt.replace(k, v)
    txt = "".join(ch for ch in txt if ch != " ")
    return txt

# Errores
class ParseError(Exception):
    pass

# Parser simple (mejorado para soportar paréntesis y negaciones)
def parsear(txt):
    txt = normalizar(txt)
    if txt == "":
        raise ParseError("Expresión vacía")
    # Recursivo para paréntesis
    def parse_expr(s):
        s = s.strip()
        # Constantes
        if s == "0" or s == "1":
            return Const(s)
        # Negación
        if s.endswith("'"):
            return Not(parse_expr(s[:-1]))
        # Paréntesis
        if s.startswith("(") and s.endswith(")"):
            # Quita paréntesis externos si están balanceados
            count = 0
            for i, c in enumerate(s):
                if c == "(": count += 1
                if c == ")": count -= 1
                if count == 0 and i != len(s)-1:
                    break
            else:
                return parse_expr(s[1:-1])
        # Operadores
        # Primero OR, luego AND
        count = 0
        for i in range(len(s)-1, -1, -1):
            if s[i] == ")": count += 1
            if s[i] == "(": count -= 1
            if count == 0 and s[i] == "+":
                return Or([parse_expr(s[:i]), parse_expr(s[i+1:])])
        count = 0
        for i in range(len(s)-1, -1, -1):
            if s[i] == ")": count += 1
            if s[i] == "(": count -= 1
            if count == 0 and s[i] == "*":
                return And([parse_expr(s[:i]), parse_expr(s[i+1:])])
        # Variable
        if re.fullmatch(r"[A-Za-z]", s):
            return Var(s)
        raise ParseError(f"Expresión inválida: {s}")
    return parse_expr(txt)

# Leyes booleanas (solo ejemplos, puedes expandir)
def ley_idempotencia(e):
    # x + x = x ; x * x = x
    if isinstance(e, Or):
        if len(e.cosas) == 2 and str(e.cosas[0]) == str(e.cosas[1]):
            return e.cosas[0], "Ley de Idempotencia"
    if isinstance(e, And):
        if len(e.cosas) == 2 and str(e.cosas[0]) == str(e.cosas[1]):
            return e.cosas[0], "Ley de Idempotencia"
    return e, ""

def ley_neutro(e):
    # x + 0 = x ; x * 1 = x
    if isinstance(e, Or):
        for c in e.cosas:
            if isinstance(c, Const) and c.v == 0:
                otros = [x for x in e.cosas if not (isinstance(x, Const) and x.v == 0)]
                if len(otros) == 1:
                    return otros[0], "Ley del Neutro"
    if isinstance(e, And):
        for c in e.cosas:
            if isinstance(c, Const) and c.v == 1:
                otros = [x for x in e.cosas if not (isinstance(x, Const) and x.v == 1)]
                if len(otros) == 1:
                    return otros[0], "Ley del Neutro"
    return e, ""

def ley_anulador(e):
    # x + 1 = 1 ; x * 0 = 0
    if isinstance(e, Or):
        for c in e.cosas:
            if isinstance(c, Const) and c.v == 1:
                return Const(1), "Ley del Anulador"
    if isinstance(e, And):
        for c in e.cosas:
            if isinstance(c, Const) and c.v == 0:
                return Const(0), "Ley del Anulador"
    return e, ""

def ley_complemento(e):
    # x + x' = 1 ; x * x' = 0
    if isinstance(e, Or):
        if len(e.cosas) == 2:
            a, b = e.cosas
            if (isinstance(a, Not) and str(a.x) == str(b)) or (isinstance(b, Not) and str(b.x) == str(a)):
                return Const(1), "Ley del Complemento"
    if isinstance(e, And):
        if len(e.cosas) == 2:
            a, b = e.cosas
            if (isinstance(a, Not) and str(a.x) == str(b)) or (isinstance(b, Not) and str(b.x) == str(a)):
                return Const(0), "Ley del Complemento"
    return e, ""

def ley_doble_negacion(e):
    # !!x = x
    if isinstance(e, Not) and isinstance(e.x, Not):
        return e.x.x, "Ley de Doble Negación"
    return e, ""


boolean_laws = [
    ley_idempotencia,
    ley_neutro,
    ley_anulador,
    ley_complemento,
    ley_doble_negacion,
]

# Simplificación paso a paso
def simplificar_paso(e):
    pasos = []
    for ley in boolean_laws:
        antes = representar(e)
        e2, nombre = ley(e)
        despues = representar(e2)
        if nombre and despues != antes:
            pasos.append((antes, nombre, despues, ""))
            e = e2
            break
    return e, pasos

def simplificar_expresion(texto):
    try:
        expr = parsear(texto)
    except Exception as err:
        return "error", [("entrada", "error parseo", str(err), "")]
    todos = []
    actual = expr
    for _ in range(10):  # Hasta 10 pasos para evitar bucles infinitos
        nuevo, pasos = simplificar_paso(actual)
        todos.extend(pasos)
        if representar(nuevo) == representar(actual):
            break
        actual = nuevo
    final = representar(actual)
    return final, todos

def representar(e):
    if isinstance(e, str):
        return e
    try:
        return str(e)
    except Exception:
        return f"{e}"