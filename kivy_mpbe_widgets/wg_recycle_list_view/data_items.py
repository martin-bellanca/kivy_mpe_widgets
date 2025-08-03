#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tree_panels.py
#
#  Copyright 2020 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License fo
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


'''
Items ListView widget for kivy_dkw \n
Created on 06/10/2024

@author: mpbe
@note:
'''
import os

from setuptools.command.saveopts import saveopts

# imports del sistema -------------------------------------------------------

# imports helpers mpbe ------------------------------------------------------
from helpers_mpbe.python import compose, compose_dict
from helpers_mpbe.python import FolderWrapper, FileWrapper
# Kivy imports --------------------------------------------------------------
import kivy
kivy.require('1.10.1')
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty, BoundedNumericProperty
# from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# from kivy.uix.image import Image
# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from helpers_mpbe.utils import rgba_to_hex_with_alpha as rgb_to_hex
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.events.widgets_events import HotlightEventDispatcher
from kivy_mpbe_widgets.events.input_events import StartEditingEventDispatcher, FinishEditingEventDispatcher
from kivy_mpbe_widgets.graphics.items_graphics import GHotlightItem, GFocusItem, GSelectItem
from kivy_mpbe_widgets.events.list_view_events import SelectItemEventDispatcher, UnSelectItemEventDispatcher
from kivy_mpbe_widgets.wg_buttons.toggle_buttons import ToggleButton, ToggleButtonLabel
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickIcon
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel as Label
from kivy_mpbe_widgets.wg_labels.font_icon_labels import FontIconLabel
# from kivy_dkw.wg_font_icons.font_icon import FontIcon
from kivy_mpbe_widgets.wg_labels.font_icon_labels import FontIconWText, FontIconLabel
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_inputs.inputs import EditableTextLabel


Builder.load_string('''
<BaseItem>:
    size_hint_y: None
    height: 50
    canvas.before:
        # Fondo ---------------------------------------------------
        Color:
            rgba: 0.8, 0.8, 0.8, self.alpha_background  # Fondo gris claro
        Rectangle:
            size: self.size[0]-self.theme.geometry['border_width']*2, self.size[1]
            pos: self.pos[0]+self.theme.geometry['border_width'], self.pos[1]
        Color:
            rgba: 0.4, 0.4, 0.4, 0.4  # Borde inferior gris oscuro
        Line:
            width: 1
            points: self.x+self.theme.geometry['border_width']+1, self.y, self.right-self.theme.geometry['border_width']*2, self.y
''')


# ------------------------------------------------------------------------------------------------------------------
class BaseDataDic:
    '''Clase para definir el diccionario para el Recycle List View'''
    def __init__(self, id=None, selected=False, start_anim=False, state_background=False):
        self._state_background = state_background
        # self.index = index
        self.l_id = id
        self.selected = selected  # puede ser 'select, to_select, unselect, to_unselect' los 'to_' se animados
        self.start_anim = start_anim  # indica si se anima la seleccion o des-seleccion, false no anima, true o coordenadas de inicio anima

    def to_dict(self):
        """
        Devuelve el diccionario de MDDocumentEditor
        Dict Parameters:
            id (int): nro. de linea.
            selected (bool): Indica si el item esta seleccionado.
            state_background (bool): Indica si se sombrea el fondo. Es para el pintado intercalado.
        """
        return {'l_id': self.l_id, 'selected':self.selected, 'start_anim':self.start_anim,
                'state_background':self._state_background}


