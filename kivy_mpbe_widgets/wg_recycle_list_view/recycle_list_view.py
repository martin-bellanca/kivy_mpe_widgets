#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  recycle_list_view.py
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
Recycle view widget for kivy_dkw \n
Created on 02/08/2020

@author: mpbe
@note:
'''
from os import MFD_ALLOW_SEALING

# imports del sistema -------------------------------------------------------
import os
import sys
import shutil

from requests.utils import prepend_scheme_if_needed

# imports helpers mpbe ------------------------------------------------------
from helpers_mpbe.python import compose, compose_dict
from helpers_mpbe.python import FolderWrapper
# Kivy imports --------------------------------------------------------------
import kivy

# from wg_lists.items_1 import BaseItem

kivy.require('1.10.1')
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.clock import Clock
from kivy.properties import StringProperty

# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets import PATH_HOME
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import FrameFocused
from kivy_mpbe_widgets.graphics.widget_graphics import GFace, GBorder, GFocus, GHotLight
from kivy_mpbe_widgets.wg_dialogs.basic_dialogs import TwoButtonsDialog
from kivy_mpbe_widgets.events.input_events import StartEditingEventDispatcher, FinishEditingEventDispatcher
from kivy_mpbe_widgets.events.file_events import DuplicateFileEventDispatcher, DeleteFileEventDispatcher, SaveFileEventDispatcher
from kivy_mpbe_widgets.wg_panels.panels import BoxPanel
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickIcon
from kivy_mpbe_widgets.wg_buttons.toggle_buttons import ToggleButton
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import FileDataDic, FileItem
from kivy_mpbe_widgets.events.recycle_view_events import SelectItemEventDispatcher, UnSelectItemEventDispatcher


Builder.load_string('''
<RecycleListViewUnfocused>:
    SelectableRecycleBoxLayout:
        id: srblayout
        default_size: None, dp(30)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: False
        touch_multiselect: False

<RecycleListView>:
    SelectableRecycleBoxLayout:
        id: srblayout
        default_size: None, dp(30)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: False
        touch_multiselect: False
