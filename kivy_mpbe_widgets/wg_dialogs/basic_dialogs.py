#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  basic_dialogs.py
#
#  Copyright 2025 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License fo
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

'''
Base Dialogs for kivy_mpbe_widgets \n
Created on 03/03/2025

@author: mpbe
@note:
'''

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButton as Button
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel as Label


class TwoButtonsDialog(Popup):
    def __init__(self, title, question_text, btn1_text, btn2_text, **kwargs):
        super(TwoButtonsDialog, self).__init__(**kwargs)
        self.title = title
        self.size_hint = (0.8, 0.4)

        # Crear el contenido del Popup
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        question = Label(text=question_text, style="button")

        question.color = (0.8, 0.8, 0.8, 1.0)


        layout.add_widget(question)

        # Botones de confirmación
        btns_layout = BoxLayout(spacing=10)
        self.button_1 = Button(text=btn1_text, size_hint=(0.5, 0.4))
        self.button_2 = Button(text=btn2_text, size_hint=(0.5, 0.4))
        btns_layout.add_widget(self.button_1)
        btns_layout.add_widget(self.button_2)
        layout.add_widget(btns_layout)

        self.content = layout

