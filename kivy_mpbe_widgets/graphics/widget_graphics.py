#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  widget_graphics.py
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
Created on 25/12/2024
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
from kivy.graphics import InstructionGroup, Color, RoundedRectangle, SmoothLine, Line
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.graphics.base_graphics import GUnfocusedBase, GFocusedBase
from kivy_mpbe_widgets.events.widgets_events import HotlightEventDispatcher


# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets as MPW

# Works Dirs ----------------------------------------------------------------
# KV_DIRECTORY = MPW.DIR_BASE + '/'
# Builder.load_file(KV_DIRECTORY+'graphics.kv')

""" Canvas Class ----------------------------------------------------------"""
class GFace(GUnfocusedBase):
    """
    Clase para dibujar la cara del Widget
    """

    def __init__(self, widget, theme=None, color='widget_face', radius=None):
        """
        Constructor de la Clase
        **Parameters:**
        - widget (Widget): Widget padre. Parametor obligatorio.
        - theme (Theme)None: Tema a aplicar en el widget. Por defecto toma el widget de la aplicacion
        - color (str)'widget_face': Color a aplicar a la cara. Puede ser 'widget_face', 'panel_face', 'window_face'
        - radius (tuple)None: Radios de esquinas. El 1er radio es el sup. izq. (tl). Por defecto aplica los del tema. Si algun valor es -1, toma el r del tema para ese radio.
        """
        # Asignación de Parámetros ----------------------------
        self._theme = theme if theme else widget.theme
        if radius:
            r = self._theme.geometry['radius']
            lr = list(radius)
            for rr in range(4):
                if lr[rr] == -1:
                    lr[rr] = r
            self._radius = tuple(lr)
        else:
            self._radius = (self._theme.geometry['radius'],) * 4
        super().__init__(widget, theme, color)
        # Activaciones --------------------------------------------
        if self._widget.disabled: self._on_disabled(self, True)

    '''Funciones de Dibujo ---------------------------------------------------------------'''
    def _draw_graphics(self):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        # rtl, rtr, rbr, rbl = self._radius
        return RoundedRectangle(pos=cp, size=cs, radius=self._radius)  # el 1er radio es el sup. izq.

    def _update_graphics(self, instance, value, *args):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        self._graphic.pos = cp
        self._graphic.size = cs
        self._graphic.radius = self._radius

    '''Eventos del widget -----------------------------------------------------------------'''
    def _on_disabled(self, instance, value):
        if value:
            self._color.rgba = self._theme.colors['disable_face']
        else:
            self._color.rgba = self._theme.colors[self._color_name]


