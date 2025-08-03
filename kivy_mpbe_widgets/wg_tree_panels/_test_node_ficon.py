#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_icons.py
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
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.metrics import dp
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_font_icons.font_icon import FontIcon
from kivy_mpbe_widgets.wg_tree_panels.nodes import FontIconNode, EditableFontIconNode

# Builder.load_string('''
# <ScrollViewPanel>:  # Lista de Filtros ----------------------------------
#     sl: slw
#     conteiner_panels: slw
#     do_scroll_x: False
#     do_scroll_y: True
#     scroll_type: ['bars', 'content']
#     scroll_wheel_distance: dp(114)
#     bar_width: dp(10)
# #     size: self.size
#     height: slw.height
# #     canvas.before:
# #         Color:
# #             rgba: 0.3, 0.3, 0.3, 1
# #         Rectangle:
# #             size: self.size
# #             pos: self.pos
#     StackLayout:
#         id: slw
#         orientation: 'lr-tb'
#         size_hint_y: None
# #         size: root.size
# ''')





class TestApp(App):
    theme = Theme(style='light')
    title = "List Icons"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']

        ly = BoxLayout(orientation='vertical')
        ic1 = EditableFontIconNode(text='Linea 01', icon_name='account')
        ly.add_widget(ic1)
        ic2 = EditableFontIconNode(text='Linea 02', icon_name = 'account')
        ly.add_widget(ic2)



        return ly

if __name__ == "__main__":
    TestApp().run()