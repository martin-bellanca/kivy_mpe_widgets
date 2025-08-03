#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_buttons.py
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
# Kivy imports -------------------------------------------------------------
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets import IMAGES_PATH
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButton, ClickButtonLabel, ClickIcon
from kivy_mpbe_widgets.wg_labels.font_icon_labels import FontIconLabel, FontIconWText
from kivy_mpbe_widgets.wg_labels.image_labels import ImageWText
from kivy_mpbe_widgets.wg_buttons.toggle_buttons import ToggleButton, ToggleButtonLabel


class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Buttons"

    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        sp = self.theme.geometry['spacing']
        pa = self.theme.geometry['padding']
        grid = GridLayout(cols=2, spacing=sp, padding=pa)

        # -------------------------------------------------------------
        # Click Buttons -----------------------------------------
        cb01 = ClickButton(text='Click Boton 01')
        grid.add_widget(cb01)

        cb02 = ClickButton(text='Click Boton 02', disabled=True)
        cb02.bind(on_click=self.on_click)
        grid.add_widget(cb02)

        cb03 = ClickButton(text='Click Boton 03')
        cb03.bind(on_click=self.on_click)
        grid.add_widget(cb03)

        cb04 = ClickButton(text='Click Boton 04')
        grid.add_widget(cb04)

        # -------------------------------------------------------------
        # Toggle Buttons -----------------------------------------
        tb01 = ToggleButton(text='Toogle Boton 01')
        tb01.bind(on_toggle_state=self.on_toggle)
        grid.add_widget(tb01)

        tb02 = ToggleButton(text='Toogle Boton 02', state='toggled')
        tb02.bind(on_toggle_state=self.on_toggle)
        grid.add_widget(tb02)

        # -------------------------------------------------------------
        # Click Buttons Label-----------------------------------------
        ic = FontIconWText(text='Btn Label 01', font_style='title', icon_name='alarm',
                           icon_align='top')
        cb01 = ClickButtonLabel(ic)
        cb01.bind(on_click=self.on_click)
        grid.add_widget(cb01)

        ic = ImageWText(text='Icono 1', font_style='error', image_source=IMAGES_PATH + 'toolbar-archive-i30.png',
                        image_align='left')
        cb02 = ClickButtonLabel(ic, disabled=True)
        cb02.bind(on_click=self.on_click)
        grid.add_widget(cb02)

        # -------------------------------------------------------------
        # Toggle Buttons Label-----------------------------------------
        ic = FontIconWText(text='Btn Label 01', font_style='title', icon_name='alarm',
                           icon_align='top')
        cb01 = ToggleButtonLabel(ic)
        cb01.bind(on_toggle_state=self.on_toggle)
        grid.add_widget(cb01)

        ic = ImageWText(text='Icono 1', font_style='error', image_source=IMAGES_PATH + 'toolbar-archive-i30.png',
                        image_align='left')
        cb02 = ToggleButtonLabel(ic)
        cb02.bind(on_toggle_state=self.on_toggle)
        grid.add_widget(cb02)

        # -------------------------------------------------------------
        # Click icons -------------------------------------------------
        ly = AnchorLayout(anchor_x='center', anchor_y='center')
        ci01 = ClickIcon(icon_name='alarm', icon_size=54)
        ci01.bind(on_click=self.on_click)
        grid.add_widget(ly)
        ly.add_widget(ci01)

        ci02 = ClickIcon(icon_name='apps', icon_size=64)
        grid.add_widget(ci02)




        return grid

    def on_click(self, instance, touch, keycode):
        print('App->Click')
        # print(f'Click en {instance.text}, {instance.ids}')

    def on_toggle(self, instance, state):
        print('App->Toggle')
        # print(f'Toggle {instance.text}, {state}')



if __name__ == "__main__":
    TestApp().run()
