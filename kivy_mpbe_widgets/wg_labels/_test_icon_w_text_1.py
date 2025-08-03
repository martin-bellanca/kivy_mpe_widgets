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
from kivy.uix.textinput import TextInput
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_labels.font_icon_labels import FontIcon, FontIconWText
from kivy_mpbe_widgets.wg_buttons.choice_buttons import Choice

class TestApp(App):
    theme = Theme(style='light')
    title = "List Icons"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        # Window.size = (800, 500)

        ly_root = BoxLayout(orientation='vertical')

        # Icon 1
        self.ic = FontIconWText(text='Icono 1', font_style='error', icon_name='alarm',
                           icon_align='top')
        ly_root.add_widget(self.ic)
        ly_btns = GridLayout(cols=2, size_hint=(1, 1))
        ly_root.add_widget(ly_btns)

        # Texto
        text = TextInput(text='Icono 1', multiline=False, size_hint=(1, None), height=28)  # Para cambiar el texto
        ly_btns.add_widget(text)
        text.bind(on_text_validate=self._on_enter)

        # Lista con Font Style
        lst = {"title": "Title", "subhead": "Sub Head", "body": "Body",
               "body_bold": "Body Bold", "caption": "Caption", "button": "Button",
               "error": "Error", "secundary": "Secundary", "hint":"Hint"}
        che_f_style = Choice(options_dict=lst, default_key="error", opening_mode='vertical',
                          size_hint=(1, None), size=(120, 45))
        ly_btns.add_widget(che_f_style)
        che_f_style.bind(on_select_item=self._on_selitem_che_f_style)

        # Lista con Ubicacion del Icono (icon_align)
        lst = {"left": "Left", "right": "Right", "top": "Top", "bottom": "Bottom"}
        che_i_align = Choice(options_dict=lst, default_key="top", opening_mode='vertical',
                             size_hint=(1, None), size=(120, 45))
        ly_btns.add_widget(che_i_align)
        che_i_align.bind(on_select_item=self._on_selitem_che_i_align)

        # Lista con nombres de iconos para cambiarlo
        lst = {"account": "Account", "airplane": "Airplane", "alarm": "Alarm", "bomb": "Bomb"}
        che_i_name = Choice(options_dict=lst, default_key='alarm', opening_mode='vertical',
                            size_hint=(1, None), size=(120, 45))
        ly_btns.add_widget(che_i_name)
        che_i_name.bind(on_select_item=self._on_selitem_che_i_name)

        # Lista con el tamaño del icono
        lst = {'16': "Small", '32': "Medium", '64': "Big", '96': "Very Big"}
        che_i_size = Choice(options_dict=lst, default_key='32', opening_mode='vertical',
                             size_hint=(1, None), size=(120, 45))
        ly_btns.add_widget(che_i_size)
        che_i_size.bind(on_select_item=self._on_selitem_che_i_size)

        return ly_root

    # --- events --------------------------------------------
    def _on_enter(self, text_input):
        print("APP->_on_enter: text:" + text_input.text)
        self.ic.text = text_input.text

    def _on_selitem_che_f_style(self, instance, key):
        print("APP->_on_selitem_che_f_style: key: " + key)
        self.ic.font_style = key

    def _on_selitem_che_i_align(self, instance, key):
        print("APP->_on_selitem_che_i_align: key: " + key)
        self.ic.icon_align = key

    def _on_selitem_che_i_name(self, instance, key):
        print("APP->_on_selitem_che_i_name: key: " + key)
        self.ic.icon_name = key

    def _on_selitem_che_i_size(self, instance, key):
        print("APP->_on_selitem_che_i_size: key: " + key)
        self.ic.icon_size = int(key)



if __name__ == "__main__":
    TestApp().run()