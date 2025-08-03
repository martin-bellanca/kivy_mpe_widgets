#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_MDLabels.py
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
Created on 10/09/2023
@author: mpbe
'''

"""------------------------------------------------------------------------"""
"""-- Test Program  -------------------------------------------------------"""
"""------------------------------------------------------------------------"""
from markdown import markdown
# Kivy imports -------------------------------------------------------------
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
# Kivy_dkw imports -------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButton
from kivy_mpbe_widgets.wg_markdown.markdown_extension import TaskListMDExtension
from kivy_mpbe_widgets.wg_markdown.md_labels import MDTextLabel

class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Markdown"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        self.md_text_1 = """**Cambia a Linea de Prueba:** texto normal"""
        self.md_text_2 = '## Cambia a Titulo'
        # html = markdown(md_text, extensions=[TaskListMDExtension()])  ## El label no renderiza html
        # return MarkdownLabel(text=html, size_hint=(1,1))
        layout = BoxLayout(orientation='horizontal')
        btn = ClickButton(text='Cambiar el Texto', size_hint=(1, 0.5))
        btn.flat = True
        layout.add_widget(btn)
        btn.bind(on_click=self.on_click_btn)
        self.md_lavel = MDTextLabel(md_text="123")
        layout.add_widget(self.md_lavel)

        return layout

    def on_click_btn(self, touch, keycode, var):
        if self.md_lavel.md_text == self.md_text_1:
            self.md_lavel.md_text = self.md_text_2
        else:
            self.md_lavel.md_text = self.md_text_1


if __name__ == "__main__":
    TestApp().run()