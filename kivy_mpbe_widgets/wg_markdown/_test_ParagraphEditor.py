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
from kivy_mpbe_widgets.wg_markdown.md_editors import MDParagraphEditor_OBSOLETO



class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Markdown"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        layout = BoxLayout(orientation='vertical')
        # layout.bind(minimum_height=layout.setter('height'))

        self.md_editor1 = MDParagraphEditor_OBSOLETO(md_text="# Titulo")
        layout.add_widget(self.md_editor1)
        self.md_editor2 = MDParagraphEditor_OBSOLETO(md_text="--- -----", type_lbl="Separator")
        layout.add_widget(self.md_editor2)
        self.md_editor3 = MDParagraphEditor_OBSOLETO(md_text="**Linea de Prueba:** asdkjfalskjdflaksdf")
        layout.add_widget(self.md_editor3)

        return layout




if __name__ == "__main__":
    TestApp().run()