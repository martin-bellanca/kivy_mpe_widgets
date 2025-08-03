#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_icon_w_text.py
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
Created on 17/06/2024

@author: mpbe
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
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_labels.font_icon_labels import FontIcon, FontIconWText


class TestApp(App):
    theme = Theme(style='light')
    title = "List Icons"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        # Window.size = (800, 500)

        ly = GridLayout(cols=2, size_hint=(1, 1))

        family = list(self.theme.icons.keys())
        LIST_ICONS = self.theme.icons[family[0]]

        # Icon 1
        ic = FontIconWText(text='Icono 1', font_style='error', icon_name='alarm',
                           icon_align='left')
        ly.add_widget(ic)
        # Icon 2
        ic = FontIconWText(text='Icono 2', font_style='title', icon_name='alarm',
                           icon_align='right')
        ly.add_widget(ic)
        # Icon 3
        ic = FontIconWText(text='Icono 3', font_style='title', icon_name='alarm',
                           icon_align='top')
        ly.add_widget(ic)
        # Icon 4
        ic = FontIconWText(text='Icono 4 mm,n jkljh ljhlkjh lhj tdgf jjkk uuuu', font_style='title', icon_name='alarm',
                           icon_align='bottom')
        ly.add_widget(ic)

        return ly


if __name__ == "__main__":
    TestApp().run()