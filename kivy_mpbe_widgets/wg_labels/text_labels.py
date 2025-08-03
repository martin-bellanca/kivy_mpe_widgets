#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  text_labels.py
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
Created on 15/09/2019

@author: mpbe
'''

# imports del sistema -------------------------------------------------------
from helpers_mpbe.python import compose_dict
# Kivy imports --------------------------------------------------------------
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.behaviors import FocusBehavior
from kivy.core.text import Label as CTLabel
from kivy.core.text.text_layout import layout_text as LText
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label as KVLabel
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import OptionProperty

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy.animation import Animation
import kivy_mpbe_widgets.rsrc_themes
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.wg_labels.base_label import BaseLabel
from kivy_mpbe_widgets.events.input_events import StartEditingEventDispatcher, FinishEditingEventDispatcher

# Works Dirs ----------------------------------------------------------------
KV_DIRECTORY = kivy_mpbe_widgets.DIR_BASE + '/wg_labels/'
Builder.load_file(KV_DIRECTORY+'text_labels.kv')

class TextLabel(KVLabel, ThemableBehavior, BaseLabel):  # , WGLabel
    '''Widget basic label.'''
    # Globals Variable ---------------------------------
    # Properties ---------------------------------------
    font_style = OptionProperty(defaultvalue="body", options=["title", "subhead", "body", "body_bold", "caption",
                                "button", "error", "secundary", "hint"])
    def __init__(self, text, style='body', halign='left', valign='middle', **kwargs):
        """
        Constructor Class.
        **Parameters:**
        **keyword arguments:**
        - text (str): <KVLabel>
        - font_style (str): Estilo del Texto. ["title", "subhead", "body", "body_bold", "caption", "button", "error", "secundary", "hint"]. Default "body"
        - halign (str): <KVLabel> auto,left, center, right
        - valign (str): <KVLabel> top, middle, bottom
        """
        # style = compose_dict(kwargs, 'font_style', str, default='body', acept_none=True)
        super(TextLabel, self).__init__(text=text, halign=halign, valign=valign, **kwargs)
        self._set_style(style)

    def text_layout_size(self, width=None):
        ctl = CTLabel()
        ctl.options['font_family'] = self.font_family
        ctl.options['bold'] = self.bold
        ctl.options['font_size'] = self.font_size
        lines = []
        w, h, clipped = LText(self.text, lines, (0, 0), (width, None), ctl.options,
                              ctl.get_cached_extents(), True, False)
        return w, h

    def _set_style(self, style:str):
        fs = self.theme.fonts[style]
        ty = self.theme.style['type']
        dt = kivy_mpbe_widgets.DEVICE_TYPE
        self.font_family = fs['family']
        if ty == "light":
            self.color = fs['color ligth']
        else:
            self.color = fs['color dark']
        self.bold = fs['bold']
        if dt == "desktop" or dt == "tablet":
            self.font_size = fs['desktop size']
        else:
            self.font_size = fs['portable size']

    def on_font_style(self, obj, new_option):
        self._set_style(new_option)

    """ Graphic Label functions -------------------------------------------------------"""
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
