#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_recycleview_document_editor.py
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
from helpers_mpbe.markdown_document.md_document import MDDocument
from helpers_mpbe.markdown_document.md_labels import BaseMDLabel, MDTextLabel, MDTableLabel, MDSeparatorLabel
from helpers_mpbe.markdown_document.md_labels import MDCodeLabel, MDHeadLabel, MDToDoLabel, MDTaskLabel, MDImageLabel
from helpers_mpbe.markdown_document.md_document import MDLine
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
from helpers_mpbe.markdown_document import MD_LINE_TYPE
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.wg_undo.undo_manager import UndoManager, Command
from kivy_mpbe_widgets.base_widgets import FrameUnfocused, FrameFocused
from kivy_mpbe_widgets.wg_markdown.md_recycleview_line_editors import MDDocumentLineEditor
from kivy_mpbe_widgets.wg_markdown.md_doc_line_widgets import *
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import BaseItem, BaseDataDic
from kivy_mpbe_widgets.events.recycle_view_events import SelectItemEventDispatcher, UnSelectItemEventDispatcher
from kivy_mpbe_widgets.events.recycle_view_events import ActivateItemEventDispatcher, UnActivateItemEventDispatcher
from kivy_mpbe_widgets.graphics.widget_graphics import GFace, GBorder, GFocus, GHotLight
from kivy_mpbe_widgets.wg_markdown.md_recycleview_le_data_item import DataThemed, DataShow, DataState, DataItemLineMDD

# from kivy_dkw.wg_markdown.render_markdown_to_widgets import render_line_markdown_to_widget

# Define el archivo KV en un string
kv = """
#:import sys sys


<MDDocumentEditor>:
    SelectableRecycleBoxLayout:
        id: srblayout
        default_size: None, dp(30)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        selectable: False
        multiselect: False
        touch_multiselect: False
    """
Builder.load_string(kv)



class SelectableRecycleBoxLayoutViejo(LayoutSelectionBehavior, RecycleBoxLayout):  # FocusBehavior, LayoutSelectionBehavior, 
    ''' Adds selection and focus behavior to the view. '''


