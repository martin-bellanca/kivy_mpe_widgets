#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  panel_graphics.py
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
Created on 03/09/2023

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
import kivy.graphics as graphics
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import OptionProperty, NumericProperty, ReferenceListProperty,\
                            ColorProperty
# kivy_mpbe_widgets ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.graphics.base_graphics import GUnfocusedBase

# Works Dirs ----------------------------------------------------------------
# KV_DIRECTORY = kivy_mpbe_widgets.DIR_BASE + '/'
# Builder.load_file(KV_DIRECTORY+'graphics.kv')


class TitleGraphic(GUnfocusedBase):
    """
        Grafico del borde del titulo del frame.
        Properties:
            title_size (tuple): Tamaño del tamaño de texto
            title_align (str option): Alineacion horizontal del titlulo. "left", "center", "right"
        Methods:
            update_colours(): Actualiza los colores del widget
            update_geometry(): Actualiza la geometria del widget
            redraw(): Redibuja el widget
        """
    def __init__(self, widget, theme=None, color='inactive_border', **kwargs):
        """Constructor de la clase
        **Patameters:**
        - widget (Widget): Widget padre. Parametor obligatorio.
        - theme (Theme)None: Tema a aplicar en el widget. Por defecto toma el widget de la aplicacion
        - color (str)'hotlight_border': Color a aplicar a la cara. Puede ser 'widget_face', 'panel_face', 'window_face'
        """
        super().__init__(widget, theme, color)

    """ Graphics metods -----------------------------------------------"""
    def _get_points(self):
        'Calcular los puntos de la linea'
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        bw = self._widget.theme.geometry['border_width']
        sp = 2
        tsz = self._widget._title_label.text_layout_size()
        top = cp[1] + cs[1]
        h = top - tsz[1] - bw / 2 - sp
        if self._widget.title_align == "left":
            x1 = cp[0] + tsz[0] + bw + sp * 4
            pons = (cp[0], h, x1, h, x1, top)
        elif self._widget.title_align == "right":
            right = cp[0] + cs[0]
            x1 = right - tsz[0] - bw - sp * 4
            pons = (x1, top, x1, h, right, h)
        else:
            x1 = cp[0] + cs[0]/2 - tsz[0]/2 - bw/2 - sp
            x2 = cp[0] + cs[0]/2 + tsz[0]/2 + bw/2 + sp
            pons = (x1, top, x1, h, x2, h, x2, top)
        return pons

    def _draw_graphics(self, *args):  # ex update_geometry
        """Draw line title"""
        bw = self._widget.theme.geometry['border_width'] / 2
        return graphics.SmoothLine(points=self._get_points(), width=bw)

    def _update_graphics(self, instance, value, *args):
        self._graphic.points = self._get_points()

