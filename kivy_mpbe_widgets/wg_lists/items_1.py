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


# imports del sistema -------------------------------------------------------

from helpers_mpbe.python import compose, compose_dict
# Kivy imports --------------------------------------------------------------
import kivy
kivy.require('1.10.1')
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty, BoundedNumericProperty
from kivy.uix.textinput import TextInput
# from kivy.uix.label import Label
# from kivy.uix.image import Image
# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from helpers_mpbe.utils import rgba_to_hex_with_alpha as rgb_to_hex
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.events.input_events import StartEditingEventDispatcher, FinishEditingEventDispatcher
from kivy_mpbe_widgets.graphics.items_graphics import GHotlightItem, GFocusItem, GSelectItem
from kivy_mpbe_widgets.events.list_view_events import SelectItemEventDispatcher, UnSelectItemEventDispatcher
from kivy_mpbe_widgets.wg_buttons.toggle_buttons import ToggleButton, ToggleButtonLabel
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButtonLabel
# from kivy_mpbe_widgets.wg_font_icons.font_icon import FontIcon
from kivy_mpbe_widgets.wg_labels.font_icon_labels import FontIconWText, FontIconLabel
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_inputs.inputs import EditableTextLabel


Builder.load_string('''
<BaseItem>:
    size_hint_y: None
    height: 30
    canvas.before:
        # Fondo ---------------------------------------------------
        Color:
            rgba: 0.8, 0.8, 0.8, self.alpha_background  # Fondo gris claro
        Rectangle:
            size: self.size[0]-self.theme.geometry['border']*2, self.size[1]
            pos: self.pos[0]+self.theme.geometry['border'], self.pos[1]
        Color:
            rgba: 0.4, 0.4, 0.4, 0.4  # Borde inferior gris oscuro
        Line:
            width: 1
            points: self.x+self.theme.geometry['border']+1, self.y, self.right-self.theme.geometry['border']*2, self.y
''')



class BaseItem(ThemeWidget, SelectItemEventDispatcher, UnSelectItemEventDispatcher):
    alpha_background = BoundedNumericProperty(defaultvalue=0.2, min=0.0, max=1.0)
    """"""
    # selected = BooleanProperty(defaultvalue=False)

    def __init__(self, parent, selected=False, multiselect=False, click_unselect=False, **kwargs):
        """
        Constructor BaseItem class
        Args:
            selected (bool): Indica si el item se inicia seleccionado
            multiselect (bool): Indica si esta habilitada la selección multiple
            click_unselect (bool): Indica si al hacer click sobre un item seleccionado, se des-selecciona
        """
        super().__init__(kwargs)
        SelectItemEventDispatcher.__init__(self)
        UnSelectItemEventDispatcher.__init__(self)
        self.selected = selected
        self.multiselect = multiselect
        self.click_unselect = click_unselect
        self.is_editable = False  # Define si el item se puede editar
        ab = compose_dict(kwargs, 'active_background', bool, False, False)
        self.activate_background(ab)
        with self.canvas.before:
            self.graphic_select = GSelectItem(self)
        with self.canvas.after:
            self.graphic_focus = GFocusItem(self)
            self.graphic_hotlight = GHotlightItem(self)
        if selected:
            self.graphic_select.animate_select(True, self.center)

    # Funciones de Animacion ------------------------------------------------
    def activate_background(self, value):
        if value == True:
            self.alpha_background = 0.2
        else:
            self.alpha_background = 0.0

    def collide_point_focus(self, x, y):  # on windows coordinates
        try:
            # Check the position of the point
            # bpx, bpy = self.to_window(self.pos[0], self.pos[1], True)
            bpx, bpy = self.pos
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

    # Eventos de Teclado --------------------------------------------------
    # def  keyboard_on_key_down(self, windows, keycode, text, modifiers):
    #     # FocusBehavior.keyboard_on_key_up(self, window, keycode)
    #     print("Keyword Item")
    #     ne = None
    #     if keycode[0] in [9] and not 'shift' in modifiers:
    #         ne = self.get_focus_next()
    #         self.focus = False
    #     elif keycode[0] in [9] and 'shift' in modifiers:
    #         ne = self.get_focus_previous()
    #         self.focus = False
    #     if ne:
    #         ne.focus = True
    #         self.animate_focus(0.0)
    #         # x, y = window.window.mouse_pos
    #     return True
    #     pass

    # Eventos de Usuario ---------------------------------------------------
    def change_focus(self, value):
        # print(f"BaseItem.change_focus {self.uid}")
        # self.focus = value
        self.graphic_focus.animate_focus(value)

    def on_touch_down(self, touch):
        # print(f"BaseItem.on_touch_down {self.uid}")
        if touch.button=='left':
            if self.collide_point_focus(*touch.pos):
                self.change_focus(True)
                if self.selected and self.click_unselect:
                    self.graphic_select.animate_select(False, touch.pos)
                    self.selected = False
                    self.unselect_item()
                    UnSelectItemEventDispatcher.do_something(self)
                    print(f"BaseItem.on_touch_down 1 - {self.uid} {self.text} Unselect-> {self.selected}")
                elif not self.selected:
                    self.graphic_select.animate_select(True, touch.pos)
                    self.selected = True
                    self.select_item()
                    SelectItemEventDispatcher.do_something(self)
                    print(f"BaseItem.on_touch_down 2 - {self.uid} {self.text} Select-> {self.selected}")
            elif self.selected:
                self.change_focus(False)
                if not self.multiselect:
                    self.graphic_select.animate_select(False, touch.pos)
                    self.selected = False
                    self.unselect_item()
                    UnSelectItemEventDispatcher.do_something(self)
                    print(f"BaseItem.on_touch_down 3 - {self.uid} {self.text} Unselect is not multiline-> {self.selected}")
        # print(self.selected)

    # def _on_focus(self, instance, value, *largs):
    #     print(f"BaseItem.on_focus {instance.uid}")
    #     self.graphic_focus.animate_focus(value)

    # Funciones Abstractas -------------------------------------------------
    def select_item(self):
        # print("Select Item")
        # raise NotImplementedError(f"BaseItem.select_item Not Implement")
        pass

    def unselect_item(self):
        # print("UnSelect Item")
        # raise NotImplementedError(f"BaseItem.unselect_item Not Implement")
        pass


