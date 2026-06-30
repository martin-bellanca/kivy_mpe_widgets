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
from kivy_mpbe_widgets.graphics.markdown_graphics import GHotlightItem, GActiveItem, GSelectItem


# from kivy_dkw.wg_markdown.render_markdown_to_widgets import render_line_markdown_to_widget

# Define el archivo KV en un string
kv = """
<MDDocumentLineEditor>:
    size_hint_y: None

    canvas.before:
        # # Fondo base del item
        # Color:
        #     rgba: self._background_color
        # Rectangle:
        #     pos: self.pos
        #     size: self.size
    
        # Rectángulo de seleccion para la animación
        Color:
            rgba: root._selected_color
        Rectangle:
            pos: root.fill_sel_pos
            size: root.fill_sel_size


    canvas.after:
        # Linea de Active Item
        #   dibuja una lina gruesa de marcar en el lado izquierdo
        #   Alternativas:
        #   1- Cambiar el color de la letra del nro de linea y el dibujar el fondo
        #   2- Agregar un widget espcifico que indique la linea activa
        Color:
            rgba: self._active_color if self.active else (1, 1, 1, 0)
        Line:
            width: 4
            points: self.x, self.y, self.x, self.top
        

        # Lineas de Hotlight
        #   dibuja las lineas si 'highlight' es True
        Color:
            rgba: self._hotlight_color if self.hotlight else (1, 1, 1, 0)
        Line:
            width: 1
            points: self.x, self.top-1, self.right, self.top-1
        Line:
            width: 1
            points: self.x, self.y+1, self.right, self.y+1


"""
# Builder.load_string(kv)


contador_refresh = 0
contador_apply = 0

