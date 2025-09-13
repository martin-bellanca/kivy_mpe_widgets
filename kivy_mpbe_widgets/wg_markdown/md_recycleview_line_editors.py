#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_recycleview_line_editors.py
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
Created on 03/09/2025
@author: mpbe
'''

# imports del sistema -------------------------------------------------------
from enum import Enum
from statistics import linear_regression

# helpers_mpbe --------------------------------------------------------------
from helpers_mpbe.python import compose_dict, compose, check_list
from helpers_mpbe.markdown_document.md_labels import BaseMDLabel,MDTextLabel, MDTableLabel, MDSeparatorLabel
from helpers_mpbe.markdown_document.md_labels import MDCodeLabel, MDHeadLabel, MDToDoLabel, MDTaskLabel, MDImageLabel
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
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
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.properties import BooleanProperty, StringProperty, OptionProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.wg_undo.undo_manager import UndoManager, Command
from kivy_mpbe_widgets.base_widgets import FrameUnfocused, FrameFocused
from kivy_mpbe_widgets.wg_markdown.md_doc_line_widgets import *
from helpers_mpbe.markdown_document.md_document import MDDocument
from helpers_mpbe.markdown_document import MD_LINE_TYPE
from helpers_mpbe.markdown_document.md_document import MDLine
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import BaseItem, BaseDataDic
from kivy_mpbe_widgets.events.recycle_view_events import SelectItemEventDispatcher, UnSelectItemEventDispatcher
from kivy_mpbe_widgets.events.recycle_view_events import ActivateItemEventDispatcher, UnActivateItemEventDispatcher
from kivy_mpbe_widgets.graphics.widget_graphics import GFace, GBorder, GFocus, GHotLight

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



class DocLineDataDic(BaseDataDic, MDLine):

    def __init__(self, id, md_line, selected=False, start_anim=False, show_number_line=True, show_tree=False,
                 show_infobar=False, cursor=(-1, -1), state_background=False):
        """Devuelve el diccionario de MDDocumentEditor
        **Dict Parameters:**
            id (int): No usar. Tomar el id de md_line.num_linea que se actualiza en forma automática
            md_line (MDLine): Clase que guarda la información de la linea
            selected (bool): Indica si el item esta seleccionado
            start_anim (bool): Indica si se anima la seleccion o des-selección
            show_id (bool): Muestra el numero de lineas
            show_tree (bool): Muestra el arbol
            show_infobar (bool): Muestra la barra de información
            state_background (bool): Indica si se sombrea el fondo. Es para el pintado intercalado.
        """
        BaseDataDic.__init__(self, None, selected, start_anim, state_background)
        self._md_line = md_line
        self._show_number_line = show_number_line
        self._show_tree = show_tree
        self._show_infobar = show_infobar
        self._cursor = cursor

    def to_dict(self):
        """Devuelve el diccionario de MDDocumentEditor
        **Dict Parameters:**
            index (int): De class BaseDic. Indica la posicion del item en la lista.
            MDLine: Clase que maneja la linea en formato markdown
            active (bool): Indica si el item esta activo
            selected (bool): De class BaseDic. Indica si el item esta seleccionado
            mode_editor (bool): De class BaseDic. Indica si esta en modo edicion
            
            cursor (list): Define la posicion del cursor para la animacion
            start_anim (bool): De class BaseDic. Indica si se anima la seleccion o des-selección
            state_background (bool): De class BaseDic. Indica si se sombrea el fondo. Es para el pintado intercalado.

            show_number_line (bool): Muestra el numero de lineas
            show_tree (bool): Muestra el arbol
            show_infobar (bool): Muestra la barra de información
        """
        return BaseDataDic.to_dict(self) | {'md_line': self._md_line,
                                            'active': False, 'selected': self.selected, 'mode_editor':False,
                                            'cursor':self._cursor, 'start_anim':False, 'state_background':self._state_background,
                                            'show_number_line': self._show_number_line,
                                            'show_tree': self._show_tree, 'show_infobar': self._show_infobar}


class MDDocumentLineEditor_prueba(BaseItem):
    line = ObjectProperty(baseclass=MDLine, defaultvalue=MDLine(md_text='', prev_line=None, next_line=None))
    num_line = NumericProperty(defaultvalue=0)  # Numero de la linea en la lista
    hidden_line = BooleanProperty(defaultvalue=False)  # Indica si el renglon no es visible en el arbol (nodo padre cerrado)
    hotlight = BooleanProperty(defaultvalue=False)  # indica la linea que tiene el cursor ensima
    focused = BooleanProperty(defaultvalue=False)  # indica si la linea en modo render es linea actual para edición

    def __init__(self):
        """
        Keyword arguments:
            show_number_line (bool): muestra el numero de linea
            show_tree_hook (bool): muestra el arbol del documento
            show_info_bar (bool): muestra la barra de informacion
        """
        super().__init__()
        # colors -----------------------------------------
        self._hotlight_color = self.theme.colors['hotlight_border']
        self._focused_color = self.theme.colors['focus_border']
        # line -------------------------------------------
        self.md_line = MDLine(md_text="", prev_line=None, next_line=None)
        # Layout -----------------------------------------
        self._layout = BoxLayout(orientation="horizontal")
        self.add_widget(self._layout)
        # Drag Hook --------------------------------------
        self.wg_drag_hook = MDDLDrag()
        self.wg_drag_hook.height = 30
        self._layout.add_widget(self.wg_drag_hook)
        # Number Line ------------------------------------
        self.wg_number_line = None

        self.lbl = Label(text="PRUEBA")
        self.lbl.height = 30
        self._layout.add_widget(self.lbl)



        # Actualiza la Altura ----------------------------
        self.height = 30

        # Eventos ----------------------------------------
        # self.wg_line_editor.bind(mode_editor=self.on_mode_editor)
        # if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
        #     Window.bind(mouse_pos=self.on_mouse_move)
        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)


    # Private Functions ----------------------------------------
    def _on_update_geometry(self, instance, value):
        self._layout.pos = self.pos
        self._layout.size = self.size

    def _update_height(self):
        self.height = 16
        # if self.wg_line_editor:
        #     self.height = self.wg_line_editor.height
        #     self.wg_drag_hook.height = self.wg_line_editor.height
        #     if self.wg_number_line:
        #         self.wg_number_line.height = self.wg_line_editor.height
        #     if self.wg_tree_hook:
        #         self.wg_tree_hook.height = self.wg_line_editor.height
        #     if self.wg_info_bar:
        #         self.wg_info_bar.height = self.wg_line_editor.height
        #     self.wg_space.height = self.wg_line_editor.height
        # else:
        #     self.height = 16


        # Funciones de RecycleDataViewBehavior -------------------------------------
        def refresh_view_attrs(self, rv, index, data):
            ''' Catch and handle the view changes - se ejecuta cuando hay un cambio en data'''
            # Asigna el md_line ---------------------------------
            # if 'md_line' in data:
            #     self.md_line = data['md_line']
            #     self.md_line.bind(md_text=self.on_line_md_text, type=self.on_line_type)
            #     self.wg_line_editor.line = self.md_line
            # if 'show_number_line' in data:
            #     self.show_number_line(data['id'], data['show_number_line'])
            # if 'show_tree' in data:
            #     self.show_tree_hook(data['show_tree'])
            # if 'show_infobar' in data:
            #     self.show_info_bar(data['show_infobar'])
            return super(MDDocumentLineEditor, self).refresh_view_attrs(rv, index, data)


class MDDocumentLineEditor(BaseItem):
    line = ObjectProperty(baseclass=MDLine, defaultvalue=MDLine(md_text='', prev_line=None, next_line=None))
    num_line = NumericProperty(defaultvalue=0)  # Numero de la linea en la lista
    hidden_line = BooleanProperty(defaultvalue=False)  # Indica si el renglon no es visible en el arbol (nodo padre cerrado)
    hotlight = BooleanProperty(defaultvalue=False)  # indica la linea que tiene el cursor ensima
    focused = BooleanProperty(defaultvalue=False)  # indica si la linea en modo render es linea actual para edición

    def __init__(self):
        """
        Keyword arguments:
            show_number_line (bool): muestra el numero de linea
            show_tree_hook (bool): muestra el arbol del documento
            show_info_bar (bool): muestra la barra de informacion
        """
        super().__init__()

        # BoxLayout.__init__(self, orientation='horizontal')
        # ThemableBehavior.__init__(self)
        # colors -----------------------------------------
        self._hotlight_color = self.theme.colors['hotlight_border']
        self._focused_color = self.theme.colors['focus_border']
        # Layout principal -------------------------------
        self._layout = BoxLayout(orientation="horizontal")
        self.add_widget(self._layout)
        # line -------------------------------------------
        self.md_line = MDLine(md_text="", prev_line=None, next_line=None)
        # Espacio ----------------------------------------
        self.wg_space = MDDLSpace()
        self._layout.add_widget(self.wg_space)
        # Drag Hook --------------------------------------
        self.wg_drag_hook = MDDLDrag()
        self._layout.add_widget(self.wg_drag_hook)
        # Number Line ------------------------------------
        self.wg_number_line = None
        # Tree Hook --------------------------------------
        self.wg_tree_hook = None
        # Info Bar ---------------------------------------
        self.wg_info_bar = None
        # # Espacio ----------------------------------------
        # self.wg_space = MDDLSpace()
        # self._layout.add_widget(self.wg_space)
        # Line Editor ------------------------------------
        self.wg_line_editor = MDLineEditor(line=self.md_line, non_focus=True)
        self._layout.add_widget(self.wg_line_editor)
        self.wg_line_editor.bind(size=self.on_resize_self)
        # Actualiza la Altura ----------------------------
        self._update_height()
        # Eventos ----------------------------------------
        self.wg_line_editor.bind(mode_editor=self.on_mode_editor)
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)
        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)

    # Properties -----------------------------------------------

    def _set_md_text(self, md_text):
        '''
        Notas:
            -self.line y self.active_label se actualizan de on_txt_change de self.md_editor
        '''
        # print('MDDocumentLineEditor->on_line')
        self.md_line.md_text = md_text
        # self.md_editor.text = md_text
        # self.active_label.md_text = md_text
        # self.line.md_text = md_text
    def _get_md_text(self):
        return self.md_line.md_text
    md_text = property(_get_md_text, _set_md_text)

    def _set_type(self, type):
        self.md_line.type = type
    def _get_type(self):
        return self.md_line.type
    type = property(_get_type, _set_type)

    def _set_mode_editor(self, value:bool):
        self.wg_line_editor.mode_editor = value
    def _get_mode_editor(self)-> bool:
        return self.wg_line_editor.mode_editor
    mode_editor = property(_get_mode_editor, _set_mode_editor)

    # Private Functions ----------------------------------------
    def _on_update_geometry(self, instance, value):
        self._layout.pos = self.pos
        self._layout.size = self.size

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

    def show_number_line(self, value: bool, num_line: int):
        if value: # Asigna
            if not self.wg_number_line: # Muestra
                # Numero de Linea -------------------
                self.wg_number_line = MDDLNumberLine()  # text=f"{self.num_line:04d}"
                self._layout.add_widget(self.wg_number_line, index=1)
                # Espacio ---------------------------
                self.wg_space_number_line = MDDLSpace()
                self._layout.add_widget(self.wg_space_number_line, index=1)
            self.num_line = num_line
        else:
            self._layout.remove_widget(self.wg_number_line)
            self._layout.remove_widget(self.wg_space_number_line)
            self.wg_number_line = None

        # if value and not self.wg_number_line:  # muestra
        #     self.num_line = num_line
        #     print(f"MDDocumentLineEditor.show_number_line({value}, {num_line})-> {self.md_line.num_line}: {self.md_line.md_text}")
        #     self.wg_number_line = MDDLNumberLine(text=f"{self.num_line:04d}")
        #     self._layout.add_widget(self.wg_number_line, index=1)
        # elif not value and self.wg_number_line:  # oculta
        #     self._layout.remove_widget(self.wg_number_line)
        #     self.wg_number_line = None

    def show_tree_hook(self, value: bool):
        if value and not self.wg_tree_hook:  # muestra
            self.wg_tree_hook = MDDLTree_hook()
            self._layout.add_widget(self.wg_tree_hook, index=2)
        elif not value and self.wg_tree_hook:  # oculta
            self._layout.remove_widget(self.wg_tree_hook)
            self.wg_tree_hook = None

    def show_info_bar(self, value: bool):
        if value and not self.wg_info_bar:  # muestra
            self.wg_info_bar = MDDLInfoBar()
            self._layout.add_widget(self.wg_info_bar, index=2)
        elif not value and self.wg_info_bar:  # oculta
            self._layout.remove_widget(self.wg_info_bar)
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

    # Funciones de RecycleDataViewBehavior -------------------------------------
    def refresh_view_attrs(self, rv, index, data):
        '''
        Catch and handle the view changes - se ejecuta cuando hay un cambio en data
        **Parameters:**
            rv (RecycleView): Clase derivada de RecycleView
            index (int): Indice del item
            data (dictionary): Diccionario con la informacion del item
                **Keys:**
                'selected' (bool): Define si el item esta seleccionado
                'start_anim' (bool): Indica si debe animar la seleccion a des-seleccion del item
                'active' (bool): Indica si el item esta activo.
                'mode_editor': Indica si esta en modo edicion.
                'md_line' (MDLine): Clase que guarda la linea a mostrar
                'cursor_col' (int): Ubicación del cursor
                'show_number_line' (bool): Indica si se muestra el numero de linea
                'show_tree' (bool): Indica si se muestran los botones de arbol
                'show_infobar' (bool): Indica si se muestra la barra de información

        '''
        # print(f"MDDocumentLineEditor.refresh_view_attrs()-> {self.md_line.num_line}: {self.md_line.md_text}")
        # Asigna el md_line ---------------------------------
        if 'md_line' in data:
            self.md_line = data['md_line']
            self.md_line.bind(md_text=self.on_line_md_text, type=self.on_line_type)
            self.wg_line_editor.line = self.md_line
            # if 'show_number_line' in data:
            self.show_number_line(data['show_number_line'], self.md_line.num_line)

        if 'active' in data:
            self.mode_editor = data['mode_editor']
            # print (f"   Cursor= {data['cursor']}")
            self.wg_line_editor.md_editor.cursor = data['cursor']
        else:
            self.mode_editor = False
        if 'show_tree' in data:
            self.show_tree_hook(data['show_tree'])
        if 'show_infobar' in data:
            self.show_info_bar(data['show_infobar'])
        # if 'start_anim' in data and data['start_anim']:  # ejecuta la animacion
        #     touch_pos = (self.x+10, self.y+self.height/2)
        #     if data['selected']:
        #         print('    Anima seleccion')
        #         self.graphic_select.animate_select(True, touch_pos)
        #     else:
        #         print('    Anima des-seleccion')
        #         self.graphic_select.animate_select(False, touch_pos)


        return super(MDDocumentLineEditor, self).refresh_view_attrs(rv, index, data)