class GBorder(GUnfocusedBase):
    """
    Clase para dibujar el borde del Widget sin foco
    """

    def __init__(self, widget, theme=None, color='inactive_border',
                 radius=None, width=None, draw_borders=(True,)*4):
        """
        Constructor de la Clase
        **Parameters:**
        - widget (Widget): Widget padre. Parametor obligatorio.
        - theme (Theme)None: Tema a aplicar en el widget. Por defecto toma el widget de la aplicacion
        - color (str)'widget_face': Color a aplicar a la cara. Puede ser 'widget_face', 'panel_face', 'window_face'
        - radius (tuple)None: Radios de esquinas. El 1er radio es el sup. izq. (tl). Por defecto aplica los del tema. Si algun valor es -1, toma el r del tema para ese radio.
        - draw_borders(tuple(bool))(True,)*4: Indica que borde dibujar
        """
        # Asignación de Parámetros ----------------------------
        self._theme = theme if theme else widget.theme
        if radius:
            r = self._theme.geometry['radius']
            lr = list(radius)
            for id, rr in enumerate(lr):
                if rr == -1:
                    lr[id] = r
        else:
            lr = list((self._theme.geometry['radius'],) * 4)
        self._radius = tuple(lr)
        self._width = width if width else self._theme.geometry['border_width']
        self._draw_borders = draw_borders
        super().__init__(widget, theme, color)
        # Activaciones --------------------------------------------
        if self._widget.disabled: self._on_disabled(self, True)

    '''Funciones de Dibujo ---------------------------------------------------------------'''
    def _draw_graphics(self):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        e = self._width
        rtl, rtr, rbr, rbl = self._radius
        border = InstructionGroup()
        self._g_arc_bl = SmoothLine(circle=(cp[0] + rbl, cp[1] + rbl, rbl, 180, 270), width=e)  # Arco Inf. Izq.
        border.add(self._g_arc_bl)  # Arco Inf. Izq.
        if self._draw_borders[0]:
            self._g_line_l = Line(points=(cp[0], cp[1] + rbl, cp[0], cp[1] + cs[1] - rtl),
                                  width=e, cap='square')
            border.add(self._g_line_l)  # Linea Izq.
        self._g_arc_tl = SmoothLine(circle=(cp[0] + rtl, cp[1] + cs[1] - rtl, rtl, 270, 360), width=e)
        border.add(self._g_arc_tl)  # Arco Sup. Izq.
        if self._draw_borders[1]:
            self._g_line_t = Line(points=(cp[0] + rtl, cp[1] + cs[1], cp[0] + cs[0] - rtr, cp[1] + cs[1]),
                                  width=e, cap='square')
            border.add(self._g_line_t)  # Linea Superior
        self._g_arc_tr = SmoothLine(circle=(cp[0] + cs[0] - rtr, cp[1] + cs[1] - rtr, rtr, 0, 90), width=e)
        border.add(self._g_arc_tr)  # Arco Sup. Der.
        if self._draw_borders[2]:
            self._g_line_r = Line(points=(cp[0] + cs[0], cp[1] + rbr, cp[0] + cs[0], cp[1] + cs[1] - rtr),
                                  width=e, cap='square')
            border.add(self._g_line_r)  # Linea Der.
        self._g_arc_br = SmoothLine(circle=(cp[0] + cs[0] - rbr, cp[1] + rbr, rbr, 90, 180), width=e)
        border.add(self._g_arc_br)  # Arco Inf. Der.
        if self._draw_borders[3]:
            self._g_line_b = Line(points=(cp[0] + rbl, cp[1], cp[0] + cs[0] - rbr, cp[1]),
                                  width=e, cap='square')
            border.add(self._g_line_b)  # Linea inferior
        return border

    def _update_graphics(self, instance, value, *args):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        rtl, rtr, rbr, rbl = self._radius
        self._g_arc_bl.circle = (cp[0] + rbl, cp[1] + rbl, rbl, 180, 270)
        if self._draw_borders[0]:
            self._g_line_l.points = (cp[0], cp[1] + rbl, cp[0], cp[1] + cs[1] - rtl)
        self._g_arc_tl.circle = (cp[0] + rtl, cp[1] + cs[1] - rtl, rtl, 270, 360)
        if self._draw_borders[1]:
            self._g_line_t.points = (cp[0] + rtl, cp[1] + cs[1], cp[0] + cs[0] - rtr, cp[1] + cs[1])
        self._g_arc_tr.circle = (cp[0] + cs[0] - rtr, cp[1] + cs[1] - rtr, rtr, 0, 90)
        if self._draw_borders[2]:
            self._g_line_r.points = (cp[0] + cs[0], cp[1] + rbr, cp[0] + cs[0], cp[1] + cs[1] - rtr)
        self._g_arc_br.circle = (cp[0] + cs[0] - rbr, cp[1] + rbr, rbr, 90, 180)
        if self._draw_borders[3]:
            self._g_line_b.points = (cp[0] + rbl, cp[1], cp[0] + cs[0] - rbr, cp[1])

    '''Eventos del widget -----------------------------------------------------------------'''
    def _on_disabled(self, instance, value):
        if value:
            self._color.rgba = self._theme.colors['disable_border']
        else:
            self._color.rgba = self._theme.colors[self._color_name]