class TextItem(BaseItem):
    text = StringProperty(defaultvalue="")

    def __init__(self, text, active_background=False):
        """
        Constructor class
        Args:
            text (str)       : text of item
        """
        super().__init__(active_background=active_background)
        self.text=text
        self._label = TextLabel(text=self.text, font_style='body', valign="center", size_hint=(1, 1))
        self._label.font_size = 16
        self._label.bold = False
        self._label.padding_x = 2 + self.theme.geometry['border'] + self.theme.geometry['hotlight']

        self.add_widget(self._label)
        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)

    def _on_update_geometry(self, instance, value):
        self._label.pos = self.pos
        self._label.size = self.size

    def select_item(self):
        pass

    def unselect_item(self):
        pass


class EditableItem(BaseItem, StartEditingEventDispatcher, FinishEditingEventDispatcher):  #SEGUIR DE ACA
    text = StringProperty(defaultvalue="")

    def __init__(self, text, active_background=False):
        """
        Constructor class
        Args:
            text (str)       : text of item
        """
        BaseItem.__init__(self, active_background=active_background)
        StartEditingEventDispatcher.__init__(self)
        FinishEditingEventDispatcher.__init__(self)
        self.is_editable = True
        self.text = text
        self._label = EditableTextLabel(text=self.text, font_style='body', valign="center", size_hint=(1, 1))
        self._label.font_size = 16
        self._label.bold = False
        self._label._label.shorten = True
        # self._label._label.padding_x = 2 + self.theme.geometry['border'] + self.theme.geometry['hotlight']
        self._label.editable = False
        self.add_widget(self._label)
        self._label.bind(on_start_editing=self._on_start_editing,
                         on_finish_editing=self._on_finish_editing)

        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)

    def _on_update_geometry(self, instance, value):
        self._label.pos = self.pos
        self._label.size = self.size

    def select_item(self):
        self._label.editable = True

    def unselect_item(self):
        print("Un select Item")
        if self._label.in_edition:
            self._label.finish_editing(self._label)
            self.change_focus(False)

        self._label.editable = False

    def _on_start_editing(self, instance):
        # print(f"Start Editing")
        self.level_render = "low"
        StartEditingEventDispatcher.do_something(self)

    def _on_finish_editing(self, instance, text):
        print(f"Finish Editing: {text}")
        instance.text = text
        self.level_render = "medium"
        self.parent.parent.parent.parent.focused = True
        self.change_focus(True)
        FinishEditingEventDispatcher.do_something(self, text=instance.text)


