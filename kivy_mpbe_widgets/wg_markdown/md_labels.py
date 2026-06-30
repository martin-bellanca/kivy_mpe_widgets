#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_labels.py
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

"""
Created on 03/08/2024
@author: mpbe
Note: Widgets the markdown elements for use in parse_markdown_to_widget.py
"""

# imports del sistema -------------------------------------------------------
import re
from markdown import markdown
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import StringProperty
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets import IMAGES_PATH
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_markdown.md_translate import translate_markdown_line_to_kvmarkup
from kivy_mpbe_widgets.wg_markdown.md_translate import TranslateMarkdownToKVMarkup, Extension
# helpers_mpbe --------------------------------------------------------------
from helpers_mpbe.python import compose_dict, check_list


Builder.load_string('''
<MDTextLabel>
    # Ids Internals Widgets ---------------
    markup: True
    size_hint_y: None
    halign: 'left'
    valign: 'center'
    color: (0,0,0,1)
    font_size: 16
    text_size: (self.size[0], None)
    height: self.texture_size[1] if self.texture_size[1] > 0 else self.font_size+4
    # on_text:
    #     self.texture_update()
    #     self.height = self.texture_size[1]

    # # SACAR CUANDO TODO FUNCIONE
    # canvas.before:
    #     Color:
    #         rgba: 0.8, 0.6, 0.8, 1  # RGB + Alpha (transparencia)
    #     Rectangle:
    #         pos: self.pos
    #         size: self.size



<MDRowLabel@Label>
    # Ids Internals Widgets ---------------
    markup: True
    size_hint_y: None
    halign: 'left'
    valign: 'bottom'
    color: (0,0,0,1)
    font_size: 16
    text_size: (self.size[0], None)
    height: self.texture_size[1] if self.texture_size[1] > 0 else self.font_size+4
    # on_text:
    #     self.texture_update()
    #     self.height = self.texture_size[1]

    # # SACAR CUANDO TODO FUNCIONE
    # canvas.before:
    #     Color:
    #         rgba: 0.8, 0.6, 0.8, 1  # RGB + Alpha (transparencia)
    #     Rectangle:
    #         pos: self.pos
    #         size: self.size


<MDSeparatorLabel>:
    size_hint_y: None
    height: 12
    canvas.before:
        # # SACAR CUANDO TODO FUNCIONE
        # Color:
        #     rgba: 0.8, 0.8, 0.2, 1  # RGB + Alpha (transparencia)
        # Rectangle:
        #     pos: self.pos
        #     size: self.size
    
    
        # Dibuja el Sepatardor
        Color:
            rgba: 0.5, 0.5, 0.5, 1
        Rectangle:
            size: (self.width, 3)
            pos: (self.x, self.y+6)


<MDTable@GridLayout>:
    size_hint_y: None
''')


class BaseMDLabel(EventDispatcher):
    """Clase base para las etiquetas de tipos Markdown
    **Attributes:**
        -
    **Properties:**
        - md_text (str): Texto en formato Markdown
    **Methods:**
        - update(): Funcion abstracta para definir la actualizacion de la etiqueta en la clases hijas
        - on_md_text(...): Evento que se genera cuando se modifica el texto de md_text
    """
    md_text = StringProperty()  # Markdown Text

    def __init__(self, **kwargs):
        """Constructor de la clase
        **Parameters:**

        **Keyword arguments:**
            md_text (str): Texto en formato Markdown
            extension (Extension): Extension Markdown a KVMarkup
            extensions (list(Extension)): Lista de extensiones Markdown a KVMarkup
        """
        self.md_text = compose_dict(kwargs, 'md_text', str, '', False)
        EventDispatcher.__init__(self)
        extension = compose_dict(kwargs, 'extension', Extension, None, acept_none=True)
        extensions = compose_dict(kwargs, 'extensions', list, None, acept_none=True)
        if extensions:
            check_list(extensions, Extension, False)
        self._translate = TranslateMarkdownToKVMarkup(extension=extension, extensions=extensions)

    def update(self):
        '''Se aplica en el documento linea a linea'''
        raise NotImplementedError("Should have implemented update()")

    # def get_height(self):
    #     '''devuelvel al altura actualizada del widget'''
    #     raise NotImplementedError("Should have implemented get_height()")

    def on_md_text(self, instance, value):
        '''Actualiza el label'''
        self.md_text = value
        instance.update()


