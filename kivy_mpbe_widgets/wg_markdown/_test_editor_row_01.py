#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_editor_row_01.py
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
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
# Kivy_dkw imports -------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_markdown.markdown_extension import TaskListMDExtension
from kivy_mpbe_widgets.wg_markdown.md_labels_viejo import MarkdownLabel
from kivy_mpbe_widgets.wg_markdown.md_labels import MDTextLabel
from kivy_mpbe_widgets.wg_markdown.md_editors import MDLineTextInput
from kivy_mpbe_widgets.wg_markdown.md_render_def import render_line_markdown_to_widget

class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Markdown"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        self.layout = BoxLayout(orientation='vertical')
        # layout.bind(minimum_height=layout.setter('height'))

        self.md_editor = MDLineTextInput()
        self.md_editor.bind(text=self.on_txt_change)
        # self.md_editor.bind(on_text_validate=self.on_txt_validate)

        self.md_label = MDTextLabel(text ="MARKDOWN ROW LABEL")
        # self.md_label = MarkdownLabel(markdown_text="MARKDOWN LABEL")
        self.layout.add_widget(self.md_editor)
        self.layout.add_widget(self.md_label)
        return self.layout

    def on_txt_change(self, instance, value):
        # Actualizar la etiqueta con el texto actual del TextInput
        self.layout.remove_widget(self.md_label)
        self.md_label = render_line_markdown_to_widget(value)
        # self.md_label.background_color = (0, 0, 0, 0.1)
        self.layout.add_widget(self.md_label)
        # self.md_label.text = value


        print("Cambio el texto"+value)

#     def on_txt_validate(self, instance):
#         # Actualizar la etiqueta cuando se pierde el foco o presiona enter
#         self.md_label.markdown_text = instance.text
#         print("Validate text")



if __name__ == "__main__":
    TestApp().run()