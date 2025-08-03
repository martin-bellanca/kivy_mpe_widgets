#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  click_buttons.py
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
Created on 05/01/2025
author: mpbe
'''

# imports del sistema -------------------------------------------------------
from helpers_mpbe.python import compose_dict
# Kivy imports --------------------------------------------------------------
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import OptionProperty, StringProperty, ObjectProperty

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.wg_labels.base_label import BaseLabel
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.base_widgets import FrameFocused
from kivy_mpbe_widgets.behaviors import TextLabelBehavior
from kivy_mpbe_widgets.behaviors import IconBehavior
from kivy_mpbe_widgets.graphics.buttons_graphics import GClickButton
from kivy_mpbe_widgets.events.buttons_events import ClickEventDispatcher
from kivy.animation import Animation



""" Widgets Class ---------------------------------------------------------"""
class ClickButton(TextLabelBehavior, FrameFocused, ClickEventDispatcher):

    def __init__(self, text, transparent=None, flat=None, **kwargs):
        """
        Constructor class.
        **Parameters:**
        - text (str): Texto a mostrar.
        - transparent (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        - flat (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        """
        TextLabelBehavior.__init__(self, text, text_halign='center', text_valign='center', text_style='button')
        FrameFocused.__init__(self, transparent=transparent, flat=flat, **kwargs)
        ClickEventDispatcher.__init__(self)
        # Widgets --------------------------------------------
        self.container.add_widget(self._text_label)
        # Canvas ---------------------------------------------
        with self.canvas.before:
            self.graphic_click = GClickButton(self)


class ClickButtonLabel(FrameFocused, ClickEventDispatcher):
    def __init__(self, label, transparent=None, flat=None, **kwargs):
        """
        Constructor class.
        **Parameters:**
        - label (Label): Clase derivada de Label.
        - transparent (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        - flat (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        """
        self._label = label
        FrameFocused.__init__(self, transparent=transparent, flat=flat, **kwargs)
        ClickEventDispatcher.__init__(self)
        # Widgets --------------------------------------------
        self.container.add_widget(self._label)
        # Canvas ---------------------------------------------
        with self.canvas.before:
            self.graphic_click = GClickButton(self)

    def add_label(self, label):
        if isinstance(label, BaseLabel):
            self.clear_widgets()
            self.add_widget(label)
        else:
            raise TypeError('Type add_label must come from BaseLabel')

    # Labels graphic events ---------------------------------------------------
    def on_disabled(self, instance, value):
        # print('ClickButtonLabel.on_disable')
        self._label.lbl_disabled(value)

    def on_hotlight(self, value, mp):
        # print(f'ClickButtonLabel.on_hotlight {value} - {mp}')
        self._label.lbl_hotlight(value)

    def on_focus(self, instance, value):
        self._label.lbl_focus(value)


    def on_click(self, touch, keycode):
        self._label.lbl_activate(True)





# TODO: SIN REVISIONAR
class ClickIcon(IconBehavior, ThemeWidget, ClickEventDispatcher):
    """Boton formado por un icono
    icon_family: str - Nombre del fuente de iconos
    icon_name: str - Nombre del icono
    icon_size: int - Tamaño del icono
    """
    level_render = OptionProperty('low', options=['low', 'medium', 'high'])

    def __init__(self, icon_name, icon_size=28, icon_family='materialdesignicons-webfont', **kwargs):
        '''
        Constructor class.
        Parameters:
        Keyword arguments:
            icon_name:
            icon_size:
            icon_family:
        '''
        IconBehavior.__init__(self, icon_name, icon_size, icon_family, **kwargs)
        ThemeWidget.__init__(self, container=self._icon)
        ClickEventDispatcher.__init__(self)
        self.size_hint_x = None
        if self.size_hint_x == None:
            self.width = self.icon_size
        if self.size_hint_y == None:
            self.height = self.icon_size
        self._icon.valign = 'center'
        self._icon.halign = 'center'
        self._hotlight_active = False
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)

    def update_hotlight_geometry(self):
        if self._hotlight_active:
            co = self.theme.colors['hotlight_border']
        else:
            co = self.theme.colors['icons']
        co[3] = 1.0
        anim = Animation(icon_color=co, duration=0.3)
        anim.start(self)

    def is_hotlight(self):
        return True if self._hotlight_active else False

    def on_mouse_move(self, instance, mp):
        hla = self.collide_point_to_window(*mp)
        if self._hotlight_active != hla:
            self._hotlight_active = hla
            self.update_hotlight_geometry()

    def on_touch_down(self, touch):
        print(f"ClickIcon.on_touch_down")
        ltouch = self.to_local(*touch.pos)
        wtouch = self.to_widget(*touch.pos)
        cpl = self.collide_point(*ltouch)
        cpw = self.collide_point(*wtouch)
        print(f"  collide: {cpl} - {cpw}")
        if touch.button == 'left' and (cpl or cpw) and not self.disabled and self.level_render == self.theme.level_render:
            touch.grab(self)
            cop = self.theme.colors['pressed_face']
            cop[3] = 1.0
            iz = self.icon_size - 2
            anim = Animation(icon_color=cop, icon_size=iz, duration=0.2)
            anim.start(self)
            return True

    def on_touch_up(self, touch):
        if touch.grab_state:
            touch.ungrab(self)
            ClickEventDispatcher.do_something(self, touch=touch, keycode=None)
            # self.focus = True
            coh = self.theme.colors['hotlight_border']
            iz = self.icon_size + 2
            anim = Animation(duration=0.4)
            anim += Animation(icon_color=coh, icon_size=iz, duration=0.6)
            anim.start(self)
            return True







#
# class ClickIcon_BAK1(IconBehavior, BoxLayout, ThemableBehavior, ClickEventDispatcher):
#     """Boton formado por un icono
#     icon_family: str - Nombre del fuente de iconos
#     icon_name: str - Nombre del icono
#     icon_size: int - Tamaño del icono
#     """
#     level_render = OptionProperty('low', options=['low', 'medium', 'high'])
#
#     def __init__(self, icon_name, icon_size=28, icon_family='materialdesignicons-webfont', **kwargs):
#         '''
#         Constructor class.
#         Parameters:
#         Keyword arguments:
#             icon_name:
#             icon_size:
#             icon_family:
#         '''
#         BoxLayout.__init__(self, **kwargs)
#         IconBehavior.__init__(self, icon_name, icon_size, icon_family, **kwargs)
#         ThemableBehavior.__init__(self, **kwargs)
#         ClickEventDispatcher.__init__(self)
#
#         self.add_widget(self._icon)
#
#         self.size_hint_x = None
#         if self.size_hint_x == None:
#             self.width = self.icon_size
#         if self.size_hint_y == None:
#             self.height = self.icon_size
#
#         self._icon.valign = 'center'
#         self._icon.halign = 'center'
#
#         self._hotlight_active = False
#         if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
#             Window.bind(mouse_pos=self.on_mouse_move)
#
#     def update_hotlight_geometry(self):
#         if self._hotlight_active:
#             co = self.theme.colors['hotlight_border']
#         else:
#             co = self.theme.colors['icons']
#         co[3] = 1.0
#         anim = Animation(icon_color=co, duration=0.3)
#         anim.start(self)
#
#     def is_hotlight(self):
#         # print(f'ClickIcon.is_hotlight {True if self._hotlight_active else False}, {self._hotlight_active}')
#         return True if self._hotlight_active else False
#
#     # def collide_point_to_win(self, x, y):  # on windows coordinates
#     #     bx, by = self.to_window(*self.pos)
#     #     bw, bh = self.size
#     #     return bx <= x <= bx + bw and by <= y <= by + bh
#
#     def on_mouse_move(self, instance, mp):
#         hla = self.collide_point_to_windows(*mp)
#         if self._hotlight_active != hla:
#             self._hotlight_active = hla
#             self.update_hotlight_geometry()
#             # if hla and not (self.disabled) and self.level_render == self.theme.level_render_widget:
#             #     self.hotlight_graphic.state = 'focused'
#             # else:
#             #     self.hotlight_graphic.state = 'inactive'
#
#     def on_touch_up(self, touch):
#         if touch.button == 'left':
#             tx, ty = self.to_window(touch.x, touch.y)
#             if touch.is_mouse_scrolling and self.level_render == self.theme.level_render:
#                 return False
#             elif self.collide_point(tx, ty) and self.level_render == self.theme.level_render:
#                 touch.grab_state = True
#                 ClickEventDispatcher.do_something(self, touch=touch, keycode=None)
#                 self.focus = True
#                 cop = self.theme.colors['pressed_face']
#                 coh = self.theme.colors['hotlight_border']
#                 anim = Animation(icon_color=cop, duration=0.4)
#                 anim += Animation(icon_color=coh, duration=0.4)
#                 anim.start(self)
#                 return True
#             return super().on_touch_up(touch)
#         else:
#             return True
#
#






