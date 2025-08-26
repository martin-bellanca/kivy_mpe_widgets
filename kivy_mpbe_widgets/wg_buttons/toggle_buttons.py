#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  toggle_buttons.py
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
from kivy.properties import OptionProperty, StringProperty, ObjectProperty

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.wg_labels.base_label import BaseLabel
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.base_widgets import FrameFocused
from kivy_mpbe_widgets.behaviors import TextLabelBehavior
from kivy_mpbe_widgets.behaviors import IconBehavior
from kivy_mpbe_widgets.graphics.buttons_graphics import GClickButton, GToggleButton
from kivy_mpbe_widgets.events.buttons_events import ToggleEventDispatcher
from kivy.animation import Animation

# OK DKW2

""" Widgets Class ---------------------------------------------------------"""
# TODO: EN PROCESO
# PROBAR ESTA CLASE
class ToggleButton(TextLabelBehavior, FrameFocused, ToggleEventDispatcher):
    # state = OptionProperty('untoggled', options=['toggled', 'untoggled'])

    def __init__(self, text, state='untoggled', transparent=None, flat=None, **kwargs):  # radius=None, draw_borders=(True,)*4
        """
        Constructor class.
        **Parameters:**
        - text (str): Texto a mostrar.
        - radius (list float): Denife radios diferentes para cada vertice
        - draw_borders (list bool):  Define si se dibujan los bordes (l, t, r, b)
        - transparent (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        - flat (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        """
        TextLabelBehavior.__init__(self, text, text_halign='center', text_valign='center', text_style='button')
        FrameFocused.__init__(self, transparent=transparent, flat=flat, **kwargs)
        ToggleEventDispatcher.__init__(self)
        # Widgets --------------------------------------------
        self.container.add_widget(self._text_label)
        # Canvas ---------------------------------------------
        self._state = state
        # self.state = state
        with self.canvas.before:
            self.graphic_toggle = GToggleButton(self)
        # with self.canvas.after:
        #     pass

    def set_state(self, value):
        self.graphic_toggle.set_state(value)
    def get_state(self):
        return self._state
    state = property(get_state, set_state)

    def change_state(self):
        self.graphic_toggle.change_state()


class ToggleButtonLabel(FrameFocused, ToggleEventDispatcher):
    # state = OptionProperty('untoggled', options=['toggled', 'untoggled'])

    def __init__(self, label, state='untoggled', transparent=None, flat=None, **kwargs):  # radius=None, draw_borders=(True,)*4
        """
        Constructor class.
        **Parameters:**
        - text (str): Texto a mostrar.
        - radius (list float): Denife radios diferentes para cada vertice
        - draw_borders (list bool):  Define si se dibujan los bordes (l, t, r, b)
        - transparent (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        - flat (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        """
        self._label = label
        FrameFocused.__init__(self, transparent=transparent, flat=flat, **kwargs)
        ToggleEventDispatcher.__init__(self)
        # Widgets --------------------------------------------
        self.container.add_widget(self._label)
        # Canvas ---------------------------------------------
        self._state = state
        # self.state = state
        with self.canvas.before:
            self.graphic_toggle = GToggleButton(self)
        # with self.canvas.after:
        #     pass

    def set_state(self, value):
        self.graphic_toggle.set_state(value)

    def get_state(self):
        return self._state

    state = property(get_state, set_state)

    def change_state(self):
        self.graphic_toggle.change_state()

    def add_label(self, label):
        if isinstance(label, BaseLabel):
            self.clear_widgets()
            self.add_widget(label)
        else:
            raise TypeError('Type add_label must come from BaseLabel')

    # Labels graphic events ---------------------------------------------------
    def on_disabled(self, instance, value):
        self._label.lbl_disabled(value)

    def on_hotlight(self, value, mp):
        # print('ToggleButtonLabel.on_hotlight')
        self._label.lbl_hotlight(value)

    def on_focus(self, instance, value):
        self._label.lbl_focus(value)

    def on_toggle_state(self, state, *args):
        # print('ToggleButtonLabel.on_activate')
        self._label.lbl_activate(state)


class ToggleIcon(IconBehavior, ThemeWidget, ToggleEventDispatcher):
    """Boton conmutador formado por un icono
    icon_family: str - Nombre del fuente de iconos
    icon_name: str - Nombre del icono
    icon_size: int - Tamaño del icono
    """
    level_render = OptionProperty('low', options=['low', 'medium', 'high'])
    state = OptionProperty('untoggled', options=['toggled', 'untoggled'])

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
        ToggleEventDispatcher.__init__(self)
        self.size_hint_x = None
        if self.size_hint_x is None:
            self.width = self.icon_size
        if self.size_hint_y is None:
            self.height = self.icon_size
        self._icon.valign = 'center'
        self._icon.halign = 'center'
        self._hotlight_active = False
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)

        self.bind(state=self.on_state_change)
        self.on_state_change(self, self.state)

    def on_state_change(self, instance, value):
        self.update_hotlight_geometry()

    def update_hotlight_geometry(self):
        if self.state == 'toggled':
            co = self.theme.colors['pressed_face']
        elif self._hotlight_active:
            co = self.theme.colors['hotlight_border']
        else:
            co = self.theme.colors['icons']

        co[3] = 1.0
        anim = Animation(icon_color=co, duration=0.2)
        anim.start(self)

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
            return True

    def on_touch_up(self, touch):
        if touch.grab_state:
            touch.ungrab(self)
            if self.collide_point(*self.to_local(*touch.pos)):
                self.state = 'toggled' if self.state == 'untoggled' else 'untoggled'
                if self.state == 'toggled':
                    cop = self.theme.colors['pressed_face']
                    cop[3] = 1.0
                    iz = self.icon_size - 2
                    anim = Animation(icon_color=cop, icon_size=iz, duration=0.2)
                    anim.start(self)
                else:
                    coh = self.theme.colors['hotlight_border']
                    iz = self.icon_size + 2
                    anim = Animation(duration=0.4)
                    anim += Animation(icon_color=coh, icon_size=iz, duration=0.2)
                    anim.start(self)

                ToggleEventDispatcher.do_something(self, self.state)
                return True
        return False
