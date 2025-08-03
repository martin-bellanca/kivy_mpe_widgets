#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  image_labels.py
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
Created on 14/07/2024

@author: mpbe
'''

# imports del sistema -------------------------------------------------------
import os
import sys
import math
from helpers_mpbe.python import compose, compose_dict
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
from kivy.uix.image import Image as KVImage
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
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.wg_labels.base_label import BaseLabel
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.behaviors import ImageBehavior

# Works Dirs ----------------------------------------------------------------
KV_DIRECTORY = kivy_mpbe_widgets.DIR_BASE + '/wg_labels/'
Builder.load_file(KV_DIRECTORY+'image_labels.kv')


class ImageLabel(BoxLayout, ImageBehavior, BaseLabel):
    """ImageLabel"""

    def __init__(self, source, image_fit_mode='scale-down', **kwargs):
        """
        Constructor Class.
        **Parameters:**
        - source: str - Path hacia la imagen
        - image_fit_mode: ('scale-down', 'fill', 'contain', 'cover')
        **Keyword arguments:**
        """
        BoxLayout.__init__(self, **kwargs)
        ImageBehavior.__init__(self, source, image_fit_mode)
        self.add_widget(self._image)
        self.size_hint = (1, 1)
        self._image.size_hint = (1, 1)


class ImageWText(ImageBehavior, BoxLayout, ThemableBehavior, BaseLabel):
    '''Label widget whith Image'''
    # Globals Variable ---------------------------------
    # Properties ---------------------------------------
    text = StringProperty(defaultvalue='')
    font_style = OptionProperty(defaultvalue="button", options=["title", "subhead",
                                "body", "body_bold", "caption", "button", "error",
                                "secundary", "hint"])
    image_align = OptionProperty(defaultvalue="top", options=["left", "right", "top", "bottom"])

    def __init__(self, text, image_source, image_align='top', font_style='body', image_fit_mode='scale-down', **kwargs):
        """
        Constructor Class.
        **Parameters:**
        - text (str): Text of label
        - image_source: str - Path hacia la imagen
        - image_align (str): Puede ser "left", "right", "top", "bottom"
        - font_style (str): Estilo del Texto. ["title", "subhead", "body", "body_bold", "caption", "button", "error", "secundary", "hint"]. Default "body"
        - image_fit_mode: ('scale-down', 'fill', 'contain', 'cover')
        **Keyword arguments:**
        """
        # Keyword arguments ----------------------------------
        BoxLayout.__init__(self, **kwargs)
        ImageBehavior.__init__(self, image_source=image_source, image_fit_mode=image_fit_mode)
        ThemableBehavior.__init__(self)
        self.text = text
        self.font_style = font_style
        self._text = TextLabel(text=self.text, font_style=self.font_style, size_hint=(1, 1))
        self.image_align = image_align
        self._image_layout = AnchorLayout()
        self._image_layout.add_widget(self._image)
        self.size_hint = (1, 1)
        self._align_image()

    def _align_image(self):
        if self.image_align == 'left':
            self.orientation = 'horizontal'
            # Image
            self._image_layout.anchor_x = 'right'
            self._image_layout.anchor_y = 'center'
            # Text
            self._text.halign = 'left'
            self._text.valign = 'center'
            # add_widgets
            self.add_widget(self._image_layout)
            self.add_widget(self._text)
        elif self.image_align == 'right':
            self.orientation = 'horizontal'
            # Image
            self._image_layout.anchor_x = 'left'
            self._image_layout.anchor_y = 'center'
            # Text
            self._text.halign = 'right'
            self._text.valign = 'center'
            # add_widgets
            self.add_widget(self._text)
            self.add_widget(self._image_layout)
        elif self.image_align == 'bottom':
            self.orientation = 'vertical'
            # Image
            self._image_layout.anchor_x = 'center'
            self._image_layout.anchor_y = 'top'
            # Text
            self._text.halign = 'center'
            self._text.valign = 'bottom'
            # add_widgets
            self.add_widget(self._text)
            self.add_widget(self._image_layout)
        else:  # Top
            self.orientation = 'vertical'
            # Image
            self._image_layout.anchor_x = 'center'
            self._image_layout.anchor_y = 'bottom'
            # Text
            self._text.halign = 'center'
            self._text.valign = 'top'
            # add_widgets
            self.add_widget(self._image_layout)
            self.add_widget(self._text)

    # Events ----------------------------------------------
    def on_image_align(self, instance, value):
        if hasattr(self, "_text") and hasattr(self, "_image_layout"):
            self.remove_widget(self._image_layout)
            self.remove_widget(self._text)
            self._align_image()

    def on_text(self, instance, value):
        if hasattr(self, "_text"):
            self._text.text = value

    def on_font_style(self, instance, value):
        if hasattr(self, "_text"):
            self._text.font_style = value

    """ Graphic Label functions ---------------------------------------------------------------"""
    def lbl_disabled(self, value):
        pass

    def lbl_hotlight(self, value):
        if value:
            co = self.theme.colors['hotlight_border']
            co[3] = 1.0
            anim = Animation(color=co, duration=.6)
            anim.start(self._text)
        else:
            co = self.theme.colors['icons']
            anim = Animation(color=co, duration=.6)
            anim.start(self._text)

    def lbl_focus(self, value):
        pass

    def lbl_activate(self, value):
        pass