class SelectableRecycleBoxLayout(RecycleBoxLayout):  # FocusBehavior, LayoutSelectionBehavior, 
    ''' Adds selection and focus behavior to the view.'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self._active_index = -1

    # # Funciones de Seleccion de Items -----------------------------------------
    # def set_active_item(self, index:int, scroll_to=False):
    #     self._active_index = index
    #     if scroll_to:
    #         self.parent.scroll_to_index(index)
    #     for view in self.children:
    #         view.active = (view.index == index)
    
    # def set_select_item(self, index:int, scroll_to=False):
    #     self._active_index = index
    #     if scroll_to:
    #         self.parent.scroll_to_index(index)
    #     for view in self.children:
    #         view.active = (view.index == index)

    # def add_select_item(self, index:int, scroll_to=False):
    #     self.
    
    # # Manejadores de Eventos de Items Hijos -----------------------------------
    # def handle_hotlight_event(self, index:int, state:bool):
    #     """Se ejecuta desde GHotlightItem cuando se activa o des-activa el hotlight"""
    #     self.hotlight = state

    # def touch_left_up_event(self, index:int, state:bool):
    #     self.set_active_item(index)



    # def animate_range_selection(self, start_index, end_index):
    #     """
    #     Orquesta la animación secuencial para una selección en rango.
    #     Se usa en selcción multiple con el mouse.
    #     """
    #     if not self.multiselect: return
    #     self.clear_selection()
        
    #     start = min(start_index, end_index)
    #     end = max(start_index, end_index)
        
    #     # Determinar dirección para un efecto natural
    #     forward = start_index < end_index
    #     indices = range(start, end + 1) if forward else range(end, start - 1, -1)
        
    #     delay_per_item = 0.03 # Pequeño retraso entre cada item
    #     delay = 0
        
    #     for i in indices:
    #         # Usar Clock para retrasar la animación de cada item
    #         Clock.schedule_once(lambda dt, index=i: self._animate_item_in_range(index), delay)
    #         delay += delay_per_item
    
    # def _animate_item_in_range(self, index):
    #     """ Selecciona y anima un solo item como parte de un rango. """
    #     self.select_node(index)
        # La animación se dispara automáticamente vía apply_selection.


# -----------------------------------------------------------------------------------------------
# --- Funciones para MDDocumentEditor  ----------------------------------------------------------
# -----------------------------------------------------------------------------------------------
class MDDocumentEditorViejo(FocusBehavior, ThemableBehavior, RecycleView,
                       ActivateItemEventDispatcher, UnActivateItemEventDispatcher,
                       SelectItemEventDispatcher, UnSelectItemEventDispatcher):
    """Clase que implementa un editor de documentos markdown basado en RecycleView
    Nota: 
        - Solo puede haber un MDDocumentEditor con foco a la vez.
        - El indice 'Index' de la lista self.data se refiere al indice del item en el data del RecycleView.
        - El indice de la data_items que es la lista completa sobre la que se aplican los filtros se corresmonde con el
            nro de linea de mdline.
        - 'Item' se refiere al widget que representa el item en el layout del RecycleView.
        - 'Data Item' se refiere al diccionario que representa el item en el data del RecycleView.

    Args:
        FocusBehavior (_type_): _description_
        ThemableBehavior (_type_): _description_
        RecycleView (_type_): _description_
        ActivateItemEventDispatcher (_type_): _description_
        UnActivateItemEventDispatcher (_type_): _description_
        SelectItemEventDispatcher (_type_): _description_
        UnSelectItemEventDispatcher (_type_): _description_
    """
    instance_focus = None
    filter = BooleanProperty(False)
    filter_txt = StringProperty('')
    filter_up = BooleanProperty(False)
    search = BooleanProperty(False)

    def __init__(self, activate_background=True, **kwargs):
        FocusBehavior.__init__(self)
        ThemableBehavior.__init__(self)
        RecycleView.__init__(self)
        self.undo_manager = UndoManager()
        # FrameFocused.__init__(self, hotlight=False)
        ActivateItemEventDispatcher.__init__(self)
        UnActivateItemEventDispatcher.__init__(self)
        SelectItemEventDispatcher.__init__(self)
        UnSelectItemEventDispatcher.__init__(self)

        # self.focused = True
        # self.filter = False
        # self.filter_txt = None
        # self.filter_up = False
        # self.search = False
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
        self.data_items = dict()  # Clase sobre la que se ejecutan los cambios para luego copiar al data del RecycleView. Para implementar filtros.
        self.undo_manager.clear_stack()
        self._md_lines = None
        self._item_hotlight = None
        self._selected_indexs = []  # Item actual seleccionado
        self._active_index = -1
        self._cursor = (1000, -1)  # es una tupla (columna, fila)
        self._mode_editor = False
        self._old_text_line = None  # Guarda el texto de la linea antes de editarla
        # Altura del layout de items
        # Nota: Hay que mantenerla actualizada con el agregado, borrado y cambio de tamañano del item en edicion
        # self.layout_height = 0

    ''' Funciones de la Interfaz -------------------------------'''
    def apply_data_items(self):
        if self.filter:
            if self.filter_txt.strip() != '':
                if self.filter_up:
                    # Incliye en el filtro las lineas padre de las que cumplen el filtro
                    pass
                else:
                    # Aplica el filtro solo a las lineas que coinciden con el filtro
                    self.data = [di for di in self.data_items if self.filter_txt in di['md_line'].md_text]
                    # self.data = []
                    # ix = 0
                    # for di in self.data_items:
                    #     if self.filter_txt in di['md_line'].md_text:
                    #         di['state'].index = ix
                    #         self.data.append(di)
                    #         ix += 1
            else:
                self.data = self.data_items.copy()
                # self.data = []
                # ix = 0
                # for di in self.data_items:
                #     di['state'].index = ix
                #     self.data.append(di)
                #     ix += 1
        else:
            # copia la lista completa
            self.data = self.data_items.copy()
        pass

    def populate_from_md_lines(self, md_lines):
        print("------------------------------------------------------------------------------------------------")
        print("+- MDDocumentEditor.populate_from_md_lines() ---------------------------------------------------")
        self.initialize_document()
        self._md_lines = md_lines
        self.data_items = []
        for id, mdl in enumerate(md_lines, start=0):
            print(f"   L{mdl.num_line}: {mdl.md_text}")
            data_line = DataItemLineMDD(md_line=mdl, data_themed=DataThemed(),
                                        data_show=DataShow(), data_state=DataState())  # no uso el id del data. Uso md_line.num_line que se auto-actualiza
            dic_line = data_line.to_dict()
            self.data_items.append(dic_line)
        self.apply_data_items()

    def on_filter(self, instance, value):
        self.filter = value
        self.apply_data_items()
    
    def on_filter_txt(self, instance, value):
        self.filter_txt = value
        self.apply_data_items()

    def on_filter_up(self, instance, value):
        self.filter_up = value
        self.apply_data_items()

    def on_search(self, instance, value):
        self.search = value
        self.apply_data_items()

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

    '''Funciones generales de data y item ---------------------------------------'''
    # OK data item
    def index_from_data(self, data):
        return self.data.index(data)

    def index_from_item(self, item:MDDocumentLineEditor):
        return self.layout.get_view_index_at(self.layout.to_local(*item.pos))
    
    def index_from_pos(self, pos:tuple):
        return self.layout.get_view_index_at(self.layout.to_widget(*pos))

    # ESTO ESTA MAL EL INDEX DEL DATA NO ES EL DEL CHILDREN
    def item_from_index(self, data_index):
        for widget, dt_index in self.layout_manager.view_indices.items():
            if dt_index == data_index:
                return widget
        return None

        

        # # Obtiene el index del widget

        # print(self.layout.view_indices.keys())
        # print(self.layout.view_indices.items())

        # view_widget_index = self.layout.view_indices.get(data_index)
        # # Si .get() devolvió None, el widget no está visible.
        # # Comprueba si se encontró el índice.
        # if view_widget_index is not None:
        #     try:
        #         return self.layout.children[view_widget_index]
        #     except IndexError:
        #         # Salvaguarda por si el layout cambia justo en ese instante.
        #         return None
        # return None

    # OK data item
    def active_md_editor(self):
        item = self.item_from_index(self._active_index)
        if item:
            return item.wg_line_editor.md_editor if self._active_index > -1 else None
        else:
            None

    # OK data item
    # def update_data_index(self, start_index):
    #     for ii in range(start_index, len(self.data)):
    #         self.data_items[ii]['index'] = ii

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



    def select_from_item(self, item:MDDocumentLineEditor, anim:bool=False, anim_type:str="point", cursor_pos:tuple=None):  # TODO: cambiar a select_from_item
        # print(f'MDDocumentEditor.select - {item.index} -----------------------')
        self.select_from_data_item(data_item=self.data[self.index_from_item(item)], anim=anim, anim_type=anim_type, cursor_pos=cursor_pos)

    def select_from_index(self, index:int, anim:bool=False, anim_type:str="point", cursor_pos:tuple=None):  # TODO: cambiar a select_from_index
        self.select_from_data_item(data_item=self.data[index], anim=anim, anim_type=anim_type, cursor_pos=cursor_pos)

    def select_from_data_item(self, data_item:dict, anim:bool=False, anim_type:str="point", cursor_pos:tuple=None):  # TODO: cambiar a select_from_data
        '''
        Selecciona la linea. Puede haber varias lineas seleccionadas pero una sola activa
        anim puede ser True, False o una tupla que indica la pos de inicio de la animacion
        '''
        print(f"MDDocumentEditor.select_data_item(data_item: {data_item})")
        # Marca el item como seleccionado
        state = data_item['state']
        themed = data_item['themed']
        state.selected = True
        themed.start_anim = anim
        themed.anim_type = anim_type
        themed.cusor_pos = cursor_pos
        # self.data_items[data_item.index]['state'].selected = True
        

        # Agrega el item al listado de seleccion
        self._selected_indexs.append(state.index)
        # Actualiza el View
        self.refresh_from_data()
        SelectItemEventDispatcher.do_something(self, data_item, state.index)

    def select_indexs(self, indexs:list, anim:bool=False, anim_type:str="point", cursor_pos:tuple=None):
        self._selected_indexs = indexs  # Re Seleccion las lineas
        for ii in indexs:
            if -1 < ii and ii < len(self.data):
                self.data[ii]['state'].selected = True
                themed = self.data[ii].themed
                themed.anim = anim
                themed.anim_type = anim
                themed.cursor_pos = cursor_pos

    def unselect_from_item(self, item, anim=False):  # TODO: cambiar a unselect_from_item
        # print(f'RecycleListView.unselect - {item.file_name} -------------------')
        self.unselect_from_data_item(self.data[self.index_from_item(item)], anim)

    def unselect_from_index(self, index, anim=False):  # TODO: cambiar a unselect_from_index
        self.unselect_from_data_item(self.data[index], anim)

    def unselect_from_data_item(self, data_item, anim=False):  # TODO: cambiar a unselect_from_data
        # print(f"MDDocumentEditor.unselect_data_item(data_item)")
        data_item['state'].selected = False
        data_item['themed'].anim = anim
        index = self.index_from_data(data_item)
        # self.refresh_from_data()
        # print(f'  Lista de Seleccionados antes{self._selected_indexs}, {data_item["l_id"]}')
        self._selected_indexs.remove(index)
        # print(f'  Lista de Seleccionados despues{self._selected_indexs}')

        UnSelectItemEventDispatcher.do_something(self, data_item, index)

    def activate_from_item(self, item:MDDocumentLineEditor, cursor_pos:tuple=None, anim:bool=False, anim_type:str="point"):
        """
        Activa el item

        Args:
            item (MDDocumentLineEditor): Widget que representa una linea de MDDocument
            cursor_pos (tuple, optional): Posicion del cursor donde se comenzar la animacion "point". Defaults to None.
            anim (bool, optional): Indica si la activacion se anima. Defaults to False.
            anim_type (str, optional): Tipo de Animacion a implementar en la activación. Defaults to "point".
        """
        self.activate_from_data(self.data[self.index_from_item(item)], cursor_pos=cursor_pos, anim=anim, anim_type=anim_type)

    def activate_from_index(self, index, cursor_pos=None, anim=False, anim_type:str="point"):
        """
        Activa el item desde el index

        Args:
            index (int): Indice del Widget que representa una linea de MDDocument
            cursor_pos (tuple, optional): Posicion del cursor donde se comenzar la animacion "point". Defaults to None.
            anim (bool, optional): Indica si la activacion se anima. Defaults to False.
            anim_type (str, optional): Tipo de Animacion a implementar en la activación. Defaults to "point".
        """
        if -1 < index and index < len(self.data):
            self.activate_from_data(self.data[index], cursor_pos=cursor_pos, anim=anim, anim_type=anim_type)

    def activate_from_data(self, data_item, cursor_pos=None, anim=False, anim_type:str="point"):
        '''
        Activa la linea, sola una linea puede estar activa. La que puede editarse y tambien esta seleccionada.
        anim puede ser True, False o una tupla que indica la pos de inicio de la animacion
        '''
        print("MDDocumentEditor.activate_from_data(...))")
        state = data_item['state']
        themed = data_item['themed']
        
        state.selected = True
        state.active = True
        themed.anim = anim
        themed.anim_type = anim_type
        state.cursor = self._cursor if cursor_pos == None else cursor_pos

        print(f'+++ Cursor= {state.cursor} ------------------------------')

        state.mode_editor = self._mode_editor
        self._active_index = self.index_from_data(data_item)
        # Agrega el item a la selccion
        if not self._active_index in self._selected_indexs:
            self._selected_indexs.append(self._active_index)
        self._old_text_line = data_item['md_line'].md_text
        # self.refresh_from_data()
        ActivateItemEventDispatcher.do_something(self, data_item, self._active_index)

    # def unactivate_from_item(self, item, anim=False):
    #     self.unactivate_from_data(self.data[item.index], anim=anim)

    # def unactivate_from_index(self, index, anim=False):
    #     if -1 < index and index < len(self.data):
    #         self.unactivate_from_data(self.data[index], anim=anim)

    # def unactivate_from_data(self, data_item, anim=False):
    #     '''anim puede ser True, False o una tupla que indica la pos de inicio de la animacion'''
    #     print("MDDocumentEditor.unactivate_from_data(...))")
    #     sel_item = self.item_from_index(data_item['l_id'])
    #     for ix in self._selected_indexs:
    #         self.data[ix]['selected'] = False
    #     self._selected_indexs.clear()
    #     if sel_item:
    #         # self._cursor = sel_item.wg_line_editor.md_editor.cursor
    #         # print(f"    En modo edicion: {self._cursor_col}, {self._item_selected.wg_line_editor.cursor_col}")
    #         data_item['start_anim'] = anim
    #         data_item['active'] = False
    #         data_item['mode_editor'] = False
    #         self.refresh_from_data()
    #         data_item['start_anim'] = False
    #         self._active_index = -1
    #         self._old_text_line = None
    #         UnActivateItemEventDispatcher.do_something(self, data_item, data_item['l_id'])

    def unactivate(self, anim=False):
        '''anim puede ser True, False o una tupla que indica la pos de inicio de la animacion'''
        # print("MDDocumentEditor.unactivate_from_data(...))")
        
        # Des-selecciona todos los item y borra la lista de selccion --------------------
        for ix in self._selected_indexs:
            if ix < len(self.data):
                self.data[ix]['state'].selected = False
                self.data[ix]['state'].mode_editor = False
        self._selected_indexs.clear()


        # for dt in self.data:
        #     dt['state'].selected = False
        #     dt['state'].mode_editor = False
        #     dt['state'].active = False
        #     dt['themed'].anim = False


        # Des-activa el item activo -----------------------------------------------------
        if -1 < self._active_index < len(self.data):
            data_item = self.data[self._active_index]            
            self.in_editing(False, anim=anim)  # Desactiva el modo de edicion
            data_item['state'].active = False
            data_item['themed'].anim = anim
            self._active_index = -1
            UnActivateItemEventDispatcher.do_something(self, data_item, self.index_from_data(data_item))


    def active_to_previus_item(self, cursor_pos=None):
        # print("MDDocumentEditor.move_to_previus_item()")
        # print(f'  Active Index= {self._active_index}')
        
        # TODO: NO ESTA ASIGNADO ACTIVE INDEX
        
        if self._active_index > 0:
            # item_prev = self.item_from_index(self._active_index)
            index = self._active_index - 1 if self._active_index > 0 else 0
            # print(f'  active index= {self._active_index}')
            
            self.unactivate(anim=True)  # Desactiva el modo de edicion del item actual
            # self.unactivate_from_index(self._active_index, anim=True)
            
            # print(f'  active index= {self._active_index}, despues de unactivate')
            # Actualiza la vista para que el nuevo item este visible
            item = self.item_from_index(index)
            if item:
                if self.item_scroll_pos_y(item) + item.height > self.y + self.height:  # Mover el item a la base del RecycleView
                    self.scroll_y += item.height / (self.layout_manager.height - self.height)
            else:
                # print(f'    Scroll por index= {(index +0.5) / len(self.data)}')
                self.scroll_y = 1- (index +0.5) / len(self.data)
        else:
            index = len(self.data) - 1
            item = self.item_from_index(index)
            self.scroll_y = 0

        self.activate_from_index(index, cursor_pos=cursor_pos, anim=True)
        return item

    def active_to_next_item(self, cursor_pos=None):
        # print("MDDocumentEditor.move_to_next_item()")
        # print(f'  Active Index= {self._active_index}')
        if self._active_index > -1:
            item_prev = self.item_from_index(self._active_index)
            index = self._active_index + 1 if self._active_index < len(self.data) - 1 else len(self.data) - 1
            
            # self.unactivate_from_index(self._active_index, anim=True)
            self.unactivate(anim=True)  # Desactiva el modo de edicion del item actual

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

    def get_previus_data_title(self):
        '''Devuelve el titulo anterior al indice indicado'''
        index = self._active_index
        if -1 < index < len(self.data):
            for ii in range(index - 1, -1, -1):
                if self.data_items[ii]['md_line'].type in (MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE):
                    return self.data_items[ii]
        return None

    def get_next_data_title(self):
        '''Devuelve el siguiente titulo despues del indice indicado'''
        index = self._active_index
        if -1 < index < len(self.data):
            for ii in range(index + 1, len(self.data)):
                if self.data_items[ii]['md_line'].type in (MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE):
                    return self.data[ii]
        return None


   # SEGUIR DE ACA. CAMBIAR A data_items Y LUEGO COPIAR A DATA

    ''' Funciones Edicion de Lineas --------------------------------------------'''
    def update_numlines(self):  # No Hace Falta. Probar sacar
        for ii, line in enumerate(self._md_lines):
            line.num_line = ii + 1

    # Actualizado a data_items
    def move_line_to(self, actual_index, new_index):  # Hay que ver que pass con actual y new index por que apuntan al data creo
        '''Mueve la linea de la posicion actual_index a la poscicion new_index'''
        # print('MDDocumentEditor.move_line_to()')
        if new_index > actual_index:  # Mueve hacia arriba
            # print('  Mueve hacia arriba')
            self._md_lines.insert(new_index, self._md_lines.pop(actual_index))  # Mueve MDLine
            self.data_items.insert(new_index, self.data_items.pop(actual_index))  # Mueve el data
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
            # Ajusta el scroll para que el item este visible
            item = self.item_from_index(actual_index)
            if self.item_scroll_pos_y(item) + item.height > self.y + self.height:  # Mover el item a la base del RecycleView
                self.scroll_y += item.height / (self.layout_manager.height - self.height)
            # Actualiza el View
            self.apply_data_items()
            self.refresh_from_data()
        elif new_index < actual_index:  # Mueve hacia abajo
            # print('  Mueve hacia abajo')
            self._md_lines.insert(new_index, self._md_lines.pop(actual_index))  # Mueve MDLine
            self.data_items.insert(new_index, self.data_items.pop(actual_index))  # Mueve el data
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
            # Ajusta el scroll para que el item este visible
            item = self.item_from_index(actual_index)
            if self.item_scroll_pos_y(item) < 0:  # Mover el item a la base del RecycleView
                self.scroll_y -= item.height / (self.layout_manager.height - self.height)
            # Actualiza el View
            self.apply_data_items()
            self.refresh_from_data()

    # Actualizado a data_items
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
        self.data_items.append(dic_line)
        # Actualiza el View
        self.refresh_from_data()
        return md_line

    def insert_line(self, index:int, md_text:str=''):
        """Inserta una linea en el indice indicado"""
        # print('MDDocument.insert_lines() -----------------------')
        if -1 < index < len(self._md_lines):
            md_line = MDLine(md_text=md_text,
                            prev_line=self._md_lines[index-1], next_line=self._md_lines[index],
                            type=MD_LINE_TYPE.TEXT, num_line=0)  # TIRA ERROR EN type NO SE POR QUE
            # Inserta md_line y ajusta las dependendencias
            self._md_lines.insert(index, md_line)
            md_line.update_type()
            if index > 0:
                self._md_lines[index - 1].next_line = self._md_lines[index]
            else:
                self._md_lines[index].prev_line = None
            self._md_lines[index + 1].prev_line = self._md_lines[index]
            md_line.num_line = index + 1
            # Inserta en data ---------------------------------------
            data_line = DocLineDataDic(index+1, md_line)
            dic_data_line = data_line.to_dict()
            self.data_items.insert(index, dic_data_line)
            self.update_data_index(index)
            # Refresca el View --------------------------------------
            self.apply_data_items()
            self.refresh_from_data()
            return md_line
        else:
            return None

    def remove_line(self, index:int):
        # Ajusta los indices de los Items Seleccionados
        for ii, value in enumerate(self._selected_indexs, start=0):
            if value > index:
                self._selected_indexs[ii] = value - 1
            # print(f'ii={ii}, value={value}, nuevo valor={self._selected_indexs[ii]}')
        # Borrar en _md_lines y ajusta las dependendencias
        del(self._md_lines[index])
        if index < len(self._md_lines)-1:
            if index > 0:
                self._md_lines[index-1].next_line = self._md_lines[index]
                self._md_lines[index].prev_line = self._md_lines[index-1]
            else:
                self._md_lines[index-1].next_line = None
                self._md_lines[index].prev_line = None
            self._md_lines[index].num_line = index + 1
        # Borra en el data
        del(self.data_items[index])
        self.update_data_index(index)
        # Refresca el View
        self.apply_data_items()
        self.refresh_from_data()

    def in_editing(self, value:bool, anim:bool=False):
        if not value and self._mode_editor and self._old_text_line != self.active_md_editor().text:
            self.undo_manager.add(_TextModifiedCommand(self, self._active_index, self._old_text_line, self.active_md_editor().text))
        # self._mode_editor =value
        if -1 < self._active_index < len(self.data):
            self.data_items[self._active_index] ['mode_editor'] = value
            self.data_items[self._active_index]['cursor'] = self._cursor
            self.data_items[self._active_index]['start_anim'] = anim
            if value:
                self._old_text_line = self.data_items[self._active_index]['md_line'].md_text
            # Actualiza el View
            self.apply_data_items()
            # self.refresh_from_data()
        else:
            self._active_index = -1

    '''Eventos de Usuario --------------------------------------------------------'''
    def on_touch_down(self, touch):
        # print(f'RecycleListView.on_touch_down')
        if self.collide_point_to_window(*touch.pos):
            # print(f'  Grab')
            touch.grab(self)  # Marca este touch como manejado por este widget
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):  # Hay que ver como con data y data_items. Deberia tener actualizada la informacion de selccion en los dos
        # print(f'RecycleListView.on_touch_up {self.uid}, collide_point={self.collide_point(*touch.pos)}')
        if touch.grab_current is self:  # Verifica si este widget "grabó" el evento touch
            # print('   Con Grab')
            # mods = touch.modifiers
            # is_shift = 'shift' in Window.keyboard_modifiers
            # is_ctrl = 'ctrl' in Window.keyboard_modifiers or 'meta' in Window.keyboard_modifiers

            dt_index = self.index_from_pos(touch.pos)

            # Verifica que el índice sea válido
            if dt_index is None or dt_index < 0 or dt_index >= len(self.data):
                touch.ungrab(self)
                return False
            item = self.item_from_index(dt_index)
            data_it = self.data[dt_index]

            # +-- SE PRESIONO EL BOTON IZQUIERDO ----------------------------------------------------------------------
            if touch.button == 'left':  #  Seleccion y Des-seleccion de los items (Boton Izquierdo)
                print('+-- RecycleListView.on_touch_down Boton Izquierdo --------------------------')
                print(f'   Item a Seleccionar: index={dt_index}, linea={data_it['md_line'].md_text}')
                

                # TODO: Verificar si esta presionado SHIFT o CTRL y seleccionar el rango
                if self._active_index != dt_index and self._active_index > -1:
                    # print(f'  RecycleListView.on_touch_down UNSELECT ++++++++++++++++++++++++++++')
                    self.unactivate(anim=True)


                # TODO: Ver el estado de edicion y mantener


                self.in_editing(True)
                self._mode_editor = True
                # Obtiene la posición del cursor del texto en el lugar del click del mouse
                cursor = item.wg_line_editor.md_editor.get_cursor_from_xy(*self.to_local(*touch.pos))                
                # Activa el Item
                self.activate_from_index(dt_index, cursor, anim=True, anim_type='point')

                # print(f'   Estado de los data:')
                # for it in self.data:
                #     st = it['state']
                #     print(f"    - index: {self.index_from_data(it)}, seleccionado: {st.selected}, active: {st.active}")

                touch.ungrab(self)
                self.refresh_from_data()
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
            in_edition = active_item.mode_editor if active_item else False  ## TODO: Usar un if general para ejecutar los if con esta condicion
            self._cursor = md_editor.cursor if md_editor else (0, 0)  # self.item_from_index(self._active_index).wg_line_editor.md_editor.cursor
            
            # Flecha arriba + Ctrl + Shift, mueve el bloque hacia arriba
            if keycode == 273 and all(kk in special_keys for kk in ['shift', 'ctrl']):  # Mueve el bloque hacia arriba
                print('  Flecha Arriba con Ctrl y Shift (mueve el bloque hacia arriba)')
                # Se supone que la lista es continua sin seleccion intercalada.
                # En este contecto borro la lines superior a la seleccion y la pego debajo de la seleccion
                ix_actual = min(self._selected_indexs) - 1
                ix_new = max(self._selected_indexs)
                if ix_actual > -1:
                    self.undo_manager.execute(_MoveLinesCommand(self, ix_actual, ix_new))
            
            # Flecha abajo + Ctrl + Shift, mueve el bloque hacia abajo
            elif keycode == 274 and all(kk in special_keys for kk in ['shift', 'ctrl']):  # Mueve el bloque hacia abajo
                # Se supone que la lista es continua sin seleccion intercalada.
                # En este contecto borro la lines inferior a la seleccion y la pego sobre la seleccion
                ix_new = min(self._selected_indexs)
                ix_actual = max(self._selected_indexs) + 1
                if ix_actual < len(self.data):
                    self.undo_manager.execute(_MoveLinesCommand(self, ix_actual, ix_new))
            
            # Flecha arriba + Ctrl, mueve al Título anterior
            elif keycode == 273 and 'ctrl' in special_keys:  # Flecha arriba + Ctrl, mueve al Título anterior
                print('  Flecha Arriba con Ctrl (mueve al Título anterior)')
                data = self.get_previus_data_title()
                if data:
                    self.unactivate()  # Desactiva el modo edicion
                    self.activate_from_data(data, anim=True)  # Activa el item
                    self.scroll_to_index(data['index'])

            # Flecha abajo + Ctrl, mueve al Siguiente Título
            elif keycode == 274 and 'ctrl' in special_keys:  # Flecha abajo + Ctrl, mueve al Siguiente Título
                print('  Flecha Abajo con Ctrl (mueve al Siguiente Título)')
                data = self.get_next_data_title()
                if data:
                    self.unactivate()  # Desactiva el modo edicion
                    self.activate_from_data(data, anim=True)  # Activa el item
                    self.scroll_to_index(data['index'])


            # Ctrl + C, Copiar linea/s seleccionada
            elif not in_edition and char == 'c' and 'ctrl' in special_keys:  # Ctrl + C, Copiar
                # print(f'texto seleccionado: {md_editor.selection_text}')
                # Crea el texto a copiar

                # SACAR not in_edition and Y VERIFICAR SI EL TEXTO EN EDICION LA SELECCION ES 0 COPIA LA LINEA SINO RETORNA TRUE

                if not in_edition or len(md_editor.selection_text) == 0:
                    cp_txt = ''
                    for ii in range(0, len(self._selected_indexs)-1):
                        cp_txt += self._md_lines[self._selected_indexs[ii]].md_text + '\n'
                    cp_txt += self._md_lines[self._selected_indexs[len(self._selected_indexs)-1]].md_text
                    Clipboard.copy(cp_txt)
                    return True
                else:
                    return False
            
            # Ctrl + V, Pegar linea/s en la papelera
            elif not in_edition and char == 'v' and 'ctrl' in special_keys:  # Ctrl + V, Pegar
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
                        self.undo_manager.execute(_InsertLinesCommand(self, self._active_index, pasted_list))

                        # for id, txt in enumerate(pasted_list, start=0):
                        #     if ix_i < u_line:
                        #         self.insert_line(ix_i+id, txt)
                        #     else:
                        #         self.append_line(txt)
                        return True
                    else:
                        return False
            
            # Ctrl + X, Cortar linea/s seleccionada
            elif not in_edition and char == 'x' and 'ctrl' in special_keys:  # Ctrl + X, Cortar
                # Corta la seleccion
                print('  Ctrl + x')
                # Crea el texto a copiar
                if not in_edition or len(md_editor.selection_text) == 0:
                    cp_txt = ''
                    for ii in range(0, len(self._selected_indexs) - 1):
                        cp_txt += self._md_lines[self._selected_indexs[ii]].md_text + '\n'
                        #self.remove_line(self._selected_indexs[ii])
                    cp_txt += self._md_lines[self._selected_indexs[len(self._selected_indexs) - 1]].md_text
                    # self.remove_line(self._selected_indexs[len(self._selected_indexs) - 1])  TODO UNDO REMOVE_LINE
                    self.undo_manager.execute(_RemoveLinesCommand(self, self._selected_indexs))
                    Clipboard.copy(cp_txt)
                    return True
                else:
                    return False
            
            # Ctrl + Z, Deshacer ultima accion
            elif not in_edition and char == 'z' and 'ctrl' in special_keys:  # Ctrl + Z, Deshacer
                self.undo_manager.undo()
                return True
            
            # Ctrl + Y, Rehacer ultima accion
            elif not in_edition and char == 'y' and 'ctrl' in special_keys:  # Ctrl + Y, Rehacer
                self.undo_manager.redo()
                return True
            
            # Ctrl + A, Selecciona todo el documento
            elif keycode == 65 and 'ctrl' in special_keys:  # Ctrl + A, Selecciona todo el documento
                print('  Ctrl + A')
                self.unactivate()  # Desactiva el modo edicion
                self._selected_indexs.clear()  # Limpia la lista de seleccionados
                for ii in range(len(self.data)):
                    self._selected_indexs.append(ii)
                for data_item in self.data:
                    data_item['selected'] = True
                self.refresh_from_data()  # Actualiza el view
                self.activate_from_index(len(self.data)-1, anim=False)  # Activa el ultimo item
                self.in_editing(False)  # Desactiva el modo edicion
                return True

            # Flecha arriba + Shift, Extiende la seleccion hacia la linea de arriba
            elif keycode == 273 and 'shift' in special_keys and self._active_index != 0:  # Extiende la seleccion hacia la linea de arriba
                self.in_editing(False)  # Inhabilita el modo edicion
                self._active_index -= 1  # Mueve el item activado
                # Agrega o borra de la lista de seleccionados
                if self._active_index in self._selected_indexs:  # Des-selecciona
                    self.unselect_index(self._active_index+1, anim=False)
                else:
                    self.select_index(self._active_index, anim=False)
                    item = self.item_from_index(self._active_index)
                    if self.item_scroll_pos_y(item) + item.height > self.y + self.height:  # Mover el item a la base del RecycleView
                        self.scroll_y += item.height / (self.layout_manager.height - self.height)
            
            # Flecha abajo + Shift, Extiende la seleccion hacia la linea de abjajo
            elif keycode == 274 and 'shift' in special_keys and self._active_index != len(self.data)-1:  # # Extiende la seleccion hacia la linea de abajo
                self.in_editing(False)  # Inhabilita el modo edicion
                self._active_index += 1  # Mueve el item activado
                # Agrega o borra de la lista de seleccionados
                if self._active_index in self._selected_indexs:  # Des-selecciona
                    self.unselect_index(self._active_index-1, anim=False)
                else:
                    self.select_index(self._active_index, anim=False)
                    item = self.item_from_index(self._active_index)
                    if self.item_scroll_pos_y(item) < 0:  # Mover el item a la base del RecycleView
                        self.scroll_y -= item.height / (self.layout_manager.height - self.height)
            
            # Flecha Arriba, Activa la linea de arriba
            elif keycode == 273 and self._active_index != 0:  # Flecha Arriba
                print(f'  Flecha Arriba')
                # TODO: Verificar si esta presionado SHIFT o CTRL y seleccionar el rango
                self.active_to_previus_item()
            
            # Flecha Abajo, Activa la linea de abajo
            elif keycode == 274 and self._active_index != len(self.data)-1:  # Flecha Abajo
                # TODO: Verificar si esta presionado SHIFT o CTRL y seleccionar el rango
                self.active_to_next_item()
            
            # Flecha Derecha y cursor al final de linea, activa la linea de abajo y mueve el cursor al principio de la linea
            elif keycode == 275 and self._active_index != len(self.data)-1 and self._cursor[0] == len(md_editor.text):  # Flecha Derecha
                print('  Flecha Derecha')
                self.active_to_next_item(cursor_pos=(0, 0))
            
            # Flecha Izquierda y cursor al principio de linea, activa la linea de arriba y mueve el cursor al final de la linea
            elif keycode == 276 and self._active_index != 0 and self._cursor[0] == 0:  # Flecha Izquierda
                print(f'  Flecha izquierda, active index= {self._active_index}')
                cur_x = len(self.data[self._active_index-1]['md_line'].md_text)
                self.active_to_previus_item(cursor_pos=(cur_x, 0))
            
            # F2, Activa o desactiva el modo edicion
            elif keycode == 283:  # Tecla F2
                self._mode_editor = not(self._mode_editor)
                self.in_editing(self._mode_editor)
                
                return True
            
            # Escape, desactiva el modo edicion sin guardar los cambios
            # TODO: Tecla escape no funciona.
            elif keycode == 27:  # Tecla Escape
                self.in_editing(False)  # Desactiva el modo edicion

            # Enter o Intro, genera un salto de linea
            elif in_edition and (keycode == 13 or keycode == 271):  # Tecla Enter o Intro
                self.undo_manager.execute(_EnterInEditionCommand(self))
            
            # Backspace con cursor al inicio de linea, fusiona la linea con la linea de arriba
            elif keycode == 8 and self._active_index != 0 and self._cursor[0] == 0: # Tecla Backspace
                print('  Tecla Backspace -> Fusiona la linea con la linea de arriba')
                
                # text = md_editor.text
                # print(f'    text: {text}')
                # self.remove_line(self._active_index)
                # cpos = len(self._md_lines[self._active_index-1].md_text)
                # self._md_lines[self._active_index -1].md_text += text
                # self.activate_from_index(self._active_index-1, cursor_pos=(cpos, 0))

                self.undo_manager.execute(_BackspaceOnStartLineCommand(self))
            
            # Suprimir (Delete) con cursor al final de linea en modo edicion, fusiona la linea con la linea de abajo
            elif keycode == 127 and self._active_index != len(self.data)-1 and self._cursor[0] == len(md_editor.text) \
                    and len(self._selected_indexs) == 1 and in_edition:  # Tecla Suprimir (Delete) en modo edicion
                print('  Tecla Suprimir -> Fusiona la linea con la linea de abajo')
                # cur_pos = len(self._md_lines[self._active_index].md_text)
                # self._md_lines[self._active_index].md_text += self._md_lines[self._active_index+1].md_text  # agrega el texto de la linea inferior
                # self.data[self._active_index]['cursor'] = (cur_pos, 0)  # Posiciona el cursor
                # self.remove_line(self._active_index+1)  # borra la linea de abajo
                # self.data[self._active_index+1]['md_line'].num_line = self.data[self._active_index]['md_line'].num_line + 1  # actualiza nro linea, prev y next
            
                self.undo_manager.execute(_DeleteOnEndLineCommand(self))

            # Suprimir (Delete) en modo no edicion, borra la linea/s seleccionada
            elif keycode == 127 and len(self._selected_indexs) > 0 and not in_edition:  # Tecla Suprimir en modo no edicion
                self.undo_manager.execute(_RemoveLinesCommand(self, self._selected_indexs))
                # self.data[self._selected_indexs[len(self._selected_indexs)-1]]['selected'] = True
            
            # Page Up, desplaza la vista hacia arriba
            elif keycode == 280:  # tecla page up
                print('  Tecla PageUp')
                delta = len(self.layout.children) - 2
                new_center_ix = self.layout.children[int(delta / 2)].index - delta   #este hay que sacarlo
                if new_center_ix > 0:
                    self.scroll_y += self.height / (self.layout_manager.height - self.height)
                else:
                    self.scroll_y = 1
            
            # Page Down, desplaza la vista hacia abajo
            elif keycode == 281:  # tecla page down
                # print('  Tecla PageDown')
                delta = len(self.layout.children) - 2
                new_center_ix = self.layout.children[int(len(self.layout.children)/2)].index + delta
                if new_center_ix < len(self.data):
                    self.scroll_y -= self.height / (self.layout_manager.height - self.height)
                else:
                    self.scroll_y = 0
            
            # Si no se reconoce la tecla, retorna False para que el evento no se consuma
            return False
        pass





class MDDocumentEditor(FocusBehavior, ThemableBehavior, RecycleView,
                       ActivateItemEventDispatcher, UnActivateItemEventDispatcher,
                       SelectItemEventDispatcher, UnSelectItemEventDispatcher):
    """Clase que implementa un editor de documentos markdown basado en RecycleView
    Nota: 
        - Solo puede haber un MDDocumentEditor con foco a la vez.
        - El indice 'Index' de la lista self.data se refiere al indice del item en el data del RecycleView.
        - El indice de la data_items que es la lista completa sobre la que se aplican los filtros se corresmonde con el
            nro de linea de mdline.
        - 'Item' se refiere al widget que representa el item en el layout del RecycleView.
        - 'Data Item' se refiere al diccionario que representa el item en el data del RecycleView.

    Args:
        FocusBehavior (_type_): _description_
        ThemableBehavior (_type_): _description_
        RecycleView (_type_): _description_
        ActivateItemEventDispatcher (_type_): _description_
        UnActivateItemEventDispatcher (_type_): _description_
        SelectItemEventDispatcher (_type_): _description_
        UnSelectItemEventDispatcher (_type_): _description_
    """
    instance_focus = None
    filter = BooleanProperty(False)
    filter_txt = StringProperty('')
    filter_up = BooleanProperty(False)
    search = BooleanProperty(False)

    def __init__(self, activate_background=True, **kwargs):
        FocusBehavior.__init__(self)
        ThemableBehavior.__init__(self)
        RecycleView.__init__(self)
        self.undo_manager = UndoManager()
        # FrameFocused.__init__(self, hotlight=False)
        ActivateItemEventDispatcher.__init__(self)
        UnActivateItemEventDispatcher.__init__(self)
        SelectItemEventDispatcher.__init__(self)
        UnSelectItemEventDispatcher.__init__(self)
        # Inicializa el Documento -------
        self.initialize_document()
        self.activate_background = activate_background  # Activa el cambio de tonalidad en el fondo de los items
        self.on_scroll_event = None  # Referencia al evento de scroll para el item en edicion
        self.layout = self.ids.srblayout
        # Canvas de graficos
        with self.canvas.after:
            if not self.flat: self.graphic_border = GBorder(self)
            self.graphic_focus = GFocus(self)
        # Eventos
        Window.bind(on_key_down=self._on_keyboard_down)

    def initialize_document(self):
        'Inicializa el documento'
        self.data_items = dict()  # Clase sobre la que se ejecutan los cambios para luego copiar al data del RecycleView. Para implementar filtros.
        self.undo_manager.clear_stack()
        self._md_lines = None
        self._item_hotlight = None  # No se si se esta asignando
        self.selected_indexs = []  # Item actual seleccionado
        self.active_index = -1
        self.active_view = None
        self._cursor = (1000, -1)  # es una tupla (columna, fila)
        self._mode_editor = False
        self._old_text_line = None  # Guarda el texto de la linea antes de editarla
        # Altura del layout de items
        # Nota: Hay que mantenerla actualizada con el agregado, borrado y cambio de tamañano del item en edicion
        # self.layout_height = 0

    ''' Funciones de la Interfaz -------------------------------'''
    def apply_data_items(self):
        if self.filter:
            if self.filter_txt.strip() != '':
                if self.filter_up:
                    # Incliye en el filtro las lineas padre de las que cumplen el filtro
                    pass
                else:
                    # Aplica el filtro solo a las lineas que coinciden con el filtro
                    self.data = [di for di in self.data_items if self.filter_txt in di['md_line'].md_text]
                    # self.data = []
                    # ix = 0
                    # for di in self.data_items:
                    #     if self.filter_txt in di['md_line'].md_text:
                    #         di['state'].index = ix
                    #         self.data.append(di)
                    #         ix += 1
            else:
                self.data = self.data_items.copy()
                # self.data = []
                # ix = 0
                # for di in self.data_items:
                #     di['state'].index = ix
                #     self.data.append(di)
                #     ix += 1
        else:
            # copia la lista completa
            self.data = self.data_items.copy()
        pass

    def populate_from_md_lines(self, md_lines):
        print("------------------------------------------------------------------------------------------------")
        print("+- MDDocumentEditor.populate_from_md_lines() ---------------------------------------------------")
        self.initialize_document()
        self._md_lines = md_lines
        self.data_items = []
        for id, mdl in enumerate(md_lines, start=0):
            print(f"   L{mdl.num_line}: {mdl.md_text}")
            data_line = DataItemLineMDD(md_line=mdl, data_themed=DataThemed(),
                                        data_show=DataShow(), data_state=DataState())  # no uso el id del data. Uso md_line.num_line que se auto-actualiza
            dic_line = data_line.to_dict()
            self.data_items.append(dic_line)
        self.apply_data_items()

    ''' Funciones de Eventos de la Intefaz ---------------------'''
    def on_filter(self, instance, value):
        self.filter = value
        self.apply_data_items()
    
    def on_filter_txt(self, instance, value):
        self.filter_txt = value
        self.apply_data_items()

    def on_filter_up(self, instance, value):
        self.filter_up = value
        self.apply_data_items()

    def on_search(self, instance, value):
        self.search = value
        self.apply_data_items()

    def on_focus(self, instance, value):
        # print(f'MDDocumentEditor._on_focus {self.uid}-{value}')
        if value == False and MDDocumentEditor.instance_focus == instance:
            # print("    Focus False")
            MDDocumentEditor.instance_focus == None
        elif value == True:
            # print("    Focus True")
            MDDocumentEditor.instance_focus = instance
        return True

    '''Funciones scroll -------------------------------------------------------'''
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

    '''Funciones de Indices ---------------------------------------------------'''
    def index_from_data(self, data):
        return self.data.index(data)

    def index_from_item(self, item:MDDocumentLineEditor):
        return self.layout.get_view_index_at(self.layout.to_local(*item.pos))
    
    def index_from_pos(self, pos:tuple):
        return self.layout.get_view_index_at(self.layout.to_widget(*pos))

    def item_from_index(self, data_index):
        for view in self.layout.children:
            if view.index == data_index:
                return view
        return None

    def active_md_editor(self):  # No sacar
        if self.active_view is not None and self.active_index > -1:
            return self.active_view.wg_line_editor  # .md_editor
        else:
            None

    '''Funciones de Selección de Items ----------------------------------------'''
    def select_from_item(self, item:MDDocumentLineEditor, anim:bool=False, anim_type:str="point", cursor_pos:tuple=None):  # TODO: cambiar a select_from_item
        # print(f'MDDocumentEditor.select - {item.index} -----------------------')
        self.select_from_data_item(data_item=self.data[self.index_from_item(item)], anim=anim, anim_type=anim_type, cursor_pos=cursor_pos)

    def select_from_index(self, index:int, anim:bool=False, anim_type:str="point", cursor_pos:tuple=None):  # TODO: cambiar a select_from_index
        self.select_from_data_item(data_item=self.data[index], anim=anim, anim_type=anim_type, cursor_pos=cursor_pos)

    def select_from_data_item(self, data_item:dict, anim:bool=False, anim_type:str="point", cursor_pos:tuple=None):  # TODO: cambiar a select_from_data
        '''
        Selecciona la linea. Puede haber varias lineas seleccionadas pero una sola activa
        anim puede ser True, False o una tupla que indica la pos de inicio de la animacion
        '''
        print(f"MDDocumentEditor.select_data_item(data_item: {data_item})")
        # Marca el item como seleccionado
        state = data_item['state']
        themed = data_item['themed']
        state.selected = True
        themed.start_anim = anim
        themed.anim_type = anim_type
        themed.cusor_pos = cursor_pos
        # self.data_items[data_item.index]['state'].selected = True
        

        # Agrega el item al listado de seleccion
        index = self.index_from_data(data_item)
        self.selected_indexs.append(index)
        # Actualiza el View
        self.refresh_from_data()
        SelectItemEventDispatcher.do_something(self, data_item, index)

    def select_indexs(self, indexs:list, anim:bool=False, anim_type:str="point", cursor_pos:tuple=None):
        self.selected_indexs = indexs  # Re Seleccion las lineas
        for ii in indexs:
            if -1 < ii and ii < len(self.data):
                self.data[ii]['state'].selected = True
                themed = self.data[ii].themed
                themed.anim = anim
                themed.anim_type = anim
                themed.cursor_pos = cursor_pos
    
    '''Funciones de Des-Selección de Items ------------------------------------'''
    def unselect_from_item(self, item, anim=False):  # TODO: cambiar a unselect_from_item
        # print(f'RecycleListView.unselect - {item.file_name} -------------------')
        self.unselect_from_data_item(self.data[self.index_from_item(item)], anim)

    def unselect_from_index(self, index, anim=False):  # TODO: cambiar a unselect_from_index
        self.unselect_from_data_item(self.data[index], anim)

    def unselect_from_data_item(self, data_item, anim=False):  # TODO: cambiar a unselect_from_data
        # print(f"MDDocumentEditor.unselect_data_item(data_item)")
        data_item['state'].selected = False
        data_item['themed'].anim = anim
        index = self.index_from_data(data_item)
        # self.refresh_from_data()
        # print(f'  Lista de Seleccionados antes{self._selected_indexs}, {data_item["l_id"]}')
        self.selected_indexs.remove(index)
        # print(f'  Lista de Seleccionados despues{self._selected_indexs}')

        UnSelectItemEventDispatcher.do_something(self, data_item, index)

    '''Funciones de Activació y Des-Activación --------------------------------'''
    def unactivate(self, anim=False):
        '''anim puede ser True, False o una tupla que indica la pos de inicio de la animacion'''
        # print("MDDocumentEditor.unactivate_from_data(...))")
        
        # Des-selecciona todos los item y borra la lista de selccion --------------------
        for ix in self.selected_indexs:
            if ix < len(self.data):
                self.data[ix]['state'].selected = False
                self.data[ix]['state'].mode_editor = False
        self.selected_indexs.clear()

        state = self.data[self.active_index]['state']
        themed = self.data[self.active_index]['themed']

        state.active = False
        state.selected = False
        themed.anim = True
        themed.anim_type = 'fade'

        self.active_index = -1

    def active_to_previus_item(self, cursor_pos=None):
        # print("MDDocumentEditor.move_to_previus_item()")
        # print(f'  Active Index= {self._active_index}')
        
        # TODO: NO ESTA ASIGNADO ACTIVE INDEX
        
        if self.active_index > 0:
            # item_prev = self.item_from_index(self._active_index)
            index = self.active_index - 1 if self.active_index > 0 else 0
            # print(f'  active index= {self._active_index}')
            
            self.unactivate(anim=True)  # Desactiva el modo de edicion del item actual
            # self.unactivate_from_index(self._active_index, anim=True)
            
            # print(f'  active index= {self._active_index}, despues de unactivate')
            # Actualiza la vista para que el nuevo item este visible
            item = self.item_from_index(index)
            if item:
                if self.item_scroll_pos_y(item) + item.height > self.y + self.height:  # Mover el item a la base del RecycleView
                    self.scroll_y += item.height / (self.layout_manager.height - self.height)
            else:
                # print(f'    Scroll por index= {(index +0.5) / len(self.data)}')
                self.scroll_y = 1- (index +0.5) / len(self.data)
        else:
            index = len(self.data) - 1
            item = self.item_from_index(index)
            self.scroll_y = 0

        self.activate_from_index(index, cursor_pos=cursor_pos, anim=True)
        return item

    def active_to_next_item(self, cursor_pos=None):
        # print("MDDocumentEditor.move_to_next_item()")
        # print(f'  Active Index= {self._active_index}')
        if self.active_index > -1:
            item_prev = self.item_from_index(self.active_index)
            index = self.active_index + 1 if self.active_index < len(self.data) - 1 else len(self.data) - 1
            
            # self.unactivate_from_index(self._active_index, anim=True)
            self.unactivate(anim=True)  # Desactiva el modo de edicion del item actual

            # Actualiza la vista para que el nuevo item este visible
            if item_prev:
                if self.item_scroll_pos_y(item_prev) - item_prev.height < 0:
                    self.scroll_y -= item_prev.height / (self.layout_manager.height - self.height)
            else:
                self.scroll_y = 1 - (self.active_index + 0.5) / len(self.data)
        else:
            index = 0
            self.scroll_y = 0
        self.activate_from_index(index, cursor_pos=cursor_pos, anim=True)
        return self.item_from_index(index)

    def activate_from_item(self, item:MDDocumentLineEditor, cursor_pos:tuple=None, anim:bool=False, anim_type:str="point"):
        """
        Activa el item

        Args:
            item (MDDocumentLineEditor): Widget que representa una linea de MDDocument
            cursor_pos (tuple, optional): Posicion del cursor donde se comenzar la animacion "point". Defaults to None.
            anim (bool, optional): Indica si la activacion se anima. Defaults to False.
            anim_type (str, optional): Tipo de Animacion a implementar en la activación. Defaults to "point".
        """
        self.activate_from_data(self.data[self.index_from_item(item)], cursor_pos=cursor_pos, anim=anim, anim_type=anim_type)

    def activate_from_index(self, index, cursor_pos=None, anim=False, anim_type:str="point"):
        """
        Activa el item desde el index

        Args:
            index (int): Indice del Widget que representa una linea de MDDocument
            cursor_pos (tuple, optional): Posicion del cursor donde se comenzar la animacion "point". Defaults to None.
            anim (bool, optional): Indica si la activacion se anima. Defaults to False.
            anim_type (str, optional): Tipo de Animacion a implementar en la activación. Defaults to "point".
        """
        if -1 < index and index < len(self.data):
            self.activate_from_data(self.data[index], cursor_pos=cursor_pos, anim=anim, anim_type=anim_type)

    def activate_from_data(self, data_item, cursor_pos=None, anim=False, anim_type:str="point"):
        '''
        Activa la linea, sola una linea puede estar activa. La que puede editarse y tambien esta seleccionada.
        anim puede ser True, False o una tupla que indica la pos de inicio de la animacion
        '''
        print("MDDocumentEditor.activate_from_data(...))")
        state = data_item['state']
        themed = data_item['themed']
        
        state.selected = True
        state.active = True
        themed.anim = anim
        themed.anim_type = anim_type
        state.cursor = self._cursor if cursor_pos == None else cursor_pos

        print(f'+++ Cursor= {state.cursor} ------------------------------')

        state.mode_editor = self._mode_editor
        self.active_index = self.index_from_data(data_item)
        # Agrega el item a la seleccion
        if not self.active_index in self.selected_indexs:
            self.selected_indexs.append(self.active_index)
        # Guarda copia del texto
        self._old_text_line = data_item['md_line'].md_text
        # Libera el evento
        ActivateItemEventDispatcher.do_something(self, data_item, self.active_index)

    '''Funciones de Items -----------------------------------------------------'''
    def get_previus_data_title(self):
        '''Devuelve el titulo anterior al indice indicado'''
        index = self.active_index
        if -1 < index < len(self.data):
            for ii in range(index - 1, -1, -1):
                if self.data_items[ii]['md_line'].type in (MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE):
                    return self.data_items[ii]
        return None

    def get_next_data_title(self):
        '''Devuelve el siguiente titulo despues del indice indicado'''
        index = self.active_index
        if -1 < index < len(self.data):
            for ii in range(index + 1, len(self.data)):
                if self.data_items[ii]['md_line'].type in (MD_LINE_TYPE.TITLE, MD_LINE_TYPE.HEAD_TITLE):
                    return self.data[ii]
        return None

    ''' Funciones Edicion de Lineas --------------------------------------------'''
    def move_line_to(self, actual_index, new_index):  # Hay que ver que pass con actual y new index por que apuntan al data creo
        '''Mueve la linea de la posicion actual_index a la poscicion new_index'''
        # print('MDDocumentEditor.move_line_to()')
        if new_index > actual_index:  # Mueve hacia arriba
            # print('  Mueve hacia arriba')
            self._md_lines.insert(new_index, self._md_lines.pop(actual_index))  # Mueve MDLine
            self.data_items.insert(new_index, self.data_items.pop(actual_index))  # Mueve el data
            # Ajusta la lista de los indices seleccionados
            for ii in range(len(self.selected_indexs)):
                self.selected_indexs[ii] -= 1
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
            self.active_index -= 1
            # Ajusta el scroll para que el item este visible
            item = self.item_from_index(actual_index)
            if self.item_scroll_pos_y(item) + item.height > self.y + self.height:  # Mover el item a la base del RecycleView
                self.scroll_y += item.height / (self.layout_manager.height - self.height)
            # Actualiza el View
            self.apply_data_items()
            self.refresh_from_data()
        elif new_index < actual_index:  # Mueve hacia abajo
            # print('  Mueve hacia abajo')
            self._md_lines.insert(new_index, self._md_lines.pop(actual_index))  # Mueve MDLine
            self.data_items.insert(new_index, self.data_items.pop(actual_index))  # Mueve el data
            # Ajusta la lista de los indices seleccionados
            for ii in range(len(self.selected_indexs)):
                self.selected_indexs[ii] += 1
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
            self.active_index += 1
            # Ajusta el scroll para que el item este visible
            item = self.item_from_index(actual_index)
            if self.item_scroll_pos_y(item) < 0:  # Mover el item a la base del RecycleView
                self.scroll_y -= item.height / (self.layout_manager.height - self.height)
            # Actualiza el View
            self.apply_data_items()
            self.refresh_from_data()

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
        data_line = DataItemLineMDD(md_line=md_line, data_themed=DataThemed(),
                                    data_show=DataShow(), data_state=DataState())  # DocLineDataDic(index, md_line)
        dic_line = data_line.to_dict()
        self.data_items.append(dic_line)
        # Actualiza el View
        self.refresh_from_data()
        return md_line

    def insert_line(self, index:int, md_text:str=''):
        """Inserta una linea en el indice indicado"""
        # print('MDDocument.insert_lines() -----------------------')
        if -1 < index < len(self._md_lines):
            md_line = MDLine(md_text=md_text,
                            prev_line=self._md_lines[index-1], next_line=self._md_lines[index],
                            type=MD_LINE_TYPE.TEXT, num_line=0)  # TIRA ERROR EN type NO SE POR QUE
            # Inserta md_line y ajusta las dependendencias
            self._md_lines.insert(index, md_line)
            md_line.update_type()
            if index > 0:
                self._md_lines[index - 1].next_line = self._md_lines[index]
            else:
                self._md_lines[index].prev_line = None
            self._md_lines[index + 1].prev_line = self._md_lines[index]
            md_line.num_line = index + 1
            # Inserta en data ---------------------------------------
            data_line = DataItemLineMDD(md_line=md_line, data_themed=DataThemed(),
                                        data_show=DataShow(), data_state=DataState())  # DocLineDataDic(index+1, md_line)
            dic_data_line = data_line.to_dict()
            self.data_items.insert(index, dic_data_line)
            self.update_data_index(index)
            # Refresca el View --------------------------------------
            self.apply_data_items()
            self.refresh_from_data()
            return md_line
        else:
            return None

    def remove_line(self, index:int):
        # Ajusta los indices de los Items Seleccionados
        for ii, value in enumerate(self.selected_indexs, start=0):
            if value > index:
                self.selected_indexs[ii] = value - 1
            # print(f'ii={ii}, value={value}, nuevo valor={self._selected_indexs[ii]}')
        # Borrar en _md_lines y ajusta las dependendencias
        del(self._md_lines[index])
        if index < len(self._md_lines)-1:
            if index > 0:
                self._md_lines[index-1].next_line = self._md_lines[index]
                self._md_lines[index].prev_line = self._md_lines[index-1]
            else:
                self._md_lines[index-1].next_line = None
                self._md_lines[index].prev_line = None
            self._md_lines[index].num_line = index + 1
        # Borra en el data
        del(self.data_items[index])
        self.update_data_index(index)
        # Refresca el View
        self.apply_data_items()
        self.refresh_from_data()

    # def in_editing(self, view:MDDocumentLineEditor, index:int, value:bool, anim:bool=False):
    #     if value is not True and self._mode_editor and self._old_text_line != self.active_md_editor().text:
    #         self.undo_manager.add(_TextModifiedCommand(self, self.active_index, view.old_text_line, self.active_md_editor().text))

    # def update_numlines(self):  # No Hace Falta. Probar sacar
    #     for ii, line in enumerate(self._md_lines):
    #         line.num_line = ii + 1

    '''Eventos de Usuario -----------------------------------------------------'''
    def on_touch_up(self, touch):
        print('MDDocument.on_touch_up->Rueda del mouse')

        if touch.button in ['scrollup', 'scrolldown']:
            for chview in self.layout.children:
                chview.graphic_hotlight.show(False)
                if self.active_index != chview.index:
                    chview.activate(value=False, cursor=None, anim=False)
                else:
                    chview.activate(value=True, cursor=None, anim=False)

        if self.on_scroll_event:
            self.on_scroll_event(self)  # Disparar el evento de scroll sobre el item en edicion
        super(RecycleView, self).on_touch_up(touch)

    # def on_touch_down(self, touch):
    #     # print(f'RecycleListView.on_touch_down')
    #     if self.collide_point_to_window(*touch.pos):
    #         # print(f'  Grab')
    #         touch.grab(self)  # Marca este touch como manejado por este widget
    #     return super().on_touch_down(touch)

    # def on_touch_up(self, touch):  # Hay que ver como con data y data_items. Deberia tener actualizada la informacion de selccion en los dos
    #     # print(f'RecycleListView.on_touch_up {self.uid}, collide_point={self.collide_point(*touch.pos)}')
    #     if touch.grab_current is self:  # Verifica si este widget "grabó" el evento touch
    #         # print('   Con Grab')
    #         # mods = touch.modifiers
    #         # is_shift = 'shift' in Window.keyboard_modifiers
    #         # is_ctrl = 'ctrl' in Window.keyboard_modifiers or 'meta' in Window.keyboard_modifiers

    #         dt_index = self.index_from_pos(touch.pos)

    #         # Verifica que el índice sea válido
    #         if dt_index is None or dt_index < 0 or dt_index >= len(self.data):
    #             touch.ungrab(self)
    #             return False
    #         item = self.item_from_index(dt_index)
    #         data_it = self.data[dt_index]
         

    #         elif touch.button == 'right':  # Modo Edicion (Boton Derecho)
    #             # print('Boton Derecho')
    #             # item.start_editing(self, data)
    #             pass
    #         elif touch.button in ['scrollup', 'scrolldown']:
    #             # print('RecycleListView.on_touch_down->Rueda del mouse')
    #             # item = self.item_from_index(self._active_index)
    #             # if item != None:
    #             #     item.stop_editing(self, data)
    #             touch.ungrab(self)
    #             return False
    #         # print("  ungrab")
    #         touch.ungrab(self)  # Libera el touch
    #         return False
    #     super(RecycleView, self).on_touch_up(touch)

    def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
        print("MDDocumentEditor._on_keyboard_up Codigo de Teclas", keycode, modifier, char, special_keys)
        # print(f'  default_h= {self.layout.default_height}, layout= {self.layout}')
        # print(f'  ul item.y= {item.y}')
        # print(f'  h Layout= {self.layout.height}, h layout manager= {self.layout_manager.height}')
        # print(f'   UID:{self.uid}')
        if MDDocumentEditor.instance_focus == self and self.theme.level_render != 'high':
            # print(f'    Instancia con Foco y nivel bajo')
            md_editor = self.active_md_editor()
            active_view = self.active_view
            in_edition = active_view.di_state.mode_editor if active_view is not None else False  ## TODO: Usar un if general para ejecutar los if con esta condicion
            self._cursor = md_editor.cursor if md_editor is not None else (0, 0)  # self.item_from_index(self._active_index).wg_line_editor.md_editor.cursor
            
            # Flecha arriba + Ctrl + Shift, mueve el bloque hacia arriba
            if keycode == 273 and all(kk in special_keys for kk in ['shift', 'ctrl']):  # Mueve el bloque hacia arriba
                print('  Flecha Arriba con Ctrl y Shift (mueve el bloque hacia arriba)')
                # Se supone que la lista es continua sin seleccion intercalada.
                # En este contecto borro la lines superior a la seleccion y la pego debajo de la seleccion
                ix_actual = min(self._selected_indexs) - 1
                ix_new = max(self._selected_indexs)
                if ix_actual > -1:
                    self.undo_manager.execute(_MoveLinesCommand(self, ix_actual, ix_new))
            
            # Flecha abajo + Ctrl + Shift, mueve el bloque hacia abajo
            elif keycode == 274 and all(kk in special_keys for kk in ['shift', 'ctrl']):  # Mueve el bloque hacia abajo
                # Se supone que la lista es continua sin seleccion intercalada.
                # En este contecto borro la lines inferior a la seleccion y la pego sobre la seleccion
                ix_new = min(self._selected_indexs)
                ix_actual = max(self._selected_indexs) + 1
                if ix_actual < len(self.data):
                    self.undo_manager.execute(_MoveLinesCommand(self, ix_actual, ix_new))
            
            # Flecha arriba + Ctrl, mueve al Título anterior
            elif keycode == 273 and 'ctrl' in special_keys:  # Flecha arriba + Ctrl, mueve al Título anterior
                print('  Flecha Arriba con Ctrl (mueve al Título anterior)')
                data = self.get_previus_data_title()
                if data:
                    self.unactivate()  # Desactiva el modo edicion
                    self.activate_from_data(data, anim=True)  # Activa el item
                    self.scroll_to_index(data['index'])

            # Flecha abajo + Ctrl, mueve al Siguiente Título
            elif keycode == 274 and 'ctrl' in special_keys:  # Flecha abajo + Ctrl, mueve al Siguiente Título
                print('  Flecha Abajo con Ctrl (mueve al Siguiente Título)')
                data = self.get_next_data_title()
                if data:
                    self.unactivate()  # Desactiva el modo edicion
                    self.activate_from_data(data, anim=True)  # Activa el item
                    self.scroll_to_index(data['index'])


            # Ctrl + C, Copiar linea/s seleccionada
            elif not in_edition and char == 'c' and 'ctrl' in special_keys:  # Ctrl + C, Copiar
                # print(f'texto seleccionado: {md_editor.selection_text}')
                # Crea el texto a copiar

                # SACAR not in_edition and Y VERIFICAR SI EL TEXTO EN EDICION LA SELECCION ES 0 COPIA LA LINEA SINO RETORNA TRUE

                if not in_edition or len(md_editor.selection_text) == 0:
                    cp_txt = ''
                    for ii in range(0, len(self._selected_indexs)-1):
                        cp_txt += self._md_lines[self._selected_indexs[ii]].md_text + '\n'
                    cp_txt += self._md_lines[self._selected_indexs[len(self._selected_indexs)-1]].md_text
                    Clipboard.copy(cp_txt)
                    return True
                else:
                    return False
            
            # Ctrl + V, Pegar linea/s en la papelera
            elif not in_edition and char == 'v' and 'ctrl' in special_keys:  # Ctrl + V, Pegar
                # print('  Ctrl + v')
                pasted_text = Clipboard.paste()
                if isinstance(pasted_text, str):  # Verifica compatibilidad del texto
                    pasted_list = pasted_text.splitlines(keepends=False)
                    print(f'  Lista de lineas: {pasted_list}')
                    # Define el punto de inserción
                    u_line = len(self._md_lines)
                    if not in_edition or len(pasted_list) > 1:
                        ix_i = self.active_index + 1 if self.active_index > -1 and self.active_index < u_line else u_line
                        print(f'    ix_i= {ix_i}, u line= {u_line}')
                        # Inserta las lineas
                        self.undo_manager.execute(_InsertLinesCommand(self, self.active_index, pasted_list))

                        # for id, txt in enumerate(pasted_list, start=0):
                        #     if ix_i < u_line:
                        #         self.insert_line(ix_i+id, txt)
                        #     else:
                        #         self.append_line(txt)
                        return True
                    else:
                        return False
            
            # Ctrl + X, Cortar linea/s seleccionada
            elif not in_edition and char == 'x' and 'ctrl' in special_keys:  # Ctrl + X, Cortar
                # Corta la seleccion
                print('  Ctrl + x')
                # Crea el texto a copiar
                if not in_edition or len(md_editor.selection_text) == 0:
                    cp_txt = ''
                    for ii in range(0, len(self._selected_indexs) - 1):
                        cp_txt += self._md_lines[self._selected_indexs[ii]].md_text + '\n'
                        #self.remove_line(self._selected_indexs[ii])
                    cp_txt += self._md_lines[self._selected_indexs[len(self._selected_indexs) - 1]].md_text
                    # self.remove_line(self._selected_indexs[len(self._selected_indexs) - 1])  TODO UNDO REMOVE_LINE
                    self.undo_manager.execute(_RemoveLinesCommand(self, self._selected_indexs))
                    Clipboard.copy(cp_txt)
                    return True
                else:
                    return False
            
            # Ctrl + Z, Deshacer ultima accion
            elif not in_edition and char == 'z' and 'ctrl' in special_keys:  # Ctrl + Z, Deshacer
                self.undo_manager.undo()
                return True
            
            # Ctrl + Y, Rehacer ultima accion
            elif not in_edition and char == 'y' and 'ctrl' in special_keys:  # Ctrl + Y, Rehacer
                self.undo_manager.redo()
                return True
            
            # Ctrl + A, Selecciona todo el documento
            elif keycode == 65 and 'ctrl' in special_keys:  # Ctrl + A, Selecciona todo el documento
                print('  Ctrl + A')
                self.unactivate()  # Desactiva el modo edicion
                self._selected_indexs.clear()  # Limpia la lista de seleccionados
                for ii in range(len(self.data)):
                    self._selected_indexs.append(ii)
                for data_item in self.data:
                    data_item['selected'] = True
                self.refresh_from_data()  # Actualiza el view
                self.activate_from_index(len(self.data)-1, anim=False)  # Activa el ultimo item
                self.in_editing(False)  # Desactiva el modo edicion
                return True

            # Flecha arriba + Shift, Extiende la seleccion hacia la linea de arriba
            elif keycode == 273 and 'shift' in special_keys and self.active_index != 0:  # Extiende la seleccion hacia la linea de arriba
                self.in_editing(False)  # Inhabilita el modo edicion
                self.active_index -= 1  # Mueve el item activado
                # Agrega o borra de la lista de seleccionados
                if self.active_index in self._selected_indexs:  # Des-selecciona
                    self.unselect_index(self.active_index+1, anim=False)
                else:
                    self.select_index(self.active_index, anim=False)
                    item = self.item_from_index(self.active_index)
                    if self.item_scroll_pos_y(item) + item.height > self.y + self.height:  # Mover el item a la base del RecycleView
                        self.scroll_y += item.height / (self.layout_manager.height - self.height)
            
            # Flecha abajo + Shift, Extiende la seleccion hacia la linea de abjajo
            elif keycode == 274 and 'shift' in special_keys and self.active_index != len(self.data)-1:  # # Extiende la seleccion hacia la linea de abajo
                self.in_editing(False)  # Inhabilita el modo edicion
                self.active_index += 1  # Mueve el item activado
                # Agrega o borra de la lista de seleccionados
                if self.active_index in self._selected_indexs:  # Des-selecciona
                    self.unselect_index(self.active_index-1, anim=False)
                else:
                    self.select_index(self.active_index, anim=False)
                    item = self.item_from_index(self.active_index)
                    if self.item_scroll_pos_y(item) < 0:  # Mover el item a la base del RecycleView
                        self.scroll_y -= item.height / (self.layout_manager.height - self.height)
            
            # Flecha Arriba, Activa la linea de arriba
            elif keycode == 273 and self.active_index != 0:  # Flecha Arriba
                print(f'  Flecha Arriba')
                # TODO: Verificar si esta presionado SHIFT o CTRL y seleccionar el rango
                self.active_to_previus_item()
            
            # Flecha Abajo, Activa la linea de abajo
            elif keycode == 274 and self.active_index != len(self.data)-1:  # Flecha Abajo
                # TODO: Verificar si esta presionado SHIFT o CTRL y seleccionar el rango
                self.active_to_next_item()
            
            # Flecha Derecha y cursor al final de linea, activa la linea de abajo y mueve el cursor al principio de la linea
            elif keycode == 275 and self.active_index != len(self.data)-1 and self._cursor[0] == len(md_editor.text):  # Flecha Derecha
                print('  Flecha Derecha')
                self.active_to_next_item(cursor_pos=(0, 0))
            
            # Flecha Izquierda y cursor al principio de linea, activa la linea de arriba y mueve el cursor al final de la linea
            elif keycode == 276 and self.active_index != 0 and self._cursor[0] == 0:  # Flecha Izquierda
                print(f'  Flecha izquierda, active index= {self.active_index}')
                cur_x = len(self.data[self.active_index-1]['md_line'].md_text)
                self.active_to_previus_item(cursor_pos=(cur_x, 0))
            
            # F2, Activa o desactiva el modo edicion
            elif keycode == 283:  # Tecla F2
                self._mode_editor = not(self._mode_editor)
                self.in_editing(self._mode_editor)
                
                return True
            
            # Escape, desactiva el modo edicion sin guardar los cambios
            
            elif keycode == 27:  # Tecla Escape  # OK 25-10
                md_editor.md_text = md_editor._mdtext_back
                active_view.show_editor(show=False, anim=False)  # Desactiva el modo edicion

            # Enter o Intro, genera un salto de linea
            elif in_edition and (keycode == 13 or keycode == 271):  # Tecla Enter o Intro
                self.undo_manager.execute(_EnterInEditionCommand(self))
            
            # Backspace con cursor al inicio de linea, fusiona la linea con la linea de arriba
            elif keycode == 8 and self.active_index != 0 and self._cursor[0] == 0: # Tecla Backspace
                print('  Tecla Backspace -> Fusiona la linea con la linea de arriba')
                
                # text = md_editor.text
                # print(f'    text: {text}')
                # self.remove_line(self._active_index)
                # cpos = len(self._md_lines[self._active_index-1].md_text)
                # self._md_lines[self._active_index -1].md_text += text
                # self.activate_from_index(self._active_index-1, cursor_pos=(cpos, 0))

                self.undo_manager.execute(_BackspaceOnStartLineCommand(self))
            
            # Suprimir (Delete) con cursor al final de linea en modo edicion, fusiona la linea con la linea de abajo
            elif keycode == 127 and self.active_index != len(self.data)-1 and self._cursor[0] == len(md_editor.text) \
                    and len(self._selected_indexs) == 1 and in_edition:  # Tecla Suprimir (Delete) en modo edicion
                print('  Tecla Suprimir -> Fusiona la linea con la linea de abajo')
                # cur_pos = len(self._md_lines[self._active_index].md_text)
                # self._md_lines[self._active_index].md_text += self._md_lines[self._active_index+1].md_text  # agrega el texto de la linea inferior
                # self.data[self._active_index]['cursor'] = (cur_pos, 0)  # Posiciona el cursor
                # self.remove_line(self._active_index+1)  # borra la linea de abajo
                # self.data[self._active_index+1]['md_line'].num_line = self.data[self._active_index]['md_line'].num_line + 1  # actualiza nro linea, prev y next
            
                self.undo_manager.execute(_DeleteOnEndLineCommand(self))

            # Suprimir (Delete) en modo no edicion, borra la linea/s seleccionada
            elif keycode == 127 and len(self._selected_indexs) > 0 and not in_edition:  # Tecla Suprimir en modo no edicion
                self.undo_manager.execute(_RemoveLinesCommand(self, self._selected_indexs))
                # self.data[self._selected_indexs[len(self._selected_indexs)-1]]['selected'] = True
            
            # Page Up, desplaza la vista hacia arriba
            elif keycode == 280:  # tecla page up
                print('  Tecla PageUp')
                delta = len(self.layout.children) - 2
                new_center_ix = self.layout.children[int(delta / 2)].index - delta   #este hay que sacarlo
                if new_center_ix > 0:
                    self.scroll_y += self.height / (self.layout_manager.height - self.height)
                else:
                    self.scroll_y = 1
            
            # Page Down, desplaza la vista hacia abajo
            elif keycode == 281:  # tecla page down
                # print('  Tecla PageDown')
                delta = len(self.layout.children) - 2
                new_center_ix = self.layout.children[int(len(self.layout.children)/2)].index + delta
                if new_center_ix < len(self.data):
                    self.scroll_y -= self.height / (self.layout_manager.height - self.height)
                else:
                    self.scroll_y = 0
            
            # Si no se reconoce la tecla, retorna False para que el evento no se consuma
            return False

        
    
    # Manejadores de Eventos de Items Hijos -----------------------------------
    def handle_hotlight_event(self, index:int, view:MDDocumentLineEditor, active:bool):
        """Se ejecuta desde GHotlightItem cuando se activa o des-activa el hotlight"""
        self.hotlight = active

    def handle_touch_left_up_event(self, index:int, view:MDDocumentLineEditor, touch):
        """
        Manejador del evento on_touch_up de MDDocumentLineEditor
        Nota: La activacion del view se realiza desde MDDocumentLineEditor
        Args:
            index: indice de data del view a activar
            view: view a activar
        """
        # Desactiva el resto de los Items
        # Des-Selecciona todos y Selecciona el Activo
        if self.active_view is not None:
            self.active_view.activate(value=False, cursor=None, anim=True, anim_type='fade')
        if self.selected_indexs is not None:
            for ix in self.selected_indexs:
                self.data[ix]['state'].selected = False
                self.data[ix]['state'].active = False
            self.selected_indexs.clear()
            self.selected_indexs.append(index)
        for chview in self.layout.children:
            if self.active_index != chview.index:
                chview.activate(value=False, cursor=None, anim=False)
            # else:
            #     chview.graphic_select.show(False)
        # Asigna el Item Activo
        self.active_index = index
        self.active_view = view
        # Lanza el evento de Activacion 
        ActivateItemEventDispatcher.do_something(self, view, index)


        


# --- Funciones Undo  ---------------------------------------------------------------------------
class _RemoveLinesCommand(Command):
    def __init__(self, md_doc_editor:MDDocumentEditor, indexs:list):
        # Los indices pueden no ser correlativos ???
        self.md_doc_editor = md_doc_editor
        self.indexs = indexs.copy()
        self.md_text = [md_doc_editor._md_lines[indice].md_text for indice in indexs]
        self.data = [md_doc_editor.data[indice] for indice in indexs]

    def execute(self):
        indexs = self.indexs[:]
        for ii, value_ii in enumerate(indexs):  # Ajusta los indices de los Items Seleccionados
            for jj, value_jj in enumerate(indexs):
                if value_jj > value_ii:
                    indexs[jj] = value_jj - 1
            self.md_doc_editor.remove_line(value_ii)  # Remueve los items
        self.md_doc_editor.unactivate()  # Des Activa el item actual
        idx = self.indexs[-1] if self.indexs[-1] < len(self.md_doc_editor.data) else len(self.md_doc_editor.data)-1
        self.md_doc_editor.activate_from_index(idx, anim=False)  # Activa el item nuevo
        self.md_doc_editor.in_editing(False)  # Desactiva el modo edicion

    def undo(self):
        # self.md_doc_editor.in_editing(False)  # Desactiva el modo edicion
        self.md_doc_editor.unactivate()  # Desactiva el item actual
        for ii, value_ii in enumerate(self.indexs):  # Re Inserta las lineas
            if value_ii > len(self.md_doc_editor.data)-1:
                self.md_doc_editor.append_line(self.md_text[ii])
            else:  # Podria verificar tambien que sea > -1
                self.md_doc_editor.insert_line(value_ii, self.md_text[ii])
        self.md_doc_editor.select_indexs(self.indexs[:])  # Re Seleccion las lineas
        self.md_doc_editor.activate_from_index(value_ii, anim=False)  # Activa la ultima linea de la seleccion
        self.md_doc_editor.in_editing(False)
        # self.md_doc_editor.refresh_from_data()


class _InsertLinesCommand(Command):  # Es la inversa de Borrar.
    # Probar con Ctrl + v
    def __init__(self, md_doc_editor:MDDocumentEditor, index:int, md_text_list:list):
        self.md_doc_editor = md_doc_editor
        self.index = index  # Se asigna en la insercion para poder borrar en undo
        self.md_text = md_text_list

    def execute(self):
        # self.md_doc_editor.in_editing(False)  # Desactiva el modo edicion
        # self.md_doc_editor.unactivate_from_index(self.md_doc_editor._active_index, anim=False)  # Desactiva el item actual
        # self.index = self.md_doc_editor._active_index RESTO TIENE QUE SER EN LA PRIMERA EJECUCION
        self.md_doc_editor.unactivate()  # Des Activa el item actual
        select = []
        for ii in  range(len(self.md_text)):  # Re Inserta las lineas
            index = self.index + ii + 1
            self.md_doc_editor.insert_line(index, self.md_text[ii])
            select.append(index)
        self.md_doc_editor.select_indexs(select)  # Re Seleccion las lineas
        self.md_doc_editor.activate_from_index(index, anim=False)  # Activa la ultima linea de la seleccion
        self.md_doc_editor.in_editing(False)  # Desactiva el modo edicion
        # self.md_doc_editor.refresh_from_data()

    def undo(self):
        for ii in range(len(self.md_text)):  # Ajusta los indices de los Items Seleccionados
            self.md_doc_editor.remove_line(self.index + 1)  # Remueve los items
        self.md_doc_editor.unactivate()  # Des Activa el item actual
        self.md_doc_editor.activate_from_index(self.index + 1, anim=False)  # Activa el item nuevo
        self.md_doc_editor.in_editing(False)  # Desactiva el modo edicion


class _MoveLinesCommand(Command):
    def __init__(self, md_doc_editor: MDDocumentEditor, actual_index: int, new_index: int):
        self.md_doc_editor = md_doc_editor
        self.actual_index = actual_index
        self.new_index = new_index

    def execute(self):
        self.md_doc_editor.move_line_to(self.actual_index, self.new_index)

    def undo(self):

        self.md_doc_editor.move_line_to(self.new_index, self.actual_index)



class _TextModifiedCommand(Command):
    """Comando para modificar el texto de una linea en el editor de documentos Markdown.
    Nota: Se llama siempre desde in_editing() cuando se cambia el texto de una linea"""
    def __init__(self, md_doc_editor: MDDocumentEditor, index: int, old_text: str, new_text: str):
        self.md_doc_editor = md_doc_editor
        self.old_index = index
        self.new_index = None
        self.old_text = old_text
        self.new_text = new_text

    def execute(self):
        self.md_doc_editor._md_lines[self.old_index].md_text = self.new_text
        self.md_doc_editor.unactivate()
        self.md_doc_editor.activate_from_index(self.new_index)
        self.md_doc_editor.refresh_from_data()

    def undo(self):
        self.new_index = self.md_doc_editor.active_index
        self.md_doc_editor._md_lines[self.old_index].md_text = self.old_text
        self.md_doc_editor.unactivate()
        self.md_doc_editor.activate_from_index(self.old_index)  # Activa la linea modificada
        self.md_doc_editor.refresh_from_data()


class _EnterInEditionCommand(Command):
    """Comando que se ejecuta cuando se presiona la tecla Enter o Intro en el editor de documentos Markdown."""
    def __init__(self, md_doc_editor: MDDocumentEditor):
        self.md_doc_editor = md_doc_editor
        self.index = self.md_doc_editor.active_index
        self.text = self.md_doc_editor.active_md_editor().text[self.md_doc_editor._cursor[0]:]

    def execute(self):
        self.md_doc_editor.insert_line(self.index + 1, self.text)
        self.md_doc_editor._md_lines[self.index].md_text = self.md_doc_editor._md_lines[self.index].md_text[:-len(self.text)]  # Elimina el texto de la linea actual
        self.md_doc_editor._md_lines[self.index + 1].num_line = self.md_doc_editor._md_lines[self.index].num_line + 1
        self.md_doc_editor._md_lines[self.index].update_type()  # Actualiza el tipo de linea
        self.md_doc_editor._md_lines[self.index + 1].update_type()  # Actualiza el tipo de linea
        self.md_doc_editor.unactivate()
        self.md_doc_editor.activate_from_index(self.index + 1)
        self.md_doc_editor.refresh_from_data()

    def undo(self):
        self.md_doc_editor.remove_line(self.index + 1)
        self.md_doc_editor._md_lines[self.index].md_text += self.text
        self.md_doc_editor._md_lines[self.index + 1].num_line = self.md_doc_editor._md_lines[self.index].num_line + 1
        self.md_doc_editor._md_lines[self.index].update_type()  # Actualiza el tipo de linea
        self.md_doc_editor.unactivate()
        self.md_doc_editor.activate_from_index(self.index)
        self.md_doc_editor.refresh_from_data()


class _DeleteOnEndLineCommand(Command):
    """Comando que se ejecuta cuando se presiona la tecla Delete al final de una linea en el editor de documentos Markdown."""
    def __init__(self, md_doc_editor: MDDocumentEditor):
        self.md_doc_editor = md_doc_editor
        self.index = self.md_doc_editor.active_index
        self.text = self.md_doc_editor._md_lines[self.index + 1].md_text[:]

    def execute(self):
        if self.index < len(self.md_doc_editor._md_lines) - 1:
            self.md_doc_editor._md_lines[self.index].md_text += self.text
            self.md_doc_editor._md_lines[self.index + 1].num_line = self.index + 1
            self.md_doc_editor._md_lines[self.index].update_type()
            self.md_doc_editor.remove_line(self.index + 1)
            if not self.md_doc_editor.in_editing:
                self.md_doc_editor.unactivate()
                self.md_doc_editor.activate_from_index(self.index)
            self.md_doc_editor.refresh_from_data()


    def undo(self):
        # Restaura el texto original de la línea que fue modificada.
        original_line = self.md_doc_editor._md_lines[self.index]
        if self.text:
            original_line.md_text = original_line.md_text[:-len(self.text)]
        original_line.update_type()
        # Vuelve a insertar la línea que fue eliminada.
        self.md_doc_editor.insert_line(self.index + 1, self.text)
        # Gestiona el foco y refresca la vista.
        self.md_doc_editor.unactivate()
        self.md_doc_editor.activate_from_index(self.index)
        self.md_doc_editor.refresh_from_data()


class _BackspaceOnStartLineCommand(Command):
    """Comando que se ejecuta cuando se presiona la tecla Backspace al inicio de una linea en el editor de documentos Markdown."""
    def __init__(self, md_doc_editor: MDDocumentEditor):
        self.md_doc_editor = md_doc_editor
        self.index = self.md_doc_editor.active_index
        self.text = self.md_doc_editor._md_lines[self.index].md_text[:]

    def execute(self):
        if self.index > 0:
            prev_line = self.md_doc_editor._md_lines[self.index - 1]
            cursor_pos = len(prev_line.md_text)
            prev_line.md_text += self.text
            prev_line.update_type()
            self.md_doc_editor.remove_line(self.index)
            self.md_doc_editor._md_lines[self.index - 1].num_line = prev_line.num_line
            # if not self.md_doc_editor.in_editing:
            self.md_doc_editor.unactivate()
            self.md_doc_editor.activate_from_index(self.index - 1)
            self._cursor = (cursor_pos, 0)  # Posiciona el cursor al final de la linea anterior
            self.md_doc_editor.data[self.index - 1]['cursor'] = self._cursor  # Posiciona el cursor al final de la linea anterior
            self.md_doc_editor.refresh_from_data()

    def undo(self):
        # Restaura el texto original de la línea que fue modificada.
        original_line = self.md_doc_editor._md_lines[self.index - 1]
        original_line.md_text = original_line.md_text[:-len(self.text)]
        original_line.update_type()
        # Vuelve a insertar la línea que fue eliminada.
        # Gestiona el foco y refresca la vista.
        self.md_doc_editor.unactivate()
        self.md_doc_editor.activate_from_index(self.index - 1)
        self.md_doc_editor.insert_line(self.index, self.text[:])
        self._cursor = (0, 0)  # Posiciona el cursor al final de la linea anterior
        self.md_doc_editor._md_lines[self.index].num_line = original_line.num_line + 1
        self.md_doc_editor.data[self.index]['cursor'] = self._cursor  # Posiciona el cursor al final de la linea anterior
        self.md_doc_editor.refresh_from_data()