class BaseItem_BACK(RecycleDataViewBehavior, ThemeWidget, HotlightEventDispatcher):
    selectable = BooleanProperty(True)
    editable = BooleanProperty(True)  # Define si el item se puede editar
    alpha_background = BoundedNumericProperty(defaultvalue=0.0, min=0.0, max=1.0)

    def __init__(self):
        """
        Constructor BaseItem class
        """
        RecycleDataViewBehavior.__init__(self)
        ThemeWidget.__init__(self)
        HotlightEventDispatcher.__init__(self)
        self.index = -1  # indice actual
        self.in_edition = False  # Define si el item esta en modo edicion
        self._touch_pos = (0, 0)
        self._state_background = None
        self._selected = False
        # Canvas -----------------------------------------------------
        with self.canvas.before:
            self.graphic_select = GSelectItem(self)
        with self.canvas.after:
            self.graphic_focus = GFocusItem(self)
            self.graphic_hotlight = GHotlightItem(self)

    def get_selected(self):
        return self._selected

    selected = property(get_selected)

    # Funciones UI ------------------------------------------------------
    def select_item(self, rv, data):
        # print('BaseItem.select ffff-------------------')
        rv.focus = True
        self._selected = True
        data['selected'] = True
        # data['selected'] = 'selected'
        # print(f'RV:{rv.uid}  {rv.focus}')

    def is_selected(self):
        return self._selected

    def unselect_item(self, rv, data):
        print('BaseItem.unselect ffff-------------------')
        self._selected = False
        data['selected'] = False
        pass

    def start_editing(self, rv, data):
        pass

    def stop_editing(self, rv, data):
        pass

    def _hotlight_event(self, state, mouse_pos):
        HotlightEventDispatcher.do_something(self, state, mouse_pos)

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
        '''
        # print(f'BaseItem.refresh_view_attrs uid={rv.uid} - item={index}')
        self.index = index
        # Establece el fondo -------------------------------
        if rv.activate_background:
            self._state_background = True if index % 2 == 0.0 else False  # Par / Impar
            self.apply_background(self._state_background)
        # # Define la altura ---------------------------------
        # if 'height' in data:
        #     self.height = data['height']  # Cambia la altura si está definida en los datos
        # Establece el estado de seleccion -----------------

        # if self._selected != data['selected']:
        self._selected = data['selected']
        if data['start_anim'] == True:
            pos_ini = (self.x + 10, self.y + self.height / 2)
        elif isinstance(data['start_anim'], tuple):
            pos_ini = data['start_anim']
        else:
            pos_ini = False

        if self._selected:  # select  (selecciona sin amimar)
            if pos_ini:
                self.graphic_select.animate_select(True, pos_ini)
            else:
                self.graphic_select.show(True)
            # self.graphic_focus.show(True)
            self.editable = True
            rv._select_index = index
            rv._item_selected = self
        else:  # unselect (des-selecciona sin animar)
            if pos_ini:
                self.graphic_select.animate_select(False, pos_ini)
            else:
                self.graphic_select.show(False)
            # self.graphic_focus.show(False)
            self.editable = False
        # print(f'BaseItem.refresh_view_attrs - data: {data}')
        # return RecycleDataViewBehavior.refresh_view_attrs(self, rv, index, data)

    # Funciones de Animacion ------------------------------------------------
    def apply_background(self, value):
        if value == True:
            self.alpha_background = 0.2
        else:
            self.alpha_background = 0.0

    # def collide_point_focus(self, x, y):  # on windows coordinates
    #
    #     bx, by = self.pos
    #     bw, bh = self.size
    #     return bx <= x <= bx + bw and by <= y <= by + bh



class BaseItem(RecycleDataViewBehavior, ThemeWidget, HotlightEventDispatcher):
    selectable = BooleanProperty(True)
    editable = BooleanProperty(True)  # Define si el item se puede editar
    alpha_background = BoundedNumericProperty(defaultvalue=0.0, min=0.0, max=1.0)

    def __init__(self):
        """
        Constructor BaseItem class
        """
        RecycleDataViewBehavior.__init__(self)
        ThemeWidget.__init__(self)
        HotlightEventDispatcher.__init__(self)
        self.index = -1  # indice actual
        self.in_edition = False  # Define si el item esta en modo edicion
        self._touch_pos = (0,0)
        self._state_background = None
        self._selected = False
        # Canvas -----------------------------------------------------
        with self.canvas.before:
            self.graphic_select = GSelectItem(self)
        with self.canvas.after:
            self.graphic_focus = GFocusItem(self)
            self.graphic_hotlight = GHotlightItem(self)

    def get_selected(self):
        return self._selected
    selected = property(get_selected)

    # Funciones UI ------------------------------------------------------
    def select_item(self, rv, data):
        # print('BaseItem.select ffff-------------------')
        rv.focus =True
        self._selected = True
        data['selected'] = True
        # data['selected'] = 'selected'
        # print(f'RV:{rv.uid}  {rv.focus}')

    def is_selected(self):
        return self._selected

    def unselect_item(self, rv, data):
        # print('BaseItem.unselect ffff-------------------')
        self._selected = False
        data['selected'] = False
        pass




    def start_editing(self, rv, data):
        pass

    def stop_editing(self, rv, data):
        pass

    def _hotlight_event(self, state, mouse_pos):
        HotlightEventDispatcher.do_something(self, state, mouse_pos)

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
        '''
        # print(f'BaseItem.refresh_view_attrs uid={rv.uid} - item={index}')
        self.index = index
        # Establece el fondo -------------------------------
        if rv.activate_background:
            self._state_background = True if index % 2 == 0.0 else False  # Par / Impar
            self.apply_background(self._state_background)
        # # Define la altura ---------------------------------
        # if 'height' in data:
        #     self.height = data['height']  # Cambia la altura si está definida en los datos
        # Establece el estado de seleccion -----------------

        # if self._selected != data['selected']:
        # self._selected = data['selected']
        if data['start_anim'] == True:
            pos_ini = (self.x+10, self.y+self.height/2)
        elif isinstance(data['start_anim'], tuple):
            pos_ini = data['start_anim']
        else:
            pos_ini = False

        if data['selected'] != self._selected:
            self._selected = data['selected']


            if self._selected:  # select
                if pos_ini:
                    self.graphic_select.animate_select(True, pos_ini)
                else:
                    self.graphic_select.show(True)
                # self.graphic_focus.show(True)
                self.editable = True
                rv._select_index = index
                rv._item_selected = self
                rv.focus = True
            else:  # unselect
                if pos_ini:
                    self.graphic_select.animate_select(False, pos_ini)
                else:
                    self.graphic_select.show(False)
                # self.graphic_focus.show(False)
                self.editable = False
                if rv._select_index == index:
                    rv._select_index = -1
                    rv._item_selected = None
        # print(f'BaseItem.refresh_view_attrs - data: {data}')
        # return RecycleDataViewBehavior.refresh_view_attrs(self, rv, index, data)

    # Funciones de Animacion ------------------------------------------------
    def apply_background(self, value):
        if value == True:
            self.alpha_background = 0.2
        else:
            self.alpha_background = 0.0





