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

        icon_size =24
        text = '[b][color=#3400db]Sub-Item de Tree nro {}[/color][/b]'.format("12")
        ly = BoxLayout()
        ly.orientation = 'horizontal'
        ly.spacing = 5  # Espacio entre el ícono y el texto
        # Tamaño del ícono
        margin = 6
        ly.height = icon_size + margin
        ly.size_hint_y = None  # Establecer altura fija para el nodo

        # Imagen para el ícono
        # family = list(self.theme.icons.keys())
        self.icon1 = FontIcon(icon_name="account", icon_size=icon_size)
        self.icon1.size_hint=(None, None)
        ly.add_widget(self.icon1)
        # Label para el texto
        self.label = Label(text=text, valign='middle', halign='left',
                           size_hint_y=None, height=ly.height, markup=True)
        self.label.bind(size=self.label.setter('text_size'))  # Ajustar el tamaño del texto
        ly.add_widget(self.label)
        # self.icon1.bind(size=self.label.setter('text_size'))
        # self.icon1.texture.height= self.label.height
        # self.icon1.texture.height = 100


        return ly

if __name__ == "__main__":
    TestApp().run()