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
        partes = []
        for c in self.cosas:
            s = str(c)
            if isinstance(c, Or):
                s = f"({s})"
            partes.append(s)
        return "*".join(partes)

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
    txt = re.sub(r"\s+", "", txt)
    txt = re.sub(r"([A-Za-z0-9)'])(?=[A-Za-z(])", r"\1*", txt)
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
    if isinstance(e, Or):
        vistos, nuevos = set(), []
        for t in e.cosas:
            k = repr(t)
            if k not in vistos:
                vistos.add(k)
                nuevos.append(t)
        if len(nuevos) != len(e.cosas):
            return (nuevos[0] if len(nuevos) == 1 else Or(tuple(nuevos))), "Ley de Idempotencia (+ n-aria)"
        return e, ""
    if isinstance(e, And):
        vistos, nuevos = set(), []
        for t in e.cosas:
            k = repr(t)
            if k not in vistos:
                vistos.add(k)
                nuevos.append(t)
        if len(nuevos) != len(e.cosas):
            return (nuevos[0] if len(nuevos) == 1 else And(tuple(nuevos))), "Ley de Idempotencia (* n-aria)"
        return e, ""
    return e, ""

def ley_asociativa(e):
    if isinstance(e, Or):
        planos = []
        for t in e.cosas:
            if isinstance(t, Or):
                planos.extend(t.cosas)
            else:
                planos.append(t)
        if len(planos) != len(e.cosas):
            return Or(tuple(planos)), "Ley Asociativa (+ aplanado)"
        return e, ""
    if isinstance(e, And):
        planos = []
        for t in e.cosas:
            if isinstance(t, And):
                planos.extend(t.cosas)
            else:
                planos.append(t)
        if len(planos) != len(e.cosas):
            return And(tuple(planos)), "Ley Asociativa (* aplanado)"
        return e, ""
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
    if isinstance(e, Or):
        t = list(e.cosas)
        for a in t:
            for b in t:
                if a is b:
                    continue
                if isinstance(b, And):
                    if any(str(a) == str(f) for f in b.cosas):
                        nuevos = [x for x in t if x is not b]
                        return (a if len(nuevos) == 1 else Or(nuevos)), "Ley de Absorción"
    if isinstance(e, And):
        t = list(e.cosas)
        for a in t:
            for b in t:
                if a is b:
                    continue
                if isinstance(b, Or):
                    if any(str(a) == str(f) for f in b.cosas):
                        nuevos = [x for x in t if x is not b]
                        return (a if len(nuevos) == 1 else And(nuevos)), "Ley de Absorción"
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

def ley_demorgan(e):
    if isinstance(e, Not) and isinstance(e.x, Or):
        return And(tuple(Not(t) for t in e.x.cosas)), "Ley de De Morgan"
    if isinstance(e, Not) and isinstance(e.x, And):
        return Or(tuple(Not(t) for t in e.x.cosas)), "Ley de De Morgan"
    return e, ""

def ley_distributiva_factor(e):
    if isinstance(e, Or):
        terms = list(e.cosas)
        ands = [t for t in terms if isinstance(t, And)]
        for i in range(len(ands)):
            for j in range(i+1, len(ands)):
                a = ands[i].cosas
                b = ands[j].cosas
                comunes = [x for x in a if any(str(x)==str(y) for y in b)]
                if comunes:
                    resto_a = [x for x in a if all(str(x)!=str(c) for c in comunes)]
                    resto_b = [x for x in b if all(str(x)!=str(c) for c in comunes)]
                    if not resto_a: resto_a = []
                    if not resto_b: resto_b = []
                    or_interno = Or(tuple({str(x):x for x in resto_a+resto_b}.values())) if (resto_a or resto_b) else None
                    nuevo = And(tuple(comunes) + ((or_interno,) if or_interno else tuple()))
                    nuevos = [x for x in terms if x not in (ands[i], ands[j])] + [nuevo]
                    return Or(tuple(nuevos)), "Ley Distributiva (factor común)"
    return e, ""

def ley_producto_suma_comun(e):
    if isinstance(e, And):
        ors = [t for t in e.cosas if isinstance(t, Or) and len(t.cosas) == 2]
        otros = [t for t in e.cosas if not isinstance(t, Or)]
        for i in range(len(ors)):
            for j in range(i + 1, len(ors)):
                a1, a2 = ors[i].cosas
                b1, b2 = ors[j].cosas
                pares = [
                    (a1, a2, b1, b2),
                    (a1, a2, b2, b1),
                    (a2, a1, b1, b2),
                    (a2, a1, b2, b1),
                ]
                for c, x, d, y_ in pares:
                    comp = (
                        (isinstance(x, Not) and repr(x.x) == repr(y_))
                        or (isinstance(y_, Not) and repr(y_.x) == repr(x))
                    )
                    if repr(c) == repr(d) and comp:
                        nuevos = otros + [c]
                        if len(nuevos) == 1:
                            return nuevos[0], "Ley de producto de sumas con común y complemento"
                        return And(nuevos), "Ley de producto de sumas con común y complemento"
    return e, ""

