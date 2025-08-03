#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  theming.py
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
Created on 24/12/2024
@author: mpbe
'''

# imports del sistema -------------------------------------------------------


# Kivy imports --------------------------------------------------------------
from kivy.config import Config

# import kivy_mpbe_widgets as mpw
# if mpw.DEVICE_TYPE == 'desktop':
#     Config.set("input", "mouse", "mouse,multitouch_on_demand")  # Desactiva la simulacion del multitouch
from kivy.app import App
from kivy.graphics import Color
from kivy.event import EventDispatcher
from kivy.properties import OptionProperty, AliasProperty, ObjectProperty, \
    StringProperty, ListProperty, BooleanProperty, BoundedNumericProperty
from kivy.uix.widget import Widget
from kivy.config import Config
# Desactivar la simulación de multitouch

# mpbe_helpers ----------------------------------------------------------
from helpers_mpbe.python import compose
# kivy_dkw imports ----------------------------------------------------------
from kivy_mpbe_widgets.rsrc_themes import THEMES, STYLES
from kivy_mpbe_widgets.rsrc_fonts_icons import ICONS

# TODO: Las fuentes desde donde se asignan (ver el init de rsrc_font_icons y rsrc_fonts)
class Theme(object):
    """
    ## Clase que define el tema de la aplicacion
    **Attributes:**
    - style (dict): Diccionario con las variables de estilo
    - theme (dict): Diccionario con el tema completo de la app
    - widgets_style (dict): Bloque de theme con las variables que definen el estilo de los widgets
    - colors (dict): Bloque de theme con las variables que definen los colores de la app
    - geometry (dict): Bloque de theme con las variables que definen los valores geometricos de la app
    - fonts (dict): Bloque de theme con las variables que definen los tipos de letras de la app
    - icons (str): Listado con el nombre de FontIcons de la app
    **Properties:**
    - level_render (str): Define el nivel de visibilidad actual de la aplicacion para recibir el foco y eventos del mouse.
                                (low: bajo por defecto, medium: para menus, high: para mensajes y alertas)
    - name (str): Nombre actual del tema
    - name_style (str): Nombre del estilo del tema actual (light, black, etc)  # no esta en uso
    """

    def __init__(self, name: str = 'default', style: str = 'light'):
        '''
        ## Constructor de la clase.
        **Parameters:**
        - name (str): Nombre del tema
        - style (str): Estilo del tema ('ligth','dark')
        '''
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        self._name = name
        self._style_name = style
        self.style = STYLES[style]
        theme = THEMES[name]
        self.widgets_style = theme['widgets_style']
        self.colors = theme['colors']
        self.geometry = theme['geometry']
        self.fonts = theme['font_style']
        self.icons = ICONS
        self._level_render = 'low'  # options=["low", "medium", "high"]
        # TODO: Definir listado de imagenes y si alguno no esta tomar Default (usar Atlas para tamaños estandar de 24, 32, 48, 56, 64)
        # self.images = IMAGES

    def _get_name(self):
        return self.name
    def _set_name(self, name: str):
        if name in THEMES.keys():
            theme = THEMES[name]
            self.colors = theme['colors']
            self.geometry = theme['geometry']
            self.fonts = theme['font_style']
            self._name = name
            return True
        else:
            return False
    name = AliasProperty(_get_name, _set_name, bind='change_theme')

    def _get_style(self):
        return self._style_name
    def _set_style(self, name: str):
        if name in STYLES.keys():
            self.style = STYLES[name]
            return True
        else:
            return False
    style_name = AliasProperty(_get_style, _set_style, bind='change_theme')

    # Level Render Widget property --------------------------------------
    def get_level_render(self):
        return self._level_render
    def set_level_render(self, value):
        if value in ['low', 'medium', 'high']:
            self._level_render = value
        else:
            raise ValueError("Level Render value must be low, medium or high")
    level_render = property(get_level_render, set_level_render)

    # ----------------------------------
    def _color_brightness(self, color):
        # Implementation of color brightness method
        brightness = color[0] * 299 + color[1] * 587 + color[2] * 114
        brightness = brightness
        return brightness

    def _black_or_white_by_color_brightness(self, color):
        if self._color_brightness(color) >= 500:
            return 'black'
        else:
            return 'white'

    def _normalized_channel(self, color):
        # Implementation of contrast ratio and relative luminance method
        if color <= 0.03928:
            return color / 12.92
        else:
            return ((color + 0.055) / 1.055) ** 2.4

    def _luminance(self, color):
        rg = self._normalized_channel(color[0])
        gg = self._normalized_channel(color[1])
        bg = self._normalized_channel(color[2])
        return 0.2126 * rg + 0.7152 * gg + 0.0722 * bg

    def _black_or_white_by_contrast_ratio(self, color) -> str:
        l_color = self._luminance(color)
        l_black = 0.0
        l_white = 1.0
        b_contrast = (l_color + 0.05) / (l_black + 0.05)
        w_contrast = (l_white + 0.05) / (l_color + 0.05)
        return 'white' if w_contrast >= b_contrast else 'black'

    def get_contrast_text_color(self, color, use_color_brightness=True):
        if use_color_brightness:
            contrast_color = self._black_or_white_by_color_brightness(color)
        else:
            contrast_color = self._black_or_white_by_contrast_ratio(color)
        if contrast_color == 'white':
            return 1, 1, 1, 1
        else:
            return 0, 0, 0, 1

    def get_widgets_style(self, key: str) -> bool:
        if key in self.widgets_style.keys():
            return self.widgets_style[key]
        else:
            return None

    def get_color(self, key: str) -> Color:
        if key in self.colors.keys():
            return Color(rgba=self.colors[key])
        else:
            return None

    def get_geometry(self, key: str) -> float:
        if key in self.geometry.keys():
            return self.colors[key]
        else:
            return None

    def get_font(self, key: str) -> dict:
        if key in self.fonts.keys():
            return self.fonts[key]
        else:
            return None


class ThemableBehavior():
    """
    ## Behavior for themeable class.
    Define el comportamiento de los widgets que usen los temas dkw.
    **Parameters:**
    - level_render (str)"low": Define el nivel de visibilidad del widget para recibir el foco y eventos del mouse. (low: bajo por defecto, medium: para menus, high: para mensajes y alertas)
    - theme (Theme): Tema actual de la aplicación
    - transparent (bool): Define el estilo transparente del fondo.
    - flat (bool): Define el estilo flat.
    """

    def __init__(self, transparent=None, flat=None, **kwargs):
        """
        ## Consturctor de la clase
        **Parameters:**
        - border (bool)None: Define la visivilidad del borde. (este podria ser un valor alpha entre 0 y 1)
        - transparent (bool)None: Define si el fondo es transparente. (este podria ser un valor alpha entre 0 y 1)
        - flat (bool)None: Define el estilo flat para los widgets
        - opposite_colors (bool)None: Define el estilo de colores opuestos.
        """
        self.theme = None
        if hasattr(App.get_running_app(), 'theme'):
            self.theme = App.get_running_app().theme
        else:
            self.theme = ThemeManager()
        self.transparent = compose(transparent, bool, False, True, self.theme.widgets_style['transparent'])
        self.flat = compose(flat, bool,False, True, self.theme.widgets_style['flat'])
        self._level_render = 'low'

    def collide_point_to_window(self, x, y):  # on windows coordinates
        try:
            # Check the position of the point
            bpx, bpy = self.to_window(self.pos[0], self.pos[1], True)
            bwidth, bheight = self.size
            # Direction X
            bpw = bpx + bwidth
            inx = True if bpx <= x <= bpw else False
            # Direction Y
            bph = bpy + bheight
            iny = True if bpy <= y <= bph else False
            # Collide
            return inx and iny
        except:
            return False

    # Level Render Widget property --------------------------------------
    def get_level_render(self):
        return self._level_render
    def set_level_render(self, value):
        if value in ['low', 'medium', 'high']:
            self._level_render = value
        else:
            raise ValueError("Level Render value must be low, medium or high")
    level_render = property(get_level_render, set_level_render)


class ThemeManager(Widget):
    # TODO: Codificar ThemeManager
    pass



