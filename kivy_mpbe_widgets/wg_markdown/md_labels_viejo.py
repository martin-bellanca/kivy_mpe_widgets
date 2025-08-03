#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_labels_viejo.py
#
#  Copyright 2024 Martin Pablo Bellanca <mbellanca@gmail.com>
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
Created on 03/08/2024
@author: mpbe
'''

# imports del sistema -------------------------------------------------------
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty, StringProperty
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.wg_markdown.md_render_def import render_markdown_to_widgets
# helpers_mpbe --------------------------------------------------------------


# Definir el archivo KV en un string
kv = """
<MarkdownLabel@BoxLayout>:
    orientation: 'vertical'
    padding: 5
    spacing: 5
"""
Builder.load_string(kv)

class MarkdownLabel(BoxLayout):
    markdown_text = StringProperty()

    def __init__(self, **kwargs):
        self.scroll = ScrollView(size_hint=(1, 1), size=(400, 600))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None)
        super(MarkdownLabel, self).__init__(**kwargs)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.add_widget(self.scroll)

    def on_markdown_text(self, instance, markdown_text):
        self.container.clear_widgets()
        widgets = render_markdown_to_widgets(markdown_text)
        for widget in widgets:
            self.container.add_widget(widget)




