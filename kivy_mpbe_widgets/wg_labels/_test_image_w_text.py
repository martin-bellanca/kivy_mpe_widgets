#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_image_w_text.py
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
Created on 04/01/2025
author: mpbe
'''

"""------------------------------------------------------------------------"""
"""-- Test Program  -------------------------------------------------------"""
"""------------------------------------------------------------------------"""
# imports del sistema -------------------------------------------------------
# Kivy imports -------------------------------------------------------------
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets import IMAGES_PATH
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_labels.image_labels import ImageLabel, ImageWText


class TestApp(App):
    theme = Theme(style='light')
    title = "Image Labels"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        # Window.size = (800, 500)

        ly = GridLayout(cols=2, size_hint=(1, 1))

        family = list(self.theme.icons.keys())
        LIST_ICONS = self.theme.icons[family[0]]

        # Icon 1
        ic = ImageWText(text='Icono 1', font_style='error', image_source=IMAGES_PATH +'toolbar-archive-i30.png',
                        image_align='left')
        ly.add_widget(ic)
        # Icon 2
        ic = ImageWText(text='Icono 2', font_style='error', image_source=IMAGES_PATH +'toolbar-add-new-i30.png',
                        image_align='right')
        ly.add_widget(ic)
        # Icon 3
        ic = ImageWText(text='Icono 3', font_style='error', image_source=IMAGES_PATH +'toolbar-archive-i30.png',
                        image_align='bottom')
        ly.add_widget(ic)
        # Icon 4
        ic = ImageWText(text='Icono 4', font_style='error', image_source=IMAGES_PATH +'toolbar-archive-i30.png')
        ly.add_widget(ic)

        return ly


if __name__ == "__main__":
    TestApp().run()