def ley_distributiva_comun_and(e):
    # reduce (x*y...) + (x*z...) cuando y y z son complementarios y x... es el factor común
    def reducir_or(or_node):
        # solo manejamos el caso de dos sumandos, ambos productos
        if not (isinstance(or_node, Or) and len(or_node.cosas) == 2):
            return None
        t1, t2 = or_node.cosas
        if not (isinstance(t1, And) and isinstance(t2, And)):
            return None

        a = list(t1.cosas)
        b = list(t2.cosas)

        # factores comunes por representación
        comunes = [x for x in a if any(str(x) == str(y) for y in b)]
        resto_a = [x for x in a if all(str(x) != str(c) for c in comunes)]
        resto_b = [x for x in b if all(str(x) != str(c) for c in comunes)]

        # necesitamos que quede exactamente 1 factor residual en cada lado
        if len(resto_a) != 1 or len(resto_b) != 1:
            return None

        ra, rb = resto_a[0], resto_b[0]
        son_complementarios = (
            (isinstance(ra, Not) and str(ra.x) == str(rb)) or
            (isinstance(rb, Not) and str(rb.x) == str(ra))
        )
        if not son_complementarios:
            return None

        # se reduce a solo el producto de los comunes
        if len(comunes) == 0:
            return Const(1)  # (a' + a) caso puro, no es el que nos interesa aquí
        if len(comunes) == 1:
            return comunes[0]
        return And(tuple(comunes))

    # caso 1: la expresión es el OR a reducir
    if isinstance(e, Or):
        nuevo = reducir_or(e)
        if nuevo is not None:
            return nuevo, "Ley distributiva con complemento"

    # caso 2: la expresión es un AND que contiene un OR reducible
    if isinstance(e, And):
        partes = list(e.cosas)
        for i, ch in enumerate(partes):
            if isinstance(ch, Or):
                reducido = reducir_or(ch)
                if reducido is not None:
                    partes[i] = reducido
                    # si el AND queda de 1 término, colapsa
                    return (partes[0] if len(partes) == 1 else And(tuple(partes))), "Ley distributiva con complemento (subexpresión)"
    return e, ""

def ley_complemento_ext(e):
    # or raíz: si hay un par complementario -> 1
    if isinstance(e, Or):
        terms = list(e.cosas)
        for i in range(len(terms)):
            for j in range(i+1, len(terms)):
                a, b = terms[i], terms[j]
                if (isinstance(a, Not) and repr(a.x) == repr(b)) or (isinstance(b, Not) and repr(b.x) == repr(a)):
                    return Const(1), "Ley del Complemento (extendida)"

        # or como hijo dentro de and: si algún hijo or tiene complemento interno, colapsa ese hijo a 1
        # y deja que la ley de identidad/anulador se encargue de limpiar el and
        return e, ""

    # and raíz: si hay un par complementario -> 0
    if isinstance(e, And):
        terms = list(e.cosas)
        for i in range(len(terms)):
            for j in range(i+1, len(terms)):
                a, b = terms[i], terms[j]
                if (isinstance(a, Not) and repr(a.x) == repr(b)) or (isinstance(b, Not) and repr(b.x) == repr(a)):
                    return Const(0), "Ley del Complemento (extendida)"

        # and que contiene un or con complemento interno: reduce ese or a 1
        nuevos = []
        changed = False
        for t in terms:
            if isinstance(t, Or):
                hijos = list(t.cosas)
                hay_comp = False
                for i in range(len(hijos)):
                    for j in range(i+1, len(hijos)):
                        a, b = hijos[i], hijos[j]
                        if (isinstance(a, Not) and repr(a.x) == repr(b)) or (isinstance(b, Not) and repr(b.x) == repr(a)):
                            hay_comp = True
                            break
                    if hay_comp: break
                if hay_comp:
                    nuevos.append(Const(1))
                    changed = True
                else:
                    nuevos.append(t)
            else:
                nuevos.append(t)
        if changed:
            return And(tuple(nuevos)), "Ley del Complemento (subexpresión)"
        return e, ""

    # not/var/const: sin cambio
    return e, ""
