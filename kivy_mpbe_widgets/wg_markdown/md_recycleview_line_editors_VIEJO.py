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
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty, BoundedNumericProperty
from kivy.clock import Clock

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.events.widgets_events import HotlightEventDispatcher, StartAnimEventDispatcher, EndAnimEventDispatcher
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
from kivy_mpbe_widgets.wg_markdown.md_recycleview_le_data_item import DataThemed, DataShow, DataState
from kivy_mpbe_widgets.graphics.markdown_graphics import GHotlightItem, GFocusItem, GSelectItem


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

        # # Dibuja lineas si 'focused' es True, dibujar la línea superior
        # Color:
        #     rgba: self._focused_color if self.focused else (1, 1, 1, 0)  # Fondo verde si tiene foco
        # Line:
        #     width: 1
        #     points: self.x, self.top, self.right, self.top
        # Line:
        #     width: 1
        #     points: self.x, self.y, self.right, self.y
"""
Builder.load_string(kv)


contador_refresh = 0
contador_apply = 0


class MDDocumentLineEditorBACK(BaseItem):
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


class MDDocumentLineEditor(RecycleDataViewBehavior, ThemeWidget, HotlightEventDispatcher):
    # # Properties -----------------------------------------------
    # active = BooleanProperty(False)  # Define si el item esta activo
    # selected = BooleanProperty(False)  # Define si el item esta seleccionado
    # mode_editor = BooleanProperty(False)  # Define si esta en modo edicion
    # state_background = BooleanProperty(False)  # Define si se sombrea el fondo
    # start_anim = BooleanProperty(False)  # Indica si se anima la seleccion o des-selección
    # cursor = ObjectProperty(defaultvalue=(-1, -1))  # Define la posicion del cursor para la animacion
    # show_number_line = BooleanProperty(True)  # Muestra el numero de lineas
    # show_tree = BooleanProperty(True)  # Muestra el arbol
    # show_infobar = BooleanProperty(True)  # Muestra la barra de información
    # state_background = BooleanProperty(False)  # Indica si se sombrea el fondo. Es para el pintado intercalado.
    
    # De BaseItem -----------------
    # selectable = BooleanProperty(True)
    # editable = BooleanProperty(True)  # Define si el item se puede editar
    alpha_background = BoundedNumericProperty(defaultvalue=0.0, min=0.0, max=1.0)
    
    
    
    
    # line = ObjectProperty(baseclass=MDLine, defaultvalue=MDLine(md_text='', prev_line=None, next_line=None))
    # index = NumericProperty(defaultvalue=-1)  # Indice del item en la lista data. Puede no coincidir con num_line si se aplican filtros
    num_line = NumericProperty(defaultvalue=0)  # Numero de la linea en la lista
    # hidden_line = BooleanProperty(defaultvalue=False)  # Indica si el renglon no es visible en el arbol (nodo padre cerrado)
    hotlight = BooleanProperty(defaultvalue=False)  # indica la linea que tiene el cursor ensima
    focused = BooleanProperty(defaultvalue=False)  # indica si la linea en modo render es linea actual para edición
    # Que relacion hay en focused y active? Son lo mismo?

    # Esto hay que definirlo todo por clases a travez de data????

    # # end Properties -------------------------------------------

    def __init__(self):
        """
        Keyword arguments:
            show_number_line (bool): muestra el numero de linea
            show_tree_hook (bool): muestra el arbol del documento
            show_info_bar (bool): muestra la barra de informacion
        """
        # - Call Super Constructors -------------------------------------------------------
        RecycleDataViewBehavior.__init__(self)
        ThemeWidget.__init__(self)
        HotlightEventDispatcher.__init__(self)
        
        # - Definicion de Variables -------------------------------------------------------
        # --- Variables internas de la clase ------------------
        # self._selected = False  # 
        self._touch_pos = (0,0)
        self._state_background = None
        # --- Variables de estado propio de la clase ----------
        self.in_edition = False  # Define si el item esta en modo edicion
        # --- Variables de Data Item --------------------------
        # self.index = -1
        self.md_line = MDLine(md_text="", prev_line=None, next_line=None)
        self.di_themed = DataThemed
        self.di_show = DataShow()
        self.di_state = DataState()
        # --- colors -----------------------------------------
        self._hotlight_color = self.theme.colors['hotlight_border']
        self._focused_color = self.theme.colors['focus_border']
        
        # - Construccion del Widget -------------------------------------------------------
        # --- Layout principal -------------------------------
        self._layout = BoxLayout(orientation="horizontal")
        self.add_widget(self._layout)
        # --- Espacio ----------------------------------------
        self.wg_space = MDDLSpace()
        self._layout.add_widget(self.wg_space)
        # --- Drag Hook --------------------------------------
        self.wg_drag_hook = MDDLDrag()
        self._layout.add_widget(self.wg_drag_hook)
        # --- Number Line ------------------------------------
        self.wg_number_line = None
        # --- Tree Hook --------------------------------------
        self.wg_tree_hook = None
        # --- Info Bar ---------------------------------------
        self.wg_info_bar = None
        # # --- Espacio ----------------------------------------
        # self.wg_space = MDDLSpace()
        # --- self._layout.add_widget(self.wg_space)
        # Line Editor ------------------------------------
        self.wg_line_editor = MDLineEditor(line=self.md_line, non_focus=True)
        self._layout.add_widget(self.wg_line_editor)
        self.wg_line_editor.bind(size=self.on_resize_self)
        # --- Actualiza la Altura ----------------------------
        self._update_height()

        # Canvas -----------------------------------------------------
        with self.canvas.before:
            self.graphic_select = GSelectItem(self)

        # --- Eventos ----------------------------------------
        self.wg_line_editor.bind(mode_editor=self.on_mode_editor)
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)
        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)


    # Widget Functions ----------------------------------------
    def _on_update_geometry(self, instance, value):  # Copiado
        self._layout.pos = self.pos
        self._layout.size = self.size

    def _update_height(self):  # Copiado
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

    def on_resize_self(self, instance, value):
        self._update_height()

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

    def on_mouse_move(self, instance, mp):  # Copiado
        # print("MDDocumentLineEditor->on_mouse_move")
        if self.collide_point(*mp):
            # print("   Hotlight True")
            self.hotlight = True
        else:
            # print("   Hotlight False")
            self.hotlight = False

    # Evento de MDLineEditor ----------------------------------
    def on_mode_editor(self, instance, value):
        # print("MDDocumentLineEditor->on_mode_editor")
        if value:
            self.focused = value

    def on_num_line(self, instance, value):
        self.num_line = value
        if self.wg_number_line:
            self.wg_number_line.text = f"{value:04d}"

    # def on_line_md_text(self, instance, value):
    #     # print('MDDocumentLineEditor->on_line_md_text')
    #     pass

    # def on_line_type(self, instance, value):
    #     # print('MDDocumentLineEditor->on_line_type')
    #     pass

    # Show Functions -------------------------------------------
    def show_number_line(self, value: bool, num_line: int):
        # print("-"*80)
        # print(f"+- MDDocumentLineEditor.show_number_line({num_line})")
        if value: # Asigna
            if not self.wg_number_line: # Muestra
                # Numero de Linea -------------------
                self.wg_number_line = MDDLNumberLine()  # text=f"{self.num_line:04d}"
                self._layout.add_widget(self.wg_number_line, index=1)
                # Espacio ---------------------------
                self.wg_space_number_line = MDDLSpace()
                self._layout.add_widget(self.wg_space_number_line, index=1)
            self.num_line = num_line  # no asigna el nro de la linea
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

    # +- Properties -----------------------------------------------
    # +--- md_text
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

    # +--- type
    def _set_type(self, type):
        self.md_line.type = type
    def _get_type(self):
        return self.md_line.type
    type = property(_get_type, _set_type)

    # +--- mode_editor
    def _set_mode_editor(self, value:bool):
        if self.di_state.editable:
            self.wg_line_editor.mode_editor = value
            self.wg_line_editor.md_editor.cursor = self.di_state.editor_cursor
    def _get_mode_editor(self)-> bool:
        return self.wg_line_editor.mode_editor
    mode_editor = property(_get_mode_editor, _set_mode_editor)





    # Funciones de RecycleDataViewBehavior -------------------------------------
    def apply_selection(self, rv, index, is_selected):    # Nuevo
        global contador_apply
        contador_apply += 1
        print(f"- MDDocumentLineEditor.apply_selection(rv, {index}, {is_selected}, {contador_apply})")
        print("         CAMBIO LA SELECION")
        
        # + Theme ------------------------------------------------
        if self.di_themed.anim:  # ejecuta la animacion
            touch_pos = (self.x+10, self.y+self.height/2)

            # TODO: Hay que agregar el tipo de animacion

            if self.di_state.selected:
                print('    ** Anima seleccion ********************************')
                self.graphic_select.animate_select(True, touch_pos)  
            else:
                print('    ** Anima des-seleccion ****************************')
                self.graphic_select.animate_select(False, touch_pos)
            
            
            # self.di_themed.anim = False  ESTE HACE QUE LA ANIMACION NO SE EJECUTE


        # print(f'   Estado de los data:')
        # for ix, it in enumerate(rv.data):
        #     st = it['state']
        #     print(f"    - index: {ix}, seleccionado: {st.selected}, active: {st.active}")

        else:
            self.graphic_select.show(self.di_state.selected)


        return super(MDDocumentLineEditor, self).apply_selection(rv, index, is_selected)
    
    def refresh_view_attrs(self, rv, index, data):  # REVISAR
        '''
        Catch and handle the view changes - se ejecuta cuando hay un cambio en data
        **Parameters:**
            rv (RecycleView): Clase derivada de RecycleView
            index (int): Indice del item
            data (dictionary): Diccionario con la informacion del item
                **Keys:**
                    md_line (MDLine): Clase que guarda la información de la linea.
                    data_themed (DataThemed): Varialbes relacionadas con el tema guardadas en data.
                    data_show (DataShow): Varialbes relacionadas con la visibilidad guardadas en data.
                    data_state (DataState): Varialbes relacionadas con el estado del item guardadas en data.
        
        **NOTA:** index es el indice de rv.layout.children que es inverso al indice de data.
                    En data la primer linea tiene index 0 y en children es len(data)
        '''
        # print("-"*80)

        global contador_refresh
        contador_refresh += 1
        print(f"MDDocumentLineEditor.refresh_view_attrs()-> {self.md_line.num_line}: {self.md_line.md_text}, {contador_refresh}")
        # Asigna el md_line ------------------------------------
        # if 'md_line' in data:
        #     self.md_line = data['md_line']
        #     # self.md_line.bind(md_text=self.on_line_md_text, type=self.on_line_type)
        #     self.wg_line_editor.line = self.md_line
        self.md_line = data.get('md_line')
        self.wg_line_editor.line = self.md_line



        # + Show -------------------------------------------------
        # self.di_show = data['show']
        self.di_show = data.get('show')
        self.show_number_line(self.di_show.number_line, self.md_line.num_line)
        self.show_tree_hook(self.di_show.tree)
        self.show_info_bar(self.di_show.infobar)

        # + State ------------------------------------------------
        # self.di_state = data['state']
        self.di_state = data.get('state')
        self.focused = self.di_state.focused
        # self.di_state.index = len(rv.data) - index - 1 hay un problema con el valor de index. NO SE POR QUE LO INVIERTE
        # self.selected = self.di_state.selected
        self.mode_editor = self.di_state.mode_editor
        
        
        print(f"   focused:{self.focused}, {self.di_state.focused}")
        print(f"   selected:{self.di_state.selected}")


        # + Theme ------------------------------------------------
        self.di_themed = data.get('themed')


        # print(f'   Estado de los data:')
        # for ix, it in enumerate(rv.data):
        #     st = it['state']
        #     print(f"    - index: {ix}, seleccionado: {st.selected}, active: {st.active}")


        return super(MDDocumentLineEditor, self).refresh_view_attrs(rv, index, data)