#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_MDLineEditor.py
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
from kivy_mpbe_widgets.wg_markdown import MD_LINE_TYPE
from kivy_mpbe_widgets.wg_markdown.md_document import MDLine
from kivy_mpbe_widgets.wg_markdown.md_editors import MDLineEditor
from kivy_mpbe_widgets.wg_markdown.md_labels import MDTextLabel, MDSeparatorLabel
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButton



class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Markdown"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        layout = BoxLayout(orientation='vertical')
        # layout.bind(minimum_height=layout.setter('height'))

        ln = MDLine(md_text='# Titulo', prev_line=None, next_line=None)
        self.md_editor1 = MDLineEditor(line=ln)
        layout.add_widget(self.md_editor1)
        ln = MDLine(md_text='**Linea de Prueba:** asdkjfalskjdflaksdf', prev_line=None, next_line=None)
        self.md_editor2 = MDLineEditor(line=ln)
        layout.add_widget(self.md_editor2)
        self.separador = MDSeparatorLabel()
        layout.add_widget(self.separador)
        self.mdlbl = MDTextLabel(md_text="# PRUEBA")
        layout.add_widget(self.mdlbl)

        # Boton 1 de prueba -------------------------------------
        btn1 = ClickButton(text='Cambiar el Texto', size_hint=(1, 0.5))
        btn1.flat = True
        layout.add_widget(btn1)
        btn1.bind(on_click=self.on_click_btn1)
        # Boton 2 de prueba -------------------------------------
        btn2 = ClickButton(text='Update Type', size_hint=(1, 0.5))
        btn2.flat = True
        layout.add_widget(btn2)
        btn2.bind(on_click=self.on_click_btn2)



        return layout

    def on_click_btn1(self, touch, keycode, var):
        self.md_editor1.md_text = "**Nuevo Texto** en formato _Markdown_"

    def on_click_btn2(self, touch, keycode, var):
        self.md_editor1.type = MD_LINE_TYPE.SEPARATOR
        # self.md_editor1.update_type()

if __name__ == "__main__":
    TestApp().run()