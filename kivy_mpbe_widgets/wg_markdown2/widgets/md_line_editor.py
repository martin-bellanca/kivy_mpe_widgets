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
from kivy_mpbe_widgets.wg_markdown2.widgets.md_line_widgets import *
from helpers_mpbe.markdown_document.md_document import MDDocument
from helpers_mpbe.markdown_document import MD_LINE_TYPE
from kivy_mpbe_widgets.wg_markdown2.widgets.md_line_widgets import MDTextLabel, MDTableLabel, MDSeparatorLabel
from helpers_mpbe.markdown_document.md_document import MDLine
# from kivy_dkw.wg_markdown.render_markdown_to_widgets import render_line_markdown_to_widget

# Define el archivo KV en un string
kv = """
<MDDocumentLineEditor>:
    size_hint_y: None
    
    canvas:
        # Dibuja lineas si 'highlight' es True, dibujar la línea superior
        Color:
            rgba: self._hotlight_color if self.hotlight else (1, 1, 1, 0)  # Fondo verde si tiene foco
        Line:
            width: 1
            points: self.x, self.top-1, self.right, self.top-1
        Line:
            width: 1
            points: self.x, self.y+1, self.right, self.y+1
    
        # Dibuja lineas si 'focused' es True, dibujar la línea superior
        Color:
            rgba: self._focused_color if self.focused else (1, 1, 1, 0)  # Fondo verde si tiene foco
        Line:
            width: 1
            points: self.x, self.top, self.right, self.top
        Line:
            width: 1
            points: self.x, self.y, self.right, self.y
    
"""
Builder.load_string(kv)



