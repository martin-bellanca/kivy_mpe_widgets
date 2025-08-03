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
Tree Base widget for kivy_dkw \n
Created on 06/10/2024

@author: mpbe
@note:
'''


# imports del sistema -------------------------------------------------------

from helpers_mpbe.python import compose, compose_dict
# Kivy imports --------------------------------------------------------------
import kivy
kivy.require('1.10.1')
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.uix.label import Label
from kivy.uix.image import Image
# kivy_dkw ------------------------------------------------------------------
from helpers_mpbe.utils import rgba_to_hex_with_alpha as rgb_to_hex
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.theming import ThemableBehavior
# from kivy_mpbe_widgets.wg_panels.panels import Panel
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickIcon
from kivy_mpbe_widgets.wg_buttons.toggle_buttons import ToggleButton
# from kivy_mpbe_widgets.events.list_view_events import SelectListItemEventDispatcher
from kivy_mpbe_widgets.events.widgets_events import HotlightEventDispatcher
from kivy_mpbe_widgets.wg_font_icons.font_icon import FontIcon
from kivy_mpbe_widgets.graphics.items_graphics import GHotlightItem, GFocusItem, GSelectItem
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_inputs.inputs import EditableTextLabel
from kivy_mpbe_widgets.wg_labels.font_icon_labels import FontIconLabel

Builder.load_string('''
<IconNode>:
    orientation: 'horizontal'
    spacing: 4
    height: self.icon_size + self.margin
    size_hint_y: None
    color_selected: self.theme.colors['pressed_face']
    Image:
        id: icon
        source: root.icon_source
        size_hint: (None, None)
        allow_stretch: True
        pos_hint:{'center_y': 0.5}
        size: (root.icon_size, root.icon_size)
        # center_y: root.center_y
    Label:
        id: label
        text: root.text
        color: root.text_color
        valign: 'middle'
        halign: 'left'
        size_hint_y: None
        height: root.height
        markup: root.markup
        text_size: self.size


# <FontIconNode>:
#     orientation: 'horizontal'
#     spacing: 4
#     height: self.icon_size + self.margin
#     size_hint_y: None
#     color_selected: self.theme.colors['pressed_face']
#     FontIcon:
#         id: font_icon
#         icon_name: root.icon_name
#         icon_size: root.icon_size
#         icon_family: root.icon_family
#         icon_color: root.icon_color
#         size_hint: (None, None)
#         allow_stretch: True
#         pos_hint:{'center_y': 0.5}
#         # center_y: root.center_y
#     Label:
#         id: label
#         text: root.text
#         color: root.text_color
#         valign: 'middle'
#         halign: 'left'
#         size_hint_y: None
#         height: root.height
#         markup: root.markup
#         text_size: self.size