class GFocus(GFocusedBase):
    """
    Clase para dibujar el borde del Widget con foco
    """

    def __init__(self, widget, theme=None, color='focus_border',
                 radius=None, width=None, draw_borders=(True,)*4):
        """
        Constructor de la Clase
        **Parameters:**
        - widget (Widget): Widget padre. Parametor obligatorio.
        - theme (Theme)None: Tema a aplicar en el widget. Por defecto toma el widget de la aplicacion
        - color (str)'focus_border': Color a aplicar a la cara. Puede ser 'widget_face', 'panel_face', 'window_face'
        - radius (tuple)None: Radios de esquinas. El 1er radio es el sup. izq. (tl). Por defecto aplica los del tema. Si algun valor es -1, toma el r del tema para ese radio.
        - draw_borders(tuple(bool))(True,)*4: Indica que borde dibujar
        """
        # Asignación de Parámetros ----------------------------
        self._theme = theme if theme else widget.theme
        if radius:
            r = self._theme.geometry['radius']
            lr = list(radius)
            for id, rr in enumerate(lr):
                if rr == -1:
                    lr[id] = r
            self._radius = tuple(lr)
        else:
            self._radius = list((self._theme.geometry['radius'],) * 4)
        self._width = width if width else self._theme.geometry['border_width']
        self._draw_borders = draw_borders
        super().__init__(widget, theme, color)
        # Eventos -------------------------------------------------
        self._widget.bind(focus=self._on_focus)

    '''Funciones de Dibujo ---------------------------------------------------------------'''
    def _draw_graphics(self):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        e = self._width
        rtl, rtr, rbr, rbl = self._radius
        border = InstructionGroup()
        self._g_arc_bl = SmoothLine(circle=(cp[0] + rbl, cp[1] + rbl, rbl, 180, 270), width=e)  # Arco Inf. Izq.
        border.add(self._g_arc_bl)  # Arco Inf. Izq.
        if self._draw_borders[0]:
            self._g_line_l = Line(points=(cp[0], cp[1] + rbl, cp[0], cp[1] + cs[1] - rtl),
                                  width=e, cap='square')
            border.add(self._g_line_l)  # Linea Izq.
        self._g_arc_tl = SmoothLine(circle=(cp[0] + rtl, cp[1] + cs[1] - rtl, rtl, 270, 360), width=e)
        border.add(self._g_arc_tl)  # Arco Sup. Izq.
        if self._draw_borders[1]:
            self._g_line_t = Line(points=(cp[0] + rtl, cp[1] + cs[1], cp[0] + cs[0] - rtr, cp[1] + cs[1]),
                                  width=e, cap='square')
            border.add(self._g_line_t)  # Linea Superior
        self._g_arc_tr = SmoothLine(circle=(cp[0] + cs[0] - rtr, cp[1] + cs[1] - rtr, rtr, 0, 90), width=e)
        border.add(self._g_arc_tr)  # Arco Sup. Der.
        if self._draw_borders[2]:
            self._g_line_r = Line(points=(cp[0] + cs[0], cp[1] + rbr, cp[0] + cs[0], cp[1] + cs[1] - rtr),
                                        width=e, cap='square')
            border.add(self._g_line_r)  # Linea Der.
        self._g_arc_br = SmoothLine(circle=(cp[0] + cs[0] - rbr, cp[1] + rbr, rbr, 90, 180), width=e)
        border.add(self._g_arc_br)  # Arco Inf. Der.
        if self._draw_borders[3]:
            self._g_line_b = Line(points=(cp[0] + rbl, cp[1], cp[0] + cs[0] - rbr, cp[1]),
                                  width=e, cap='square')
            border.add(self._g_line_b)  # Linea inferior
        return border

    def _update_graphics(self, instance, value, *args):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        rtl, rtr, rbr, rbl = self._radius
        self._g_arc_bl.circle = (cp[0] + rbl, cp[1] + rbl, rbl, 180, 270)
        if self._draw_borders[0]:
            self._g_line_l.points = (cp[0], cp[1] + rbl, cp[0], cp[1] + cs[1] - rtl)
        self._g_arc_tl.circle = (cp[0] + rtl, cp[1] + cs[1] - rtl, rtl, 270, 360)
        if self._draw_borders[1]:
            self._g_line_t.points = (cp[0] + rtl, cp[1] + cs[1], cp[0] + cs[0] - rtr, cp[1] + cs[1])
        self._g_arc_tr.circle = (cp[0] + cs[0] - rtr, cp[1] + cs[1] - rtr, rtr, 0, 90)
        if self._draw_borders[2]:
            self._g_line_r.points = (cp[0] + cs[0], cp[1] + rbr, cp[0] + cs[0], cp[1] + cs[1] - rtr)
        self._g_arc_br.circle = (cp[0] + cs[0] - rbr, cp[1] + rbr, rbr, 90, 180)
        if self._draw_borders[3]:
            self._g_line_b.points = (cp[0] + rbl, cp[1], cp[0] + cs[0] - rbr, cp[1])

    '''Funciones de Animación ------------------------------------------------------------'''
    def animate(self, value=False):
        self._active = value
        if value:
            af = 1.0
        else:
            af = 0.0
        anim_alf = Animation(a=af, duration=0.6)
        anim_alf.start(self._color)

    '''Eventos del widget -----------------------------------------------------------------'''
    def _on_focus(self, instance, value):
        # print(f'GFocus._on_focus {self.uid} {value}')
        self.animate(value)


