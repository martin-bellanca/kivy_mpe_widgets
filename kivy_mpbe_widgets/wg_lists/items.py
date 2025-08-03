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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.uix.label import Label
from kivy.uix.image import Image
# kivy_dkw ------------------------------------------------------------------
from helpers_mpbe.utils import rgba_to_hex_with_alpha as rgb_to_hex
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.events.list_view_events import SelectItemEventDispatcher
from kivy_mpbe_widgets.wg_buttons.toggle_buttons import ToggleButton, ToggleButtonLabel
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButtonLabel
# from kivy_dkw.wg_font_icons.font_icon import FontIcon
from kivy_mpbe_widgets.wg_labels.font_icon_labels import FontIconWText, FontIconLabel


Builder.load_string('''
<BaseListItem@BoxLayout>:
    orientation: 'horizontal'
    # spacing: 4
    # height: self.icon_size + self.margin
    size_hint_y: None
''')


class BaseListItem(BoxLayout, SelectItemEventDispatcher):
    # item_selected = BooleanProperty(defaultvalue=False)

    def __init__(self):
        super().__init__()

    def activate_item(self):
        raise NotImplementedError(f"{self.__name__}.activate_item Not Implement")

    def desactivate_item(self):
        raise NotImplementedError(f"{self.__name__}.desactivate_item Not Implement")


class TextItem(BaseListItem):
    text = StringProperty(defaultvalue="")

    def __init__(self, text):
        """Constructor class
        Args:
            text (str)       : text of item
        """
        super().__init__()
        item = ToggleButton(text=text, size_hint=(1, None), text_halign="left", radius=(0, 0, 0, 0),
                            draw_borders=(False, True, False, True), not_off=True)
        item.flat = True
        item.label.font_style = 'body'
        item.label.font_size = 16
        item.label.bold = False
        item.height = dp(24)
        item.bind(on_change_state = self._on_toggle_item)
        self._item = item
        self.add_widget(item)
        self.text = text
        self.height = dp(24)


    # Item manipulation functions ----------------------------------------------
    def activate_item(self):
        self._item.set_state('on')

    def desactivate_item(self):
        self._item.set_state('off')

    # Event functions -----------------------------------------------------------
    def on_text(self, instance, value):
        self._item.text_label = value

    def _on_toggle_item(self, instance, state):
        if state == "on":
            instance.focus = True
            self._item.set_state(True)
            SelectItemEventDispatcher.do_something(self)
        else:
            self._item.set_state(False)


class IconItem(BaseListItem):
    text = StringProperty(defaultvalue="")
    icon_name = StringProperty(defaultvalue='alarm')
    icon_size = StringProperty(defaultvalue=24)

    def __init__(self, text, icon_name='alarm', icon_size=24):
        """Constructor class
        Args:
            text (str)       : text of item
            icon_name (str)  : icon name
            icon_size (int)  : size of icons
        """
        super().__init__()
        lbl = FontIconWText(text=text, font_style='body', icon_name=icon_name,
                            icon_align='left', icon_size=icon_size)
        lbl._text.font_size = 16
        lbl._text.halign = 'left'
        lbl._text.shorten = True
        lbl._icon.size_hint = (None, 1)
        item = ToggleButtonLabel(widget_label=lbl, size_hint=(1, None), radius=(0, 0, 0, 0),
                                 draw_borders=(False, True, False, True), not_off=True)
        item.flat = True
        hit = icon_size + 10
        item.height = dp(hit)
        item.bind(on_change_state=self._on_toggle_item)
        self._item = item
        self.add_widget(item)
        self.text = text
        self.height = dp(hit)

    # Item manipulation functions ----------------------------------------------
    def activate_item(self):
        self._item.set_state('on')

    def desactivate_item(self):
        self._item.set_state('off')

    # Event functions -----------------------------------------------------------
    def on_text(self, instance, value):
        self._item.widget_label.text = value

    def _on_toggle_item(self, instance, state):
        if state == "on":
            instance.focus = True
            self._item.set_state(True)
            SelectItemEventDispatcher.do_something(self)
        else:
            self._item.set_state(False)