# AGREGAR VARIABLE PARA INDICAR FOCO QUE PUEDA MOVERSE CON FLECHAS Y TAB FUERA DE EDICION (hightlight)
class MDDocumentLineEditor(BoxLayout, ThemableBehavior):
    line = ObjectProperty(baseclass=MDLine, defaultvalue=MDLine(md_text='', prev_line=None, next_line=None))
    num_line = NumericProperty(defaultvalue=0)  # Numero de la linea en la lista
    hidden_line = BooleanProperty(defaultvalue=False)  # Indica si el renglon no es visible en el arbol (nodo padre cerrado)
    hotlight = BooleanProperty(defaultvalue=False)  # indica la linea que tiene el cursor ensima
    focused = BooleanProperty(defaultvalue=False)  # indica si la linea en modo render es linea actual para edición

    def __init__(self, mdline, **kwargs):
        """
        Keyword arguments:
            show_number_line (bool): muestra el numero de linea
            show_tree_hook (bool): muestra el arbol del documento
            show_info_bar (bool): muestra la barra de informacion
        """


        BoxLayout.__init__(self, orientation='horizontal')
        ThemableBehavior.__init__(self)
        # colors -----------------------------------------
        self._hotlight_color = self.theme.colors['hotlight_border']
        self._focused_color = self.theme.colors['focus_border']
        # line -------------------------------------------
        self.line = compose(mdline, MDLine, False)
        self.line.bind(md_text=self.on_line_md_text)
        self.line.bind(type=self.on_line_type)
        # Drag Hook --------------------------------------
        self.wg_drag_hook = MDDLDrag()
        self.add_widget(self.wg_drag_hook)
        # Number Line ------------------------------------
        sw = compose_dict(kwargs, 'show_number_line', bool, True)
        nl = compose_dict(kwargs, 'num_line', int, 0)
        if sw:
            self.wg_number_line = MDDLNumberLine(text=f"{nl:04d}")
            self.add_widget(self.wg_number_line)
            self.num_line = nl
        else:
            self.wg_number_line = None
        # Tree Hook --------------------------------------
        sw = compose_dict(kwargs, 'show_tree_hook', bool, False)
        if sw:
            self.wg_tree_hook = MDDLTree_hook()
            self.add_widget(self.wg_tree_hook)
        else:
            self.wg_tree_hook = None
        # Info Bar ---------------------------------------
        sw = compose_dict(kwargs, 'show_info_bar', bool, False)
        if sw:
            self.wg_info_bar = MDDLInfoBar()
            self.add_widget(self.wg_info_bar)
        else:
            self.wg_info_bar = None
        # Espacio ----------------------------------------
        self.wg_space = MDDLSpace()
        self.add_widget(self.wg_space)
        # Line Editor ------------------------------------
        self.wg_line_editor = MDLineEditor(line=self.line, non_focus=True)
        self.add_widget(self.wg_line_editor)
        self.wg_line_editor.bind(size=self.on_resize_self)
        # Actualiza la Altura ----------------------------
        self._update_height()
        # Eventos ----------------------------------------
        self.wg_line_editor.bind(mode_editor=self.on_mode_editor)
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)

    # Properties -----------------------------------------------
    def _set_md_text(self, md_text):
        '''
        Notas:
            -self.line y self.active_label se actualizan de on_txt_change de self.md_editor
        '''
        # print('MDDocumentLineEditor->on_line')
        self.line.md_text = md_text
        # self.md_editor.text = md_text
        # self.active_label.md_text = md_text
        # self.line.md_text = md_text
    def _get_md_text(self):
        return self.line.md_text
    md_text = property(_get_md_text, _set_md_text)

    def _set_type(self, type):
        self.line.type = type
    def _get_type(self):
        return self.line.type
    type = property(_get_type, _set_type)

    def _set_mode_editor(self, value):
        self.wg_line_editor.mode_editor = value
    def _get_mode_editor(self):
        return self.wg_line_editor.mode_editor
    mode_editor = property(_get_mode_editor, _set_mode_editor)

    # Private Functions ----------------------------------------
    def _update_height(self):
        if self.wg_line_editor:
            self.height = self.wg_line_editor.height
            self.wg_drag_hook.height = self.wg_line_editor.height
            if self.wg_number_line:
                self.wg_number_line.height = self.wg_line_editor.height
            if self.wg_tree_hook:
                self.wg_tree_hook.height = self.wg_line_editor.height
            if self.wg_info_bar:
                self.wg_info_bar.height = self.wg_line_editor.height
            self.wg_space.height = self.wg_line_editor.height
        else:
            self.height = 16

    # Public Funtions ------------------------------------------
    def collide_point(self, x, y):  # on windows coordinates
        try:
            # Check the position of the point
            # bpx, bpy = self.to_window(self.pos[0], self.pos[1], True)
            bpx, bpy = self.to_window(self.pos[0], self.pos[1], True)
            bwidth, bheight = self.size
            # Direction X
            bpw = bpx + bwidth
            inx = True if bpx <= x <= bpw else False
            # Direction Y
            bph = bpy + bheight
            iny = True if bpy <= y <= bph else False
            # Collide
            return inx and iny
        except:
            return False

    def show_number_line(self, value:bool, number:int):
        if value and not self.wg_number_line:  # muestra
            self.wg_number_line = MDDLNumberLine(text=f"{self.num_line:04d}")
            self.add_widget(self.wg_number_line, index=1)
        elif not value and self.wg_number_line:  # oculta
            self.remove_widget(self.wg_number_line)
            self.wg_number_line = None

    def show_tree_hook(self, value: bool):
        if value and not self.wg_tree_hook:  # muestra
            self.wg_tree_hook = MDDLTree_hook()
            self.add_widget(self.wg_tree_hook, index=2)
        elif not value and self.wg_tree_hook:  # oculta
            self.remove_widget(self.wg_tree_hook)
            self.wg_tree_hook = None

    def show_info_bar(self, value: bool):
        if value and not self.wg_info_bar:  # muestra
            self.wg_info_bar = MDDLInfoBar()
            self.add_widget(self.wg_info_bar, index=2)
        elif not value and self.wg_info_bar:  # oculta
            self.remove_widget(self.wg_info_bar)
            self.wg_info_bar = None

    # Funtions events ---------------------------------------------------
    def on_resize_self(self, instance, value):
        self._update_height()

    def on_num_line(self, instance, value):
        self.num_line = value
        if self.wg_number_line:
            self.wg_number_line.text = f"{value:04d}"

    def on_line(self, instance, value):
        # print('MDDocumentLineEditor->on_line')
        pass

    def on_line_type(self, instance, value):
        # print('MDDocumentLineEditor->on_line_type')
        pass

    def on_line_md_text(self, instance, value):
        # print('MDDocumentLineEditor->on_line_md_text')
        pass

    def on_mouse_move(self, instance, mp):
        # print("MDDocumentLineEditor->on_mouse_move")
        if self.collide_point(mp[0], mp[1]):
            self.hotlight = True
        else:
            self.hotlight = False

    def on_mode_editor(self, instance, value):
        # print("MDDocumentLineEditor->on_mode_editor")
        if value:
            self.focused = value