# ------------------------------------------------------------------------------------------------------------------
class TextDataDic(BaseDataDic):
    '''Clase para definir el diccionario para el Recycle List View'''
    def __init__(self, id=None, text='', selected=False, state_background=False):
        BaseDataDic.__init__(self, id, selected, state_background)
        self.text = text

    def to_dict(self):
        return BaseDataDic.to_dict(self) | {'text':self.text, 'selected':self.selected}


class TextItem(BaseItem):
    text = StringProperty(defaultvalue="")

    def __init__(self):
        """
        Constructor class
        Args:
            text (str)       : text of item
        """
        super().__init__()
        self._label = TextLabel(text='', font_style='body', valign="center", size_hint=(1, 1))
        self._label.font_size = 16
        self._label.bold = False
        self._label.padding_x = 2 + self.theme.geometry['border'] + self.theme.geometry['hotlight']

        self.add_widget(self._label)
        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)

    def _on_update_geometry(self, instance, value):
        self._label.pos = self.pos
        self._label.size = self.size

    def on_text(self, instance, value):
        self.text = value
        self._label.text = value

    # Funciones de RecycleDataViewBehavior -------------------------------------
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes - se ejecuta cuando hay un cambio en data'''
        # Asigna el Texto ---------------------------------
        if 'text' in data:
            self.text = data['text']  # Cambia el texto
        return super(TextItem, self).refresh_view_attrs(rv, index, data)



# TODO: No andan las flechas derecha y izquierda al editar
# TODO: En modo edicion al hacer click en el item en edicion lo cierra, deberia mover el cursor a esa posicion

# ------------------------------------------------------------------------------------------------------------------
class EditableDataDic(BaseDataDic):
    '''Clase para definir el diccionario para el Recycle List View'''
    def __init__(self, id=None, text='', selected=False, state_background=False):
        BaseDataDic.__init__(self, id, selected, state_background)
        self.text = text

    def to_dict(self):
        return BaseDataDic.to_dict(self) | {'text':self.text}  # , 'selected':self.selected


class EditableItem(BaseItem, StartEditingEventDispatcher, FinishEditingEventDispatcher):  #SEGUIR DE ACA
    text = StringProperty(defaultvalue="")

    def __init__(self):
        """
        Constructor class
        Args:
            text (str)       : text of item
        """
        self._label = EditableTextLabel(text='', font_style='body', valign="center", size_hint=(1, 1))
        BaseItem.__init__(self)
        StartEditingEventDispatcher.__init__(self)
        FinishEditingEventDispatcher.__init__(self)
        # self.editable = True
        self.text = ''
        self._label.font_size = 16
        self._label.bold = False
        self._label._label.shorten = True
        self._label._label.padding_x = 2 + self.theme.geometry['border'] + self.theme.geometry['hotlight']
        self._label.editable = False
        self.add_widget(self._label)
        self._label.bind(on_finish_editing=self._on_finish_editing)  # on_start_editing=self._on_start_editing,
        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)

    def _on_update_geometry(self, instance, value):
        self._label.pos = self.pos
        self._label.size = self.size

    # Funciones de Seleccion ----------------------------------------------------
    def select_item(self, rv, data):
        # print('Select Item')
        BaseItem.select_item(self, rv, data)
        self._label.editable = True

    def unselect_item(self, rv, data):
        # print("Un select Item")
        if self._label.in_edition:
            self._label.finish_editing(self._label)
            self.graphic_focus.animate_focus(False)
        self._label.editable = False

    # Funciones de Edicion ------------------------------------------------------
    def start_editing(self, rv, data):
        if self._label.start_editing():
            StartEditingEventDispatcher.do_something(self)

    def stop_editing(self, rv, data):
        self._label.finish_editing(self._label)
        # rv.on_scroll_event = None

    def _on_finish_editing(self, instance, text):
        print(f"Finish Editing: {text}")
        self.text = text
        self.parent.parent.data[self.index]['text'] = text
        # self.level_render = "medium"
        # self.parent.parent.parent.parent.focused = True
        self.graphic_focus.animate_focus(True)
        FinishEditingEventDispatcher.do_something(self, text=text)

    def on_text(self, instance, value):
        self.text = value
        self._label.text = value

    # Funciones de RecycleDataViewBehavior -------------------------------------
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes - se ejecuta cuando hay un cambio en data'''
        # print(f'EditableItem.refresh_view_attrs, {index}, {data}, editable: {self.editable}')
        rt = super(EditableItem, self).refresh_view_attrs(rv, index, data)
        # Asigna el Texto ---------------------------------
        if 'text' in data:
            self.text = data['text']  # Cambia el texto
        return rt

    # Eventos de Usuario ---------------------------------------------------