''')


class IconNode(BoxLayout, TreeViewNode, ThemableBehavior):
    text = StringProperty(defaultvalue='')
    text_color = ListProperty((0, 0, 0, 1))
    markup = BooleanProperty(defaultvalue=False)
    icon_source = StringProperty(defaultvalue='')
    icon_size = NumericProperty(defaultvalue=24)
    icon_color = ListProperty((0.8, 0.8, 0.8, 1))
    margin = NumericProperty(defaultvalue=6)
    path_node = StringProperty(default=None)


# class FontIconNode_BK(BoxLayout, TreeViewNode, ThemableBehavior):
#     text = StringProperty(defaultvalue='Item')
#     text_color = ListProperty((0, 0, 0, 1))
#     markup = BooleanProperty(defaultvalue=False)
#     icon_name = StringProperty(defaultvalue='')
#     icon_size = NumericProperty(defaultvalue=24)
#     icon_family = StringProperty(defaultvalue='materialdesignicons-webfont')
#     icon_color = ListProperty((0.8, 0.8, 0.8, 1))
#     margin = NumericProperty(defaultvalue=6)
#     path_node = StringProperty(default=None)


class FontIconNode(TreeViewNode, ThemeWidget, HotlightEventDispatcher):
    text = StringProperty(defaultvalue='Item')
    # text_color = ListProperty((0, 0, 0, 1))
    markup = BooleanProperty(defaultvalue=False)
    icon_name = StringProperty(defaultvalue='')
    icon_size = NumericProperty(defaultvalue=24)
    # icon_family = StringProperty(defaultvalue='materialdesignicons-webfont')
    icon_color = ListProperty((0.8, 0.8, 0.8, 1))
    path_node = StringProperty(default=None)

    def __init__(self, text, icon_name='home', markup=True, icon_size=24, icon_color=None, type=None):
        """
        Constructor class
        """
        TreeViewNode.__init__(self)
        ThemeWidget.__init__(self)
        # argumentos -------------------------------------
        self._touch_pos = (0,0)
        self.text = text
        self.icon_name = icon_name
        self.icon_size = icon_size
        self.icon_color = icon_color if icon_color else self.theme.colors['icons']
        self.type = type  # Para definir que tipo de nodo es
        # Node config ------------------------------------
        self.size_hint_y = None
        self.height = self.icon_size + 6
        self.color_selected = self.theme.colors['pressed_face']
        self.color_selected[3] = 1.0
        self._selected = False
        # Text label -------------------------------------
        self._label = TextLabel(text=self.text, font_style='body', valign="center", size_hint=(1, 1))
        self._label.font_size = 16
        self._label.bold = False
        self._label.shorten = True
        # Icon -------------------------------------------
        self._icon = FontIconLabel(icon_name=self.icon_name, icon_color=self.icon_color,
                                   icon_size=self.icon_size, size_hint_x=None)
        self._icon.width += 2
        # Asigna al contenedor ---------------------------
        # self._ly_icon = BoxLayout(orientation='horizontal')
        self.container.orientation = 'horizontal'
        self.container.add_widget(self._icon)
        self.container.add_widget(self._label)
        # Canvas -----------------------------------------
        # with self.canvas.before:
        #     pass
        with self.canvas.after:
            # self.graphic_select = GSelectItem(self)
            # self.graphic_focus = GFocusItem(self)
            self.graphic_hotlight = GHotlightItem(self)

    def _hotlight_event(self, state, mouse_pos):
        # HotlightEventDispatcher.do_something(self, state, mouse_pos)
        if self.parent:
            self.parent.on_hotlight_item(self, state)
            self._label.editable = state

    # def on_select(self, instance, value):
    #     print('FontIconNode.Seleted')




class EditableFontIconNode(TreeViewNode, ThemeWidget, HotlightEventDispatcher):
    text = StringProperty(defaultvalue='Item')
    # text_color = ListProperty((0, 0, 0, 1))
    markup = BooleanProperty(defaultvalue=False)
    icon_name = StringProperty(defaultvalue='')
    icon_size = NumericProperty(defaultvalue=24)
    # icon_family = StringProperty(defaultvalue='materialdesignicons-webfont')
    icon_color = ListProperty((0.8, 0.8, 0.8, 1))
    path_node = StringProperty(default=None)

    def __init__(self, text, icon_name='home', markup=True, icon_size=24, icon_color=None, type=None):
        """
        Constructor class
        """
        TreeViewNode.__init__(self)
        ThemeWidget.__init__(self)
        # argumentos -------------------------------------
        self._touch_pos = (0,0)
        self.text = text
        self.icon_name = icon_name
        self.icon_size = icon_size
        self.icon_color = icon_color if icon_color else self.theme.colors['icons']
        self.type = type  # Para definir que tipo de nodo es
        # Node config ------------------------------------
        self.size_hint_y = None
        self.height = self.icon_size + 6
        self.color_selected = self.theme.colors['pressed_face']
        self.color_selected[3] = 1.0
        self._selected = False
        # Text label -------------------------------------
        self.label = EditableTextLabel(text=self.text, font_style='body', valign="center", size_hint=(1, 1))
        self.label.font_size = 16
        self.label.bold = False
        self.label._label.shorten = True
        self.label.editable = False
        # Icon -------------------------------------------
        self._icon = FontIconLabel(icon_name=self.icon_name, icon_color=self.icon_color,
                                   icon_size=self.icon_size, size_hint_x=None)
        self._icon.width += 2
        # Asigna al contenedor ---------------------------
        # self._ly_icon = BoxLayout(orientation='horizontal')
        self.container.orientation = 'horizontal'
        self.container.add_widget(self._icon)
        self.container.add_widget(self.label)
        # Canvas -----------------------------------------
        # with self.canvas.before:
        #     pass
        with self.canvas.after:
            # self.graphic_select = GSelectItem(self)
            # self.graphic_focus = GFocusItem(self)
            self.graphic_hotlight = GHotlightItem(self)

    def _hotlight_event(self, state, mouse_pos):
        # HotlightEventDispatcher.do_something(self, state, mouse_pos)
        if self.parent:
            self.parent.on_hotlight_item(self, state)
            self.label.editable = state




class FileNode(EditableFontIconNode):
    def __init__(self, text, icon_name='home', markup=True, icon_size=24, icon_color=None, type=None):
        EditableFontIconNode.__init__(self, text=text, icon_name=icon_name, markup=markup,
                              icon_size=icon_size, icon_color=icon_color, type=type)
        # Botones IconClick
        self.btn_new_file = None
        self.btn_new_folder = None
        self.btn_rename = None
        self.btn_duplicate = None
        self.btn_delete = None

    '''Visualizacion de Botones -----------------------------------------------'''
    def _show_btn(self, btn):
        # print(f"FileNode._show_btn {btn.icon_name}")
        col = self.theme.colors['icons']
        col[3] = 0
        btn.icon_color = col
        self.container.add_widget(btn)
        col[3] = 1
        anim = Animation(icon_color=col, duration=1.2)
        anim.start(btn)

    def _hide_btn(self, btn):
        def remove_btn(anim, var):
            self.container.remove_widget(btn)
        if btn:
            # print(f"FileNode._hide_btn {btn.icon_name}")
            col = self.icon_color
            col[3] = 0
            anim = Animation(icon_color=col, duration=0.6)
            anim.bind(on_complete=remove_btn)
            anim.start(btn)

    def _hotlight_event(self, state, mouse_pos):
        # HotlightEventDispatcher.do_something(self, state, mouse_pos)
        # print(f"FileNode._hotlight_event - selected: {self.is_selected}")
        # print(f"FileNode._hotlight_event node:{self.text}, state:{state}, type:{self.type}")
        if self.parent:
            if state:  # nodo con hightlight
                # self.parent.on_hotlight_item(self, state)
                self.label.editable = state
                # Botones IconClick
                if self.type == "folder":
                    self.btn_new_file = ClickIcon(icon_name='note-plus', icon_size=18, size_hint_x=None)
                    self._show_btn(self.btn_new_file)
                    self.btn_new_folder = ClickIcon(icon_name='folder-plus', icon_size=18, size_hint_x=None)
                    self._show_btn(self.btn_new_folder)
                    if not(self.is_selected):
                        self.btn_rename = ClickIcon(icon_name='rename-box', icon_size=18, size_hint_x=None)
                        self._show_btn(self.btn_rename)
                        self.btn_delete = ClickIcon(icon_name='delete', icon_size=18, size_hint_x=None)
                        self._show_btn(self.btn_delete)

                elif self.type == "file" and not(self.is_selected):
                    self.btn_rename = ClickIcon(icon_name='rename-box', icon_size=18, size_hint_x=None)
                    self._show_btn(self.btn_rename)
                    self.btn_duplicate = ClickIcon(icon_name='file-multiple', icon_size=18, size_hint_x=None)
                    self._show_btn(self.btn_duplicate)
                    self.btn_delete = ClickIcon(icon_name='delete', icon_size=18, size_hint_x=None)
                    self._show_btn(self.btn_delete)

                elif self.type == "root_folder":
                    self.btn_new_file = ClickIcon(icon_name='note-plus', icon_size=18, size_hint_x=None)
                    self._show_btn(self.btn_new_file)
                    self.btn_new_folder = ClickIcon(icon_name='folder-plus', icon_size=18, size_hint_x=None)
                    self._show_btn(self.btn_new_folder)
            else:  # nodo sin hightlight
                if self.type == "folder":
                    self._hide_btn(self.btn_new_file)
                    self.btn_new_file = None
                    self._hide_btn(self.btn_new_folder)
                    self.btn_new_folder = None
                    if not(self.is_selected):
                        self._hide_btn(self.btn_rename)
                        self.btn_rename = None
                        self._hide_btn(self.btn_delete)
                        self.btn_delete = None
                elif self.type == "file" and not(self.is_selected):
                    self._hide_btn(self.btn_rename)
                    self.btn_rename = None
                    self._hide_btn(self.btn_duplicate)
                    self.btn_duplicate = None
                    self._hide_btn(self.btn_delete)
                    self.btn_delete = None
                elif self.type == "root_folder":
                    self._hide_btn(self.btn_new_file)
                    self.btn_new_file = None
                    self._hide_btn(self.btn_new_folder)
                    self.btn_new_folder = None

    def on_touch_down(self, touch):
        # Verifica si el toque ocurrió dentro del área del nodo
        if self.collide_point(*touch.pos):
            # print(f"Nodo seleccionado: {self.text}")
            self._hide_btn(self.btn_rename)
            self.btn_rename = None
            self._hide_btn(self.btn_delete)
            self.btn_delete = None

            return True  # Indica que el evento ha sido manejado
        return super(FileNode, self).on_touch_down(touch)




# class IconNode_BK(BoxLayout, TreeViewNode):
#
#     def __init__(self, icon_source, text, markup=False, icon_size=24, **kwargs):
#         super().__init__(**kwargs)
#         self.orientation = 'horizontal'
#         self.spacing = 5  # Espacio entre el ícono y el texto
#         # Tamaño del ícono
#         margin = 6
#         self.height = icon_size + margin
#         self.size_hint_y = None  # Establecer altura fija para el nodo
#
#         # Imagen para el ícono
#         self.icon = Image(source=icon_source, size_hint = (None, None), size = (icon_size, icon_size),
#                           allow_stretch = True, pos_hint={'center_y': 0.5})
#         self.add_widget(self.icon)
#         # Label para el texto
#         self.label = Label(text=text, valign='middle', halign='left',
#                            size_hint_y=None, height=self.height, markup=markup)
#         self.label.bind(size=self.label.setter('text_size'))  # Ajustar el tamaño del texto
#         self.add_widget(self.label)
#
#         # schedule -------------------------------------------
#         Clock.schedule_once(self._finish_init, 1.0)
#
#     def _finish_init(self, dt):
#         self.icon.center_y = self.center_y
#
#
# class FontIconNode_BK(BoxLayout, TreeViewNode):
#     # text = StringProperty(defaultvalue='Item')
#     # icon_source = StringProperty(defaultvalue='')
#
#     def __init__(self, text, markup=False, icon_size=24, **kwargs):
#         """
#         Icono en formato de letra
#             icon_family: str - Nombre del fuente de iconos
#             icon_name: str - Nombre del icono
#             icon_size: int - Tamaño del icono
#             icon_color: list RGBA
#         """
#         name = compose_dict(kwargs, "icon_name", str, 'account', acept_none=False)
#         super().__init__(**kwargs)
#         self.orientation = 'horizontal'
#         self.spacing = 5  # Espacio entre el ícono y el texto
#         # Tamaño del ícono
#         margin = 6
#         self.height = icon_size + margin
#         self.size_hint_y = None  # Establecer altura fija para el nodo
#
#         # Imagen para el ícono
#         # family = list(self.theme.icons.keys())
#         self.font_icon = FontIcon(icon_name=name, icon_size=icon_size)   # NO TOMA EL ICONO
#         self.add_widget(self.font_icon)
#         # Label para el texto
#         self.label = Label(text=text, valign='middle', halign='left',
#                            size_hint_y=None, height=self.height, markup=markup)
#         self.label.bind(size=self.label.setter('text_size'))  # Ajustar el tamaño del texto
#         self.add_widget(self.label)
#
#         # schedule -------------------------------------------
#         Clock.schedule_once(self._finish_init, 1.0)
#
#     def _finish_init(self, dt):
#         self.font_icon.center_y = self.center_y