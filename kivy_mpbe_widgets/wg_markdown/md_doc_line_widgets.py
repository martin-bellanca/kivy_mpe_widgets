#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_editors.py
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
Created on 04/08/2024
@author: mpbe
'''

# imports del sistema -------------------------------------------------------
from enum import Enum
# helpers_mpbe --------------------------------------------------------------
from helpers_mpbe.python import compose_dict, compose, check_list
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window, WindowBase
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import BooleanProperty, StringProperty, OptionProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import FrameUnfocused, FrameFocused
from kivy_mpbe_widgets.wg_markdown.md_document import MDDocument
from kivy_mpbe_widgets.wg_markdown import MD_LINE_TYPE
from kivy_mpbe_widgets.wg_markdown.md_inputs import MDLineTextInput
from kivy_mpbe_widgets.wg_markdown.md_labels import MDTextLabel, MDTableLabel, MDSeparatorLabel
from kivy_mpbe_widgets.wg_markdown.md_labels import BaseMDLabel, MDCodeLabel, MDHeadLabel, MDToDoLabel, MDTaskLabel, MDImageLabel
from kivy_mpbe_widgets.wg_markdown.md_document import MDLine
# from kivy_dkw.wg_markdown.render_markdown_to_widgets import render_line_markdown_to_widget

# Define el archivo KV en un string
kv = """
<MDLineEditor>:
    size_hint_y: None
    # height: md_label.font_size+8

    # canvas.before:
    #     Color:
    #         rgba: 0.1, 0.6, 0.8, 1  # RGB + Alpha (transparencia)
    #     Rectangle:
    #         pos: self.pos
    #         size: self.size


<MDDLDrag>:
    size_hint_x: None
    width: 10
    size_hint_y: None
    canvas.before:
        # Dibuja el borde
        Color:
            rgba: 0, 0, 0, 1  # Color Negro
        Line:
            width: 1  # Grosor del borde
            rectangle: self.x, self.y, self.width, self.height
        # Dibuja el Centro
        Color:
            rgba: 0.5, 0.5, 0.5, 1
        Rectangle:
            size: (self.width-6, self.height-6)
            pos: (self.x+3, self.y+3)


<MDDLNumberLine>
    size_hint_x: None
    width: 38
    size_hint_y: None
    color: 0, 0, 0, 1
    canvas.before:
        # # Dibuja el Centro
        # Color:
        #     rgba: 0.5, 0.5, 0.5, 1
        # Rectangle:
        #     size: self.size
        #     pos: self.pos

        # Dibuja el borde
        Color:
            rgba: 0, 0, 0, 1  # Color Negro
        # Línea en el borde izquierdo
        Line:
            width: 1
            points: self.x, self.y, self.x, self.top  # Desde el fondo hasta la parte superior en el borde izquierdo

        # Línea en el borde derecho
        Line:
            points: self.right, self.y, self.right, self.top  # Desde el fondo hasta la parte superior en el borde derecho
           
    
        
<MDDLTree_hook>
    size_hint_x: None
    width: 16
    size_hint_y: None
    canvas.before:
        # # Dibuja el Centro
        # Color:
        #     rgba: 0.5, 0.5, 0.5, 1
        # Rectangle:
        #     size: self.size
        #     pos: self.pos

        # Dibuja el borde
        Color:
            rgba: 0, 0, 0, 1  # Color Negro
        # Línea en el borde izquierdo
        Line:
            width: 1
            points: self.x, self.y, self.x, self.top  # Desde el fondo hasta la parte superior en el borde izquierdo

        # Línea en el borde derecho
        Line:
            points: self.right, self.y, self.right, self.top  # Desde el fondo hasta la parte superior en el borde derecho
            
        # Line:
        #     width: 1  # Grosor del borde
        #     rectangle: self.x, self.y, self.width, self.height


<MDDLInfoBar>
    size_hint_x: None
    width: 80
    size_hint_y: None
    canvas.before:
        # # Dibuja el Centro
        # Color:
        #     rgba: 0.5, 0.5, 0.5, 1
        # Rectangle:
        #     size: self.size
        #     pos: self.pos

        # Dibuja el borde
        Color:
            rgba: 0, 0, 0, 1  # Color Negro
        Line:
            width: 1  # Grosor del borde
            rectangle: self.x, self.y, self.width, self.height


<MDDLSpace>
    size_hint_x: None
    width: 6
    size_hint_y: None

"""
Builder.load_string(kv)



class MDLineEditor(FloatLayout):
    """Widget que muestra una linea de Markdown. Esta formada de varios widgets:
        - Un espacio para Drag and Drop -> MDDLDrag
        - El numero de linea -> MDDLNumberLine
        - El arbol del documento -> MDDLTree_hook
        - Un separador -> MDDLSpace
        - La etiqueta que representa la linea de texto Markdown renderizada -> Clase derivada de BaseMDLabel
    **Attributes:**
        active_label (Clase derivada de BaseMDLabel): Guarda la etiqueta actual
    **Properties:**
        mode_editor (BooleanProperty): Indica si la linea esta en modo edicion
        line (MDLine): Clase que manipula la linea de texto markdown
        md_text (str): Texto en formato markdown
        type (MD_LINE_TYPE): Guarda el tipo de linea actual [TEXT, SEPARATOR, TABLE, ...]
    **Methods:**
        update_type(): Actualiza el tipo de linea [type]
    **Events:**

        """
    mode_editor = BooleanProperty(defaultvalue=False)
    line = ObjectProperty(baseclass=MDLine, defaultvalue=MDLine(md_text='', prev_line=None, next_line=None))
    # TODO: cambiar nombre a md_line

    # md_text = StringProperty(defaultvalue="**Texto en Negrita**")


    def __init__(self, **kwargs):
        """Constructor
        **Parameters:**

        **Keyword arguments:**
            - non_focus (bool): indica si la linea puede recibir el foco
            - line (MDLine): Clase que manipula la linea de texto markdown
        """
        super(MDLineEditor, self).__init__()
        # self.editor_on_return = False
        # Editor de texto -----------------------------------
        self.md_editor = MDLineTextInput(background_color=(0.8, 0.8, 0.8, 0.80),
                                          size_hint_y=None, pos_hint={'x': 0, 'y': 0},
                                          opacity=1)  # , font_size=12
        # self.md_editor.text = self.line.md_text
        # print(self.md_editor.font_size)
        self.md_editor.bind(text=self.on_txt_change)
        non_focus = compose_dict(kwargs, 'non_focus', bool, False)
        if not non_focus:
            self.md_editor.bind(focus=self.on_focus)
        # Label -----------------------------------------------
        self.active_label = None
        Window.bind(on_key_up=self.on_key_up)
        #self.update_type()
        # Asigna md_text --------------------------------------
        self.line = compose_dict(kwargs, 'line', MDLine, False)
        self.line.bind(md_text=self.on_line_md_text)
        self.line.bind(type=self.on_line_type)
        self.md_editor.text = self.line.md_text
        # -------------
        self._mdtext_back = ""

    # Properties -----------------------------------------------
    def _set_md_text(self, md_text):
        self.line.md_text = md_text
    def _get_md_text(self):
        return self.line.md_text
    md_text = property(_get_md_text, _set_md_text)

    def _set_type(self, type):
        self.line.type = type
        self.update_type()
    def _get_type(self):
        return self.line.type
    type = property(_get_type, _set_type)

    # Private Functions ----------------------------------------
    def _md_editor_focus(self):
        self.md_editor.focus = True

    def _update_height(self):
        if self.active_label and self.active_label.height > 0:
            if self.md_editor.height > self.active_label.height:
                self.height = self.md_editor.height
                self.active_label.height = self.height
            else:
                self.height = self.active_label.height
        else:
            self.height = 16  # self.active_label.font_size + 4

    def update_type(self):  # TODO: CODIFICAR
        type = self.line.type
        if isinstance(self.active_label, BaseMDLabel):
            self.remove_widget(self.active_label)
        if type == MD_LINE_TYPE.TEXT:
            self.active_label = MDTextLabel(md_text=self.line.md_text)
        elif MD_LINE_TYPE.TITLE:  # TODO: Codificar widget propio
            self.active_label = MDTextLabel(md_text=self.line.md_text)
        elif type == MD_LINE_TYPE.SEPARATOR:
            self.active_label = MDSeparatorLabel()
        elif type == MD_LINE_TYPE.TABLE:
            self.active_label = MDTableLabel(md_text=self.line.md_text)

        self.active_label.pos_hint = {'x': 0, 'y': 0}
        self.add_widget(self.active_label, index=1)
        self.active_label.bind(size=self.on_resize_self)
        self.md_editor.text = self.line.md_text
        # self._update_height()

    # funtions events ---------------------------------------------------
    def on_resize_self(self, instance, value):
        self._update_height()

    def on_line(self, instance, value):
        self.update_type()
        pass

    def on_line_md_text(self, instance, value):
        self.md_editor.text = value
        self.update_type()

    def on_line_type(self, instance, value):
        self.update_type()

    def on_mode_editor(self, instance, value):
        if value and value == self.mode_editor:
            self.add_widget(self.md_editor)
            Clock.schedule_once(lambda dt: self._md_editor_focus(), 0.15)
            # self.editor_on_return = True
        else:
            self.remove_widget(self.md_editor)

    def on_txt_change(self, instance, value):
        self.active_label.md_text = value
        self.line.md_text = value  # TODO: la funcion on_md_text de MDLine deberia actualizar el tipo

    def on_touch_up(self, touch):
        if touch.button == 'left':
            if self.collide_point(touch.x, touch.y):
                self.mode_editor = True
                self._mdtext_back = self.active_label.md_text
            else:
                self.mode_editor = False
            return False
        # super().on_touch_up(touch)

    def on_key_up(self, window, keycode, scancode):
        # print("MDLineEditor->_on_keyboard_up")
        # Detectar si se presionó la tecla Escape
        if self.mode_editor == True:
            self._mdtext_back = self.active_label.md_text
            if keycode == 27:  # Escape
                self.mode_editor=False
                self.active_label.md_text = self._mdtext_back
                self.line.md_text = self._mdtext_back
                return False  # True Evitar que otros controladores manejen la tecla
        return False  # Permitir que otros controladores manejen la tecla

    def on_focus(self, instance, value):
        # print("MDLineEditor->on_focus")
        if not value:  # Cuando pierde el foco
            self.mode_editor = False
            # return True
        else:  # Cuando gana el foco
            # self.editor_on_return = True
            pass


class MDDLDrag(Widget):
    _widgets_drag = []
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._widgets_drag.append(self.uid)
        self._is_mouseover = False
        Window.bind(mouse_pos=self.on_mouseover)

    def on_mouseover(self, instance, pos):
        # Verificar si el mouse está sobre este widget
        if self.collide_point(*self.to_widget(*pos)) and self.uid in self._widgets_drag:
            self._is_mouseover = True
            Window.set_system_cursor('hand')
        elif self._is_mouseover:
            Window.set_system_cursor('arrow')
            self._is_mouseover = False

    def on_remove(self):
        """Asegurarse de desvincular el evento cuando el widget es destruido."""
        Window.unbind(mouse_pos=self.on_mouseover)
        self._widgets_drag.remove(self.uid)


class MDDLNumberLine(Label):
    pass


class MDDLTree_hook(Widget):
    pass


class MDDLInfoBar(StackLayout):
    pass


class MDDLSpace(Widget):
    pass
