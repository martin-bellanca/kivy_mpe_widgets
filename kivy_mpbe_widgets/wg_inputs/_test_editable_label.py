#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_text_align.py
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
Created on 13/04/2024

@author: mpbe
'''

from kivy.config import Config
# Desactivar la simulación de multitouch
Config.set('input', 'mouse', 'mouse,disable_multitouch')

"""------------------------------------------------------------------------"""
"""-- Test Program  -------------------------------------------------------"""
"""------------------------------------------------------------------------"""
# imports del sistema -------------------------------------------------------
# Kivy imports -------------------------------------------------------------
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button as KVButton
from kivy.uix.label import Label as KVLabel
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel as Label
from kivy_mpbe_widgets.wg_inputs.inputs import EditableTextLabel as EDTL

class TestApp(App):
    theme = Theme(style='dark')
    title = "Test Labels"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']

        bl = BoxLayout(orientation='vertical', size_hint=(1, 1))


        # right -------------------
        lbl = EDTL(text="Right Align", halign="right", valign="center", style="title", size_hint=(1, 1))
        bl.add_widget(lbl)

        return bl




if __name__ == "__main__":
    TestApp().run()