class FileItem(BaseListItem):
    text = StringProperty(defaultvalue="")
    icon_name = StringProperty(defaultvalue='file-document')
    icon_size = StringProperty(defaultvalue=18)
    show_save = BooleanProperty(defaultvalue=False)

    def __init__(self, text, icon_name='file-document', icon_size=24):
        """Constructor class
        Args:
            text (str)       : text of item
            icon_name (str)  : icon name
            icon_size (int)  : size of icons
        """
        super().__init__()
        # Label con el icon del archivo
        lbl = FontIconWText(text=text, font_style='body', icon_name=icon_name,
                            icon_align='left', icon_size=icon_size)
        lbl._text.font_size = 16
        lbl._text.halign = 'left'
        lbl._text.shorten = True
        lbl._icon.size_hint = (None, 1)
        item = ToggleButtonLabel(widget_label=lbl, size_hint=(1, None), radius=(0, 0, 0, 0),
                                 draw_borders=(False, True, False, True), not_off=True)
        item.flat = True
        hit = icon_size + 10
        item.height = dp(hit)
        item.bind(on_change_state=self._on_toggle_item)
        self._item = item
        self.add_widget(item)
        self.text = text
        # Boton de grabar
        lbl = FontIconLabel(icon_name='content-save', icon_size=icon_size)
        # lbl.padding = 0
        # lbl.spacing = 0
        self.btn_save = ClickButtonLabel(widget_label=lbl, size_hint_x=None, radius=(0, 0, 0, 0))
        self.btn_save.widget_graphic.border_width = 1
        # self.add_widget(self.btn_save)
        self.btn_save.width = hit
        # Boton de opciones
        lbl = FontIconLabel(icon_name='dots-vertical', icon_size=icon_size)
        self.btn_options = ClickButtonLabel(widget_label=lbl, size_hint_x=None, radius=(0, 0, 0, 0))
        self.btn_options.widget_graphic.border_width = 1
        # self.add_widget(self.btn_options)
        self.btn_options.width = 18

        self.height = dp(hit)

    # Item manipulation functions ----------------------------------------------
    def activate_item(self):
        self._item.set_state('on')
        self.add_widget(self.btn_save)
        self.add_widget(self.btn_options)

    def desactivate_item(self):
        self._item.set_state('off')
        self.remove_widget(self.btn_save)
        self.remove_widget(self.btn_options)

    # Event functions -----------------------------------------------------------
    def on_text(self, instance, value):
        self._item.widget_label.text = value

    def _on_toggle_item(self, instance, state):
        if state == "on":
            instance.focus = True
            self.activate_item()
            SelectItemEventDispatcher.do_something(self)
        else:
            self.desactivate_item()






class ImageItem(BaseListItem):  # TODO: Sin Terminar
    text = StringProperty(defaultvalue="")
    image_source = StringProperty(defaultvalue=None)

    def __init__(self, text=None, img_source=None):
        """Constructor class
        Args:
            text (str)       : text of item
            img_source (str) : image source path
        """
        super().__init__()
        item = ToggleButtonLabel(source=img_source, text=text, size_hint=(1, None),
                                     radius=(0, 0, 0, 0), draw_borders=(False, True, False, True))
        item.flat = True
        item.label.font_style = 'body'
        item.label.font_size = 16
        item.label.bold = False
        item.height = dp(image_size + 8)
        self._item = item
        self.add_widget(item)
        self.text = text

    # Item manipulation functions ----------------------------------------------

    # Event functions -----------------------------------------------------------
    def on_text(self, instance, value):
        self._item.text_label = value

    def on_image_source(self, instance, value):
        pass

    def _on_toggle_item(self, instance, state):
        instance.focus = True
        if state == "down":
            self.item_selected = True