def ley_identidad_anulador_ext(e):
    # or: 1 domina; 0 es neutro (se elimina)
    if isinstance(e, Or):
        terms = list(e.cosas)
        if any(isinstance(t, Const) and t.v == 1 for t in terms):
            return Const(1), "Identidad/Anulador (+ extendida)"
        nuevos = [t for t in terms if not (isinstance(t, Const) and t.v == 0)]
        if len(nuevos) != len(terms):
            if len(nuevos) == 0:
                return Const(0), "Identidad/Anulador (+ extendida)"
            if len(nuevos) == 1:
                return nuevos[0], "Identidad/Anulador (+ extendida)"
            return Or(tuple(nuevos)), "Identidad/Anulador (+ extendida)"
        return e, ""

    # and: 0 domina; 1 es neutro (se elimina)
    if isinstance(e, And):
        terms = list(e.cosas)
        if any(isinstance(t, Const) and t.v == 0 for t in terms):
            return Const(0), "Identidad/Anulador (* extendida)"
        nuevos = [t for t in terms if not (isinstance(t, Const) and t.v == 1)]
        if len(nuevos) != len(terms):
            if len(nuevos) == 0:
                return Const(1), "Identidad/Anulador (* extendida)"
            if len(nuevos) == 1:
                return nuevos[0], "Identidad/Anulador (* extendida)"
            return And(tuple(nuevos)), "Identidad/Anulador (* extendida)"
        return e, ""

    return e, ""

def ley_complemento_and_en_or(e):
    if not isinstance(e, Or):
        return e, ""
    partes = list(e.cosas)
    cambio = False

    def and_tiene_complemento(n):
        t = list(n.cosas)
        for i in range(len(t)):
            for j in range(i+1, len(t)):
                a, b = t[i], t[j]
                if (isinstance(a, Not) and repr(a.x) == repr(b)) or (isinstance(b, Not) and repr(b.x) == repr(a)):
                    return True
        return False

    for i, term in enumerate(partes):
        if isinstance(term, And) and and_tiene_complemento(term):
            partes[i] = Const(0)
            cambio = True

    if not cambio:
        return e, ""

    # limpiar OR: 1 domina; 0 es neutro
    if any(isinstance(x, Const) and x.v == 1 for x in partes):
        return Const(1), "Complemento en AND dentro de OR"
    partes = [x for x in partes if not (isinstance(x, Const) and x.v == 0)]
    if len(partes) == 0:
        return Const(0), "Complemento en AND dentro de OR"
    if len(partes) == 1:
        return partes[0], "Complemento en AND dentro de OR"
    return Or(tuple(partes)), "Complemento en AND dentro de OR"


def ley_complemento_en_or_general(e):
    def flatten_or_terms(node):
        pila = [node]
        planos = []
        while pila:
            t = pila.pop()
            if isinstance(t, Or):
                pila.extend(t.cosas)
            else:
                planos.append(t)
        return planos

    if isinstance(e, Or):
        terms = flatten_or_terms(e)
        if len(terms) != len(e.cosas):
            return Or(tuple(terms)), "Ley Asociativa (+ aplanado)"
        for i in range(len(terms)):
            for j in range(i+1, len(terms)):
                a, b = terms[i], terms[j]
                if (isinstance(a, Not) and repr(a.x) == repr(b)) or (isinstance(b, Not) and repr(b.x) == repr(a)):
                    return Const(1), "Ley del Complemento (OR n-ario)"
        return e, ""

    if isinstance(e, And):
        partes = list(e.cosas)
        cambio = False
        for idx, term in enumerate(partes):
            if isinstance(term, Or):
                terms = flatten_or_terms(term)
                if len(terms) != len(term.cosas):
                    partes[idx] = Or(tuple(terms))
                    cambio = True
                    continue
                hay_comp = False
                for i in range(len(terms)):
                    for j in range(i+1, len(terms)):
                        a, b = terms[i], terms[j]
                        if (isinstance(a, Not) and repr(a.x) == repr(b)) or (isinstance(b, Not) and repr(b.x) == repr(a)):
                            hay_comp = True
                            break
                    if hay_comp:
                        break
                if hay_comp:
                    partes[idx] = Const(1)
                    cambio = True
        if cambio:
            if any(isinstance(x, Const) and x.v == 0 for x in partes):
                return Const(0), "Identidad/Anulador (* extendida)"
            partes = [x for x in partes if not (isinstance(x, Const) and x.v == 1)]
            if len(partes) == 0:
                return Const(1), "Identidad/Anulador (* extendida)"
            if len(partes) == 1:
                return partes[0], "Identidad/Anulador (* extendida)"
            return And(tuple(partes)), "Identidad/Anulador (* extendida)"
        return e, ""
    return e, ""


boolean_laws = [
    ley_distributiva_comun_and,
    ley_distributiva_factor,
    ley_asociativa,
    ley_complemento_and_en_or,       # <- NUEVA
    ley_complemento_en_or_general,
    ley_identidad_anulador_ext,
    ley_idempotencia,
    ley_producto_suma_comun,
    ley_neutro,
    ley_anulador,
    ley_complemento_ext,
    ley_complemento,
    ley_doble_negacion,
    ley_absorcion,
    ley_demorgan,
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