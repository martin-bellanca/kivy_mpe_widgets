#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_recycleview_editors.py
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
Created on 24/03/2025
@author: mpbe
'''

# imports del sistema -------------------------------------------------------
from enum import Enum
from statistics import linear_regression

# helpers_mpbe --------------------------------------------------------------
from helpers_mpbe.python import compose_dict, compose, check_list
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
from kivy_mpbe_widgets.base_widgets import FrameUnfocused, FrameFocused
from kivy_mpbe_widgets.wg_markdown.md_doc_line_widgets import *
from kivy_mpbe_widgets.wg_markdown.md_document import MDDocument
from kivy_mpbe_widgets.wg_markdown import MD_LINE_TYPE
from kivy_mpbe_widgets.wg_markdown.md_labels import MDTextLabel, MDTableLabel, MDSeparatorLabel
from kivy_mpbe_widgets.wg_markdown.md_labels import BaseMDLabel, MDCodeLabel, MDHeadLabel, MDToDoLabel, MDTaskLabel, \
    MDImageLabel
from kivy_mpbe_widgets.wg_markdown.md_document import MDLine
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import BaseItem, BaseDataDic
from kivy_mpbe_widgets.events.recycle_view_events import SelectItemEventDispatcher, UnSelectItemEventDispatcher
from kivy_mpbe_widgets.events.recycle_view_events import ActivateItemEventDispatcher, UnActivateItemEventDispatcher
from kivy_mpbe_widgets.graphics.widget_graphics import GFace, GBorder, GFocus, GHotLight

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


<MDDocumentEditor>:
    SelectableRecycleBoxLayout:
        id: srblayout
        default_size: None, dp(30)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: False
        touch_multiselect: False"""
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
            id (int): De class BaseDic. Nro. de linea
            selected (bool): De class BaseDic. Indica si el item esta seleccionado
            state_background (bool): De class BaseDic. Indica si se sombrea el fondo. Es para el pintado intercalado.

            show_id (bool): Muestra el numero de lineas
            show_tree (bool): Muestra el arbol
            show_infobar (bool): Muestra la barra de información
            MDLine: Clase que maneja la linea en formato markdown
        """
        return BaseDataDic.to_dict(self) | {'md_line': self._md_line, 'active': False, 'selected': False,
                                            'cursor':self._cursor, 'start_anim':False, 'mode_editor':False,
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


class SelectableRecycleBoxLayout(LayoutSelectionBehavior, RecycleBoxLayout):  # FocusBehavior
    ''' Adds selection and focus behavior to the view. '''


class MDDocumentEditor(FocusBehavior, ThemableBehavior, RecycleView,
                       ActivateItemEventDispatcher, UnActivateItemEventDispatcher,
                       SelectItemEventDispatcher, UnSelectItemEventDispatcher):
    instance_focus = None

    def __init__(self, activate_background=True, **kwargs):
        FocusBehavior.__init__(self)
        ThemableBehavior.__init__(self)
        RecycleView.__init__(self)
        # FrameFocused.__init__(self, hotlight=False)
        ActivateItemEventDispatcher.__init__(self)
        UnActivateItemEventDispatcher.__init__(self)
        SelectItemEventDispatcher.__init__(self)
        UnSelectItemEventDispatcher.__init__(self)

        # self.focused = True
        self.initialize_document()
        # self._select_unselect = sel_unsel  # Define si al hacer click sobre un item seleccionado este se des selecciona
        # self.multiselect = mutilselect  # Permite la multiseleccion de items
        self.activate_background = activate_background  # Activa el cambio de tonalidad en el fondo de los items
        self.on_scroll_event = None  # Referencia al evento de scroll para el item en edicion
        self.layout = self.ids.srblayout
        # print(f'RecycleListView.__init__->is_focuseable = {self.is_focusable}')
        with self.canvas.after:
            if not self.flat: self.graphic_border = GBorder(self)
            self.graphic_focus = GFocus(self)

        Window.bind(on_key_down=self._on_keyboard_up)
        # Window.bind(on_key_down=self._on_keyboard_down)

    def initialize_document(self):
        'Inicializa el documento'
        self._md_lines = None
        self._item_hotlight = None
        self._selected_indexs = []  # Item actual seleccionado
        self._active_index = -1
        self._cursor = (1000, -1)  # es una tupla (columna, fila)
        self._mode_editor = False
        # Altura del layout de items
        # Nota: Hay que mantenerla actualizada con el agregado, borrado y cambio de tamañano del item en edicion
        # self.layout_height = 0

    ''' Funciones de la Interfaz -------------------------------'''
    def populate_from_md_lines(self, md_lines):
        self.initialize_document()
        self._md_lines = md_lines
        self.data = []
        for id, mdl in enumerate(md_lines, start=1):
            data_line = DocLineDataDic(id=None, md_line=mdl)  # no uso el id del data. Uso md_line.num_line que se auto-actualiza
            dic_line = data_line.to_dict()
            self.data.append(dic_line)
        # self.doc_editor.refresh_from_data()
        # self.update_layout_height()  NO ANDA

    def on_hotlight_item(self, item, state):
        if state:
            self._item_hotlight = item

    def on_focus(self, instance, value):
        # print(f'MDDocumentEditor._on_focus {self.uid}-{value}')
        if value == False and MDDocumentEditor.instance_focus == instance:
            # print("    Focus False")
            MDDocumentEditor.instance_focus == None
        elif value == True:
            # print("    Focus True")
            MDDocumentEditor.instance_focus = instance
        return True

    # def update_layout_height(self):
    #     # bk_sc = self.scroll_y
    #     # self.scroll_y = 1
    #     # # self.activate_from_index(0)
    #     # self.layout_height = self.layout_manager.height
    #     # self.scroll_y = bk_sc
    #
    #     self.layout_height = 0
    #     for ditem in self.data:
    #         widget = self.viewclass()
    #         widget.refresh_view_attrs(self, ditem['l_id']-1, ditem)
    #         # widget.wg_line_editor.height
    #
    #         widget.wg_line_editor.update_type()
    #         widget.wg_line_editor._update_height()
    #
    #         widget.wg_line_editor.active_label.texture_update()
    #         print(f'wg_h= {widget.wg_line_editor.active_label.texture_size}')
    #         altura = widget.wg_line_editor.texture_size[1] + widget._layout.padding[0] + self.layout_manager.spacing
    #         self.layout_height += altura


    '''Funciones generales de data y item ---------------------------------------'''
    # def scroll_to_item(self, item, position='center'):  NO ANDA POR QUE ly_height ESTA MAL Y NO HAY FORMA FACIL DE CALCULARLO
    #     ''' Scrolls the RecycleView to bring the item at 'index' into view.
    #         'position' can be 'top', 'center', or 'bottom'.
    #     '''
    #     # index = item.index
    #     # layout = self.layout_manager
    #
    #     # if not layout or index is None or not (0 <= index < len(self.data)):
    #     #     return
    #
    #     # item_pos = self.item_scroll_pos_y(item)
    #
    #     layout = self.layout_manager
    #     ly_height = layout.height
    #     rv_height = self.height
    #     delta_1 = ly_height - rv_height
    #     delta_it = self.y - self.item_scroll_pos_y(item)   # self.y = 0
    #
    #     # RecycleBoxLayout.default_height
    #
    #     if position == 'bottom':
    #         new_scroll = 1 - delta_it / delta_1
    #         self.scroll_y = new_scroll
    #
    #     print('MDDocument.scroll_to_item()')
    #     print(f'  ly_h= {ly_height}, rv_h= {rv_height}')
    #     print(f'  item.y= {item.y}')
    #     print(f'  item.y= {self.item_scroll_pos_y(item)}, View y= {self.y}')
    #     print(f'  delta_1= {delta_1}, delta_it= {delta_it}')
    #     print(f'  new_scroll= {new_scroll}')

    def index_from_data(self, data):  # EX data_index
        return self.data.index(data)

    def item_from_index(self, index, auto_scroll=True):
        item = None
        for it in self.layout.children:
            if it.index == index:
                item = it
                break
        return item

    def active_md_editor(self):
        item = self.item_from_index(self._active_index)
        if item:
            return item.wg_line_editor.md_editor if self._active_index > -1 else None
        else:
            None

    ''' Funciones Edicion de Lineas --------------------------------------------'''
    def append_line(self, md_text):
        '''Agrega una linea'''
        index = len(self._md_lines)-1
        # md_line
        md_line = MDLine(md_text=md_text,
                         prev_line=self._md_lines[index], next_line=None,
                         type=MD_LINE_TYPE.TEXT, num_line=index+2)
        self._md_lines[index].next_line = md_line
        self._md_lines.append(md_line)
        # Data
        data_line = DocLineDataDic(index, md_line)
        dic_line = data_line.to_dict()
        self.data.append(dic_line)
        # Actualiza el View
        self.refresh_from_data()
        return md_line

    def insert_line(self, index:int, md_text:str=''):
        """Inserta una linea en el indice indicado"""
        # print('MDDocument.insert_lines() -----------------------')
        # print('  Lineas actuales:')
        # for ii in range (index-2, index+2):
        #     print(f'    {ii}: {self._md_lines[ii].md_text}')

        md_line = MDLine(md_text=md_text,
                         prev_line=self._md_lines[index].prev_line, next_line=self._md_lines[index],
                         type=MD_LINE_TYPE.TEXT, num_line=0)
        # Inserta md_line y ajusta las dependendencias
        self._md_lines.insert(index, md_line)
        # self._md_lines[index - 1].next_line = self._md_lines[index]
        # self._md_lines[index + 1].prev_line = self._md_lines[index]
        md_line.num_line = index + 1
        # print('  Lineas Insertadas:')
        # for ii in range(index - 2, index + 2):
        #     print(f'              previus line: {self._md_lines[ii].prev_line.uid}')
        #     print(f'    {ii}, {self._md_lines[ii].uid}: Num_line= {self._md_lines[ii].num_line},  {self._md_lines[ii].md_text}')
        #     print(f'              next line: {self._md_lines[ii].next_line.uid}')
        #     print( '    ------------------------------------------------------------------------------------------------')

        # Inserta en data
        data_line = DocLineDataDic(index+1, md_line)
        dic_line = data_line.to_dict()
        self.data.insert(index, dic_line)
        # Refresca el View
        self.refresh_from_data()
        return md_line

    def remove_line(self, index:int):
        print('MDDocument.remove_line --------------------------')
        print(f'  Linea a borrar: index={index}, texto={self._md_lines[index].md_text}')

        # Ajusta los indices de los Items Seleccionados
        for ii, value in enumerate(self._selected_indexs, start=0):
            if value > index:
                self._selected_indexs[ii] = value - 1
            print(f'ii={ii}, value={value}, nuevo valor={self._selected_indexs[ii]}')
        # Borrar en _md_lines y ajusta las dependendencias
        del(self._md_lines[index])
        self._md_lines[index].num_line = index + 1
        self._md_lines[index].prev_line = self._md_lines[index-1]
        self._md_lines[index-1].next_line = self._md_lines[index]
        # Borra en el data
        del(self.data[index])
        # Refresca el View

        self.refresh_from_data()

        # print('  Depues de Borrar:')
        # for ii in range(index - 2, index + 2):
        #     print(f'              previus line: {self._md_lines[ii].prev_line.uid}')
        #     print(f'    {ii}, {self._md_lines[ii].uid}: Num_line= {self._md_lines[ii].num_line},  {self._md_lines[ii].md_text}')
        #     print(f'              next line: {self._md_lines[ii].next_line.uid}')
        #     print( '    ------------------------------------------------------------------------------------------------')


    '''Funciones sobre cursor line -------------------------------------------------------'''
    def scroll_to_index(self, index):
        self.scroll_y = 1 - index / len(self.data)

    def item_scroll_pos_y(self, item):
        '''
        Devuelve la coordenada y del item respecto al sistema de coordenadas del RecycleView
        La diferencia de altura del layout - recycle view por el valor de scroll_y que va de 0 a 1 es el coef de paso
        entre el sistema de coordenadas del view y del layout.
        para scrool_y = 0 -> rv_y = ly_y
        para scroll_y = 1 -> rv_y + rv_height = ly_y + ly_heignt
        '''
        if item:
            layout = self.layout
            ly_height = layout.height
            rv_height = self.height
            delta_1 = ly_height - rv_height
            delta = delta_1 * self.scroll_y
            return item.y - delta
        else:
            return 0

    def select_item(self, item, anim=False):  # TODO: cambiar a select_from_item
        # print(f'MDDocumentEditor.select - {item.index} -----------------------')
        self.select_data_item(self.data[item.index], anim)

    def select_index(self, index, anim=False):  # TODO: cambiar a select_from_index
        self.select_data_item(self.data[index], anim)

    def select_data_item(self, data_item, anim=False):  # TODO: cambiar a select_from_data
        '''
        Selecciona la linea. Puede haber varias lineas seleccionadas pero una sola activa
        anim puede ser True, False o una tupla que indica la pos de inicio de la animacion
        '''
        # print(f"MDDocumentEditor.select_data_item(data_item: {data_item})")
        data_item['selected'] = True
        data_item['start_anim'] = anim


        self._selected_indexs.append(data_item['md_line'].num_line - 1)

        # print(f'  Lista de Seleccionados{self._selected_indexs}')

        self.refresh_from_data()
        SelectItemEventDispatcher.do_something(self, data_item, data_item['md_line'].num_line - 1)

    def unselect_item(self, item, anim=False):  # TODO: cambiar a unselect_from_item
        # print(f'RecycleListView.unselect - {item.file_name} -------------------')
        self.unselect_data_item(self.data[item.index], anim)

    def unselect_index(self, index, anim=False):  # TODO: cambiar a unselect_from_index
        self.unselect_data_item(self.data[index], anim)

    def unselect_data_item(self, data_item, anim=False):  # TODO: cambiar a unselect_from_data
        # print(f"MDDocumentEditor.unselect_data_item(data_item)")
        data_item['selected'] = False
        data_item['start_anim'] = anim
        self.refresh_from_data()
        # print(f'  Lista de Seleccionados antes{self._selected_indexs}, {data_item["md_line"].num_line - 1}')
        self._selected_indexs.remove(data_item['md_line'].num_line - 1)
        # print(f'  Lista de Seleccionados despues{self._selected_indexs}')

        UnSelectItemEventDispatcher.do_something(self, data_item, data_item['md_line'].num_line - 1)

    def activate_from_item(self, item, cursor_pos=None, anim=False):
        self.activate_from_data(self.data[item.index], cursor_pos=cursor_pos, anim=anim)

    def activate_from_index(self, index, cursor_pos=None, anim=False):
        self.activate_from_data(self.data[index], cursor_pos=cursor_pos, anim=anim)

    def activate_from_data(self, data_item, cursor_pos=None, anim=False):
        '''
        Activa la linea, sola una linea puede estar activa. La que puede editarse y tambien esta seleccionada.
        anim puede ser True, False o una tupla que indica la pos de inicio de la animacion
        '''
        print("MDDocumentEditor.activate_from_data(...))")
        data_item['selected'] = True
        data_item['start_anim'] = anim
        data_item['cursor'] = self._cursor if cursor_pos == None else cursor_pos
        data_item['active'] = True
        data_item['mode_editor'] = self._mode_editor
        self._active_index = data_item['md_line'].num_line - 1
        # Agrega el item a la selccion
        if not self._active_index in self._selected_indexs:
            self._selected_indexs.append(self._active_index)
        print(f'  Lista de Seleccionados{self._selected_indexs}')

        self.refresh_from_data()
        ActivateItemEventDispatcher.do_something(self, data_item, self._active_index)

    def unactivate_from_item(self, item, anim=False):
        self.unactivate_from_data(self.data[item.index], anim=anim)

    def unactivate_from_index(self, index, anim=False):
        self.unactivate_from_data(self.data[index], anim=anim)

    def unactivate_from_data(self, data_item, anim=False):
        '''anim puede ser True, False o una tupla que indica la pos de inicio de la animacion'''
        print("MDDocumentEditor.unactivate_from_data(...))")
        sel_item = self.item_from_index(data_item['md_line'].num_line - 1)
        for ix in self._selected_indexs:
            self.data[ix]['selected'] = False
        self._selected_indexs.clear()
        if sel_item:
            # self._cursor = sel_item.wg_line_editor.md_editor.cursor
            # print(f"    En modo edicion: {self._cursor_col}, {self._item_selected.wg_line_editor.cursor_col}")
            data_item['start_anim'] = anim
            data_item['active'] = False
            data_item['mode_editor'] = False
            self.refresh_from_data()
            data_item['start_anim'] = False
            self._active_index = -1
            UnActivateItemEventDispatcher.do_something(self, data_item, data_item['md_line'].num_line - 1)

    def active_to_previus_item(self, cursor_pos=None):
        print("MDDocumentEditor.move_to_previus_item()")
        print(f'  Active Index= {self._active_index}')
        if self._active_index > 0:
            item_prev = self.item_from_index(self._active_index)
            index = self._active_index - 1 if self._active_index > 0 else 0
            # print(f'  active index= {self._active_index}')
            self.unactivate_from_index(self._active_index, anim=True)
            # print(f'  active index= {self._active_index}, despues de unactivate')
            # Actualiza la vista para que el nuevo item este visible
            item = self.item_from_index(index)
            if item:
                if self.item_scroll_pos_y(item) + item.height > self.y + self.height:  # Mover el item a la base del RecycleView
                    self.scroll_y += item.height / (self.layout_manager.height - self.height)
            else:
                print(f'    Scroll por index= {(index +0.5) / len(self.data)}')
                self.scroll_y = 1- (index +0.5) / len(self.data)
        else:
            index = len(self.data) - 1
            self.scroll_y = 0
        self.activate_from_index(index, cursor_pos=cursor_pos, anim=True)
        return item

    def active_to_next_item(self, cursor_pos=None):
        print("MDDocumentEditor.move_to_next_item()")
        print(f'  Active Index= {self._active_index}')
        if self._active_index > -1:
            item_prev = self.item_from_index(self._active_index)
            index = self._active_index + 1 if self._active_index < len(self.data) - 1 else len(self.data) - 1
            self.unactivate_from_index(self._active_index, anim=True)
            # Actualiza la vista para que el nuevo item este visible
            if item_prev:
                if self.item_scroll_pos_y(item_prev) - item_prev.height < 0:
                    self.scroll_y -= item_prev.height / (self.layout_manager.height - self.height)
            else:
                self.scroll_y = 1 - (self._active_index + 0.5) / len(self.data)
        else:
            index = 0
            self.scroll_y = 0
        self.activate_from_index(index, cursor_pos=cursor_pos, anim=True)
        return self.item_from_index(index)

    def move_line_to(self, actual_index, new_index):
        '''Mueve la linea de la posicion actual_index a la poscicion new_index'''
        # print('MDDocumentEditor.move_line_to()')
        if new_index > actual_index:  # Mueve hacia arriba
            # print('  Mueve hacia arriba')
            self._md_lines.insert(new_index, self._md_lines.pop(actual_index))  # Mueve MDLine
            self.data.insert(new_index, self.data.pop(actual_index))  # Mueve el data
            # Ajusta la lista de los indices seleccionados
            for ii in range(len(self._selected_indexs)):
                self._selected_indexs[ii] -= 1
            # Ajustar prev y next
            if actual_index > 0:
                self._md_lines[actual_index - 1].next_line = self._md_lines[actual_index]
                self._md_lines[actual_index].prev_line = self._md_lines[actual_index - 1]
            else:
                self._md_lines[actual_index].prev_line = None  #  Para la primer linea
            self._md_lines[new_index-1].next_line = self._md_lines[new_index]
            self._md_lines[new_index].prev_line = self._md_lines[new_index-1]
            if new_index < len(self._md_lines) - 1:
                self._md_lines[new_index].next_line = self._md_lines[new_index + 1]
                self._md_lines[new_index + 1].prev_line = self._md_lines[new_index]
            else:
                self._md_lines[new_index].next_line = None  # Ultima linea
            # Ajusta los nros de linea
            nl = 1 if actual_index == 0 else self._md_lines[actual_index - 1].num_line + 1
            self._md_lines[actual_index].num_line = nl
            # Actualiza el Active Index
            self._active_index -= 1
            # Actualiza el View
            item = self.item_from_index(actual_index)
            if self.item_scroll_pos_y(item) + item.height > self.y + self.height:  # Mover el item a la base del RecycleView
                self.scroll_y += item.height / (self.layout_manager.height - self.height)
            self.refresh_from_data()
        elif new_index < actual_index:  # Mueve hacia abajo
            # print('  Mueve hacia abajo')
            self._md_lines.insert(new_index, self._md_lines.pop(actual_index))  # Mueve MDLine
            self.data.insert(new_index, self.data.pop(actual_index))  # Mueve el data
            # Ajusta la lista de los indices seleccionados
            for ii in range(len(self._selected_indexs)):
                self._selected_indexs[ii] += 1
            # Ajustar prev y next
            if new_index > 0:
                self._md_lines[new_index - 1].next_line = self._md_lines[new_index]
                self._md_lines[new_index].prev_line = self._md_lines[new_index - 1]
            else:
                self._md_lines[new_index].prev_line = None  # Primera Linea
            self._md_lines[new_index].next_line = self._md_lines[new_index + 1]
            self._md_lines[new_index + 1].prev_line = self._md_lines[new_index]

            if actual_index < len(self._md_lines) - 1:
                self._md_lines[actual_index].next_line = self._md_lines[actual_index + 1]
                self._md_lines[actual_index + 1].prev_line = self._md_lines[actual_index]
            else:
                self._md_lines[actual_index].next_line = None  # Ultima Linea
            # Ajusta los nros de linea
            self._md_lines[new_index].num_line = self._md_lines[new_index - 1].num_line + 1
            # Actualiza el Active Index
            self._active_index += 1
            # Actualiza el View
            item = self.item_from_index(actual_index)
            if self.item_scroll_pos_y(item) < 0:  # Mover el item a la base del RecycleView
                self.scroll_y -= item.height / (self.layout_manager.height - self.height)
            self.refresh_from_data()

    '''Eventos de Usuario --------------------------------------------------------'''
    def on_touch_down(self, touch):
        # print(f'RecycleListView.on_touch_down')
        if self.collide_point_to_window(*touch.pos):
            # print(f'  Grab')
            touch.grab(self)  # Marca este touch como manejado por este widget
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        # print(f'RecycleListView.on_touch_up {self.uid}, collide_point={self.collide_point(*touch.pos)}')
        if touch.grab_current is self:  # Verifica si este widget "grabó" el evento touch
            # print('   Con Grab')
            for item in self.layout.children:  # busca el item sobre el que se hizo el touch
                if item.collide_point_to_window(*touch.pos):
                    break
            data = self.data[item.index]
            # print(f'presion sobre el item {item.id}, {item.index}, {data}')
            if touch.button == 'left':  #  Seleccion y Des-seleccion de los items (Boton Izquierdo)
                # print('  RecycleListView.on_touch_down Boton Izquierdo')
                data_us = self.data[self._active_index]
                # TODO: Verificar si esta presionado SHIFT o CTRL y seleccionar el rango
                if self._active_index != item.index:
                    # print(f'  RecycleListView.on_touch_down UNSELECT ++++++++++++++++++++++++++++')
                    if self._active_index > -1:
                        self.unactivate_from_index(self._active_index, anim=True)
                    # print(f'  RecycleListView.on_touch_down SELECT {self._select_index} y {item.index}')
                self._mode_editor = True
                cursor = item.wg_line_editor.md_editor.get_cursor_from_xy(*self.to_local(*touch.pos))
                self.activate_from_item(item, cursor)
                touch.ungrab(self)
                return True
                # self.refresh_from_data()  # no hace falta por que actualizo en select_item y unselect_item

            elif touch.button == 'right':  # Modo Edicion (Boton Derecho)
                # print('Boton Derecho')
                # item.start_editing(self, data)
                pass
            elif touch.button in ['scrollup', 'scrolldown']:
                # print('RecycleListView.on_touch_down->Rueda del mouse')
                # item = self.item_from_index(self._active_index)
                # if item != None:
                #     item.stop_editing(self, data)
                touch.ungrab(self)
                return False
            # print("  ungrab")
            touch.ungrab(self)  # Libera el touch
            return False
        super(RecycleView, self).on_touch_up(touch)

    def on_scroll_move(self, touch):
        # print('RecycleListView.on_scroll_move->Rueda del mouse')
        super().on_scroll_move(touch)
        if self.on_scroll_event:
            self.on_scroll_event(self)  # Disparar el evento de scroll sobre el item en edicion

    # def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
    #     print("MDDocumentEditor->_on_keyboard_down Codigo de Teclas", keycode, modifier, char, special_keys)


    def _on_keyboard_up(self, window, keycode, modifier, char, special_keys):
        print("MDDocumentEditor._on_keyboard_up Codigo de Teclas", keycode, modifier, char, special_keys)
        # print(f'  default_h= {self.layout.default_height}, layout= {self.layout}')
        # print(f'  ul item.y= {item.y}')
        # print(f'  h Layout= {self.layout.height}, h layout manager= {self.layout_manager.height}')
        # print(f'   UID:{self.uid}')
        if MDDocumentEditor.instance_focus == self and self.theme.level_render != 'high':
            # print(f'    Instancia con Foco y nivel bajo')
            md_editor = self.active_md_editor()
            active_item = self.item_from_index(self._active_index)
            in_edition = active_item.mode_editor if active_item else False
            self._cursor = md_editor.cursor if md_editor else (0, 0)  # self.item_from_index(self._active_index).wg_line_editor.md_editor.cursor
            if keycode == 273 and all(kk in special_keys for kk in ['shift', 'ctrl']):  # Mueve el bloque hacia arriba
                print('  Flecha Arriba con Ctrl y Shift (mueve el bloque hacia arriba)')
                # Se supone que la lista es continua sin seleccion intercalada.
                # En este contecto borro la lines superior a la seleccion y la pego debajo de la seleccion
                ix_actual = min(self._selected_indexs) - 1
                ix_new = max(self._selected_indexs)
                if ix_actual > -1:
                    self.move_line_to(ix_actual, ix_new)
            elif keycode == 274 and all(kk in special_keys for kk in ['shift', 'ctrl']):  # Mueve el bloque hacia abajo
                print('  Flecha Abajo con Ctrl y Shift (mueve el bloque hacia abajo)')
                # Se supone que la lista es continua sin seleccion intercalada.
                # En este contecto borro la lines inferior a la seleccion y la pego sobre la seleccion
                ix_new = min(self._selected_indexs)
                ix_actual = max(self._selected_indexs) + 1
                if ix_actual < len(self.data):
                    self.move_line_to(ix_actual, ix_new)
            elif char == 'c' and 'ctrl' in special_keys:  # Ctrl + C, Copiar
                # print(f'texto seleccionado: {md_editor.selection_text}')
                # Crea el texto a copiar
                if not in_edition or len(md_editor.selection_text) == 0:
                    cp_txt = ''
                    for ii in range(0, len(self._selected_indexs)-1):
                        cp_txt += self._md_lines[self._selected_indexs[ii]].md_text + '\n'
                    cp_txt += self._md_lines[self._selected_indexs[len(self._selected_indexs)-1]].md_text
                    Clipboard.copy(cp_txt)
                    return True
                else:
                    return False
            elif char == 'v' and 'ctrl' in special_keys:  # Ctrl + V, Pegar
                # print('  Ctrl + v')
                pasted_text = Clipboard.paste()
                if isinstance(pasted_text, str):  # Verifica compatibilidad del texto
                    pasted_list = pasted_text.splitlines(keepends=False)
                    print(f'  Lista de lineas: {pasted_list}')
                    # Define el punto de inserción
                    u_line = len(self._md_lines)
                    if not in_edition or len(pasted_list) > 1:
                        ix_i = self._active_index + 1 if self._active_index > -1 and self._active_index < u_line else u_line
                        print(f'    ix_i= {ix_i}, u line= {u_line}')
                        # Inserta las lineas
                        for id, txt in enumerate(pasted_list, start=0):
                            if ix_i < u_line:
                                self.insert_line(ix_i+id, txt)
                            else:
                                self.append_line(txt)
                        return True
                    else:
                        return False
            elif char == 'x' and 'ctrl' in special_keys:  # Ctrl + X, Cortar
                # Corta la seleccion
                print('  Ctrl + x')
                # Crea el texto a copiar
                if not in_edition or len(md_editor.selection_text) == 0:
                    cp_txt = ''
                    for ii in range(0, len(self._selected_indexs) - 1):
                        cp_txt += self._md_lines[self._selected_indexs[ii]].md_text + '\n'
                        self.remove_line(self._selected_indexs[ii])
                    cp_txt += self._md_lines[self._selected_indexs[len(self._selected_indexs) - 1]].md_text
                    self.remove_line(self._selected_indexs[len(self._selected_indexs) - 1])
                    Clipboard.copy(cp_txt)
                    return True
                else:
                    return False
            elif keycode == 273 and 'shift' in special_keys and self._active_index != 0:  # Selecciona la linea de arriba
                print('  Flecha Arriba con Shift (selecciona la linea de arriba)')
                # Inhabilita el modo edicion
                self.data[self._active_index]['mode_editor'] = False  # Inhabilita el modo edicion
                self.data[self._active_index]['start_anim'] = False  # Desactiva la animacion
                self._active_index -= 1  # Mueve el item activado
                # Agrega o borra de la lista de seleccionados
                if self._active_index in self._selected_indexs:  # Des-selecciona
                    print('    Deselecciona')
                    self.unselect_index(self._active_index+1, anim=False)
                else:
                    self.select_index(self._active_index, anim=False)
                    item = self.item_from_index(self._active_index)
                    if self.item_scroll_pos_y(item) + item.height > self.y + self.height:  # Mover el item a la base del RecycleView
                        self.scroll_y += item.height / (self.layout_manager.height - self.height)
            elif keycode == 274 and 'shift' in special_keys and self._active_index != len(self.data)-1:  # Selecciona la linea de abajo
                print('  Flecha Abajo con Shift (selecciona la linea de abajo)')
                self.data[self._active_index]['mode_editor'] = False  # Inhabilita el modo edicion
                self.data[self._active_index]['start_anim'] = False  # Desactiva la animacion
                self._active_index += 1  # Mueve el item activado
                # Agrega o borra de la lista de seleccionados
                if self._active_index in self._selected_indexs:  # Des-selecciona
                    print('    Deselecciona')
                    self.unselect_index(self._active_index-1, anim=False)
                else:
                    self.select_index(self._active_index, anim=False)
                    item = self.item_from_index(self._active_index)
                    if self.item_scroll_pos_y(item) < 0:  # Mover el item a la base del RecycleView
                        self.scroll_y -= item.height / (self.layout_manager.height - self.height)
            elif keycode == 273 and self._active_index != 0:  # Flecha Arriba
                print(f'  Flecha Arriba')
                # TODO: Verificar si esta presionado SHIFT o CTRL y seleccionar el rango
                self.active_to_previus_item()
            elif keycode == 274 and self._active_index != len(self.data)-1:  # Flecha Abajo
                print("    Flecha Abajo")
                # TODO: Verificar si esta presionado SHIFT o CTRL y seleccionar el rango
                self.active_to_next_item()
            if keycode == 275 and self._active_index != len(self.data)-1 and self._cursor[0] == len(md_editor.text):  # Flecha Derecha
                print('  Flecha Derecha')
                self.active_to_next_item(cursor_pos=(0, 0))
            if keycode == 276 and self._active_index != 0 and self._cursor[0] == 0:  # Flecha Izquierda
                print(f'  Flecha izquierda, active index= {self._active_index}')
                cur_x = len(self.data[self._active_index-1]['md_line'].md_text)
                self.active_to_previus_item(cursor_pos=(cur_x, 0))
            elif keycode == 283:  # Tecla F2
                self._mode_editor =not(self._mode_editor)
                self.data[self._active_index] ['mode_editor'] = self._mode_editor
                self.data[self._active_index]['cursor'] = self._cursor
                self.data[self._active_index]['start_anim'] = False
                self.refresh_from_data()
                return False
            elif keycode == 27:  # Tecla Escape
                self._mode_editor =False
            # print(f'    cursor= {self._cursor}, {self.item_from_index(self._active_index).wg_line_editor.md_editor.cursor}')
            elif keycode == 13 or keycode == 271:  # Tecla Enter o Intro
                print('  Tecla Enter')
                l_text = md_editor.text[0:self._cursor[0]]
                r_text = md_editor.text[self._cursor[0]:len(md_editor.text)]
                print(f'    cursor= {self._cursor}, {md_editor.cursor}')
                print(f'    l_text= {l_text}, r_text= {r_text}')
                # insertar linea
                md_editor.text = l_text
                self.insert_line(index=self._active_index+1, md_text=r_text)
                ai = self._active_index
                self.unactivate_from_index(index=ai, anim=True)
                self.activate_from_index(index=ai+1, cursor_pos=(0,0), anim=True)
            elif keycode == 8 and self._active_index != 0 and self._cursor[0] == 0: # Tecla Backspace
                print('  Tecla Backspace -> Fusiona la linea con la linea de arriba')
                text = md_editor.text
                print(f'    text: {text}')
                self.remove_line(self._active_index)
                cpos = len(self._md_lines[self._active_index-1].md_text)
                self._md_lines[self._active_index -1].md_text += text
                self.activate_from_index(self._active_index-1, cursor_pos=(cpos, 0))
            elif keycode == 127 and self._active_index != len(self.data)-1 and self._cursor[0] == len(md_editor.text) \
                    and len(self._selected_indexs) == 1:  # Tecla Suprimir en modo edicion
                print('  Tecla Suprimir -> Fusiona la linea con la linea de abajo')
                cur_pos = len(self._md_lines[self._active_index].md_text)
                self._md_lines[self._active_index].md_text += self._md_lines[self._active_index+1].md_text  # agrega el texto de la linea inferior
                self.data[self._active_index]['cursor'] = (cur_pos, 0)  # Posiciona el cursor
                self.remove_line(self._active_index+1)  # borra la linea de abajo
                self.data[self._active_index+1]['md_line'].num_line = self.data[self._active_index]['md_line'].num_line + 1  # actualiza nro linea, prev y next
            elif keycode == 127 and len(self._selected_indexs) > 0 and not in_edition:
                for ix in self._selected_indexs:
                    self.remove_line(ix)
                self.refresh_from_data()
            elif keycode == 280:  # tecla page up
                print('  Tecla PageUp')
                delta = len(self.layout.children) - 2
                new_center_ix = self.layout.children[int(delta / 2)].index - delta   #este hay que sacarlo
                if new_center_ix > 0:
                    self.scroll_y += self.height / (self.layout_manager.height - self.height)
                else:
                    self.scroll_y = 1
            elif keycode == 281:  # tecla page down
                # print('  Tecla PageDown')
                delta = len(self.layout.children) - 2
                new_center_ix = self.layout.children[int(len(self.layout.children)/2)].index + delta
                if new_center_ix < len(self.data):
                    self.scroll_y -= self.height / (self.layout_manager.height - self.height)
                else:
                    self.scroll_y = 0
            return False
        pass


