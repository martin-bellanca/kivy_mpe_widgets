#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ejemplo de Extension para el modulo markdown que agrega la traduccion tareas a html"""


from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re


class WhiteLineMDExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(WhiteLineMDPreprocessor(md), 'tasklist', 175)

class WhiteLineMDPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            # Reemplaza 2 espacios por un HTML <br>
            line = re.sub(r'^ {2}$', r'<br>', line, flags=re.MULTILINE)
            new_lines.append(line)
        return new_lines


class TaskListMDExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(TaskListMDPreprocessor(md), 'tasklist', 175)

class TaskListMDPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            # Reemplaza [>] por un HTML que indique 'en proceso'
            line = re.sub(r'^\s*\[>\]\s*(.*)', r'<p><span style="color: blue;">🔄 \1</span></p>', line)
            # Reemplaza [o] por un HTML que indique 'paralizada'
            line = re.sub(r'^\s*\[o\]\s*(.*)', r'<p><span style="color: orange;">⏸ \1</span></p>', line)
            # Reemplaza [-] por un HTML que indique 'anulada'
            line = re.sub(r'^\s*\[-\]\s*(.*)', r'<p><span style="color: red;">- \1</span></p>', line)
            new_lines.append(line)
        return new_lines



'''-----------------------------------------------------------------------------'''
# Uso del renderizador
# import markdown
#
# md_text = """
# Cabecera
# ===
#
# ## Tipos de Texto
# Texto Normal
# **Negrita**
# *Cursiva*
# _Italica_
#
# ---
# ## Referencia a Imagenes
# ![Imagen de ejemplo](https://via.placeholder.com/150)
#
# ---
# ## Tablas
# | Columna 1 | Columna 2 | Columna 3 |
# | --------- | --------- | --------- |
# | Valor 1   | Valor 2   | Valor 3   |
#
# ---
# ## Enlaces
# [Enlace a Kivy](https://kivy.org)
#
# ---
# ## Definicion de Listas y Tareas
#
# **Lista**
# - item 1
#     - Sbu Item 1
# - item 2
#
# **Lista de Comprobacion**
# - [ ] Tarea sin iniciar
#     - [x] Sub Tarea
# - [x] Tarea completada
#
# **Lista de Tareas o Tarea (MPBE)**
# [ ] Tarea Sin Inicar
# [>] Tarea En Proceso
# [o] Tarea Paralizada
# [x] Tarea Finalizada
# [-] Tarea Anulada
# """
# html = markdown.markdown(md_text, extensions=[TaskListMDExtension(), WhiteLineMDExtension()])
# print(html)