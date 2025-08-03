#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  font_icon_labels.py
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
Created on 11/09/2019

@author: mpbe
'''

# imports del sistema -------------------------------------------------------
import os
import sys
import math
from helpers_mpbe.python import compose_dict
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.event import EventDispatcher
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import Label as CTLabel
from kivy.core.text.text_layout import layout_text as LText
from kivy.uix.label import Label as KVLabel
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.properties import Property, NumericProperty, StringProperty, ListProperty
from kivy.properties import ObjectProperty, BooleanProperty, BoundedNumericProperty
from kivy.properties import OptionProperty, ReferenceListProperty, AliasProperty
from kivy.properties import DictProperty, VariableListProperty, ConfigParserProperty
# kivy_mpw ------------------------------------------------------------------
import kivy_mpbe_widgets
import kivy_mpbe_widgets.rsrc_themes
from helpers_mpbe.utils import rgba_to_hex_with_alpha as rgb_to_hex
from kivy_mpbe_widgets.theming import ThemableBehavior, Theme
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel

# Works Dirs ----------------------------------------------------------------
# KV_DIRECTORY = kivy_dkw.DIR_BASE + '/wg_font_icons/'
# Builder.load_file(KV_DIRECTORY+'font_icon.kv')
Builder.load_string('''
<FontIcon>:
    # Ids Internals Widgets ---------------
    font_name: self.icon_family
    font_size: self.icon_size
    color: self.icon_color
    valign: 'center'
    halign: 'center'
    # size_hint: (None, None)
    text_size: self.size
    width: self.texture_size[0] if self.size_hint_x == None else self.size_hint_x * root.width
    height: self.texture_size[1] if self.size_hint_y == None else self.size_hint_y * root.height
''')


class FontIcon(KVLabel, ThemableBehavior):
    """
    Icono en formato de letra
    """
    icon_family = StringProperty('materialdesignicons-webfont')
    icon_name = StringProperty('apps')
    icon_size = NumericProperty(32)
    icon_color = ListProperty([0, 0, 0, 1])  # Color en formato hexadecimal

    def __init__(self, icon_name='apps', icon_size=16, icon_family='materialdesignicons-webfont', **kwargs):
        '''
        Constructor class.
        **Parameters:**
        - icon_family (str):
        - icon_name (str):
        - icon_size (int):
        - icon_color (list): Lista con valores (R,G,B,A)
        - halign (str): Indica la alineación horizontal del icono. Puede ser 'left', 'center' o 'right'
        - valign (str): Indica la alineación vertical del icono. Puede ser 'top', 'middle', 'bottom'
        '''
        ThemableBehavior.__init__(self)
        self.icon_family = icon_family
        self._list_icons = self.theme.icons[icon_family]
        self.icon_name = icon_name
        KVLabel.__init__(self, **kwargs)
        self.icon_size = icon_size
        self.text = self._list_icons[self.icon_name]
        self.icon_color = self.theme.colors['icons']


    # Events ----------------------------------------------
    def on_icon_family(self, instance, value):
        self.icon_family = value
        icons = self.theme.icons[value]
        self._list_icons = icons

    def on_icon_name(self, instance, value):
        self.text = self._list_icons[self.icon_name]

    # def on_icon_size(self, instance, value):
    #     self.icon_size = value
    #
    # def on_icon_color(self, instance, value):
    #     self.icon_color = value


