#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_document.py
#
#  Copyright 2012 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

'''
Created on 18/08/2024
@author: mpbe
'''

# imports del sistema -------------------------------------------------------
import re
# helpers_mpbe --------------------------------------------------------------
from helpers_mpbe.python import compose, compose_dict, check_list
# kivy ----------------------------------------------------------------------
from kivy.uix.boxlayout import BoxLayout
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, OptionProperty, ObjectProperty, NumericProperty
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.wg_markdown import MD_LINE_TYPE
from kivy_mpbe_widgets.wg_markdown import TYPE_PATTERNS
from kivy_mpbe_widgets.wg_markdown.md_translate import TranslateMarkdownToKVMarkup, ExtKVTable
from kivy_mpbe_widgets.wg_markdown.md_labels import MDTextLabel, MDSeparatorLabel, MDHeadLabel, MDTaskLabel, MDToDoLabel
from kivy_mpbe_widgets.wg_markdown.md_labels import MDTableLabel, MDImageLabel, MDCodeLabel
# from kivy_dkw.wg_markdown.md_editors import MDLineEditor

md_doc_example_1 = """Título PRINCIPAL
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


class MDLine(EventDispatcher):
    """Clase que define una linea de texto en formato markdown
    **Properties:**
        type (MD_LINE_TYPE): Define el tipo de texto markdown que contiene la linea.
        md_text (str): Guarda el texto de la linea en formato markdown.
        num_line (int): Numero de Linea.
    **Atributes:**
        prev_line (MDLine): Referencia a la linea anterior.
        next_line (MDLine): Referencia a la linea siguiente.
        translate_markup (TranlateMarkdownToKVMarkup): Traductor del formato Markdown a Markup de Kivy.
    **Methods:**
        get_tab_level(): Devuelve la cantidad de tabulaciones al inicio de la linea.
        get_list_Childs(): Devuelve una lista con las lineas hijas de la linea actual.
        get_list_parent(): Devuelve la linea padre de la linea actual.
        get_list_prev(): Devuelve la linea previa a la linea actual en el mismo nivel de la lista.
        get_list_next(): Devuelve la linea siguiente a la linea actual en el mismo nivel de la lista.
        get_title_level(): Devuelve el nivel de título.
        get_title_Childs(): Devuelve los Titulos Hijos de la linea.
        get_title_first_child(): Devuelve la primer linea de titulo hijo del título actual.
        get_title_parent(): Devuelve el título padre de la linea de título actual.
        get_title_prev_same_level(): Devuelve el título previo del mismo nivel.
        get_title_next_same_level(): Devuelve el título siguiente del mismo nivel.
        get_title_prev(): Devuelve el título previo.
        get_title_next(): Devuelve el título siguiente.
        get_markup_text(extensions=None):
        update_type():
    **Events:**
        on_type(instance, new_type)
        on_txt_change(instance, value)
        on_num_line(instance, value)
    """
    type = ObjectProperty(baseclass=MD_LINE_TYPE, defaultvalue=MD_LINE_TYPE.TEXT)
    md_text = StringProperty(defaultvalue='')
    num_line = NumericProperty(defaultvalue=-1)

    def __init__(self, md_text, prev_line, next_line, type=MD_LINE_TYPE.TEXT, num_line=-1):
        """
        Constructor class
        Parameters:
            md_text (str): Texto de la linea en formato Markdown.
            prev_line (MDLine): Referencia a la linea anterior, None si es la primer linea.
            next_line(MDLine): Referencia a la linea siguiente, None si es la ultima linea.
            type (MD_LINE_TYPE): Texto que identifica el tipo de linea.  (YA NO HACE FALTA?)
        """
        self.md_text = compose(md_text, str, None)
        self.type = compose(type, MD_LINE_TYPE, None)
        self.num_line = num_line
        EventDispatcher.__init__(self)
        # variables del arbol ---------------
        # self.md_text = compose(md_text, str, False)
        self.prev_line = compose(prev_line, MDLine, True)
        self.next_line = compose(next_line, MDLine, True)
        # self.parent = compose(parent, MDLine, True)
        # childs = compose(childs, list, True)
        # if childs:
        #     self.childs = check_list(childs, MDLine, True)
        # self._type = compose(type, MD_LINE_TYPES, False)  # ToDo VER SI HACE FALTA PASAR O LLAMO Update_Type()
        # Define el traductor a MarkUp ------
        extensions = [ExtKVTable]
        self.tranlate_markup = TranslateMarkdownToKVMarkup(extensions=extensions)
        # Widgets ---------------------------
        # self.size_hint_y = 1
        # self._editor = MDLineEditor(self.md_text)
        # self._editor.md_editor.bind(text=self.on_txt_change)
        # self.add_widget(self._editor)

    # def __repr__(self):
    #     return f'Line(type={self.type}, text={self.md_text})'

    # Properties Functions  ----------------------------------------------------------------
    # def _get_type(self):
    #     return self._type
    # def _set_type(self, md_type):
    #     if self._type != md_type:
    #         self._type = compose(md_type, MD_LINE_TYPES, False)
    #         # ToDo Actualizar el Label de MDLineEditor
    #         # ToDo Chequear si el cambio afecta al arbol
    # type = property(_get_type, _set_type)

    """List, task, todo Function ------------------------------------------------------------"""
    def get_tab_level(self):
        '''Calcula la cantidad de tabulaciones al inicio de la linea'''
        contador = 0
        for char in self.md_text:
            if char == ' ':
                contador += 1
            else:
                break
        return int(contador/4)

    def get_list_Childs(self):  # TODO: Sin Codificar
        '''Devuelve una lista con las lineas hijas de la linea actual'''
        pass

    def get_list_parent(self):  # TODO: Sin Codificar
        '''Devuelve la linea padre de la linea actual'''
        pass

    def get_list_prev(self):  # TODO: Sin Codificar
        '''Devuelve la linea previa a la linea actual en el mismo nivel de la lista'''
        pass

    def get_list_next(self):  # TODO: Sin Codificar
        '''Devuelve la linea siguiente a la linea actual en el mismo nivel de la lista'''
        pass


    """Title Function -----------------------------------------------------------------------"""
    def get_title_level(self):
        '''Devuelve el nivel de título'''
        if self.type == MD_LINE_TYPE.HEAD_TITLE:
            contador = 1
        else:
            contador = 0
            for char in self.md_text:
                if char == '#':
                    contador += 1
                else:
                    break
        return contador

    def get_title_Childs(self): # SEGUIR DE ACA
        '''Devuelve los Titulos Hijos de la linea'''
        parent_level = self.get_title_level()
        childs_level = parent_level + 1
        childs = []
        line = self.next_line
        while line != None:
            if line.type in [MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE]:
                level = line.get_title_level()
                if level == childs_level:
                    childs.append(line)
                elif level == parent_level:
                    return childs
            line = line.next_line
        return childs

    def get_title_first_child(self):
        '''Devuelve la primer linea de titulo hijo del título actual'''
        current_level = self.get_title_level()
        if self.next_line != None:
            line = self.next_line
            while line != None:
                if line.type in [MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE]:
                    level = line.get_title_level()
                    if level-1 == current_level:
                        return line
                line = line.next_line
            return None

    def get_title_parent(self):
        '''Devuelve el título padre de la linea de título actual'''
        parent_level = self.get_title_level() - 1
        if self.prev_line != None:
            line = self.prev_line
            while line != None:
                if line.type in [MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE]:
                    level = line.get_title_level()
                    if level == parent_level:
                        return line
                line = line.prev_line
            return None

    def get_title_prev_same_level(self):
        '''Devuelve el título previo del mismo nivel'''
        current_level = self.get_title_level()
        if self.prev_line != None:
            line = self.prev_line
            while line != None:
                if line.type in [MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE]:
                    level = line.get_title_level()
                    if level == current_level:
                        return line
                line = line.prev_line
            return None

    def get_title_next_same_level(self):
        '''Devuelve el título siguiente del mismo nivel'''
        current_level = self.get_title_level()
        if self.next_line != None:
            line = self.next_line
            while line != None:
                if line.type in [MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE]:
                    level = line.get_title_level()
                    if level == current_level:
                        return line
                line = line.next_line
            return None

    def get_title_prev(self):
        '''Devuelve el título previo'''
        if self.prev_line != None:
            line = self.prev_line
            while line != None:
                if line.type in [MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE]:
                    return line
                line = line.prev_line
            return None

    def get_title_next(self):
        '''Devuelve el título siguiente'''
        if self.next_line != None:
            line = self.next_line
            while line != None:
                if line.type in [MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE]:
                        return line
                line = line.next_line
            return None

    """Process Function ---------------------------------------------------------------------"""
    def get_markup_text(self, extensions=None):  # Todo: SACAR
        """Devuelve el texto en formato Markup segun el tipo.
        Para tablas retorna un texto con los datos para generar el grid"""
        return self.tranlate_markup.translate(self.md_text)

    def update_type(self):
        """
        Actualiza el tipo de linea y devuelve None o el tipo anterior si cambio
        Parameters:
            previus_line: Linea Anterior a la Actual
        """
        # TODO: Cambiar a diccionario de patrones como en MDDocument
        # Expresiones regulares para detectar diferentes tipos de párrafos
        tabla_patron = r'^\|.*\|$'  # Para detectar cualquier fila de una tabla
        lista_patron = r'^\s*- [^\[].*'  # Para listas regulares  ^\s*[-*+]\s+.*
        lista_o_patron = r'^\d{1,2}\.\s.+$'  # Para listas numeradas
        tarea_patron = r'^\s*-\s\[[x\s]\].*'  # Para listas de tareas (checkbox)  ^\s*[-*+] \[.\]\s+.*
        todo_patron = r'^\s*-\[[xo>\-\s].*'  # Para tareas tipo ToDo    ^\s*-\[\s\]\s+.*
        titulo_patron = r'^#{1,6}\s+.*$'  # Para títulos con #
        titulo_subrayado_patron = r'^===[=\s]*$'  # Para títulos subrayados con ===   ^.*\n=+$
        separador_patron = r'^---[-\s]*$'  # Para separador horizontal (linea horizontal)
        imagen_patron = r'^!\[.*?\]\(.*?\)$'  # Imagen

        # Variables Internas
        type = MD_LINE_TYPE.TEXT
        old_type = self.type
        mdl = self.md_text

        # ToDo RE-HACER CON LA DEFINICION DE Next, Prev, Parent y Childs

        # Texto ----------------------------------------------
        if mdl.lstrip()[0].isalnum():  # verifica si el primer caracter es una letra (mayuscula o minuscula)
            self.type = MD_LINE_TYPE.TEXT
        # Encabezado -----------------------------------------  COFIDICADO
        elif re.match(titulo_subrayado_patron, mdl) and self.prev_line.prev_line == None:
            self.type = MD_LINE_TYPE.UNDERLINE_TITLE
            self.prev_line.type = MD_LINE_TYPE.HEAD_TITLE
            # Todo tiene que actualizar el widget
        # Detectar títulos con # -----------------------------
        elif re.match(titulo_patron, mdl):
            self.type = MD_LINE_TYPE.TITLE
            # ToDo FALTA ACTUAILZAR EL ARBOL DE TITULOS

        # Detectar Separadores de Linea ----------------------  COFIDICADO
        elif re.match(separador_patron, mdl):
            self.type = MD_LINE_TYPE.SEPARATOR
        # Detectar Listas ------------------------------------
        elif re.match(lista_patron, mdl):
            self.type = MD_LINE_TYPE.LIST
            # ToDo FALTA ACTUAILZAR EL ARBOL DE TITULOS

        # Detectar Listas Numeradas --------------------------
        elif re.match(lista_o_patron.strip(), mdl):
            self.type = MD_LINE_TYPE.ORDER_LIST
            # ToDo FALTA ACTUAILZAR EL ARBOL DE TITULOS

        # Detectar Tareas -----------------------------------
        elif re.match(tarea_patron, mdl):
            self.type = MD_LINE_TYPE.TASK
            # ToDo FALTA ACTUAILZAR EL ARBOL DE TITULOS

        # Detectar Todo -------------------------------------
        elif re.match(todo_patron, mdl):
            self.type = MD_LINE_TYPE.TODO
            # ToDo FALTA ACTUAILZAR EL ARBOL DE TITULOS

        # Detectar Tablas ------------------------------------  CODIFICADO
        elif re.match(tabla_patron, mdl):
            self.type = MD_LINE_TYPE.TABLE
        # Detectar Blockquote -------------------------------  CODIFICADO
        elif mdl.strip().startswith('>'):
            self.type = MD_LINE_TYPE.BLOCKQUOTE
        # Detectar Imagenes ---------------------------------  CODIFICADO
        elif re.match(imagen_patron, mdl.strip()):
            self.type = MD_LINE_TYPE.IMAGEN
        # Detectar linea de codigo ---------------------------
        elif mdl.startswith('```') or (mdl == '```' and self.prev_line.type != MD_LINE_TYPE.CODE):  # Bloque de código Inicio
            self.type = MD_LINE_TYPE.START_CODE
            # ToDo Falta buscar para abajo y modificar todas las lineas hasta el proximo ´´´
            # SI CAMBIA HACIA ABAJO DEBERIA ACTUALIZAR EL WIGGET
        # Detectar Texto ---------------------------------  CODIFICADO
        else:
            self.type = MD_LINE_TYPE.TEXT

        if old_type != self.type:
            # ToDo esto tiene que cambiar a chequear en funcion del valor del anterior si hay que actualizar la estructura del arbol
            # Si viejo tenia arbol, hay que modificarlo
            self._activate_type()
            return old_type
        else:
            return None

    # Events functions ------------------------------------------------------------------------------
    def on_type(self, instance, new_type):
        if self.type != new_type:
            self.type = new_type
            pass
            # ToDo Actualizar el Label de MDLineEditor
            # ToDo Chequear si el cambio afecta al arbol

    def on_txt_change(self, instance, value):
        self.md_text = value

    def on_num_line(self, instance, value):
        '''Actualizacion automatica de los numeros de linea'''
        # print(f"MDLine.on_num_line")
        if self.next_line:
            # print(f"  value= {value}-> {self.md_text}")
            self.next_line.num_line = value + 1



# class MDParagraph(object):
#     def __init__(self, md_text, type):
#         """
#         Constructor class
#         md_text (str): Texto del parafo en formato Markdown
#         type (str): Texto que identifica el tipo de parrafo.
#                     ("Text", "Title", "Separator", "Table", "List", "Task", "ToDo")
#         """
#         self.md_text = compose(md_text, str, False)
#         self._types = ('Text', 'Title', 'Separator', 'Table', 'List', 'Task', 'ToDo')
#         if type in self._types:
#             self.type = type
#         else:
#             raise ValueError(f'{type} is not in type value ("Text", "Title", "Separator", "Table", "List", "Task", "ToDo")')
#
#     def __repr__(self):
#         return f'Paragraph(type={self.type}, text={self.md_text})'
#
#     def get_markup_text(self, extensions=None):
#         """Devolve el texto en formato Markup segun el tipo.
#         Para tablas retorna un texto con los datos para generar el grid"""
#         translate_mku = TranslateMarkdownToKVMarkup(extensions)
#         if self.type == 'Table':
#             self.translate_mku.append_extension(ExtKVTable)
#         return translate_mku.translate(self.document)


