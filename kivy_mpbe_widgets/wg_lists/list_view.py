#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  list_view.py
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
List view widget for kivy_dkw \n
Created on 02/08/2020

@author: mpbe
@note:
'''


# imports del sistema -------------------------------------------------------

from helpers_mpbe.python import compose, compose_dict
# Kivy imports --------------------------------------------------------------
import kivy
kivy.require('1.10.1')
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.wg_panels.panels import BoxPanel
from kivy_mpbe_widgets.wg_buttons.toggle_buttons import ToggleButton
from kivy_mpbe_widgets.events.list_view_events import SelectListItemEventDispatcher



# class ListView_BK(BoxPanel, SelectListItemEventDispatcher):
#     """
#     Widget Kivy_KDW String List View
#     Events: on_select_list_item(selected_id, text)
#     """
#
#     def __init__(self, name='string list view', **kwargs):
#         """Constructor class
#         Args:
#             txt_list (string list): list of items texts
#             img_list (image list) : list of image text source
#             icon_list (icon list) : list of icon text name
#             icon_size (int)       : size of icons
#             multi_select (bool)   : multiple selection. Default False.
#         """
#         # text list arg ------------------------------------------
#         txt_list = ["text_item 00", "text_item 01", "text_item 02", "text_item 03", "text_item 04"]
#         txt_list = compose_dict(kwargs, 'txt_list', list, txt_list, True)
#         # image list arg -----------------------------------------
#         img_list = [None for x in range(len(txt_list))]
#         img_list = compose_dict(kwargs, 'img_list', list, img_list, True)
#         # icon list arg ------------------------------------------
#         icon_list = [None for x in range(len(txt_list))]
#         icon_list = compose_dict(kwargs, 'icon_list', list, icon_list, True)
#         icon_size = compose_dict(kwargs, 'icon_size', int, 22, False)
#         # multi select -------------------------------------------
#         self._multi_select = compose_dict(kwargs, 'multi_select', bool, False, False)
#         # base init ------------------------------------------
#         super().__init__(name=name, **kwargs)
#         self.container.spacing = 0
#         self.container.padding = [0, self.theme.geometry['padding']]
#         # themes config --------------------------------------
#         # UI widgets -----------------------------------------
#         self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True,
#                                       scroll_type=['bars', 'content'], scroll_wheel_distance=dp(50), bar_width=dp(10))
#         self.scroll_view.bar_color = self.theme.colors['accent_face']
#         self.container.add_widget(self.scroll_view)
#         self.panels = GridLayout(cols=1, size_hint=(1, None))
#         self.panels.bind(minimum_height=self.panels.setter('height'))  # Permitir el autoajuste de altura
#         self.scroll_view.add_widget(self.panels)
#         # add panels
#         hp = 0
#         # txt_list.reverse()
#         for ii, txt in enumerate(txt_list):
#             self.add_item(txt, img_list[ii], icon_list[ii], icon_size)
#         self._scroll_y_mouse = 0
#         # Seleccion de iconos
#         self._selected_id = -1
#         # schedule -------------------------------------------
#         # Clock.schedule_once(lambda dt: self.update_geometry(dt))
#
#
#     """ UI Functions ------------------------------------------------"""
#     def update_geometry(self, dt=0):
#         '''Update button position value'''
#         # bb = self.theme.geometry['border']
#         # w, h = self.size
#         # x, y = self.pos
#         # self.scroll_view.pos = self.pos  # (x + bb, y +bb)
#         # self.scroll_view.size = self.size  # (w-bb*2, h-bb*2)
#         # super().update_geometry()
#         pass
#
#     def redraw(self, instance, args):
#         super().redraw(instance, args)
#         # for btn in self.panels.children:
#         #     btn.redraw(instance, args)
#         # self.update_geometry()
#
#     """ List functions ----------------------------------------------"""
#     def _create_item(self, text:str, img_source:str=None, icon_name:str=None, icon_size=16):
#
#         if img_source:  # ImageClickButton
#
#             item = ImageToggleButton(name=len(self.panels.children), source=img_source, text=text, size_hint=(1, None),
#                                      radius=(0, 0, 0, 0), draw_borders=(False, True, False, True))
#         elif icon_name:  # IconClickButton
#             item = IconToggleButton(name=len(self.panels.children), icon_name=icon_name, icon_size=icon_size,
#                                    text=text, size_hint=(1, None), radius=(0, 0, 0, 0), draw_borders=(False, True, False, True))
#         else:   # ClickButton
#             item = ToggleButton(name=len(self.panels.children), text_label=text, size_hint=(1, None),
#                                 text_halign="left", radius=(0, 0, 0, 0), draw_borders=(False, True, False, True))
#         item.flat = True
#         item.label.font_style = 'body'
#         item.label.font_size = 16
#         item.label.bold = False
#
#         # item.background_graphic._flat_color = self.theme.style[self.background_graphic.theme_color_face]
#         # item.text_halign = 'left'
#         # w, h = item.optimal_size()
#         item.height = dp(24)
#         item.bind(on_change_state=self._on_toggle_item)
#         # item.bind(on_click=self.on_click_item)
#         return item
#
#     def add_item(self, text:str, img_source:str=None, icon_name:str=None, icon_size=16):
#         item = self._create_item(text, img_source, icon_name, icon_size)
#         self.panels.add_widget(item)
#         self.panels.height += item.height
#         return item
#
#     def insert_item(self, id:int, text:str, img_source:str=None, icon_name:str=None, icon_size=16):
#         item = self._create_item(text, img_source, icon_name, icon_size)
#         self.panels.add_widget(item, len(self.panels.children) - id)
#         self.panels.height += item.height
#         return item
#
#     def remove_item(self, id:int, long:int=1):
#         lc = len(self.panels.children)
#         if id > lc or id < 0:
#             return False
#         if id+long-1 > lc:
#             long = lc - id
#         for ii in range(id, id + long):
#             item = self.panels.children[lc - ii - 1]  # , len(self.panels.children) - pos
#             self.panels.remove_widget(item)
#             self.panels.height -= item.height
#         return True
#
#     def get_item(self, id:int):
#         lc = len(self.panels.children)
#         return self.panels.children[lc - id - 1].text
#
#     def is_item(self, txt:str):
#         lc = len(self.panels.children)
#         for ii, item in enumerate(self.panels.children):
#             if txt == item.text:
#                 return lc - ii - 1
#         return -1
#
#     def modify_item(self, id:int, new_text:str, new_img:str=None, new_icon:str=None, new_icon_size=16):
#         # try:
#         lc = len(self.panels.children)
#         item = self.panels.children[lc - id - 1]
#         item.text = new_text
#         if isinstance(item, ImageClickButton):
#             item.image.source = new_img
#         elif isinstance(item, IconClickButton):
#             item.icon_name = new_icon
#             item.icon_size = new_icon_size
#         return True
#         # except:
#         #     return False
#
#     def clear_items(self):
#         self.panels.clear_widgets()
#
#     def add_list_items(self, txt_list:list, img_list:list=None, icon_list:list=None, icon_size=16):
#         try:
#             if not img_list:
#                 img_list = [None for x in range(len(txt_list))]
#             if not icon_list:
#                 icon_list = [None for x in range(len(txt_list))]
#             for ii, txt in enumerate(txt_list):
#                 self.add_item(txt, img_list[ii], icon_list[ii], icon_size)
#             return True
#         except:
#             return False
#
#     def insert_list_items(self, id:int, txt_list:list, img_list:list=None, icon_list:list=None, icon_size=16):
#         try:
#             if not img_list:
#                 img_list = [None for x in range(len(txt_list))]
#             if not icon_list:
#                 icon_list = [None for x in range(len(txt_list))]
#             for ii, txt in enumerate(txt_list):
#                 self.insert_item(id, txt, img_list[ii], icon_list[ii], icon_size)
#                 id += 1
#             return True
#         except:
#             return False
#
#     def get_txt_items(self):
#         txts = []
#         for it in self.panels.children:
#             txts.append(it.text)
#         txts.reverse()
#         return txts
#
#     def get_img_src_items(self):
#         imgs = []
#         for it in self.panels.children:
#             if isinstance(it, ImageClickButton):
#                 imgs.append(it.image.source)
#             else:
#                 imgs.append(None)
#         return imgs
#
#     def get_icon_name_items(self):
#         icons = []
#         for it in self.panels.children:
#             if isinstance(it, IconClickButton):
#                 icons.append(it.icon.icon_name)
#             else:
#                 icons.append(None)
#         return icons
#
#     def set_multi_select(self, value):
#         self._multi_select = compose(value, bool, False)
#
#     def get_multi_select(self):
#         return self._multi_select
#
#     multi_select = property(get_multi_select, set_multi_select)
#
#     def select(self, id:int):
#         tgl = self.panels.children[id]
#         tgl.state = 'down'
#         self._selected_id = id
#
#
#     """ UI Events ---------------------------------------------------"""
#     def _on_toggle_item(self, instance, state):
#         id = self.panels.children.index(instance)
#         # if not(self._scroll_y_mouse):
#         if not self._multi_select:
#             for tgl in self.panels.children:
#                 if tgl != instance:
#                     tgl.set_state('off')
#         instance.focus = True
#         self._selected_id = id
#         SelectListItemEventDispatcher.do_something(self, selected_id=id, text=instance.text_label)
#


class ListView(FocusBehavior, BoxPanel, SelectListItemEventDispatcher):  # Esto ESTA OBSOLETO. Derivar de RecycleView
    """
    Widget Kivy_KDW String List View
    Events: on_select_list_item(selected_id, text)
    """

    def __init__(self, name='string list view', **kwargs):
        """Constructor class
        Args:
            items_list (icon list) : list of icon text name
            multi_select (bool)   : multiple selection. Default False.
        """
        # text list arg ------------------------------------------
        items_list = compose_dict(kwargs, 'items_list', list, [], True)
        # multi select -------------------------------------------
        self._multi_select = compose_dict(kwargs, 'multi_select', bool, False, False)
        self.level_render = "medium"  # Se modifica cuando un item entra en edicion y pasa a "low"
        # base init ------------------------------------------
        super().__init__(name=name, **kwargs)
        self.container.spacing = 0
        self.container.padding = [0, self.theme.geometry['padding']]
        # themes config --------------------------------------
        # UI widgets -----------------------------------------
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True,
                                      scroll_type=['bars', 'content'], scroll_wheel_distance=dp(50), bar_width=dp(10))
        self.scroll_view.bar_color = self.theme.colors['accent_face']
        self.container.add_widget(self.scroll_view)
        # self.panels = GirdLayout(cols=1, size_hint=(1, None))
        self.panels = BoxLayout(orientation='vertical', size_hint_y=None)
        self.panels.bind(minimum_height=self.panels.setter('height'))  # Permitir el autoajuste de altura
        self.scroll_view.add_widget(self.panels)
        # add panels
        hp = 0
        # txt_list.reverse()
        for ii, item in enumerate(items_list):
            self.add_item(item)
        self._scroll_y_mouse = 0
        # Seleccion de iconos
        self._selected_id = -1
        self.level_render = "medium"
        Window.bind(on_key_down=self._on_keyboard_down)
        # schedule -------------------------------------------
        # Clock.schedule_once(lambda dt: self.update_geometry(dt))



    """ UI Functions ------------------------------------------------"""
    def update_geometry(self, dt=0):
        '''Update button position value'''
        # bb = self.theme.geometry['border']
        # w, h = self.size
        # x, y = self.pos
        # self.scroll_view.pos = self.pos  # (x + bb, y +bb)
        # self.scroll_view.size = self.size  # (w-bb*2, h-bb*2)
        # super().update_geometry()
        pass

    def redraw(self, instance, args):
        super().redraw(instance, args)
        # for btn in self.panels.children:
        #     btn.redraw(instance, args)
        # self.update_geometry()

    """ List functions ----------------------------------------------"""
    def add_item(self, item):
        self.panels.add_widget(item)
        item.bind(on_select_item=self._on_select_item)
        self.panels.height += item.height
        return item

    def insert_item(self, id:int, item):
        self.panels.add_widget(item, len(self.panels.children) - id)
        item.bind(on_select_item=self._on_select_item)
        self.panels.height += item.height
        return item

    def remove_item(self, item):
        self.panels.remove_widget(item)
        item.unbind('on_select_item')
        self.panels.height -= item.height
        return True

    def remove_items(self, item, long:int=1):
        id = self.panels.index(item)
        lc = len(self.panels.children)
        if id > lc or id < 0:
            return False
        if id+long-1 > lc:
            long = lc - id
        for ii in range(id, id + long):
            item = self.panels.children[lc - ii - 1]  # , len(self.panels.children) - pos
            self.panels.remove_widget(item)
            self.panels.height -= item.height
        return True

    def get_item(self, id:int):
        lc = len(self.panels.children)
        return self.panels.children[lc - id - 1].text

    def clear_items(self):
        self.panels.clear_widgets()

    def add_list_items(self, items_list:list):
        try:
            for ii, item in enumerate(items_list):
                self.add_item(item)
            return True
        except:
            return False

    def insert_list_items(self, id:int, items_list:list):
        try:
            for ii, item in enumerate(items_list):
                self.insert_item(len(self.panels.children) - ii, item)
            return True
        except:
            return False

    def set_multi_select(self, value):
        self._multi_select = compose(value, bool, False)
    def get_multi_select(self):
        return self._multi_select
    multi_select = property(get_multi_select, set_multi_select)

    def get_seledted_id(self):
        return self._selected_id

    def get_selected_file_name(self):
        return self.panels.children[self._selected_id].text

    """ UI Events ---------------------------------------------------"""
    def _on_select_item(self, instance):
        print("ListViewItem._on_select_item")
        id = self.panels.children.index(instance)
        # if not self._multi_select:
        #     for it in self.panels.children:
        #         if it != instance:
        #             it.unselect_item()
        # instance.focus = True
        SelectListItemEventDispatcher.do_something(self, selected_id=id, item=instance)


        self._selected_id = id

    def on_focus(self, instance, value, *largs):
        print(f"ListView.on_focus {instance.uid} {value}")
        if self._selected_id > -1:
            self.panels.children[self._selected_id].change_focus(value)

    def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
        print("MDDocumentEditor->_on_keyboard_down Codigo de Teclas", keycode, modifier)
        print (self.focused)
        if self.focused:
            if keycode == 273:  # Flecha Arriba

                print("Flecha Arriba")
            elif keycode == 274:  # Flecha Abajo
                print("Flecha Abajo")