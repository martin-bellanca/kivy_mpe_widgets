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
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
# from kivy_mpbe_widgets.wg_font_icons.font_icon import FontIcon
from kivy_mpbe_widgets.wg_labels.font_icon_labels import FontIconLabel

Builder.load_string('''
<ScrollViewPanel>:  # Lista de Filtros ----------------------------------
    sl: slw
    conteiner_panels: slw
    do_scroll_x: False
    do_scroll_y: True
    scroll_type: ['bars', 'content']
    scroll_wheel_distance: dp(114)
    bar_width: dp(10)
#     size: self.size
    height: slw.height
#     canvas.before:
#         Color:
#             rgba: 0.3, 0.3, 0.3, 1
#         Rectangle:
#             size: self.size
#             pos: self.pos
    StackLayout:
        id: slw
        orientation: 'lr-tb'
        size_hint_y: None
#         size: root.size
''')


class ScrollViewPanel(ScrollView):
    def __init__(self, **kwargs):
        super(ScrollViewPanel, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.update_height()

    def update_height(self):
        self.conteiner_panels.height = 35000  # self.sl.height


class TestApp(App):
    theme = Theme(style='light')
    title = "List Icons"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']

        SVP = ScrollViewPanel()

        id_icons = 1
        family = list(self.theme.icons.keys())
        LIST_ICONS = self.theme.icons[family[id_icons]]
        for k in LIST_ICONS.keys():
            ic = FontIconLabel(icon_name=k, icon_size=48, icon_family=family[id_icons])
            lbl = TextLabel(text=k, style='body_bold', halign='center', valign='top')
            bx = BoxLayout(orientation='vertical', size_hint=(None, None), width=250)
            bx.add_widget(ic)
            bx.add_widget(lbl)
            SVP.sl.add_widget(bx)
        SVP.update_height()
        return SVP

if __name__ == "__main__":
    TestApp().run()