''')



class SelectableRecycleBoxLayout(LayoutSelectionBehavior, RecycleBoxLayout):  # FocusBehavior
    ''' Adds selection and focus behavior to the view. '''


# class RecycleListViewUnfocused(ThemableBehavior, RecycleView, SelectItemEventDispatcher, UnSelectItemEventDispatcher):
#     instace_focus = None
#
#     def __init__(self, activate_background=True, **kwargs):
#         ThemableBehavior.__init__(self)
#         RecycleView.__init__(self, **kwargs)
#         # FocusBehavior.__init__(self)
#         SelectItemEventDispatcher.__init__(self)
#         UnSelectItemEventDispatcher.__init__(self)
#         # self.focused = True
#         self._item_hotlight = None
#         self._item_selected = None
#         self._select_index = -1  # Item actual seleccionado
#         # self._select_unselect = sel_unsel  # Define si al hacer click sobre un item seleccionado este se des selecciona
#         # self.multiselect = mutilselect  # Permite la multiseleccion de items
#         self.activate_background = activate_background  # Activa el cambio de tonalidad en el fondo de los items
#         self.on_scroll_event = None  # Referencia al evento de scroll para el item en edicion
#         self.layout = self.ids.srblayout
#         Window.bind(on_key_down=self._on_keyboard_down)
#
#     def data_index(self, data):
#         return self.data.index(data)
#
#     def on_hotlight_item(self, item, state):
#         if state:
#             self._item_hotlight = item
#
#     # Eventos de Usuario --------------------------------------------------------
#     def on_focus(self, instance, value):
#         # print(f'RecycleListView._on_focus {self.uid}-{value}')
#         if value == False and RecycleListView.instace_focus == instance:
#             RecycleListView.instace_focus == None
#         elif value == True:
#             RecycleListView.instace_focus = instance
#         return True
#
#     def on_touch_down(self, touch):
#         # print(f'RecycleListView.on_touch_down')
#         if self.collide_point_to_window(*touch.pos):
#             # print(f'  Grab')
#             touch.grab(self)  # Marca este touch como manejado por este widget
#         return super().on_touch_down(touch)
#
#     def on_touch_up(self, touch):
#         # print(f'RecycleListView.on_touch_up {self.uid}, collide_point={self.collide_point(*touch.pos)}')
#         if touch.grab_current is self:  # Verifica si este widget "grabó" el evento touch
#             # print('   Con Grab')
#             for item in self.layout.children:  # busca el item sobre el que se hizo el touch
#                 if item.collide_point_to_window(*touch.pos):
#                     break
#             data = self.data[item.index]
#             # print(f'presion sobre el item {item.id}, {item.index}, {data}')
#             if touch.button == 'left':  #  Seleccion y Des-seleccion de los items (Boton Izquierdo)
#                 # print('  RecycleListView.on_touch_down Boton Izquierdo')
#                 if self._select_index != item.index:
#                     # print(f'  RecycleListView.on_touch_down UNSELECT ++++++++++++++++++++++++++++')
#                     if self._item_selected:
#                         self.unselect_item(self._item_selected, self.data[self._select_index], touch.pos)
#                     # print(f'  RecycleListView.on_touch_down SELECT {self._select_index} y {item.index}')
#                     self.select_item(item, data, touch.pos)
#                 touch.ungrab(self)
#                 return True
#                 # self.refresh_from_data()  # no hace falta por que actualizo en select_item y unselect_item
#
#             elif touch.button == 'right':  # Modo Edicion (Boton Derecho)
#                 # print('Boton Derecho')
#                 # item.start_editing(self, data)
#                 pass
#             elif touch.button in ['scrollup', 'scrolldown']:
#                 # print('RecycleListView.on_touch_down->Rueda del mouse')
#                 item = None
#                 for it in self.layout.children:
#                     if it.index == self._select_index:
#                         item = it
#                         break
#                 if item != None:
#                     item.stop_editing(self, data)
#                 touch.ungrab(self)
#                 return False
#             # print("  ungrab")
#             touch.ungrab(self)  # Libera el touch
#             return False
#         super(RecycleView, self).on_touch_up(touch)
#
#     def on_scroll_move(self, touch):
#         # print('RecycleListView.on_scroll_move->Rueda del mouse')
#         super().on_scroll_move(touch)
#         if self.on_scroll_event:
#             self.on_scroll_event(self)  # Disparar el evento de scroll sobre el item en edicion
#
#     def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
#         # print("RecycleListView->_on_keyboard_down Codigo de Teclas", keycode, modifier)
#         # print(f'   UID:{self.uid}')
#         if RecycleListView.instace_focus == self and self.theme.level_render != 'high':
#             # print(f'RecycleListView._on_keyboard_down -> Instancia con Foco y nivel bajo')
#             if keycode == 273 and self._select_index < len(self.data)-1:  # Flecha Arriba
#                 pass  # Desactivado por que deberia mover el hotlight y seleccion con la tecla return
#                 # # print("Flecha Arriba")
#                 # # sel = self._select_index + 1
#                 # # Busca los items a preocesar
#                 # usitem = None
#                 # sitem = None
#                 # for item in self.layout.children:  # busca el item a des seleccionar
#                 #     if usitem:
#                 #         sitem = item
#                 #         break
#                 #     if item.index == self._select_index:
#                 #         usitem = item
#                 #     aitem = item
#                 # # Unselect Item
#                 # if usitem:
#                 #     self.unselect_item(usitem, self.data[self._select_index], usitem.center)
#                 # # Select Item
#                 # if sitem:
#                 #     self.select_item(sitem, self.data[self._select_index-1], sitem.center)
#             elif keycode == 274:  # Flecha Abajo
#                 pass  # Desactivado por que deberia mover el hotlight y seleccion con la tecla return
#                 # # print("Flecha Abajo")
#                 # # Busca los items a preocesar
#                 # usitem = None
#                 # sitem = None
#                 # for item in self.layout.children:  # busca el item a des seleccionar
#                 #     if item.index == self._select_index:
#                 #         usitem = item
#                 #         sitem = aitem
#                 #         break
#                 #     aitem = item
#                 # # Unselect Item
#                 # if usitem:
#                 #     self.unselect_item(usitem, self.data[self._select_index], usitem.center)
#                 # # Select Item
#                 # if sitem:
#                 #     self.select_item(sitem, self.data[self._select_index + 1], sitem.center)
#
#             return True
#         # print("RecycleListView->_on_keyboard_down -> Sale")
#         return False
#
#
#     # Funciones sobre items -------------------------------------------------------
#     def select_item(self, item, data, touch_pos):
#         # print(f'RecycleListView.select - {item.file_name} -------------------')
#         # desactiva items
#         # for dd in self.data:
#         #     dd['selected'] = False
#         # Activa el nuevo item
#         item.graphic_select.animate_select(True, touch_pos)
#         # item.graphic_focus.animate_focus(True)
#         item.editable = True
#         self._item_selected = item
#         self._select_index = item.index
#         item.select_item(self, data)
#
#         SelectItemEventDispatcher.do_something(self, data, item.index)
#
#     def unselect_item(self, item, data, touch_pos):
#         # print(f'RecycleListView.unselect - {item.file_name} -------------------')
#         if item != None:
#
#             item.graphic_select.animate_select(False, touch_pos)
#             # item.graphic_focus.animate_focus(False)
#             item.editable = False
#             item.unselect_item(self, data)
#             self._item_selected = None
#             self._select_index = -1
#         UnSelectItemEventDispatcher.do_something(self, data, self._select_index)


class RecycleListView(FocusBehavior, ThemableBehavior, RecycleView, SelectItemEventDispatcher, UnSelectItemEventDispatcher):
    instance_focus = None

    def __init__(self, activate_background=True, **kwargs):
        FocusBehavior.__init__(self)
        ThemableBehavior.__init__(self)
        RecycleView.__init__(self)
        # FrameFocused.__init__(self, hotlight=False)
        SelectItemEventDispatcher.__init__(self)
        UnSelectItemEventDispatcher.__init__(self)
        # self.focused = True
        self._item_hotlight = None
        self._item_selected = None
        self._select_index = -1  # Item actual seleccionado
        # self._select_unselect = sel_unsel  # Define si al hacer click sobre un item seleccionado este se des selecciona
        # self.multiselect = mutilselect  # Permite la multiseleccion de items
        self.activate_background = activate_background  # Activa el cambio de tonalidad en el fondo de los items
        self.on_scroll_event = None  # Referencia al evento de scroll para el item en edicion
        self.layout = self.ids.srblayout
        # print(f'RecycleListView.__init__->is_focuseable = {self.is_focusable}')
        with self.canvas.after:
            if not self.flat: self.graphic_border = GBorder(self)
            self.graphic_focus = GFocus(self)

        Window.bind(on_key_down=self._on_keyboard_down)

    def data_index(self, data):
        return self.data.index(data)

    def on_hotlight_item(self, item, state):
        if state:
            self._item_hotlight = item

    # Eventos de Usuario --------------------------------------------------------
    def on_focus(self, instance, value):
        # print(f'RecycleListView._on_focus {self.uid}-{value}')
        if value == False and RecycleListView.instance_focus == instance:
            RecycleListView.instance_focus == None
        elif value == True:
            RecycleListView.instance_focus = instance
        return True

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
                if self._select_index != item.index:
                    # print(f'  RecycleListView.on_touch_down UNSELECT ++++++++++++++++++++++++++++')
                    if self._item_selected:
                        self.unselect_item(self._item_selected, self.data[self._select_index], touch.pos)
                    # print(f'  RecycleListView.on_touch_down SELECT {self._select_index} y {item.index}')
                    self.select_item(item, data, touch.pos)
                touch.ungrab(self)
                return True
                # self.refresh_from_data()  # no hace falta por que actualizo en select_item y unselect_item

            elif touch.button == 'right':  # Modo Edicion (Boton Derecho)
                # print('Boton Derecho')
                # item.start_editing(self, data)
                pass
            elif touch.button in ['scrollup', 'scrolldown']:
                # print('RecycleListView.on_touch_down->Rueda del mouse')
                item = None
                for it in self.layout.children:
                    if it.index == self._select_index:
                        item = it
                        break
                if item != None:
                    item.stop_editing(self, data)
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

    def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
        # print("RecycleListView->_on_keyboard_down Codigo de Teclas", keycode, modifier)
        # print(f'   UID:{self.uid}')
        # if RecycleListView.instace_focus == self and self.theme.level_render != 'high':
        #     # print(f'RecycleListView._on_keyboard_down -> Instancia con Foco y nivel bajo')
        #     if keycode == 273 and self._select_index < len(self.data)-1:  # Flecha Arriba
        #         pass  # Desactivado por que deberia mover el hotlight y seleccion con la tecla return
        #         # # print("Flecha Arriba")
        #         # # sel = self._select_index + 1
        #         # # Busca los items a preocesar
        #         # usitem = None
        #         # sitem = None
        #         # for item in self.layout.children:  # busca el item a des seleccionar
        #         #     if usitem:
        #         #         sitem = item
        #         #         break
        #         #     if item.index == self._select_index:
        #         #         usitem = item
        #         #     aitem = item
        #         # # Unselect Item
        #         # if usitem:
        #         #     self.unselect_item(usitem, self.data[self._select_index], usitem.center)
        #         # # Select Item
        #         # if sitem:
        #         #     self.select_item(sitem, self.data[self._select_index-1], sitem.center)
        #     elif keycode == 274:  # Flecha Abajo
        #         pass  # Desactivado por que deberia mover el hotlight y seleccion con la tecla return
        #         # # print("Flecha Abajo")
        #         # # Busca los items a preocesar
        #         # usitem = None
        #         # sitem = None
        #         # for item in self.layout.children:  # busca el item a des seleccionar
        #         #     if item.index == self._select_index:
        #         #         usitem = item
        #         #         sitem = aitem
        #         #         break
        #         #     aitem = item
        #         # # Unselect Item
        #         # if usitem:
        #         #     self.unselect_item(usitem, self.data[self._select_index], usitem.center)
        #         # # Select Item
        #         # if sitem:
        #         #     self.select_item(sitem, self.data[self._select_index + 1], sitem.center)
        #
        #     return True
        # # print("RecycleListView->_on_keyboard_down -> Sale")
        # return False
        pass


    # Funciones sobre items -------------------------------------------------------
    def select_item(self, item, data, touch_pos):
        # print(f'RecycleListView.select - {item.file_name} -------------------')
        # desactiva items
        # for dd in self.data:
        #     dd['selected'] = False
        # Activa el nuevo item
        item.graphic_select.animate_select(True, touch_pos)
        # item.graphic_focus.animate_focus(True)
        item.editable = True
        self._item_selected = item
        self._select_index = item.index
        item.select_item(self, data)

        SelectItemEventDispatcher.do_something(self, data, item.index)

    def unselect_item(self, item, data, touch_pos):
        # print(f'RecycleListView.unselect - {item.file_name} -------------------')
        if item != None:

            item.graphic_select.animate_select(False, touch_pos)
            # item.graphic_focus.animate_focus(False)
            item.editable = False
            item.unselect_item(self, data)
            self._item_selected = None
            self._select_index = -1
        UnSelectItemEventDispatcher.do_something(self, data, self._select_index)


class FileListView(RecycleListView, StartEditingEventDispatcher, FinishEditingEventDispatcher,
                   DeleteFileEventDispatcher, DuplicateFileEventDispatcher, SaveFileEventDispatcher):
    """
    Lista de archivos del directorio indicado. Solo trabaja con seleccion simple
    Attributes:

    Properties:

    Methods:

    Events:
        on_select_item: Se activa al seleccionar un archivo
        on_unselect_item: Se activa cuando se des-selecciona un archivo
        on_save_file: Se activa al hacer click en el boton save
        on_duplitate_file: Se activa al hacer click en el boton duplicate
    """
    # Propiedades Kivy
    folder = StringProperty(defaultvalue=PATH_HOME)  # Camino completo a la carpeta

    def __init__(self, folder=PATH_HOME, extensions='*', activate_background=True, **kwargs):
        """Constructor
        Parameter:
            folder (string): Camino al directorio a mostar. Default 'directorio home'
            extensions (string): Lista de extensiones de archivos a mostar separadas por coma (* todas). Default '*'
            activate_background (bool): Activa resaltado del interlineado
        """
        RecycleListView.__init__(self, mutilselect=False, activate_background=activate_background, **kwargs)
        StartEditingEventDispatcher.__init__(self)
        FinishEditingEventDispatcher.__init__(self)
        DeleteFileEventDispatcher.__init__(self)
        DuplicateFileEventDispatcher.__init__(self)
        SaveFileEventDispatcher.__init__(self)
        self.viewclass = 'FileItem'
        self.extensions = extensions
        self.folder = folder
        self.on_folder(self, folder)
        # Text Editor
        self._text_editor = TextInput(text='', multiline=False, on_text_validate=self.on_finish_editing)
        self._text_editor.bind(focus=self.on_text_focus)
        # Botones IconClick
        # self.btn_save = ClickIcon(icon_name='content-save', icon_size=24, size_hint=(None, 1))
        self.btn_duplicate = ClickIcon(icon_name='file-multiple', icon_size=18, size_hint_x=None)  # 'content-duplicate'
        self.btn_rename = ClickIcon(icon_name='rename-box', icon_size=18, size_hint_x=None)
        self.btn_delete = ClickIcon(icon_name='delete', icon_size=18, size_hint_x=None)

        Window.bind(on_key_down=self._on_keyboard_down)

    def on_folder(self, instance, folder):
        # print(f'FileListView.on_directory - {folder}')
        self.populate(folder)

    def populate(self, folder, select_file=''):
        # print(f'FileListView.populate - {folder}')
        self.folder = folder
        if os.path.exists(folder):
            self.data.clear()  # borra los archivos actuales
            wrapper = FolderWrapper(folder)
            lstfolders, lstfiles = wrapper.getChildsNames(sorted, show_hidden=False, filters=self.extensions)
            for ff in lstfiles:
                selected = False if ff != select_file else True
                df = FileDataDic(file_name=ff, folder=folder, selected=selected, show_btn_save=selected).to_dict()
                # df |= {'save':self._save, 'duplicate':self._duplicate}
                self.data.append(df)
            self.refresh_from_data()
            # for it in self.layout.children:
            #     if it._selected:
            #         self._select_index = it.index
            #         self._item_selected = it
            #         break

    def update_folder(self):
        self.populate(self.folder)

    # def on_touch_up(self, touch):
    #     # print(f'FileListView.on_touch_up')
    #     # super(RecycleView, self).on_touch_down(touch)
    #     ltouch = self.to_local(*touch.pos)
    #     if self.collide_point(*ltouch) and len(self.data)>0 and self.theme.level_render != 'high':  # self.collide_point_to_window(*touch.pos)
    #         for item in self.layout.children:  # busca el item sobre el que se hizo el touch
    #             if item.collide_point_to_window(*touch.pos):
    #                 break
    #         data = self.data[item.index]
    #         # print(f'presion sobre el item {item.id}, {item.index}, {data}')
    #         if touch.button == 'left':  # Seleccion y Des-seleccion de los items (Boton Izquierdo)
    #             # print('  Boton Izquierdo')
    #             # Chequeo de botones
    #             if self.btn_duplicate.is_hotlight():
    #                 # print('FileListView.on_touch_down->btn duplicate presionado')
    #                 self._duplicate_file(self._item_hotlight)
    #                 # VERIFICAR ESTE
    #                 return True
    #             elif self.btn_rename.is_hotlight():
    #                 print('FileListView.on_touch_down->btn rename presionado')
    #                 self.start_edition()
    #                 return True
    #             elif self.btn_delete.is_hotlight():
    #                 # print('FileListView.on_touch_down->btn delete presionado')
    #                 self._delete_file(self._item_hotlight)
    #                 return True
    #             elif item.btn_save and item.btn_save.is_hotlight():  # Boton Save
    #                 self._save_file(self._item_selected.file_name)
    #                 return True
    #         RecycleListView.on_touch_up(self, touch)

    # def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
    #     # print("FileListView._on_keyboard_down - Codigo de Teclas", keycode, modifier)
    #     if keycode == 27 and self.theme.level_render == 'high':  # Tecla Escape
    #         self.stop_editing()
    #         return True
    #     if keycode == 283 and not self._item_hotlight.in_edition:
    #         self.start_edition()
    #         return True
    #     return RecycleListView._on_keyboard_down(self, window, keycode, modifier, char, special_keys)

    def on_touch_down(self, touch):
        # print(f'FileListView.on_touch_down')
        # super(RecycleView, self).on_touch_down(touch)
        ltouch = self.to_widget(*touch.pos, True)
        if self.collide_point(*touch.pos) and len(self.data)>0 and self.theme.level_render != 'high':  # self.collide_point_to_window(*touch.pos)
            # print("  Presion en el FileListView")
            for item in self.layout.children:  # busca el item sobre el que se hizo el touch
                if item.collide_point(*ltouch):  # item.collide_point_to_window(*touch.pos)
                    break
            data = self.data[item.index]
            # print(f'    Presion sobre el item {item.file_name}, {item.index}, {data}')
            if touch.button == 'left':  # Seleccion y Des-seleccion de los items (Boton Izquierdo)
                # print('  Boton Izquierdo')
                # Chequeo de botones
                if self.btn_duplicate.is_hotlight():
                    # print('    FileListView.on_touch_down->btn duplicate presionado')
                    self.btn_duplicate.on_touch_down(touch)
                    self._duplicate_file(self._item_hotlight)
                    return True
                elif self.btn_rename.is_hotlight():
                    # print('    FileListView.on_touch_down->btn rename presionado')
                    self.btn_rename.on_touch_down(touch)
                    self.start_edition()
                    return True
                elif self.btn_delete.is_hotlight():
                    # print('    FileListView.on_touch_down->btn delete presionado')
                    self.btn_delete.on_touch_down(touch)
                    self._delete_file(self._item_hotlight)
                    return True
                elif item.btn_save and item.btn_save.is_hotlight():  # Boton Save
                    item.btn_save.on_touch_down(touch)
                    self._save_file(self._item_selected.file_name)
                    return True
                # Si no es ningun boton se selecciono un item y esconde los botones de Rename y Delete
                self._hide_btn(item, self.btn_delete)
                self._hide_btn(item, self.btn_rename)
            RecycleListView.on_touch_down(self, touch)

    def on_text_focus(self, instance, value):
        # print("FileListView.on_text_focus")
        if not value and self.theme.level_render == 'high':  # El foco se perdió
            print('  Finaliza la edicion')
            self.finish_editing()

    def on_finish_editing(self, instance):
        self.finish_editing()

    # Funciones de Seleccion -----------------------------------------------------
    def select_item(self, item, data, touch_pos):

        # for dd in self.data:
        #     print(f"State: {dd['selected']} - {dd['file_name']}")

        RecycleListView.select_item(self, item, data, touch_pos)
        data['show_btn_save'] = True
        # print('FileListView.select item()')

    def unselect_item(self, item, data, touch_pos):
        RecycleListView.unselect_item(self, item, data, touch_pos)
        data['show_btn_save'] = False
        # print('FileListView.unselect item()')
        # if item:
        #     item._ly_icon.remove_widget(self.btn_save)
        #     # self.refresh_from_data()

    # Funciones de Edicion -------------------------------------------------------
    def _init_edition(self, dt):
        self._text_editor.focus = True
        pos = self._text_editor.text.rfind('.')
        if pos == -1:
            pos = len(self._text_editor.text)
        self._text_editor.cursor = (pos, 0)
        # self._text_editor.select_all()
        self._text_editor.select_text(0, pos)

    def start_edition(self):
        # print(f'FileListView.start_edition() - in_edition {self._item_hotlight.in_edition}')
        if not self._item_hotlight.in_edition:
            self._item_hotlight.in_edition = True
            self.theme.level_render = 'high'
            # data = self.data[self._item_hotlight.index]
            self._text_editor.text = self._item_hotlight.file_name
            # asigna el editor -----------------
            self._item_hotlight.container.remove_widget(self._item_hotlight._label)
            pos = 4 if self._item_hotlight._selected else 3
            self._item_hotlight.container.add_widget(self._text_editor, pos)
            Clock.schedule_once(self._init_edition, 0.4)
            StartEditingEventDispatcher.do_something(self, text=self._text_editor.text)

    def stop_editing(self):
        print("FileListView.stop_editing")
        self._item_hotlight.in_edition = False
        self.theme.level_render = 'low'
        # asigna el editor -----------------
        self._text_editor.focus = False
        self._item_hotlight.container.remove_widget(self._text_editor)
        pos = 4 if self._item_hotlight._selected else 3
        self._item_hotlight.container.add_widget(self._item_hotlight._label, pos)

    def finish_editing(self):
        # print("FileListView.finish_editing")
        # Guardar el texto editado y desactivar edición
        if self._item_hotlight.in_edition:
            self._item_hotlight.in_edition = False
            self.theme.level_render = 'low'
            # Reasigna el label -------------------
            self._item_hotlight.container.remove_widget(self._text_editor)
            pos = 4 if self._item_hotlight._selected else 3
            self._item_hotlight.container.add_widget(self._item_hotlight._label, pos)
            # Renombra el archivo ----------------
            actual_name = self.folder + os.sep + self._item_hotlight.file_name
            new_name = self.folder + os.sep + self._text_editor.text
            try:
                os.rename(actual_name, new_name)
            except:
                self.log.write("Error creando el directorio:\n")
                self.log.write(str(sys.exc_info()[0]) + '\n')
                self.log.write(str(sys.exc_info()[1]) + '\n')
                return None
            # Actualiza el item -------------------
            FinishEditingEventDispatcher.do_something(self, new_text=self._text_editor.text)
            data = self.data[self._item_hotlight.index]
            data['file_name'] = self._text_editor.text
            self._item_hotlight.file_name = self._text_editor.text

    # Funciones de Archivos ------------------------------------------------------
    def _show_btn(self, item, btn):
        col = self.theme.colors['icons']
        col[3] = 0
        btn.icon_color = col
        # print(f'state select {item._state_select}')
        ii = 0 if not item._selected else 1
        # item._ly_icon.add_widget(btn, ii)
        item.container.add_widget(btn, ii)
        # Clock.schedule_once(lambda dt: item._ly_icon.add_widget(self.btn_duplicate), 0.4)
        col[3] = 1
        # anim = Animation(duration=0.4)
        anim = Animation(icon_color=col, duration=0.4)
        anim.start(btn)

    def _hide_btn(self, item, btn):
        # print(f'item btn a apagar {item}')
        if item:
            # item._ly_icon.remove_widget(btn)
            item.container.remove_widget(btn)
            # col = self.theme.colors['icons']
            # col[3] = 0
            # anim = Animation(icon_color=col, duration=0.4)
            # anim.start(self.btn_duplicate)
            #
            # Clock.schedule_once(lambda dt: item._ly_icon.remove_widget(self.btn_duplicate), 0.4)

    def on_hotlight_item(self, item, state):
        if state:
            self._hide_btn(self._item_hotlight, self.btn_rename)
            if not(item._selected):
                self._show_btn(item, self.btn_rename)
            self._hide_btn(self._item_hotlight, self.btn_duplicate)
            self._show_btn(item, self.btn_duplicate)
            self._hide_btn(self._item_hotlight, self.btn_delete)
            if not (item._selected):
                self._show_btn(item, self.btn_delete)

            # self._item_hotlight = item
            # item._ly_icon.remove_widget(self.btn_duplicate)
        RecycleListView.on_hotlight_item(self, item, state)

    def _save_file(self, file_name):
        # print(f'FileListView._save_file(file={file_name})')
        SaveFileEventDispatcher.do_something(self, file_name)

    def _duplicate_file(self, item):
        # Duplica el archivo ---------------------------------
        if self._item_selected:
            sel_file = self._item_selected.file_name
        else:
            sel_file = ''
        file_name = item.file_name
        # print(f'FileListView._duplicate_file(file={file_name})')
        actual_name = self.folder + os.sep + file_name
        name, ext = os.path.splitext(file_name)
        new_name =  self.folder + os.sep + name + '-copy' + ext
        try:
            shutil.copy(actual_name, new_name)
        except:
            self.log.write("Error copiando FileWrapper:\n")
            self.log.write(str(sys.exc_info()[0]) + '\n')
            self.log.write(str(sys.exc_info()[1]) + '\n')
            return False
        # Actualiza la lista ----------------------------
        self.populate(folder=self.folder, select_file=sel_file)
        DuplicateFileEventDispatcher.do_something(self, new_name, actual_name)
        # df = FileDataDic(file_name=name + '-copy' + ext, folder=self.folder).to_dict()
        # self.data.append(df)
        # self.refresh_from_data()

    def _delete_file(self, item):  # OK
        """
        Elimina un archivo dado su nombre.
        args:
            item (FileItem): Item del archivo a eliminar
        """
        # Borra el archivo ---------------------------------
        def on_yes(instance, touch, keycode):
            popup.dismiss()
            if self._item_selected:
                sel_file = self._item_selected.file_name
            else:
                sel_file = ''
            if item.selected:
                self.data[item.index]['selected'] = False
                self._select_index = -1
                self._item_selected = False
            file_name = item.file_name
            # print(f'FileListView._delete_file(file={file_name})')
            file = self.folder + os.sep + file_name
            try:
                if os.path.exists(file):
                    os.remove(file)
                else:
                    print(f"El archivo '{file}' no existe.")
            except Exception as e:
                print(f"Error al intentar eliminar el archivo: {e}")
                return False
            # Actualiza la lista ----------------------------
            self.populate(self.folder, sel_file)
            DeleteFileEventDispatcher().do_something(file_name)
            # # Borra el item en data -----------------------------
            # del self.data[id]
            # # Actualiza el index del item seleccionado ----------
            # if self._item_selected:
            #     if self._select_index > id and self._select_index > 0:
            #         print('  Resta al el Index')
            #         self._select_index -= 1
            #     self._item_selected = self.layout.children[self._select_index]

        popup = TwoButtonsDialog(title="File System", question_text=f"Are you sure you want to delete {item.file_name}?",
                                 btn1_text="Yes", btn2_text="Cancel")
        popup.button_1.bind(on_click=on_yes)
        popup.button_2.bind(on_click=popup.dismiss)
        popup.open()


class FileListView_BACK(RecycleListView, StartEditingEventDispatcher, FinishEditingEventDispatcher,
                   DeleteFileEventDispatcher, DuplicateFileEventDispatcher, SaveFileEventDispatcher):
    """
    Lista de archivos del directorio indicado. Solo trabaja con seleccion simple
    Attributes:

    Properties:

    Methods:

    Events:
        on_select_item: Se activa al seleccionar un archivo
        on_unselect_item: Se activa cuando se des-selecciona un archivo
        on_save_file: Se activa al hacer click en el boton save
        on_duplitate_file: Se activa al hacer click en el boton duplicate
    """
    # Propiedades Kivy
    folder = StringProperty(defaultvalue=PATH_HOME)  # Camino completo a la carpeta

    def __init__(self, folder=PATH_HOME, extensions='*', activate_background=True, **kwargs):
        """Constructor
        Parameter:
            folder (string): Camino al directorio a mostar. Default 'directorio home'
            extensions (string): Lista de extensiones de archivos a mostar separadas por coma (* todas). Default '*'
            activate_background (bool): Activa resaltado del interlineado
        """
        RecycleListView.__init__(self, mutilselect=False, activate_background=activate_background, **kwargs)
        StartEditingEventDispatcher.__init__(self)
        FinishEditingEventDispatcher.__init__(self)
        DeleteFileEventDispatcher.__init__(self)
        DuplicateFileEventDispatcher.__init__(self)
        SaveFileEventDispatcher.__init__(self)
        self.viewclass = 'FileItem'
        self.extensions = extensions
        self.folder = folder
        self.on_folder(self, folder)
        # Text Editor
        self._text_editor = TextInput(text='', multiline=False, on_text_validate=self.on_finish_editing)
        self._text_editor.bind(focus=self.on_text_focus)
        # Botones IconClick
        # self.btn_save = ClickIcon(icon_name='content-save', icon_size=24, size_hint=(None, 1))
        self.btn_duplicate = ClickIcon(icon_name='file-multiple', icon_size=18, size_hint_x=None)  # 'content-duplicate'
        self.btn_rename = ClickIcon(icon_name='rename-box', icon_size=18, size_hint_x=None)
        self.btn_delete = ClickIcon(icon_name='delete', icon_size=18, size_hint_x=None)

        Window.bind(on_key_down=self._on_keyboard_down)

    def on_folder(self, instance, folder):
        # print(f'FileListView.on_directory - {folder}')
        self.populate(folder)

    def populate(self,folder, select_file=''):
        # print(f'FileListView.populate - {folder}')
        self.folder = folder
        self.data.clear()  # borra los archivos actuales
        wrapper = FolderWrapper(folder)
        lstfolders, lstfiles = wrapper.getChildsNames(sorted, show_hidden=False, filters=self.extensions)
        for ff in lstfiles:
            selected = False if ff != select_file else True
            df = FileDataDic(file_name=ff, folder=folder, selected=selected, show_btn_save=selected).to_dict()
            # df |= {'save':self._save, 'duplicate':self._duplicate}
            self.data.append(df)
        self.refresh_from_data()
        # for it in self.layout.children:
        #     if it._selected:
        #         self._select_index = it.index
        #         self._item_selected = it
        #         break

    def on_touch_down(self, touch):
        print(f'FileListView.on_touch_down')
        # super(RecycleView, self).on_touch_down(touch)
        if self.collide_point_to_window(*touch.pos) and len(self.data)>0 and self.theme.level_render != 'high':
            for item in self.layout.children:  # busca el item sobre el que se hizo el touch
                if item.collide_point_to_window(*touch.pos):
                    break
            data = self.data[item.index]
            # print(f'presion sobre el item {item.id}, {item.index}, {data}')
            if touch.button == 'left':  # Seleccion y Des-seleccion de los items (Boton Izquierdo)
                # print('  Boton Izquierdo')
                # Chequeo de botones
                if self.btn_duplicate.is_hotlight():
                    # print('FileListView.on_touch_down->btn duplicate presionado')
                    self._duplicate_file(self._item_hotlight)
                    # VERIFICAR ESTE
                    return True
                elif self.btn_rename.is_hotlight():
                    # print('FileListView.on_touch_down->btn rename presionado')
                    self.start_edition()
                    return True
                elif self.btn_delete.is_hotlight():
                    # print('FileListView.on_touch_down->btn delete presionado')
                    self._delete_file(self._item_hotlight)
                    return True
                elif item.btn_save and item.btn_save.is_hotlight():  # Boton Save
                    self._save_file(self._item_selected.file_name)
                    return True
            RecycleListView.on_touch_up(self, touch)

    def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
        # print("FileListView._on_keyboard_down - Codigo de Teclas", keycode, modifier)
        if keycode == 27 and self.theme.level_render == 'high':  # Tecla Escape
            self.stop_editing()
            return True
        if keycode == 283 and not self._item_hotlight.in_edition:
            self.start_edition()
            return True
        return RecycleListView._on_keyboard_down(self, window, keycode, modifier, char, special_keys)

    def on_text_focus(self, instance, value):
        # print("FileListView.on_text_focus")
        if not value and self.theme.level_render == 'high':  # El foco se perdió
            print('  Finaliza la edicion')
            self.finish_editing()

    def on_finish_editing(self, instance):
        self.finish_editing()

    # Funciones de Seleccion -----------------------------------------------------
    def select_item(self, item, data, touch_pos):

        # for dd in self.data:
        #     print(f"State: {dd['selected']} - {dd['file_name']}")

        RecycleListView.select_item(self, item, data, touch_pos)
        data['show_btn_save'] = True
        # print('FileListView.select item()')

    def unselect_item(self, item, data, touch_pos):
        RecycleListView.unselect_item(self, item, data, touch_pos)
        data['show_btn_save'] = False
        # print('FileListView.unselect item()')
        # if item:
        #     item._ly_icon.remove_widget(self.btn_save)
        #     # self.refresh_from_data()

    # Funciones de Edicion -------------------------------------------------------
    def _init_edition(self, dt):
        self._text_editor.focus = True
        pos = self._text_editor.text.rfind('.')
        if pos == -1:
            pos = len(self._text_editor.text)
        self._text_editor.cursor = (pos, 0)
        # self._text_editor.select_all()
        self._text_editor.select_text(0, pos)

    def start_edition(self):
        # print(f'FileListView.start_edition() - in_edition {self._item_hotlight.in_edition}')
        if not self._item_hotlight.in_edition:
            self._item_hotlight.in_edition = True
            self.theme.level_render = 'high'
            # data = self.data[self._item_hotlight.index]
            self._text_editor.text = self._item_hotlight.file_name
            # asigna el editor -----------------
            self._item_hotlight.container.remove_widget(self._item_hotlight._label)
            pos = 4 if self._item_hotlight._selected else 3
            self._item_hotlight.container.add_widget(self._text_editor, pos)
            Clock.schedule_once(self._init_edition, 0.4)
            StartEditingEventDispatcher.do_something(self, text=self._text_editor.text)

    def stop_editing(self):
        print("FileListView.stop_editing")
        self._item_hotlight.in_edition = False
        self.theme.level_render = 'low'
        # asigna el editor -----------------
        self._text_editor.focus = False
        self._item_hotlight.container.remove_widget(self._text_editor)
        pos = 4 if self._item_hotlight._selected else 3
        self._item_hotlight.container.add_widget(self._item_hotlight._label, pos)

    def finish_editing(self):
        print("FileListView.finish_editing")
        # Guardar el texto editado y desactivar edición
        if self._item_hotlight.in_edition:
            self._item_hotlight.in_edition = False
            self.theme.level_render = 'low'
            # Reasigna el label -------------------
            self._item_hotlight.container.remove_widget(self._text_editor)
            pos = 4 if self._item_hotlight._selected else 3
            self._item_hotlight.container.add_widget(self._item_hotlight._label, pos)
            # Renombra el archivo ----------------
            actual_name = self.folder + os.sep + self._item_hotlight.file_name
            new_name = self.folder + os.sep + self._text_editor.text
            try:
                os.rename(actual_name, new_name)
            except:
                self.log.write("Error creando el directorio:\n")
                self.log.write(str(sys.exc_info()[0]) + '\n')
                self.log.write(str(sys.exc_info()[1]) + '\n')
                return None
            # Actualiza el item -------------------
            FinishEditingEventDispatcher.do_something(self, new_text=self._text_editor.text)
            data = self.data[self._item_hotlight.index]
            data['file_name'] = self._text_editor.text
            self._item_hotlight.file_name = self._text_editor.text

    # Funciones de Archivos ------------------------------------------------------
    def _show_btn(self, item, btn):
        col = self.theme.colors['icons']
        col[3] = 0
        btn.icon_color = col
        # print(f'state select {item._state_select}')
        ii = 0 if not item._selected else 1
        # item._ly_icon.add_widget(btn, ii)
        item.container.add_widget(btn, ii)
        # Clock.schedule_once(lambda dt: item._ly_icon.add_widget(self.btn_duplicate), 0.4)
        col[3] = 1
        # anim = Animation(duration=0.4)
        anim = Animation(icon_color=col, duration=0.4)
        anim.start(btn)

    def _hide_btn(self, item, btn):
        # print(f'item btn a apagar {item}')
        if item:
            # item._ly_icon.remove_widget(btn)
            item.container.remove_widget(btn)
            # col = self.theme.colors['icons']
            # col[3] = 0
            # anim = Animation(icon_color=col, duration=0.4)
            # anim.start(self.btn_duplicate)
            #
            # Clock.schedule_once(lambda dt: item._ly_icon.remove_widget(self.btn_duplicate), 0.4)

    def on_hotlight_item(self, item, state):
        if state:
            self._hide_btn(self._item_hotlight, self.btn_rename)
            self._show_btn(item, self.btn_rename)
            self._hide_btn(self._item_hotlight, self.btn_duplicate)
            self._show_btn(item, self.btn_duplicate)
            self._hide_btn(self._item_hotlight, self.btn_delete)
            self._show_btn(item, self.btn_delete)

            # self._item_hotlight = item
            # item._ly_icon.remove_widget(self.btn_duplicate)
        RecycleListView.on_hotlight_item(self, item, state)

    def _save_file(self, file_name):
        # print(f'FileListView._save_file(file={file_name})')
        SaveFileEventDispatcher.do_something(self, file_name)

    def _duplicate_file(self, item):
        # Duplica el archivo ---------------------------------
        if self._item_selected:
            sel_file = self._item_selected.file_name
        else:
            sel_file = ''
        file_name = item.file_name
        # print(f'FileListView._duplicate_file(file={file_name})')
        actual_name = self.folder + os.sep + file_name
        name, ext = os.path.splitext(file_name)
        new_name =  self.folder + os.sep + name + '-copy' + ext
        try:
            shutil.copy(actual_name, new_name)
        except:
            self.log.write("Error copiando FileWrapper:\n")
            self.log.write(str(sys.exc_info()[0]) + '\n')
            self.log.write(str(sys.exc_info()[1]) + '\n')
            return False
        # Actualiza la lista ----------------------------
        self.populate(folder=self.folder, select_file=sel_file)
        DuplicateFileEventDispatcher.do_something(self, new_name, actual_name)
        # df = FileDataDic(file_name=name + '-copy' + ext, folder=self.folder).to_dict()
        # self.data.append(df)
        # self.refresh_from_data()

    def _delete_file(self, item):  # OK
        """
        Elimina un archivo dado su nombre.
        args:
            item (FileItem): Item del archivo a eliminar
        """
        # Borra el archivo ---------------------------------
        if self._item_selected:
            sel_file = self._item_selected.file_name
        else:
            sel_file = ''
        if item.selected:
            self.data[item.index]['selected'] = False
            self._select_index = -1
            self._item_selected = False
        file_name = item.file_name
        # print(f'FileListView._delete_file(file={file_name})')
        file = self.folder + os.sep + file_name
        try:
            if os.path.exists(file):
                os.remove(file)
            else:
                print(f"El archivo '{file}' no existe.")
        except Exception as e:
            print(f"Error al intentar eliminar el archivo: {e}")
            return False
        # Actualiza la lista ----------------------------
        self.populate(self.folder, sel_file)
        DeleteFileEventDispatcher().do_something(file_name)
        # # Borra el item en data -----------------------------
        # del self.data[id]
        # # Actualiza el index del item seleccionado ----------
        # if self._item_selected:
        #     if self._select_index > id and self._select_index > 0:
        #         print('  Resta al el Index')
        #         self._select_index -= 1
        #     self._item_selected = self.layout.children[self._select_index]


