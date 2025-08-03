#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_MDLabels.py
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
Created on 10/09/2023
@author: mpbe
'''

"""------------------------------------------------------------------------"""
"""-- Test Program  -------------------------------------------------------"""
"""------------------------------------------------------------------------"""
from markdown import markdown
# Kivy imports -------------------------------------------------------------
from kivy.app import App
from kivy.core.window import Window
# Kivy_dkw imports -------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_markdown.markdown_extension import TaskListMDExtension
from kivy_mpbe_widgets.wg_markdown.md_translate import TranslateMarkdownToKVMarkup
from kivy_mpbe_widgets.wg_markdown.md_labels_viejo import MarkdownLabel


class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Markdown"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        md_text="""
# Cabecera
===
  
##Tipos de Texto
Texto Normal
**Negrita**
*Cursiva*
_Italica_
~~Tachado~~
~Subrayado~
---
## Referencia a Imagenes
![Imagen de ejemplo](https://via.placeholder.com/150)

---
## Tablas
| Columna 1 | Columna 2 | Columna 3 |
| --------- | --------- | --------- |
| Valor 1   | Valor 2   | Valor 3   |

---
## Enlaces
[Enlace a Kivy](https://kivy.org)

---  
### Definicion de Listas y Tareas

**Lista**
- item 1
    - Sbu Item 1
- item 2
  
**Lista de Comprobacion**
- [ ] Tarea sin iniciar
    - [x] Sub Tarea
- [x] Tarea completada

**Lista de Tareas o Tarea (MPBE)**
[ ] Tarea Sin Inicar
[>] Tarea En Proceso
[o] Tarea Paralizada
[x] Tarea Finalizada
[-] Tarea Anulada
"""
        # html = markdown(md_text, extensions=[TaskListMDExtension()])  ## El label no renderiza html
        # return MarkdownLabel(text=html, size_hint=(1,1))
        tr = TranslateMarkdownToKVMarkup()
        kvmu = tr.translate(md_text)
        return MarkdownLabel(markdown_text=kvmu, size_hint=(1,1))


if __name__ == "__main__":
    TestApp().run()