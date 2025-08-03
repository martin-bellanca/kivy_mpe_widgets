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
import kivy_mpbe_widgets.rsrc_themes
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.events.input_events import StartEditingEventDispatcher, FinishEditingEventDispatcher

# Works Dirs ----------------------------------------------------------------
KV_DIRECTORY = kivy_mpbe_widgets.DIR_BASE + '/wg_labels/'
Builder.load_string("""
<EditableTextLabel>:
    size_hint_y: None
    height: 30
""")


class EditableTextLabel(FocusBehavior, BoxLayout, StartEditingEventDispatcher, FinishEditingEventDispatcher):
    editable = BooleanProperty(True)
    text = StringProperty(defaultvalue="")
    padding_x = NumericProperty(0)

    def __init__(self, text, style='body',padding_x=0, **kwargs):
        FocusBehavior.__init__(self)
        BoxLayout.__init__(self)
        StartEditingEventDispatcher.__init__(self)
        FinishEditingEventDispatcher.__init__(self)
        self.focus = True
        self._padding_x = padding_x
        self._label = TextLabel(text=text, valign='center', style=style, padding_x=padding_x)
        self._text_input = None
        self.text = text
        self.add_widget(self._label)
        self._label.font_size = 16
        self.in_edition = False
        self.back_text = None
        self.bind(on_touch_up=self._on_label_touch_up)
        Window.bind(on_key_down=self._on_keyboard_down)

    '''Funciones de Edición -----------------------------------------------------------'''
    def _init_edition(self, dt):
        self._text_input.cursor = (1000, 0)
        self._text_input.select_all()

    def start_editing(self):
        '''Inicia la edición del texto'''
        if not self.in_edition:
            self.in_edition = True
            self.back_text = self.text
            StartEditingEventDispatcher.do_something(self, self.text)
            self._text_input = TextInput(text=self.text, multiline=False, padding_x=self._padding_x
                                         , on_text_validate=self.finish_editing)
            self._text_input.focus = True
            self.remove_widget(self._label)
            self.add_widget(self._text_input)
            Clock.schedule_once(self._init_edition, 0.4)
            return True
        return False

    def finish_editing(self, instance):
        '''Guarda el texto editado y desactivar edición'''
        if self.in_edition:
            self._label.text = self._text_input.text
            self.text = self._text_input.text
            # self.editable = False
            self.remove_widget(self._text_input)
            self.add_widget(self._label)
            self._text_input = None
            self.in_edition = False
            FinishEditingEventDispatcher.do_something(self, new_text=instance.text)

    '''Eventos -----------------------------------------------------------------------'''
    def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
        if self.in_edition:
            if keycode == 27:  # Tecla Escape
                self.text = self.back_text
                self._text_input.text = self.back_text
                self.finish_editing(self._text_input)
                return True
            elif keycode in [13, 271]:  # Tecla Return
                self.finish_editing(self._text_input)
                return True
            return False
        elif not self.in_edition and self.editable and keycode == 283:  # Tecla F2
            self.start_editing()

    def _on_label_touch_up(self, instance, mouse):
        if self.editable and mouse.button=='right' and self.collide_point(mouse.x, mouse.y):
            self.start_editing()
            return True

    def on_text(self,instance, value):
        self._label.text = value

    def on_padding_x(self, instance, value):
        self._padding_x = value

