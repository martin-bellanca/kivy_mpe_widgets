import re


class Parrafo:
    def __init__(self, texto, tipo):
        self.texto = texto
        self.tipo = tipo

    def __repr__(self):
        return f'Parrafo(tipo={self.tipo}, texto={self.texto})'


def separar_parrafos(texto):
    # Expresiones regulares para detectar diferentes tipos de párrafos
    tabla_patron = r'^\|.*\|$'  # Para detectar cualquier fila de una tabla
    lista_patron = r'^\s*- [^\[].*'  # Para listas regulares  ^\s*[-*+]\s+.*
    tarea_patron = r'^\s*-\s\[[x\s]\].*'  # Para listas de tareas (checkbox)  ^\s*[-*+] \[.\]\s+.*
    todo_patron = r'^\s*-\[[xo>\-\s].*'  # Para tareas tipo ToDo    ^\s*-\[\s\]\s+.*
    titulo_patron = r'^#{1,6}\s+.*$'  # Para títulos con #
    titulo_subrayado_patron = r'^===[=\s]*$'  # Para títulos subrayados con ===   ^.*\n=+$
    separador_patron = r'^---[-\s]*$'  # Para separador horizontal (linea horizontal)

    lineas = texto.splitlines(keepends=True)
    parrafos = []
    parrafo_actual = []
    tipo_actual = None
    dentro_tabla = False

    """
    NOTAS:
        Sacar los .strip() que sacanr los espacios anteriores y posteriores"""

    for i, linea in enumerate(lineas):
        if linea == None:
            continue
        if linea == '\n':
            if tipo_actual == 'Parrafo':
                parrafo_actual.append(linea)
                parrafos.append(Parrafo(''.join(parrafo_actual), "Parrafo"))
                dentro_tabla = False
                parrafo_actual = []
            else:
                if parrafo_actual:
                    parrafos.append(Parrafo(''.join(parrafo_actual), tipo_actual))
                parrafos.append(Parrafo(linea, "Parrafo"))
                dentro_tabla = False
                parrafo_actual = []
            continue
        # Detectar títulos con # -----------------------------
        if re.match(titulo_patron, linea):
            if parrafo_actual:
                parrafos.append(Parrafo(''.join(parrafo_actual), tipo_actual))
                parrafo_actual = []
            parrafos.append(Parrafo(linea, "Titulo"))
        # Detectar títulos subrayados con === ----------------
        elif i < len(lineas) - 1 and re.match(titulo_subrayado_patron, lineas[i + 1]):  # f"{linea}\n{lineas[i + 1]}")
            if parrafo_actual:
                parrafos.append(Parrafo(''.join(parrafo_actual), tipo_actual))
                parrafo_actual = []
            parrafos.append(Parrafo(linea+lineas[i+1], "Titulo"))
            lineas[i + 1] = None  # Evitar volver a procesar la línea de subrayado
        # Detectar Separadores de Linea -------------------------
        elif re.match(separador_patron, linea):
            if parrafo_actual:
                parrafos.append(Parrafo(''.join(parrafo_actual), tipo_actual))
                parrafo_actual = []
            parrafos.append(Parrafo(linea, "Separador"))

        # Detectar Tablas ------------------------------------
        elif re.match(tabla_patron, linea):
            if not dentro_tabla and parrafo_actual:
                parrafos.append(Parrafo(''.join(parrafo_actual), tipo_actual))
                parrafo_actual = []
            parrafo_actual.append(linea)
            tipo_actual = "Tabla"
            dentro_tabla = True
        # Detectar Listas -----------------------------------
        elif re.match(lista_patron, linea):
            if parrafo_actual and tipo_actual != "Tabla":
                parrafos.append(Parrafo(''.join(parrafo_actual), tipo_actual))
                parrafo_actual = []
            parrafos.append(Parrafo(linea, "Lista"))
        # Detectar Tareas -----------------------------------
        elif re.match(tarea_patron, linea):
            if parrafo_actual and tipo_actual != "Tabla":
                parrafos.append(Parrafo(''.join(parrafo_actual), tipo_actual))
                parrafo_actual = []
            parrafos.append(Parrafo(linea, "Tarea"))
        # Detectar Todo -------------------------------------
        elif re.match(todo_patron, linea):
            if parrafo_actual and tipo_actual != "Tabla":
                parrafos.append(Parrafo(''.join(parrafo_actual), tipo_actual))
                parrafo_actual = []
            parrafos.append(Parrafo(linea, "ToDo"))
        # Detectar Parrafos ---------------------------------
        # elif linea:
        else:
            if dentro_tabla:
                parrafo_actual.append(linea)
            else:
                if not parrafo_actual:
                    tipo_actual = "Parrafo"
                parrafos.append(Parrafo(linea, "Parrafo"))
    if parrafo_actual:
        parrafos.append(Parrafo(''.join(parrafo_actual), tipo_actual))

    return parrafos


# Ejemplo de uso:
texto = """Título PRINCIPAL
===
Este es un párrafo normal.
Misma linea del parrafo.  
Otra Linea del mismo parrafo.

---
--- --    ----

Otro Parrafo.
Otra linea.
Texto subrayado con ===
=======================

# Lista: ++++++++++++++++++++++

- Item de una lista
    - sub item
- Otro item de la lista

# Tareas: +++++++++++++++++++++
- [ ] Tarea pendiente
- [x] Tarea completada
    - [x] Sub Tarea

# ToDo: +++++++++++++++++++++++
-[ ] ToDo item sin espacio
  -[>] Todo en proceso
-[o] Todo paralizada
-[-] Todo Anulada
-[x] Todo Finalizada

Tabla: ++++++++++++++++++++++++
| Columna 1 | Columna 2 |
| --------- | --------- |
| Valor 1   | Valor 2   |

Este es un segundo párrafo que no está relacionado con la lista ni la tabla.
Ultima Linea.
"""

parrafos = separar_parrafos(texto)
for parrafo in parrafos:
    print(parrafo.texto+"  -> Tipo:"+parrafo.tipo)

# print()
# print('---------------------------------------------------------------')
# print('---------------------------------------------------------------')
# par = ''
# for parrafo in parrafos:
#     par += parrafo.texto
# print(par)