# class ClickIcon_BAK(BoxLayout, IconBehavior, ThemableBehavior, ClickEventDispatcher):
#     """Boton formado por un icono
#     icon_family: str - Nombre del fuente de iconos
#     icon_name: str - Nombre del icono
#     icon_size: int - Tamaño del icono
#     """
#     level_render = OptionProperty('low', options=['low', 'medium', 'high'])
#
#     def __init__(self, **kwargs):
#         '''
#         Constructor class.
#         Parameters:
#         Keyword arguments:
#             icon_name:
#             icon_size:
#             icon_family:
#         '''
#         BoxLayout.__init__(self, **kwargs)
#         IconBehavior.__init__(self, **kwargs)
#         ThemableBehavior.__init__(self, **kwargs)
#         ClickEventDispatcher.__init__(self)
#
#         self.add_widget(self._icon)
#
#         self.size_hint_x = None
#         if self.size_hint_x == None:
#             self.width = self.icon_size
#         if self.size_hint_y == None:
#             self.height = self.icon_size
#
#         self._icon.valign = 'center'
#         self._icon.halign = 'center'
#
#         self._hotlight_active = False
#         if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
#             Window.bind(mouse_pos=self.on_mouse_move)
#
#     def update_hotlight_geometry(self):
#         if self._hotlight_active:
#             co = self.theme.colors['hotlight_border']
#         else:
#             co = self.theme.colors['icons']
#         co[3] = 1.0
#         anim = Animation(icon_color=co, duration=0.3)
#         anim.start(self)
#
#     def is_hotlight(self):
#         # print(f'ClickIcon.is_hotlight {True if self._hotlight_active else False}, {self._hotlight_active}')
#         return True if self._hotlight_active else False
#
#     def collide_point_to_win(self, x, y):  # on windows coordinates
#         bx, by = self.to_window(*self.pos)
#         bw, bh = self.size
#         return bx <= x <= bx + bw and by <= y <= by + bh
#
#     def on_mouse_move(self, instance, mp):
#         hla = self.collide_point_to_win(*mp)
#         if self._hotlight_active != hla:
#             self._hotlight_active = hla
#             self.update_hotlight_geometry()
#             # if hla and not (self.disabled) and self.level_render == self.theme.level_render_widget:
#             #     self.hotlight_graphic.state = 'focused'
#             # else:
#             #     self.hotlight_graphic.state = 'inactive'
#
#     def on_touch_up(self, touch):
#         if touch.button == 'left':
#             tx, ty = self.to_window(touch.x, touch.y)
#             if touch.is_mouse_scrolling and self.level_render == self.theme.level_render:
#                 return False
#             elif self.collide_point(tx, ty) and self.level_render == self.theme.level_render:
#                 touch.grab_state = True
#                 ClickEventDispatcher.do_something(self, touch=touch, keycode=None)
#                 self.focus = True
#                 cop = self.theme.colors['pressed_face']
#                 coh = self.theme.colors['hotlight_border']
#                 anim = Animation(icon_color=cop, duration=0.4)
#                 anim += Animation(icon_color=coh, duration=0.4)
#                 anim.start(self)
#                 return True
#             return super().on_touch_up(touch)
#         else:
#             return True