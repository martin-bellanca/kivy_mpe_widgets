#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_inputs.py
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
Created on 04/08/2024
@author: mpbe
'''

# imports del sistema -------------------------------------------------------
from enum import Enum
# helpers_mpbe --------------------------------------------------------------
from helpers_mpbe.python import compose_dict, compose, check_list
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window, WindowBase
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import BooleanProperty, StringProperty, OptionProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import FrameUnfocused, FrameFocused
from kivy_mpbe_widgets.wg_markdown.md_document import MDDocument
from kivy_mpbe_widgets.wg_markdown import MD_LINE_TYPE
from kivy_mpbe_widgets.wg_markdown.md_labels import MDTextLabel, MDTableLabel, MDSeparatorLabel
from kivy_mpbe_widgets.wg_markdown.md_labels import BaseMDLabel, MDCodeLabel, MDHeadLabel, MDToDoLabel, MDTaskLabel, \
    MDImageLabel
from kivy_mpbe_widgets.wg_markdown.md_document import MDLine

# from kivy_dkw.wg_markdown.render_markdown_to_widgets import render_line_markdown_to_widget

# Define el archivo KV en un string
kv = """
<MDLineTextInput@TextInput>:
    multiline: False
    size_hint_y: None
    font_size: 14
    height: self.font_size * 2.0
    # background_color: (0, 0, 0, 0.1)

<MarkdownRowTextInputWLabel_OBSOLETO@FloatLayout>:
    size_hint_y: 1
    # height: md_label.font_size+8

    canvas.before:
        Color:
            rgba: 0.1, 0.6, 0.8, 1  # RGB + Alpha (transparencia)
        Rectangle:
            pos: self.pos
            size: self.size
"""
Builder.load_string(kv)


class MDLineTextInput(TextInput):
    def __init__(self, **kwargs):
        super(MDLineTextInput, self).__init__(**kwargs)
        self.multiline = False
        self._pairs = {
            '*': '**',
            '"': '""',
            '(': '()',
            '[': '[]',
            '{': '{}',
            '_': '__',
        }
        self._start_with = {
            '[ ': '[ ] ',
            '-[': '- [ ] ',
            '- [': '- [ ] ',
            '-x': '- [x] ',
            '[>': '[>] ',
            '[<': '[>] ',
            '[o': '[o] ',
            '[0': '[o] ',
            '[O': '[o] ',
            '[x': '[x] ',
            '[-': '[-] '
        }

    def insert_text(self, substring, from_undo=False):
        # Reemplaza el tab por 4 espacios
        if substring == '\t':  # Detectar tabulador
            substring = ' ' * 4  # Reemplazar con 4 espacios
        # Reemplaza los inicios -------------------------
        cc = self.cursor_col - 1
        if -1 < cc < 2:  # menos de 4 caracteres
            autext = self.text[:cc + 1] + substring
            if autext in self._start_with:
                new_txt = self._start_with[autext]
                if len(self.text) >= len(new_txt):
                    if self.text[:len(new_txt)] != new_txt:
                        self.do_replace_start(new_txt, autext)
                    else:
                        return super().insert_text(substring, from_undo=from_undo)
                else:
                    self.do_replace_start(new_txt, autext)
            else:
                return super().insert_text(substring, from_undo=from_undo)
        # Reemplaza los caracteres de par
        elif substring in self._pairs:
            pair = self._pairs[substring]
            self.do_insert_pair(pair, len(substring))
        else:
            return super().insert_text(substring, from_undo=from_undo)

        # AGREGAR EVENTO DE CAMBIO DE TEXTO
        return None

    def do_insert_pair(self, pair, offset):
        # Insert the pair and move cursor to middle
        cursor_pos = self.cursor_index()
        self.text = self.text[:cursor_pos] + pair + self.text[cursor_pos:]
        self.cursor = (cursor_pos + offset, 0)

    def do_replace_start(self, new_txt, old_txt):
        if new_txt[0] in self._pairs:
            cc = len(old_txt)
        else:
            cc = len(old_txt) - 1
        self.text = new_txt + self.text[cc:]
        self.cursor = (len(new_txt), 0)