# ------------------------------------------------------------------------------------------------------------------
class IconEditableDataDic(BaseDataDic):
    '''Clase para definir el diccionario para el Recycle List View'''
    def __init__(self, id=None, text='', icon_name='alarm', icon_size=24, selected=False, state_background=False):
        BaseDataDic.__init__(self, id, selected, state_background)
        self.text = text
        self.icon_name = icon_name
        self.icon_size = icon_size

    def to_dict(self):
        return BaseDataDic.to_dict(self) | {'text':self.text, 'icon_name':self.icon_name, 'icon_size':self.icon_size}


class IconEditableItem(BaseItem, StartEditingEventDispatcher, FinishEditingEventDispatcher):  #SEGUIR DE ACA
    text = StringProperty(defaultvalue='')
    icon_name =  StringProperty(defaultvalue=None)
    icon_size = StringProperty(defaultvalue=24)

    def __init__(self):
        """
        Constructor class
        Args:
            text (str)       : text of item
        """
        self._label = EditableTextLabel(text='', font_style='body', valign="center", size_hint=(1, 1))
        BaseItem.__init__(self)
        StartEditingEventDispatcher.__init__(self)
        FinishEditingEventDispatcher.__init__(self)
        # self.editable = True
        # Widget del texto
        self._label.font_size = 16
        self._label.bold = False
        self._label._label.shorten = True
        # self._label._label.padding_x = 2 + self.theme.geometry['border'] + self.theme.geometry['hotlight']
        self._label.editable = False
        self._label.bind(on_finish_editing=self._on_finish_editing)  # on_start_editing=self._on_start_editing,
        # Widget IconLabel
        # self.icon_name = None
        self._ly_icon = BoxLayout(orientation='horizontal')
        # self._ly_icon.padding_x = self.theme.geometry['padding']+10
        # Widget del icono
        self._icon = FontIconLabel(size_hint_x=None, icon_size=self.icon_size)
        self._icon.width += 2 + self.theme.geometry['border_width'] + self.theme.geometry['hotlight_width']
        # Agrega los Widget
        self._ly_icon.add_widget(self._icon)
        self._ly_icon.add_widget(self._label)
        self.add_widget(self._ly_icon)

        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)

    def _on_update_geometry(self, instance, value):
        self._ly_icon.pos = self.pos
        self._ly_icon.size = self.size
        # self._label.pos = self.pos
        # self._label.size = self.size

    # Funciones del Icono -------------------------------------------------------
    def on_icon_name(self, instance, value):
        self.icon_name = value
        self._icon.icon_name = value

    def on_icon_size(self, instance, value):
        self.icon_size = value
        self._icon.icon_size = value

    # Funciones de Seleccion ----------------------------------------------------
    def select_item(self, rv, data):
        # print('Select Item')
        BaseItem.select_item(self, rv, data)
        self._label.editable = True

    def unselect_item(self, rv, data):
        # print("Un select Item")
        if self._label.in_edition:
            self._label.finish_editing(self._label)
            self.graphic_focus.animate_focus(False)
        self._label.editable = False

    # Funciones de Edicion -----------------------------------------------------
    def start_editing(self, rv, data):
        if self._label.start_editing():
            StartEditingEventDispatcher.do_something(self)

    def stop_editing(self, rv, data):
        self._label.finish_editing(self._label)
        # rv.on_scroll_event = None

    def _on_finish_editing(self, instance, text):
        print(f"Finish Editing: {text}")
        self.text = text
        self.parent.parent.data[self.index]['text'] = text
        # self.level_render = "medium"
        # self.parent.parent.parent.parent.focused = True
        self.graphic_focus.animate_focus(True)
        FinishEditingEventDispatcher.do_something(self, text=text)

    def on_text(self, instance, value):
        self.text = value
        self._label.text = value

    # Funciones de RecycleDataViewBehavior -------------------------------------
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes - se ejecuta cuando hay un cambio en data'''
        # print(f'EditableItem.refresh_view_attrs, {index}, {data}, editable: {self.editable}')
        rt = BaseItem.refresh_view_attrs(self, rv, index, data)
        # Asigna el Texto ---------------------------------
        if 'text' in data:
            self.text = data['text']  # Cambia el texto
        if 'icon_name' in data:
            self.icon_name = data['icon_name']  # Cambia el icono
        if 'icon_size' in data:
            self.icon_size = data['icon_size']  # Cambia el tamaño del icono
        return rt


# ------------------------------------------------------------------------------------------------------------------
class FileDataDic(IconEditableDataDic):
    '''Clase para definir el diccionario para el Recycle List View'''
    def __init__(self, id=None, file_name='', folder='',
                 icon_name='file-document', icon_size=24, selected=False, state_background=False,
                 show_btn_save=False):
        BaseDataDic.__init__(self, id, selected, state_background)
        self.file_name = file_name
        self.folder = folder
        self.icon_name = icon_name
        self.icon_size = icon_size
        self.show_btn_save = show_btn_save

    def to_dict(self):
        return BaseDataDic.to_dict(self) | {'file_name':self.file_name, 'folder':self.folder,
                                            'icon_name':self.icon_name, 'icon_size':self.icon_size,
                                            'show_btn_save':self.show_btn_save}


class FileItem(BaseItem, StartEditingEventDispatcher, FinishEditingEventDispatcher):  #SEGUIR DE ACA
    file_name = StringProperty(defaultvalue='')
    icon_name =  StringProperty(defaultvalue=None)
    icon_size = StringProperty(defaultvalue=24)
    show_btn_save = BooleanProperty(defaultvalue=False)

    def __init__(self):
        """
        Constructor class
        Args:
            text (str)       : text of item
        """
        self._label = TextLabel(text='', font_style='body', valign="center", size_hint=(1, 1))
        BaseItem.__init__(self)
        StartEditingEventDispatcher.__init__(self)
        FinishEditingEventDispatcher.__init__(self)
        # self.editable = True
        # Widget del texto
        self._label.font_size = 16
        self._label.bold = False
        self._label.shorten = True
        # self._label._label.padding_x = 2 + self.theme.geometry['border'] + self.theme.geometry['hotlight']
        # self._label.editable = False
        # self._label.bind(on_finish_editing=self._on_finish_editing)  # on_start_editing=self._on_start_editing,
        # Widget IconLabel
        # self.icon_name = None
        self._ly_icon = BoxLayout(orientation='horizontal')
        # self._ly_icon.padding_x = self.theme.geometry['padding']+10
        # Widget del icono
        self._icon = FontIconLabel(size_hint_x=None, icon_size=self.icon_size)
        self._icon.width += 2 + self.theme.geometry['border_width'] + self.theme.geometry['hotlight_width']
        # Agrega los Widget
        self.container.orientation = 'horizontal'
        self.container.add_widget(self._icon)
        self.container.add_widget(self._label)

        # self._ly_icon.add_widget(self._icon)
        # self._ly_icon.add_widget(self._label)
        # self.add_widget(self._ly_icon)
        # Botones IconClick
        self.btn_save = None
        # self.btn_save = ClickIcon(icon_name='content-save', icon_size=24, size_hint=(None, 1))
        # self.btn_duplicate = ClickIcon(icon_name='file-multiple', icon_size=16, size_hint_x=None)  # 'content-duplicate'
        # self.btn_rename = ClickIcon(icon_name='rename-box', icon_size=16, size_hint_x=None)
        # self.btn_delete = ClickIcon(icon_name='delete', icon_size=16, size_hint_x=None)

        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)

    def _on_update_geometry(self, instance, value):
        self._ly_icon.pos = self.pos
        self._ly_icon.size = self.size
        # self._label.pos = self.pos
        # self._label.size = self.size

    # Funciones del Icono -------------------------------------------------------
    def on_icon_name(self, instance, value):
        self.icon_name = value
        self._icon.icon_name = value

    def on_icon_size(self, instance, value):
        self.icon_size = value
        self._icon.icon_size = value

    # def show_btn_save(self, instance, value):




    # Funciones de Seleccion ----------------------------------------------------
    def select_item(self, rv, data):
        BaseItem.select_item(self, rv, data)
        # print('FileItem.Select Item')
        # self._label.editable = True

        # btn Save
        self.btn_save = ClickIcon(icon_name='content-save', icon_size=24, size_hint=(None, 1))
        col = self.theme.colors['icons']
        col[3] = 0
        self.btn_save.icon_color = col
        # self._ly_icon.add_widget(self.btn_save)
        self.container.add_widget(self.btn_save)
        col[3] = 1
        anim = Animation(duration=0.4)  # demora el inicio
        anim += Animation(icon_color=col, duration=0.6)
        anim.start(self.btn_save)

    def unselect_item(self, rv, data):
        BaseItem.unselect_item(self, rv, data)
        # print("FileItem.Un select Item")
        if self.in_edition:
            self._label.finish_editing(self._label)
            self.graphic_focus.animate_focus(False)
        # Remueve el btn_save
        if self.btn_save:
            # self._ly_icon.remove_widget(self.btn_save)
            self.container.remove_widget(self.btn_save)
            self.btn_save = None
        # self._label.editable = False

    # Funciones de Hotlight -----------------------------------------------------
    def on_hotlight(self, state, mp):
        if self.parent:
            self.parent.parent.on_hotlight_item(self, state)
            self._label.editable = state

    # # Funciones de Edicion -----------------------------------------------------
    # def start_editing(self, rv, data):
    #     if self._label.start_editing():
    #         StartEditingEventDispatcher.do_something(self)
    #         print(f'FileItem.start_editing')
    #         print(f'  in_edition: {self._label.in_edition}')
    #
    # def stop_editing(self, rv, data):
    #     self._label.finish_editing(self._label)
    #     self.theme.level_render_widget = 'low'
    #     # rv.on_scroll_event = None
    #
    # def _on_finish_editing(self, instance, text):
    #     print(f"Finish Editing: {self.folder+os.sep+self.file_name}")
    #     self.theme.level_render_widget = 'low'
    #     # Renombra el Archivo
    #     actual_name = self.folder+os.sep+self.file_name
    #     new_name = self.folder+os.sep+text
    #     try:
    #         os.rename(actual_name, new_name)
    #     except:
    #         self.log.write("Error creando el directorio:\n")
    #         self.log.write(str(sys.exc_info()[0]) + '\n')
    #         self.log.write(str(sys.exc_info()[1]) + '\n')
    #         return None
    #     # Actualiza el ListView
    #     self.file_name = text
    #     self.parent.parent.data[self.index]['text'] = text
    #     # self.level_render = "medium"
    #     # self.parent.parent.parent.parent.focused = True
    #     self.graphic_focus.animate_focus(True)
    #     # FinishEditingEventDispatcher.do_something(self, text=text)

    # Funciones del archivo ----------------------------------------------------
    def on_file_name(self, instance, value):
        self.file_name = value
        self._label.text = value

    # Funciones de RecycleDataViewBehavior -------------------------------------
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes - se ejecuta cuando hay un cambio en data'''
        # print(f'EditableItem.refresh_view_attrs, {index}, {data}, editable: {self.editable}')
        rt = BaseItem.refresh_view_attrs(self, rv, index, data)
        self.file_name = data['file_name']  # Asigna el texto
        self.folder = data['folder']  # Asigna la carpeta
        self.icon_name = data['icon_name']  # Asigna el icono
        self.icon_size = data['icon_size']  # Asigna el tamaño del icono
        if data['show_btn_save']:  # and not self.btn_save
            self.btn_save = ClickIcon(icon_name='content-save', icon_size=24, size_hint=(None, 1))
            # self._ly_icon.add_widget(self.btn_save)
            self.container.add_widget(self.btn_save)


        elif self.btn_save:
            # self._ly_icon.remove_widget(self.btn_save)
            self.container.remove_widget(self.btn_save)
            self.btn_save = None

        # if self._selected == True:  # select  (agrega botones de iconos)
        #     self._ly_icon.add_widget(self.btn_save)
        #     self._ly_icon.add_widget(self.btn_duplicate)
        # elif self._selected == False:  # unselect (saca botones de iconos)
        #     pass
            # self._ly_icon.remove_widget(self.btn_save)
            # self._ly_icon.remove_widget(self.btn_duplicate)

        # TODO: puedo colocar un fusible inicializacion en __init__
        # self.btn_save.bind(on_click=data['save'])
        # self.btn_duplicate.bind(on_click=data['duplicate'])

        return rt