class MDTextLabel(Label, BaseMDLabel):  # Widget que representa una linea de texto
    """Etiqueta para mostrar texto general en formato markdown
    **Attributes:**
        -
    **Properties:**
        - md_text (str): Texto en formato Markdown
    **Methods:**
        - update(): Funcion abstracta para definir la actualizacion de la etiqueta en la clases hijas
        - on_md_text(...): Evento que se genera cuando se modifica el texto de md_text
    """
    def __init__(self, **kwargs):
        """Constructor
        **Parameters:**

        **Keyword arguments:**
            md_text (str): Texto en formato Markdown
            extension (Extension): Extension Markdown a KVMarkup
            extensions (list(Extension)): Lista de extensiones Markdown a KVMarkup
        """
        Label.__init__(self, **kwargs)
        BaseMDLabel.__init__(self, **kwargs)
        self.update()

    def update(self):
        self.text = self._translate.translate(self.md_text)


class MDSeparatorLabel(Widget, BaseMDLabel):
    """Etiqueta para mostrar el separador del formato markdown
    **Attributes:**
        -
    **Properties:**
        - md_text (str): Texto en formato Markdown
    **Methods:**
        - update(): Funcion abstracta para definir la actualizacion de la etiqueta en la clases hijas
        - on_md_text(...): Evento que se genera cuando se modifica el texto de md_text
    """
    def __init__(self, **kwargs):
        BaseMDLabel.__init__(self, **kwargs)
        Widget.__init__(self, **kwargs)

    def update(self):
        pass


class MDHeadLabel(Label, BaseMDLabel):  # Resaltar fondo.
    """Etiqueta para mostrar el encabezado del formato markdown
    **Attributes:**
        -
    **Properties:**
        - md_text (str): Texto en formato Markdown
    **Methods:**
        - update(): Funcion abstracta para definir la actualizacion de la etiqueta en la clases hijas
        - on_md_text(...): Evento que se genera cuando se modifica el texto de md_text
    """
    pass


class MDTaskLabel(MDTextLabel):
    """Etiqueta para mostrar un item de tarea del formato markdown
    **Attributes:**
        -
    **Properties:**
        - md_text (str): Texto en formato Markdown
    **Methods:**
        - update(): Funcion abstracta para definir la actualizacion de la etiqueta en la clases hijas
        - on_md_text(...): Evento que se genera cuando se modifica el texto de md_text
    """
    pass


class MDToDoLabel(MDTextLabel):
    """Etiqueta para mostrar un item de lista por hacer del formato markdown
    **Attributes:**
        -
    **Properties:**
        - md_text (str): Texto en formato Markdown
    **Methods:**
        - update(): Funcion abstracta para definir la actualizacion de la etiqueta en la clases hijas
        - on_md_text(...): Evento que se genera cuando se modifica el texto de md_text
    """
    pass


class MDTableLabel(GridLayout, BaseMDLabel):
    """Etiqueta para mostrar tablas del formato markdown
    **Attributes:**
        -
    **Properties:**
        - md_text (str): Texto en formato Markdown
    **Methods:**
        - update(): Funcion abstracta para definir la actualizacion de la etiqueta en la clases hijas
        - on_md_text(...): Evento que se genera cuando se modifica el texto de md_text
    """
    def __init__(self, html_table="|a|b|c|"):
        # Convertir una tabla HTML en un GridLayout de Kivy

        # Definir la cantidad de columnas
        if html_table.startswith('|'):
            self.cols = len(re.findall(r'\|', html_table[0]))-1
        else:
            raise TypeError('Tables must begin with the | character.')
        # Actualiza la altura minima en funcion de la altura
        self.bind(minimum_height=self.setter('height'))
        # Extraer filas y celdas usando expresiones regulares
        rows = re.findall(r'<tr>(.*?)</tr>', html_table, re.DOTALL)
        for row in rows:
            cells = re.findall(r'<t[dh]>(.*?)</t[dh]>', row, re.DOTALL)
            for cell in cells:
                label = Label(text=cell.strip(), markup=True, size_hint_y=None, height=30)
                self.add_widget(label)


class MDImageLabel(MDTextLabel):
    """Etiqueta para mostrar imagenes del formato markdown
    **Attributes:**
        -
    **Properties:**
        - md_text (str): Texto en formato Markdown
    **Methods:**
        - update(): Funcion abstracta para definir la actualizacion de la etiqueta en la clases hijas
        - on_md_text(...): Evento que se genera cuando se modifica el texto de md_text
    """
    pass


class MDCodeLabel(MDTaskLabel):
    """Etiqueta para mostrar código de programación en formato markdown
    **Attributes:**
        -
    **Properties:**
        - md_text (str): Texto en formato Markdown
    **Methods:**
        - update(): Funcion abstracta para definir la actualizacion de la etiqueta en la clases hijas
        - on_md_text(...): Evento que se genera cuando se modifica el texto de md_text
    """
    pass
