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
from kivy.animation import Animation
import kivy_mpbe_widgets.rsrc_themes
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.wg_font_icons.font_icon import FontIcon
from kivy_mpbe_widgets.behaviors import IconBehavior
from kivy_mpbe_widgets.wg_labels.base_label import BaseLabel
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_font_icons.font_icon import FontIcon


class FontIconLabel(FontIcon, BaseLabel):
    """ Graphic Label functions -----------------------------------------------------------"""

    def lbl_disabled(self, value):
        pass

    def lbl_hotlight(self, value):
        if value:
            co = self.theme.colors['hotlight_border']
            co[3] = 1.0
            anim = Animation(color=co, duration=.6)
            anim.start(self)
        else:
            co = self.theme.colors['icons']
            anim = Animation(color=co, duration=.6)
            anim.start(self)

    def lbl_focus(self, value):
        pass

    def lbl_activate(self, value):
        pass


class FontIconWText(IconBehavior, BoxLayout, ThemableBehavior, BaseLabel):
    '''Label widget whith font icon'''
    # Globals Variable ---------------------------------
    # Properties ---------------------------------------
    text = StringProperty(defaultvalue='')
    font_style = OptionProperty(defaultvalue="button", options=["title", "subhead", "body", "body_bold", "caption", "button", "error",
                                         "secundary", "hint"])
    icon_align = OptionProperty(defaultvalue="center", options=["left", "right", "top", "bottom"])

    def __init__(self, text, icon_name, font_style='body', icon_size=24, icon_align='top',
                 icon_family='materialdesignicons-webfont', **kwargs):
        """
        Constructor Class.
        **Parameters:**
        - text (str): Text of label
        - icon_name:
        - font_style (str): Estilo del Texto. ["title", "subhead", "body", "body_bold", "caption", "button", "error", "secundary", "hint"]. Default "body"
        - icon_size:
        - icon_family:
        - icon_align (str): "left", "right", "top", "bottom"
        **Keyword arguments:**
        """
        # Keyword arguments ----------------------------------
        BoxLayout.__init__(self, **kwargs)
        IconBehavior.__init__(self, icon_name, icon_size, icon_family, **kwargs)
        ThemableBehavior.__init__(self)
        self._text = TextLabel(text=text, font_style=self.font_style, size_hint=(1, 1))
        self.text =  text
        self.font_style = font_style
        self.icon_align = icon_align
        self.size_hint = (1, 1)

    def _align_icon(self):
        if self.icon_align == 'left':
            self.orientation = 'horizontal'
            # Icon
            self._icon.halign = 'right'
            self._icon.valign = 'center'
            # Text
            self._text.halign = 'left'
            self._text.valign = 'center'
            # add_widgets
            self.add_widget(self._icon)
            self.add_widget(self._text)
        elif self.icon_align == 'right':
            self.orientation = 'horizontal'
            # Icon
            self._icon.halign = 'left'
            self._icon.valign = 'center'
            # Text
            self._text.halign = 'right'
            self._text.valign = 'center'
            # add_widgets
            self.add_widget(self._text)
            self.add_widget(self._icon)
        elif self.icon_align == 'bottom':
            self.orientation = 'vertical'
            # Icon
            self._icon.halign = 'center'
            self._icon.valign = 'top'
            # Text
            self._text.halign = 'center'
            self._text.valign = 'bottom'
            # add_widgets
            self.add_widget(self._text)
            self.add_widget(self._icon)
        else:  # Top
            self.orientation = 'vertical'
            # Icon
            self._icon.halign = 'center'
            self._icon.valign = 'bottom'
            # Text
            self._text.halign = 'center'
            self._text.valign = 'top'
            # add_widgets
            self.add_widget(self._icon)
            self.add_widget(self._text)

    """ Graphic Label functions -----------------------------------------------------------"""
    def lbl_disabled(self, value):
        pass

    def lbl_hotlight(self, value):
        if value:
            co = self.theme.colors['hotlight_border']
            co[3] = 1.0
            anim = Animation(color=co, duration=.6)
            anim.start(self._icon)
            anim.start(self._text)
        else:
            co = self.theme.colors['icons']
            anim = Animation(color=co, duration=.6)
            anim.start(self._icon)
            anim.start(self._text)

    def lbl_focus(self, value):
        pass

    def lbl_activate(self, value):
        pass

    # Events ----------------------------------------------
    def on_icon_align(self, instance, value):
        if self._text and self._icon:
            self.remove_widget(self._icon)
            self.remove_widget(self._text)
            self._align_icon()

    def on_text(self, instance, value):
        if self._text:
            self._text.text = value

    def on_font_style(self, instance, value):
        if hasattr(self, "_text"):
            self._text.font_style = value