class MDDocumentLineEditor(RecycleDataViewBehavior, ThemeWidget, HotlightEventDispatcher):
    # +- Properties -----------------------------------------------
    # --- de actualizacion de datos
    num_line = NumericProperty(defaultvalue=0)  # Numero de la linea en la lista. VER SI NO USO PROPERTY
    # --- Actualizaciones del widget
    # mode_editor = BooleanProperty(defaultvalue=False)

    # --- de graficas
    # selected = BooleanProperty(defaultvalue=False)
    # activate = BooleanProperty(defaultvalue=False)
    hotlight = BooleanProperty(defaultvalue=False)  # indica la linea que tiene el cursor ensima
    fill_sel_pos = ListProperty([0, 0])
    fill_sel_size = ListProperty([0, 0])
    # +- end Properties -------------------------------------------

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
        self.index = -1
        # --- Variables internas de la clase ------------------ 
        self._touch_pos = (0,0)
        self._state_background = None
        self.old_text_line = None  # Back del texto de la linea
        # --- Variables de estado propio de la clase ----------
        # self._anim_editor = False
        # self._cursor = (1000, 0)
        # --- Variables de Data Item --------------------------
        # self.index = -1
        self.md_line = MDLine(md_text="", prev_line=None, next_line=None)
        self.di_themed = DataThemed
        self.di_show = DataShow()
        self.di_state = DataState()
        # # --- colors -----------------------------------------
        # self._hotlight_color = self.theme.colors['hotlight_border']
        # self._selected_color = self.theme.colors['pressed_face']
        # self._selected_color[3] = 0.6  # define alfa color
        # self._active_color = self.theme.colors['focus_border']
        # self._active_color[3] = 1.0  # define alfa color
        # --- Eventos ------------------------------------------
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)

        
        # - Construccion del Widget -------------------------------------------------------
        self.size_hint_y = None
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
        with self.canvas.after:
            self.graphic_active = GActiveItem(self)
            self.graphic_hotlight = GHotlightItem(self)
            

        # --- Eventos ----------------------------------------
        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)

    # +- Widget Update Functions --------------------------------------------------------
    def _on_update_geometry(self, instance, value):
        self._layout.pos = self.pos
        self._layout.size = self.size
        self.graphic_hotlight.update_graphics()
        self.graphic_select.update_graphics()
        self.graphic_active.update_graphics()

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

    
    # +- Show sub widgets Functions -----------------------------------------------------
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




    # +- Eventos de MDLineEditor --------------------------------------------------------
    def on_num_line(self, instance, value):
        self.num_line = value
        if self.wg_number_line:
            self.wg_number_line.text = f"{value:04d}"

    # +- Properties ---------------------------------------------------------------------
    # +--- md_text ------------------------------
    def _set_md_text(self, md_text):
        '''
        Notas:
            -self.line y self.active_label se actualizan de on_txt_change de self.md_editor
        '''
        # print('MDDocumentLineEditor->on_line')
        # self.md_line.md_text = md_text
        self.wg_line_editor.md_text = md_text
        # self.active_label.md_text = md_text
        # self.line.md_text = md_text
    def _get_md_text(self):
        return self.md_line.md_text
    md_text = property(_get_md_text, _set_md_text)

    # +--- md_line type  ------------------------
    def _set_line_type(self, type):
        self.md_line.type = type
    def _get_line_type(self):
        return self.md_line.type
    line_type = property(_get_line_type, _set_line_type)

    # +--- cursor_pos type  ------------------------
    def _set_cursor_pos(self, value:tuple):
        self.wg_line_editor.md_editor.cursor = value
    def _get_cursor_pos(self):
        return self.wg_line_editor.md_editor.cursor  #.editor_cursor_pos
    editor_cursor_pos = property(_get_cursor_pos, _set_cursor_pos)


    # +- Funciones del Editor -----------------------------------------------------------
    # def on_mode_editor(self, instance, value:bool):
    #     # print(">- MDDocumentLineEditor.on_mode_editor()")
    #     if self.di_state.editable:
    #         self.show_editor(value)


    # +- Funciones de visualización -----------------------------------------------------
    def show_editor(self, show:bool, anim:bool, cursor:tuple=None):
        """Muestra o esconde el editor el editor"""
        
        # HACER SEGUIMIENTO DESDE ACA
        
        self.di_state.mode_editor = show
        if anim is True:
            self.wg_line_editor.show_anim_editor(show, cursor)
        else:
            self.wg_line_editor.show_editor(show, cursor)

    def select(self, value:bool, anim:bool, anim_type:str='fade'):
        """Seleciona o des-seleciona el view"""
        self.di_state.selected = value
        if anim is True:  # seleccion animada
            if anim_type == 'up':
                self.graphic_select.animate_up(value)
            elif anim_type == 'down':
                self.graphic_select.animate_down(value)
            else:
                self.graphic_select.animate_fade(value)
        else:
            self.graphic_select.show(value)

    def activate(self, value:bool, show_editor:bool=False, cursor:tuple=None, anim:bool=True, anim_type:str='fade'):
        """Activa o Desactiva el view (anima la visualización)"""
        # print(f"Activate, index={self.index}, value{value}, show_editor={show_editor}, anim={anim}")
        
        # Selecciona --------------------------------------
        self.select(value, anim, anim_type)
        # Modo Edicion ------------------------------------
        self.show_editor(show_editor, anim, cursor)
        # Activacion --------------------------------------
        self.di_state.active = value
        if anim is True:
            self.graphic_active.animate(value)
        else:
            self.graphic_active.show(value)
        # TODO: Cambiar el color del nro de la linea al activar?'
    

    # +- Funciones de RecycleDataViewBehavior ------------------------------------- 
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

        # global contador_refresh
        # contador_refresh += 1
        # print(f"MDDocumentLineEditor.refresh_view_attrs()-> {self.md_line.num_line}: {self.md_line.md_text}, {contador_refresh}")
        
        self.index = index
        # Asigna el md_line ------------------------------------
        self.md_line = data.get('md_line')
        self.wg_line_editor.line = self.md_line

        # + Theme ------------------------------------------------
        self.di_themed = data.get('themed')

        # + Show -------------------------------------------------
        self.di_show = data.get('show')
        self.show_number_line(self.di_show.number_line, self.md_line.num_line)
        self.show_tree_hook(self.di_show.tree)
        self.show_info_bar(self.di_show.infobar)

        # + State ------------------------------------------------
        self.di_state = data.get('state')    
        self.mode_editor = self.di_state.mode_editor
        self.graphic_select.show(self.di_state.selected)
        self.graphic_active.show(self.di_state.active)

        # + Actualiza el view ------------------------------------
        if self.di_state.active is not True:
            self.wg_line_editor.show_editor(False)
        else:
            self.wg_line_editor.show_editor(True, cursor=None)  # self._cursor

        return super(MDDocumentLineEditor, self).refresh_view_attrs(rv, index, data)
    

    # +- Eventos del Widget -------------------------------------------------------
    def on_mouse_move(self, instance, mp):
        hla = self.collide_point_to_window(*mp)
        # print(f"+- GHotlightItem.on_mouse_move(): active:{self._active} collide {hla} widget: {self._widget.md_line.num_line}")
        if self.di_state.active != hla and not self.disabled and self.level_render == self.theme.level_render:
            self.graphic_hotlight.animate(hla)  # Ejecuta la animacion
            self.di_state.active = hla  # Asigna el nuevo valor al data
            if self.parent:
                self.parent.parent.handle_hotlight_event(index=self.index, view=self, active=hla)

    def on_touch_down(self, touch):
        # print(f'>- MDDocumentLineEditor.on_touch_down, index={self.index}, collide_point={self.collide_point(*(self.to_window(*touch.pos)))}')
        # print(f'>--- Line= {self.md_line.md_text}')
        # TODO: Para seleccion multiple, agregar aca la deteccion de shit presionado
        if self.collide_point(*(self.to_window(*touch.pos))):
            touch.grab(self)  # Marca este touch como manejado por este widget
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):  # Hay que ver como con data y data_items. Deberia tener actualizada la informacion de selccion en los dos
        # print(f'>- MDDocumentLineEditor.on_touch_up {self.uid}')
        if touch.grab_current is self:  # Verifica si este widget "grabó" el evento touch
            # +-- SE PRESIONO EL BOTON IZQUIERDO ----------------------------------------------------------------------
            if touch.button == 'left' and self.parent:  #  Seleccion y Des-seleccion de los items (Boton Izquierdo)
                # print('>--- RecycleListView.on_touch_down Boton Izquierdo --------------------------')
                # print(f'>---- Item a Seleccionar: index={self.index}, linea={self.md_line.md_text}')
                self.parent.parent.handle_touch_left_up_event(index=self.index, view=self, touch=touch)  # Llama al manejador de RecycleView
                
                print(f"active={self.di_state.active}, editable={self.di_state.editable} ")

                self.di_state.active = True
                cursor = self.wg_line_editor.md_editor.get_cursor_from_xy(*self.to_local(*touch.pos))  # Obtiene la posicion del cursor
                self.activate(value=True, show_editor=True, cursor=cursor, anim=True, anim_type='fade')  # Activa el view actual
                return True
            touch.ungrab(self)



