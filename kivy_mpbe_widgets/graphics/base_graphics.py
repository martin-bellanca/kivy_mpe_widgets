#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  base_graphics.py
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
import math
# mpbe imports --------------------------------------------------------------
from helpers_mpbe.python import compose
from helpers_mpbe.python import compose_dict
# Kivy imports --------------------------------------------------------------
from kivy.lang import Builder
from kivy.event import EventDispatcher
from kivy.core.window import Window
import kivy.graphics as graphics
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import InstructionGroup, Color
from kivy.properties import OptionProperty, NumericProperty, ReferenceListProperty,\
                            ColorProperty
# Kivy mpw imports --------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme



# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets as MPW


""" Canvas Class ----------------------------------------------------------"""
class GUnfocusedBase(InstructionGroup):
    """
    Clase para dibujar en el widget sin foco
    **Attributes:**

    **Methods:**
    - _draw_graphics(self): Funcion a implementar en las clases hijas para dibujar el widget.
    - _update_graphics(self, instance, value, *args): Funcion a implementar en las clases hijas para actualizar la posicion y tamaño del grafico
    - _on_disabled(self, instance, value): Funcion a implementar en las clases hijas para deshabilitar el widget.
    """
    def __init__(self, widget, theme=None, color='widget_face'):
        """
        Constructor de la Clase
        **Parameters:**
        - widget (Widget): Widget padre. Parametor obligatorio.
        - theme (Theme)None: Tema a aplicar en el widget. Por defecto toma el widget de la aplicacion
        - color (str)'widget_face': Color a aplicar a la cara. Puede ser cualquiera del tema
        """
        super().__init__()
        # Asignación de Parámetros ----------------------------
        self._widget = widget
        self._theme = theme if theme else widget.theme
        self._color_name = color
        self._color = Color(rgba=self._theme.colors[color])
        # Asigna el Gráfico -------------------------------------
        self._graphic = self._draw_graphics()
        self.add(self._color)
        self.add(self._graphic)
        # Asignación de Eventos ---------------------------------
        self._widget.bind(pos=self._update_graphics,
                          size=self._update_graphics,
                          disabled= self._on_disabled)

    '''Funciones de Dibujo ---------------------------------------------------------------'''
    def _get_pos_size(self):
        bw = self._theme.geometry['border_width']
        ps = tuple(xx + bw / 2 for xx in self._widget.pos)
        sz = tuple(xx - bw for xx in self._widget.size)
        return ps, sz

    def _draw_graphics(self):
        """
        Dibuja el grafico.
        Debe devolver una variable grafica que se asigna a self._graphic
        """
        raise NotImplementedError("Should have implemented _draw_graphics()")

    def _update_graphics(self, instance, value, *args):
        '''Funcion a implementar en las clases hijas para actualizar la posicion y tamaño del grafico'''
        raise NotImplementedError("Should have implemented _update_graphics()")

    '''Eventos -----------------------------------------------------------------------------'''
    def _on_disabled(self, instance, value):
        '''Funcion a implementar en las clases hijas para deshabilitar el widget'''
        raise NotImplementedError("Should have implemented _on_disabled()")


class GFocusedBase(InstructionGroup):
    """
    Clase para dibujar en el widget con foco
    **Attributes:**

    **Methods:**
    - _draw_graphics(self): Funcion a implementar en las clases hijas para dibujar el widget.
    - _update_graphics(self, instance, value, *args): Funcion a implementar en las clases hijas para actualizar la posicion y tamaño del grafico
    - show(self, value): Muestra el o Esconde el grafico sin animar
    - animate(self, value=False): Funcion a implementar en las clases hijas para iniciar la animacion de activacion/desactivacion
    - _on_disabled(self, instance, value): Funcion a implementar en las clases hijas para deshabilitar el widget.
    """
    def __init__(self, widget, theme=None, color='widget_face'):
        """
        Constructor de la Clase
        **Parameters:**
        - widget (Widget): Widget padre. Parametor obligatorio.
        - theme (Theme)None: Tema a aplicar en el widget. Por defecto toma el widget de la aplicacion
        - color (str)'widget_face': Color a aplicar a la cara. Puede ser 'widget_face', 'panel_face', 'window_face'
        """
        super().__init__()
        # Asignación de Parámetros ----------------------------
        self._widget = widget
        self._theme = theme if theme else widget.theme
        self._color_name = color
        self._color = Color(rgba=self._theme.colors[color])
        self._active = False
        # Asigna el Gráfico -------------------------------------
        self._graphic = self._draw_graphics()
        self.add(self._color)
        self.add(self._graphic)
        # Asignación de Eventos ---------------------------------
        self._widget.bind(pos=self._update_graphics, size=self._update_graphics)

    '''Funciones de Dibujo ---------------------------------------------------------------'''
    def _get_pos_size(self):
        bw = self._theme.geometry['border_width']
        ps = tuple(xx + bw / 2 for xx in self._widget.pos)
        sz = tuple(xx - bw for xx in self._widget.size)
        return ps, sz

    def _draw_graphics(self):
        """
        Dibuja el grafico.
        Debe devolver una variable grafica que se asigna a self._graphic
        """
        raise NotImplementedError("Should have implemented _draw_graphics()")

    def _update_graphics(self, instance, value, *args):
        '''Funcion a implementar en las clases hijas para actualizar la posicion y tamaño del grafico'''
        raise NotImplementedError("Should have implemented _update_graphics()")

    '''Funciones de Animación ------------------------------------------------------------'''
    def show(self, value):
        '''Muestra el o Esconde el grafico sin animar'''
        # print(f'Show - {value}')
        self.update_colours()
        if value == True:
            self._color.a = 1.0
        else:
            self._color.a = 0.0

    def animate(self, value=False):
        '''Funcion a implementar en las clases hijas para iniciar la animacion de activacion/desactivacion'''
        raise NotImplementedError("Should have implemented animate()")

    '''Eventos -----------------------------------------------------------------------------'''
    def _on_disabled(self, instance, value):
        '''Funcion a implementar en las clases hijas para deshabilitar el widget'''
        raise NotImplementedError("Should have implemented _on_disabled")
