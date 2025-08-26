class const:
    def __init__(self, v):
        # v deberia ser 0 o 1 pero ahorita no valido
        self.v = v
    def __repr__(self):
        return str(self.v)

class var:
    def __init__(self, nombre):
        # deberia convertir a mayusculas
        self.nombre = nombre
    def __repr__(self):
        return self.nombre

class no:
    def __init__(self, x):
        self.x = x
    def __repr__(self):
        # falta parentesis en casos raros, lo dejo asi para mientras
        return f"{self.x}'"

class y:
    # and
    def __init__(self, cosas):
        self.cosas = tuple(cosas)  # deberia aplanar, luego veo
    def __repr__(self):
        # esto solo es una prueba
        return "*".join(str(c) for c in self.cosas)

class o:
    # or
    def __init__(self, cosas):
        self.cosas = tuple(cosas)
    def __repr__(self):
        return "+".join(str(c) for c in self.cosas)


# intento de normalizador
simbolos = {
    "∨": "+",
    "|": "+",
    "+": "+",
    "·": "*",
    "∙": "*",
    "∧": "*",
    "&": "*",
    "*": "*",
    "¬": "'",
    "~": "'",
    "!": "'",
}

def normalizar(txt):
    # pasar simbolos a los basicos
    for k, v in simbolos.items():
        txt = txt.replace(k, v)
    # quitar espacios (luego veo si rompo algo)
    txt = "".join(ch for ch in txt if ch != " ")
    return txt

# errores
class parse_error(Exception):
    pass

# parser medio inventado (falta jerarquia correcta)
# necesito que me ayudes a poder recibir las expresiones ya formateadas y asi elimino esto
def parsear(txt):
    t = normalizar(txt)
    if t == "":
        # tal vez deberia usar parse_error, despues
        raise Exception("expr vacia")
    # esto deberia construir ast de verdad pero no me dio tiempo, mejor espero a que ya tengas la ui
    # por ahora si hay un '+' asumo or de dos partes y ya
    if "+" in t:
        partes = t.split("+")
        # oaun no mira parentesis
        return o(partes)
    elif "*" in t:
        partes = t.split("*")
        return y(partes)
    elif t.endswith("'"):
        # negacion b
        return no(t[:-1])
    elif t in ("0", "1"):
        return const(int(t))
    else:
        return var(t)

# leyes
# idea: cada funcion recibe una expr y devuelve (expr_nueva, nombre_ley)
# ahora solo devuelven lo mismo para tener donde colgar luego
def ley_idempotencia(e):
    # x+x = x ; x*x = x
    return e, "ley idempotencia (borrador)"

def ley_identidad(e):
    # x+0=x ; x*1=x ; x+1=1 ; x*0=0
    return e, "ley identidad (borrador)"

def ley_complemento(e):
    # x + x' = 1 ; x * x' = 0
    # pendiente: detectar complementos de verdad
    return e, "ley complemento (borrador)"

def ley_absorcion(e):
    # x + x*y = x ; x*(x+y)=x
    return e, "ley absorcion (borrador)"

def ley_demorgan(e):
    # (x+y)' = x'*y' ; (x*y)' = x' + y'
    return e, "ley demorgan (borrador)"

boolean_laws = [
    ley_idempotencia,
    ley_identidad,
    ley_complemento,
    ley_absorcion,
    ley_demorgan,
]

# funcion de simplificar paso a paso (no hace nada real aun)
def simplificar_paso(e):
    # deberia caminar bottom-up pero no se bien todavia
    # por ahora solo intento aplicar una ley y me rindo jajajaj
    pasos = []
    for ley in boolean_laws:
        antes = representar(e)
        e2, nombre = ley(e)
        despues = representar(e2)
        if despues != antes:
            pasos.append((antes, nombre, despues, "nota: wip"))
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
    for _ in range(3):
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
    except:
        # plan b
        return f"{e}"