class MDDocument(object):
    """
    Clase para manejar documentos Markdown
    **Attributes:**
        document (str): Document in markdown format
        path_doc (str): Directory where the document file is located
        doc_name (str): File name with its extension
    **Properties:**
        md_lines (list(MDLines): Lista de solo lectura con las lineas del documento.
        can_lines (int): Cantidad de lineas del documento. De solo lectura.
    **Methods:**
        load_doc(path, doc_name): Lee le documento markdown de un archivo
        save_doc(): Guarda el documento en el archivo
        save_as_doc(path, doc_name): Guarda el documento en el directorio y nombre indicados.
        separate_lines(): Devuelve una lista MDLine con las lineas del documento.
        join_lines(): Genera el documento desde la lista de lineas MDLine y lo guarda en document.
        get_first_title(): Devuelve la primera linea con titulo.
        rebulid_title_tree(): Reconstruye el arbol de títulos.
        title_level(md_txt): Devuelve el nivel del título
        find_children_titles(parent_title): Devuelve una lista MDLine con los titulos hijos del título indicado.
        append_line(md_text_line):
        append_line(md_text_lines):
        insert_line(id_line, md_text_line):
        insert_lines(id_line, md_text_lines):
        remove_line(md_line):
        remove_lines(md_lines):
        clear_lines():
        move_line_up(md_line)
        move_up_lines(ed_line, cant_lines):
        move_line_down(md_line):
        move_down_lines(ed_line, cant_lines):
        move_line_to(num_line, ed_line):
        move_lines_to(num_line, ed_line, cant_lines):
        get_markup_text(extensions=None):
        update_type_line(md_line):
        update_family(self, mdline):
    """

    def __init__(self, **kwargs):
        """
        Class constructor
        Keyword arguments:
            document (str): Document in markdown format
            path_doc (str): Directory where the document file is located
            doc_name (str): File name with its extension
        """
        # # Expresiones regulares para detectar diferentes tipos de párrafos
        # self._type_patterns = {
        # 'table':r'^\|.*\|$',  # Para detectar cualquier fila de una tabla
        # 'list':r'^\s*- [^\[].*',  # Para listas regulares  ^\s*[-*+]\s+.*
        # 'ordered_list':r'^\d{1,2}\.\s.+$',  # Para listas numeradas
        # 'task':r'^\s*-\s\[[x\s]\].*',  # Para listas de tareas (checkbox)  ^\s*[-*+] \[.\]\s+.*
        # 'todo':r'^\s*-\[[xo>\-\s].*',  # Para tareas tipo ToDo    ^\s*-\[\s\]\s+.*
        # 'title':r'^#{1,6}\s+.*$',  # Para títulos con #
        # 'underlined_title':r'^===[=\s]*$',  # Para títulos subrayados con ===   ^.*\n=+$
        # 'separator':r'^---[-\s]*$',  # Para separador horizontal (linea horizontal)
        # 'image':r'^!\[.*?\]\(.*?\)$'  # Imagen
        # }


        self.document = compose_dict(kwargs,'md_document',str,None, acept_none=True)
        doc_name = compose_dict(kwargs, 'doc_name', str, None, acept_none=True)
        doc_path = compose_dict(kwargs, 'doc_path', str, None, acept_none=True)
        super().__init__(**kwargs)
        if not self.document:
            self.doc_name = doc_name
            self.doc_path = doc_path
            if self.doc_path and not self.doc_path.endswith('/'):
                self.doc_path += '/'
            self.load_doc()
        self._md_lines = list()
        # self.first_title = None

    """ Document Functions -----------------------------------------------------"""
    def get_md_lines(self):
        return self._md_lines
    md_lines = property(get_md_lines)

    def load_doc(self, path=None, doc_name=None):
        """Carga el documento de un archivo"""
        if path:
            if not path.endswith('/'):
                path += '/'
            self.doc_path = path
        if doc_name:
            self.doc_name = doc_name
        if self.doc_path and self.doc_name:
            ruta_archivo = self.doc_path + self.doc_name
        else:
            return False
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                self.document = archivo.read()
                self._md_lines = list()
                self.separate_lines()
                self._md_lines[0].num_line = 1
                # self.rebulid_title_tree()

                # print("MDDocument.load_doc()-> Numeros de lineas")
                # for ll in self._md_lines:
                #     print(f"    {ll.num_line}\t{ll.md_text}")

                return True
        except FileNotFoundError:
            print(f"El archivo {ruta_archivo} no se encontró.")
        except Exception as e:
            print(f"Se produjo un error al leer el archivo: {e}")
            self._md_lines[0].num_line = 1

    def save_doc(self):
        """Guarda el documento en el path y con el doc_name registrado"""
        ruta_archivo = self.doc_path + self.doc_name
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                archivo.write(self.document)
                return True
            print(f"El archivo {ruta_archivo} se ha guardado correctamente.")
        except Exception as e:
            print(f"Se produjo un error al escribir en el archivo: {e}")

    def save_as_doc(self, path=None, doc_name=None):
        if path:
            if not path.endswith('/'):
                path += '/'
            self.doc_path = path
        if doc_name:
            self.doc_name = doc_name
        self.save_doc()

    def separate_lines(self):
        """Devuelve una lista con la clase MDLine que representa las lineas del documento.
        Notas: Los bloques especiales como las tablas, se devuelven completos.
        """
        # Variables Internas
        md_text = self.document.splitlines(keepends=True)
        nls = len(md_text)
        self._md_lines = []
        # previus_line = None
        # set_mark = MD_LINE_TYPE.TEXT
        # type = MD_LINE_TYPE.TEXT

        parent = None  # para listas
        childs = None  # para listas

        # Procesamiento de Lineas ------------------------------
        print("MDDocument.separate_lines -> Inicia Lectura")
        for i, md_txt_line in enumerate(md_text):
            md_txt_line = md_txt_line.rstrip("\n")
            md_line = self.append_line(md_txt_line)
        print("MDDocument.separate_lines -> Finaliza Lectura")
        return True

    def join_lines(self):
        '''Genera el documento desde la lista de lineas MDLine y lo guarda en document'''
        if self._md_lines:
            par = ""
            for line in self._md_lines:
                par += line.md_text + "\n"
            self.document = par
            return True
        else:
            return False

    def get_first_title(self):
        '''Devuelve la primera linea con titulo'''
        for line in self._md_lines:
            if line.type in [MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE]:
                return line
        return None

    def rebulid_title_tree(self):
        '''Reconstruye el arbol de títulos'''
        root_title = None
        for ii, mdl in enumerate(self._md_lines):
            print(f"Linea {ii}: {mdl.md_text}")
            if mdl.md_text.startswith("=== "):
                root_title = self._md_lines[0]
            elif re.match(self._type_patterns['title'], mdl.md_text):
                self.find_children_titles(mdl)

    def title_level(md_txt):
        '''Devuelve el nivel del título'''
        # Usamos una expresión regular para encontrar los hashes al inicio de la línea
        level = re.match(r"^#+", md_txt)
        if level:
            return len(level.group(0))
        else:
            return 0

    def find_children_titles(self, parent_title):
        """Devuelve una lista MDLine con los titulos hijos del título indicado.
        **Arguments:**
            parent_title (MDLine): Titulo padre
        """
        print(f"MDDocument.find_children_titles -> {parent_title.md_text}")
        parent_level = self.title_level(parent_title.md_text)
        childs_level = parent_level + 1
        parent_id = self._md_lines.index(parent_title)
        childs = []
        parent_title.childs = childs
        for ii in range(parent_id+1, len(self._md_lines)):
            md_line = self._md_lines[ii]
            if re.match(self._type_patterns['title'], md_line.md_text):
                level = self.title_level(md_line.md_text)
                if level == childs_level:
                    md_line.parent = parent_title
                    childs.append(md_line)
                elif level == parent_level:
                    return True
        return True

    """ MDLines list Functions -------------------------------------------------------"""
    def _can_lines(self):
        return len(self._md_lines)
    can_lines = property(_can_lines)

    def append_line(self, md_text_line):  #, prev_line=None, next_line=None, parent=None, childs=None):
        nls = len(self._md_lines)
        if len(self._md_lines) > 0:
            prev_line = self._md_lines[-1]
        else:
            prev_line = None
        # print(f"MDDocument.append_line(), num_line={num_line}")
        new_line = MDLine(md_text_line, type=MD_LINE_TYPE.TEXT, prev_line=prev_line, next_line=None)
        self._md_lines.append(new_line)
        if prev_line != None:  # Actuliza la referencia de la lines previa
            prev_line.next_line = new_line
        self.update_type_line(new_line)  # Actualiza al tipo de linea


        # TODO: Actualizar el arbol

        return new_line

    def append_lines(self, md_text_lines):  # TODO: Sin Codificar
        '''md_text puede ser un texto multilinea o una lista lineas de texto'''
        if isinstance(md_text_lines, str):
            md_text = md_text_lines.splitlines(keepends=True)
        elif not (isinstance(md_text_lines, list)):
            raise ValueError("md_text is not a string or list")
        for md_txt_line in md_text:
            md_txt_line = md_txt_line.rstrip("\n")
            self.append_line(md_txt_line)
        return True

    def insert_line(self, id_line, md_text_line):
        '''Inserta una nueva linea delante del id_line indicado'''
        prev_line = self._md_lines[id_line-1]
        next_line = self._md_lines[id_line]
        new_line = MDLine(md_text_line, type=MD_LINE_TYPE.TEXT, prev_line=prev_line, next_line=next_line)
        self._md_lines.insert(id_line, new_line)
        self.update_type_line(new_line)  # Actualiza al tipo de linea
        # Actualizar las referencias de las linea previa y posterior
        prev_line.next_line = new_line
        next_line.prev_line = new_line


        # TODO: Actualizar el arbol

        return new_line

    def insert_lines(self, id_line, md_text_lines):
        """
        Inserta las nuevas lineas delante del id_line indicado
        md_text puede ser un texto multilinea o una lista lineas de texto
        """
        if isinstance(md_text_lines, str):
            md_text = md_text_lines.splitlines(keepends=True)
        elif not (isinstance(md_text_lines, list)):
            raise ValueError("md_text is not a string or list")
        for md_txt_line in md_text_lines:
            md_txt_line = md_txt_line.rstrip("\n")
            self.insert_line(id_line, md_txt_line)
            id_line += 1
        return True

    def remove_line(self, md_line):
        id_line = self._md_lines.index(md_line)
        prevl = self._md_lines[id_line - 1]
        nextl = self._md_lines[id_line + 1]
        prevl.next_line = nextl
        nextl.prev_line = prevl
        self._md_lines.remove(md_line)
        self.update_type_line(prevl)  # TODO: Esto puede no funcionar con tablas o bloques si se borra la inicializacion o finalizacion del bloque
        self.update_type_line(nextl)
        return True

    def remove_lines(self, md_lines):
        if not (isinstance(md_lines, list)):
            raise ValueError("md_text is not a list")
        for md_line in md_lines:
            self.remove_line(md_line)
        return True

    def clear_lines(self):
        self._md_lines.clear()

    def move_line_up(self, md_line):
        id = self._md_lines.index(md_line)
        mdd = self._md_lines
        mdd[id], mdd[id - 1] = mdd[id - 1], mdd[id]

    def move_up_lines(self, ed_line, cant_lines):
        """
        Parameters:
            ed_line (MDEditorLine): Primer linea de la seleccion
            cant_lines (int): Cantidad de lineas selccionadas debajo de ed_line.
        """
        # TODO: Sin Codificar
        pass

    def move_line_down(self, md_line):  # TODO: EN PROCESO
        id = self._md_lines.index(md_line)
        mdd = self._md_lines
        mdd[id], mdd[id + 1] = mdd[id + 1], mdd[id]
        # mdd = self._md_document
        # mdd.md_lines[id], mdd.md_lines[id + 1] = mdd.md_lines[id + 1], mdd.md_lines[id]

    def move_down_lines(self, ed_line, cant_lines):
        """
        Parameters:
            ed_line (MDEditorLine): Primer linea de la seleccion
            cant_lines (int): Cantidad de lineas selccionadas debajo de ed_line.
        """
        # TODO: Sin Codificar
        pass

    def move_line_to(self, num_line, ed_line):
        '''Mueve ed_line a la poscion num_line'''
        # TODO: Sin Codificar
        pass

    def move_lines_to(self, num_line, ed_line, cant_lines):
        """
        Parameters:
            num_line (int): Numero de linea destino de la seleccion
            ed_line (MDEditorLine): Primer linea de la seleccion
            cant_lines (int): Cantidad de lineas selccionadas debajo de ed_line.
        """
        # TODO: Sin Codificar
        pass

    """ MarkDown Functions -----------------------------------------------------------"""
    def get_markup_text(self, extensions=None):
        translate_mku = TranslateMarkdownToKVMarkup(extensions)
        return translate_mku.translate(self.document)

    def update_type_line(self, md_line):  # retorna type, set_mark
        '''Update md_line type and related md_lines'''
        type = MD_LINE_TYPE.TEXT
        md_txt_line = md_line.md_text.rstrip("\n")
        # Linea vacia ----------------------------------------
        if md_txt_line == None:
            type = None
        # Detecta un set_Mark --------------------------------
        if md_txt_line.startswith('```'):  # Bloque de código
            raise ValueError("BLOQUE SIN CODIFICAR (Tipo Bloque de Codigo)")
            pass  # TODO: Hacer con el uso de Previus y Next. RECODIFICAR
            # if set_mark == MD_LINE_TYPE.CODE:  # ciera el bloque
            #     set_mark = MD_LINE_TYPE.TEXT
            #     type = MD_LINE_TYPE.CODE
            # else:  # abre el bloque
            #     set_mark = MD_LINE_TYPE.CODE
            #     type = MD_LINE_TYPE.CODE
        # Detectar lineas vacias -----------------------------
        # elif md_line == '\n':
        # prev_line = self.append_line(md_line, set_mark)
        # Detectar títulos con # -----------------------------
        elif re.match(TYPE_PATTERNS.title, md_txt_line):
            md_line.type = MD_LINE_TYPE.TITLE
        # Detectar títulos subrayados con === ----------------
        elif re.match(TYPE_PATTERNS.underlined_title, md_txt_line):
            md_line.prev_line.type = MD_LINE_TYPE.HEAD_TITLE
            md_line.type = MD_LINE_TYPE.SEPARATOR
        # Detectar Separadores de Linea ----------------------
        elif re.match(TYPE_PATTERNS.separator, md_txt_line):
            md_line.type = MD_LINE_TYPE.SEPARATOR
        # Detectar Tablas ------------------------------------
        elif re.match(TYPE_PATTERNS.table, md_txt_line):
            md_line.type = MD_LINE_TYPE.TABLE
        # Detectar Listas ------------------------------------
        elif re.match(TYPE_PATTERNS.list, md_txt_line):
            md_line.type = MD_LINE_TYPE.LIST
        # Detectar Listas Numeradas --------------------------
        elif re.match(TYPE_PATTERNS.ordered_list, md_txt_line):  # lista_o_patron.strip()
            md_line.type = MD_LINE_TYPE.ORDER_LIST
        # Detectar Tareas -----------------------------------
        elif re.match(TYPE_PATTERNS.task, md_txt_line):
            md_line.type = MD_LINE_TYPE.TASK
        # Detectar Todo -------------------------------------
        elif re.match(TYPE_PATTERNS.todo, md_txt_line):
            md_line.type = MD_LINE_TYPE.TODO
        # Detectar Blockquote -------------------------------
        elif md_txt_line.strip().startswith('>'):
            md_line.type = MD_LINE_TYPE.BLOCKQUOTE
        # Detectar Imagenes ---------------------------------
        elif re.match(TYPE_PATTERNS.image, md_txt_line.strip()):
            md_line.type = MD_LINE_TYPE.IMAGEN
        # Detectar Texto ------------------------------------
        else:
            md_line.type = MD_LINE_TYPE.TEXT

    def update_family(self, mdline):  # TODO: Sin Codificar
        '''Update parent and childs of md_line and related md_lines'''
        raise ValueError("BLOQUE SIN CODIFICAR")
