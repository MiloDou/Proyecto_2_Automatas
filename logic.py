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
        parts = []
        for c in self.cosas:
            s = str(c)
            if isinstance(c, Or):
                s = f"({s})"
            parts.append(s)
        return "*".join(parts)

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
    # normaliza símbolos alternativos y quita espacios
    for k, v in simbolos.items():
        txt = txt.replace(k, v)
    txt = re.sub(r"\s+", "", txt)
    # inserta and implícito: letra/0/1/)' seguido de letra/(
    txt = re.sub(r"([A-Za-z0-9\)'])(?=[A-Za-z\(])", r"\1*", txt)
    return txt

# Errores
class ParseError(Exception):
    pass

def parsear(txt):
    txt = normalizar(txt)
    if txt == "":
        raise ParseError("Expresión vacía")

    def strip_outer_parens(s: str) -> str:
        # quita un par de paréntesis exteriores si están balanceados
        if not (s.startswith("(") and s.endswith(")")):
            return s
        count = 0
        for i, ch in enumerate(s):
            if ch == "(":
                count += 1
            elif ch == ")":
                count -= 1
            if count == 0 and i != len(s) - 1:
                return s  # hay algo fuera del par externo
        return s[1:-1]

    def parse_expr(s: str):
        s = s.strip()
        if s == "":
            raise ParseError("Expresión incompleta")
        s = strip_outer_parens(s)

        # 1) buscar + al nivel superior (derecha→izquierda)
        count = 0
        for i in range(len(s)-1, -1, -1):
            ch = s[i]
            if ch == ")":
                count += 1
            elif ch == "(":
                count -= 1
            elif count == 0 and ch == "+":
                left = s[:i]
                right = s[i+1:]
                return Or([parse_expr(left), parse_expr(right)])

        # 2) buscar * al nivel superior
        count = 0
        for i in range(len(s)-1, -1, -1):
            ch = s[i]
            if ch == ")":
                count += 1
            elif ch == "(":
                count -= 1
            elif count == 0 and ch == "*":
                left = s[:i]
                right = s[i+1:]
                return And([parse_expr(left), parse_expr(right)])

        # 3) NOT postfijo sobre el factor (una o más comillas)
        if s.endswith("'"):
            n = len(s) - len(s.rstrip("'"))
            core = s[:-n]
            if core == "":
                raise ParseError("Negación sin operando")
            node = parse_expr(core)
            for _ in range(n):
                node = Not(node)
            return node

        # 4) constantes
        if s == "0" or s == "1":
            return Const(s)

        # 5) variable de una letra
        if re.fullmatch(r"[A-Za-z]", s):
            return Var(s)

        # 6) caso de paréntesis internos o forma inválida
        if s.startswith("(") and s.endswith(")"):
            return parse_expr(strip_outer_parens(s))

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

def ley_absorcion(e):
    # x + x*y = x ; x*(x+y) = x
    if isinstance(e, Or):
        # busca un término que sea And y otro igual a uno de sus factores
        for t in e.cosas:
            for u in e.cosas:
                if t is u:
                    continue
                if isinstance(u, And):
                    if any(str(t) == str(f) for f in u.cosas):
                        nuevos = [x for x in e.cosas if x is not u]
                        return (t if len(nuevos) == 1 else Or(nuevos)), "Ley de Absorción"


    if isinstance(e, And):
        for t in e.cosas:
            for u in e.cosas:
                if t is u:
                    continue
                if isinstance(u, Or):
                    if any(str(t) == str(f) for f in u.cosas):
                        nuevos = [x for x in e.cosas if x is not u]
                        return (t if len(nuevos) == 1 else And(nuevos)), "Ley de Absorción"
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
    ley_doble_negacion,
    ley_idempotencia,
    ley_neutro,
    ley_anulador,
    ley_complemento,
    ley_absorcion,
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