class GHotLight(GFocusedBase):
    """
    Clase para dibujar el borde del Widget con foco
    """

    def __init__(self, widget, theme=None, color='hotlight_border',
                 radius=None, width=None):
        """
        Constructor de la Clase
        **Parameters:**
        - widget (Widget): Widget padre. Parametor obligatorio.
        - theme (Theme)None: Tema a aplicar en el widget. Por defecto toma el widget de la aplicacion
        - color (str)'hotlight_border': Color a aplicar a la cara. Puede ser 'widget_face', 'panel_face', 'window_face'
        - radius (tuple)None: Radios de esquinas. El 1er radio es el sup. izq. (tl). Por defecto aplica los del tema. Si algun valor es -1, toma el r del tema para ese radio.
        """
        # Asignación de Parámetros ----------------------------
        self._theme = theme if theme else widget.theme
        if radius:
            r = self._theme.geometry['radius']
            lr = list(radius)
            for id, rr in enumerate(lr):
                if rr == -1:
                    lr[id] = r
            self._radius = tuple(lr)
        else:
            self._radius = list((self._theme.geometry['radius'],) * 4)
        self._width = width if width else self._theme.geometry['hotlight_width']
        super().__init__(widget, theme, color)
        # Activaciones --------------------------------------------
        if MPW.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self._on_mouse_move)

    '''Funciones de Dibujo ---------------------------------------------------------------'''
    def _draw_graphics(self):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        w = self._theme.geometry['border_width']
        wh = self._width
        hl = graphics.InstructionGroup()
        rtl, rtr, rbr, rbl = self._radius
        x1 = cp[0] + w + wh
        x2 = cp[0] + cs[0] - w - wh
        self._g_line_l = graphics.Line(points=(x1, cp[1] + rbl, x1, cp[1] + cs[1] - rtl), width=wh, cap='none')
        hl.add(self._g_line_l)  # Linea Izq.
        self._g_line_r = graphics.Line(points=(x2, cp[1] + rbr, x2, cp[1] + cs[1] - rtr), width=wh, cap='none')
        hl.add(self._g_line_r)  # Linea Der.
        return hl

    def _update_graphics(self, instance, value, *args):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        w = self._theme.geometry['border_width']
        wh = self._width
        hl = graphics.InstructionGroup()
        rtl, rtr, rbr, rbl = self._radius
        x1 = cp[0] + w + wh
        x2 = cp[0] + cs[0] - w - wh
        self._g_line_l.points = (x1, cp[1] + rbl + w/2, x1, cp[1] + cs[1] - rtl - w/2)
        self._g_line_r.points = (x2, cp[1] + rbr + w/2, x2, cp[1] + cs[1] - rtr - w/2)

    '''Funciones de Animación ------------------------------------------------------------'''
    def animate(self, value=False):
        self._active = value
        if value:
            af = 1.0
        else:
            af= 0.0
        anim_alf = Animation(a=af, duration=0.6)
        anim_alf.start(self._color)

    '''Eventos del widget -----------------------------------------------------------------'''
    def _on_mouse_move(self, instance, mp):
        hla = self._widget.collide_point(mp[0], mp[1])
        if self._active != hla and not self._widget.disabled and self._widget.level_render == self._widget.theme.level_render:
            self._active = hla
            if hla:  # activa
                self.animate(True)
                HotlightEventDispatcher.do_something(self._widget, True, mp)
            else:  # desactiva
                self.animate(False)
                HotlightEventDispatcher.do_something(self._widget, False, mp)
            return True
