#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  buttons_graphics.py
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

# imports del sistema -------------------------------------------------------
import math
# mpbe imports --------------------------------------------------------------
from helpers_mpbe.python import compose
from helpers_mpbe.python import compose_dict
# Kivy imports --------------------------------------------------------------
from kivy.lang import Builder
from kivy.event import EventDispatcher
import kivy.graphics as graphics
from kivy.graphics import InstructionGroup, Color, RoundedRectangle, SmoothLine, Line
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.events.buttons_events import ClickEventDispatcher, ToggleEventDispatcher
# from kivy_dkw.rsrc_graphics.base_graphics import BaseGraphics
from kivy_mpbe_widgets.graphics.base_graphics import GFocusedBase

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets

# Works Dirs ----------------------------------------------------------------
KV_DIRECTORY = kivy_mpbe_widgets.DIR_BASE + '/'
# Builder.load_file(KV_DIRECTORY+'graphics.kv')


class GClickButton(GFocusedBase):
    """
    Clase para dibujar el click del Widget con foco
    """
    selected = None

    def __init__(self, widget, theme=None, color='pressed_face',
                 radius=None, width=None):
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
        super().__init__(widget, theme, color)
        # Eventos -------------------------------------------------
        self._widget.bind(on_touch_down=self._on_touch_down, on_touch_up=self._on_touch_up)

    '''Funciones de Dibujo ---------------------------------------------------------------'''
    def _draw_graphics(self):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        rtl, rtr, rbr, rbl = self._radius
        return RoundedRectangle(pos=cp, size=cs, radius=(rtl, rtr, rbr, rbl))  # el 1er radio es el sup. izq.

    def _update_graphics(self, instance, value, *args):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        self._graphic.pos = cp
        self._graphic.size = cs

    '''Funciones de Animación ------------------------------------------------------------'''
    def animate(self, value=False, mouse_pos=None):
        #TODO: Tambien hay que animar el color del borde
        # print(f'GClickButton.animate value={value}')
        if value:
            af = 1.0
            dur = 0.3
            dur1= 0.0
            self.on_anim(mouse_pos)
        else:
            af = 0.0
            dur = 1.0
            dur1 = 1.0
            self.off_anim(mouse_pos)

        anim_alf = Animation(duration=dur1)
        anim_alf += Animation(a=af, duration=dur)
        anim_alf.start(self._color)

    def on_anim(self, mouse_pos):
        cp, cs = self._get_pos_size()
        if not mouse_pos:
            mouse_pos = self._widget.center
        i_size = 6
        self._graphic.size = (i_size, i_size)
        mx, my = mouse_pos
        self._graphic.pos = [x-i_size/2 for x in mouse_pos]
        anim_rec = Animation(size=(i_size, cs[1]), pos=(mx-i_size/2, cp[1]), duration=.2)
        anim_rec += Animation(size=cs, pos=cp, duration=0.2)
        anim_rec.start(self._graphic)

    def off_anim(self, mouse_pos):
        cp, cs = self._get_pos_size()
        if not mouse_pos:
            mouse_pos = self._widget.center
        i_size = 6
        mx, my = [x - i_size / 2 for x in mouse_pos]
        anim_rec = Animation(duration=0.4)
        anim_rec += Animation(size=(cs[0], i_size), pos=(cp[0], my), duration=.2)
        anim_rec += Animation(size=(i_size, i_size), pos=(mx, my), duration=0.3)
        anim_rec.start(self._graphic)

    '''Eventos del widget -----------------------------------------------------------------'''
    def _on_touch_down(self, instance, touch):
        # print(f'GClickButton._on_touch_down')
        hla = self._widget.collide_point(*touch.pos)
        if hla and self._active != hla and not self._widget.disabled and self._widget.level_render == self._widget.theme.level_render:
            print(f'Grag {self.uid}')
            touch.grab(self._widget)
            GClickButton.selected = self._widget
            self.animate(True, touch.pos)
            return False

    def _on_touch_up(self, instance, touch):
        # print(f'GClickButton._on_touch_up {self.uid} - grab {touch.grab_state}')
        if touch.grab_state and GClickButton.selected == self._widget:
            touch.ungrab(self._widget)
            GClickButton.selected = None
            self.animate(False, touch.pos)
            ClickEventDispatcher.do_something(self._widget, touch, None)
            return False


class GToggleButton(GFocusedBase):
    """
    Clase para dibujar el click del Widget con foco
    """
    selected = None

    def __init__(self, widget, theme=None, color='pressed_face',
                 radius=None, width=None):
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
        super().__init__(widget, theme, color)
        if widget.state == 'toggled':
            self._color.a = 1.0

        # Eventos -------------------------------------------------
        self._widget.bind(on_touch_down=self._on_touch_down, on_touch_up=self._on_touch_up)

    def set_state(self, new_state, mouse_pos):
        if new_state != self._widget._state:
            self._widget._state = new_state
            if self._widget._state == 'toggled':
                self.animate(True, mouse_pos)
            else:
                self.animate(False, mouse_pos)
            print(f'GToggleButton.set_state -> evento {self._widget.state}')
            ToggleEventDispatcher.do_something(self._widget, self._widget.state)

    def change_state(self, mouse_pos):
        if self._widget._state == 'untoggled':
            self.set_state('toggled', mouse_pos)
        else:
            self.set_state('untoggled', mouse_pos)

    '''Funciones de Dibujo ---------------------------------------------------------------'''
    def _draw_graphics(self):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        rtl, rtr, rbr, rbl = self._radius
        return RoundedRectangle(pos=cp, size=cs, radius=self._radius)  # el 1er radio es el sup. izq.

    def _update_graphics(self, instance, value, *args):
        cp, cs = self._get_pos_size()  # Canvas Position and Size
        self._graphic.pos = cp
        self._graphic.size = cs

    '''Funciones de Animación ------------------------------------------------------------'''
    def animate(self, value=False, mouse_pos=None):
        if value:
            # TODO: Animar la presion
            af = 1.0
            dur = 0.3
            self.on_anim(mouse_pos)
        else:
            # TODO: Animar soltar
            af = 0.0
            dur = 1.0
            self.off_anim(mouse_pos)
        anim_alf = Animation(a=af, duration=dur)
        anim_alf.start(self._color)

    def on_anim(self, mouse_pos):
        cp, cs = self._get_pos_size()
        if not mouse_pos:
            mouse_pos = self._widget.center
        i_size = 6
        self._graphic.size = (i_size, i_size)
        mx, my = mouse_pos
        self._graphic.pos = [x-i_size/2 for x in mouse_pos]
        anim_rec = Animation(size=(i_size, cs[1]), pos=(mx-i_size/2, cp[1]), duration=.2)
        anim_rec += Animation(size=cs, pos=cp, duration=0.2)
        anim_rec.start(self._graphic)

    def off_anim(self, mouse_pos):
        cp, cs = self._get_pos_size()
        if not mouse_pos:
            mouse_pos = self._widget.center
        i_size = 6
        mx, my = [x - i_size / 2 for x in mouse_pos]
        anim_rec = Animation(size=(cs[0], i_size), pos=(cp[0], my), duration=.2)
        anim_rec += Animation(size=(i_size, i_size), pos=(mx, my), duration=0.3)
        anim_rec.start(self._graphic)


    '''Eventos del widget -----------------------------------------------------------------'''
    def _on_touch_down(self, instance, touch):
        hla = self._widget.collide_point(*touch.pos)
        if hla and self._active != hla and not self._widget.disabled and self._widget.level_render == self._widget.theme.level_render:
            touch.grab(self._widget)
            GClickButton.selected = self._widget
            return False

    def _on_touch_up(self, instance, touch):
        # print(f'on_touch_up {touch.pos}')
        if touch.grab_state and GClickButton.selected == self._widget:
            touch.ungrab(self._widget)
            GClickButton.selected = None
            self.change_state(touch.pos)
            # ToggleEventDispatcher.do_something(self._widget, self._widget.state)
            return False




# ANTERIORES COMO REFERENCIAS -----------------------------------------------------
# class ButtonClickGraphic(BaseGraphics):
#     """Grafico de botones click, el borde y la cara
#     Keyword arguments:
#     pos    -- botton left position of the rectangle that contains the widget
#     size   -- size of graphic
#     width  -- width of border the widget
#     radius -- border radius of widget
#     color_border  -- color border of graphic
#     color_face  -- color face of graphic
#     """
#
#     def __init__(self, theme, theme_color_face='widget_face', **kwargs):
#         """Constructor de la clase
#         Keyword arguments:
#
#         """
#         super().__init__(theme, **kwargs)
#         # Graphics Properties ------------------------------
#         self._border_width = self.theme.geometry['border_width']
#         self._radius = compose_dict(kwargs, "radius", tuple, None, acept_none=True)
#         r = self.theme.geometry['radius']
#         self.theme_color_face='widget_face'  # Ver que pasa cuando el boton es flat
#         # Colours and sizes --------------------------------
#         self.fade_bg = None
#         self.end_fade = True
#         # Click graphic -----------------------------------
#         self.rgba_click = self._rgba_click_state('up')
#         self.color_click = graphics.Color(rgba=self.rgba_click)
#         self.graph_click = self._draw_click()
#         # Anim --------------------------------------------
#         self._anim_expand = None
#         self._anim_fade = None
#
#     """ Graphic Metods -----------------------------------------------"""
#     def _rgba_click_state(self, state):
#         """Return color
#         Keyword arguments:
#         state: str   -- up or down
#         """
#         if not(state in ['up', 'down']):
#             raise ValueError("The value of state must be up or down")
#         cup = (self.theme.colors['pressed_face'])[:]
#         if state == 'up':
#             cup[3] = 0.0
#         return cup
#
#     def _get_canvas_size(self):
#         return tuple(xx - self._border_width for xx in self._graphic_size)
#
#     def _get_canvas_pos(self):
#         return tuple(xx + self._border_width/2 for xx in self._graphic_pos)
#
#     def _draw_click(self):
#         background = graphics.InstructionGroup()
#         cs = self._get_canvas_size()  # Canvas Size
#         cp = self._get_canvas_pos()  # Canvas Position
#
#         rtl ,rtr ,rbr ,rbl = self._radius
#         return graphics.RoundedRectangle(pos=cp, size=cs, radius=(rtl ,rtr ,rbr ,rbl))  # el 1er radio es el sup. izq.
#
#     """ Update metods -----------------------------------------------"""
#     def update_colours(self):
#         pass
#
#     def update_geometry(self):
#         super().update_geometry()
#         b = self.theme.geometry['border_width']
#         x, y = self._get_canvas_pos()
#         w, h = self._get_canvas_size()
#         self.graph_click.pos = (x+b/2+3, y+b/2+3)
#         self.graph_click.size = (w-b-6, h-b-6)
#         self.graph_click.radius = (self._radius,)
#
#     def redraw(self):
#         self.clear()
#         self.add(self.color_click)
#         self.add(self.graph_click)
#
#     """ Anim metods -------------------------------------------------"""
#     def start_anim(self):
#         if self._anim_expand:
#             self._anim_expand.stop(self.graph_click)
#         if self._anim_fade:
#             self._anim_fade.stop(self.color_click)
#         l = 4
#         b = self.theme.geometry['border']
#         x, y = self._get_canvas_pos()
#         w, h = self._get_canvas_size()
#         self.graph_click.pos = (x+w/2-l/2, y+h/2-l/2)
#         self.graph_click.size = (l, l)
#         self.rgba_click = self._rgba_click_state('down')
#         self._anim_expand = Animation(duration=0.3, pos=(x+b/2+3, y+b/2+3), size=(w-b-6, h-b-6))
#         self._anim_fade = Animation(duration=0.3, rgba=self.rgba_click)
#         self._anim_fade.bind(on_complete = self._on_end_down_anim)
#         self._anim_expand.start(self.graph_click)
#         self._anim_fade.start(self.color_click)
#
#     def _on_end_down_anim(self, anim, instance):
#         self.rgba_click = self._rgba_click_state('up')
#         an = Animation(duration=0.2, rgba=self.rgba_click)
#         an.start(self.color_click)
#         self.update_colours()
#         self.update_geometry()
#         self.redraw()
#
#     def _anim_up(self):
#         self.rgba_click = self._rgba_click_state('up')
#         if self.end_fade:
#             an = Animation(duration=0.2, rgba=self.rgba_click)
#             an.start(self.color_click)
#             self.end_fade = True
#
#     """ Propierties -------------------------------------------------"""
#     # --- Radius -----
#     def _get_radius(self):
#         return self._radius
#
#     def _set_radius(self, value):
#         self._radius = value
#         self.update_geometry()
#
#     radius = property(_get_radius, _set_radius)
#
#
# class ToggleButtonGraphic(BaseGraphics):
#     """Grafico de botones toggle, el borde y la cara
#     Properties:
#     pos (tuple): botton left position of the rectangle that contains the widget
#     size (tuple): size of graphic
#     width (float): width of border the widget
#     radius (tuple): border radius of widget
#     color_border (): color border of graphic
#     color_face (): color face of graphic
#     """
#
#     def __init__(self, theme, theme_color_face='widget_face', **kwargs):
#         """Constructor de la clase
#         Keyword arguments:
#
#         """
#         super().__init__(theme, **kwargs)
#         # Graphics Properties ------------------------------
#         self._border_width = self.theme.geometry['border']
#         self._radius = compose_dict(kwargs, "radius", tuple, None, acept_none=True)
#         r = self.theme.geometry['radius']
#         self.theme_color_face='widget_face'  # Ver que pasa cuando el boton es flat
#         # Colours and sizes --------------------------------
#         self.fade_bg = None
#         self.end_fade = True
#         # Click graphic -----------------------------------
#         self.rgba_click = self._rgba_click_state('up')
#         self.color_click = graphics.Color(rgba=self.rgba_click)
#         self.graph_click = self._draw_toggle()
#         # Anim --------------------------------------------
#         self._anim_expand = None
#         self._anim_fade = None
#
#     """ Graphic Metods -----------------------------------------------"""
#     def _rgba_click_state(self, state):
#         """Return color
#         Keyword arguments:
#         state: str   -- up or down
#         """
#         if not(state in ['up', 'down']):
#             raise ValueError("The value of state must be up or down")
#         cup = (self.theme.colors['pressed_face'])[:]
#         if state == 'up':
#             cup[3] = 0.0
#         return cup
#
#     def _draw_toggle(self):
#         b = self.theme.geometry['border']
#         x, y = self._graphic_pos  # self._get_canvas_pos()
#         w, h = self._graphic_size  #self._get_canvas_size()
#         cs = (w-b-6, h-b-6)  # Canvas Size
#         cp = (x+b/2+3, y+b/2+3)  # Canvas Position
#         return graphics.RoundedRectangle(pos=cp, size=cs, radius=self._radius)  # el 1er radio es el sup. izq.
#
#     """ Update metods -----------------------------------------------"""
#     def update_colours(self):
#         pass
#
#     def update_geometry(self):
#         super().update_geometry()
#         self.graph_click = self._draw_toggle()
#
#     def redraw(self):
#         self.clear()
#         self.add(self.color_click)
#         self.add(self.graph_click)
#
#     """ Anim metods -------------------------------------------------"""
#     def on_anim(self):
#         if self._anim_expand:
#             self._anim_expand.stop(self.graph_click)
#         if self._anim_fade:
#             self._anim_fade.stop(self.color_click)
#         l = 4
#         b = self.theme.geometry['border']
#         x, y = self._graphic_pos  # self._get_canvas_pos()
#         w, h = self._graphic_size  # self._get_canvas_size()
#         self.graph_click.pos = (x+w/2-l/2, y+h/2-l/2)
#         self.graph_click.size = (l, l)
#         self.rgba_click = self._rgba_click_state('down')
#         self._anim_expand = Animation(duration=0.3, pos=(x+b/2+3, y+b/2+3), size=(w-b-6, h-b-6))
#         self._anim_fade = Animation(duration=0.3, rgba=self.rgba_click)
#         # self._anim_fade.bind(on_complete = self._on_end_down_anim)
#         self._anim_expand.start(self.graph_click)
#         self._anim_fade.start(self.color_click)
#
#     def off_anim(self):
#         self.rgba_click = self._rgba_click_state('up')
#         if self.end_fade:
#             an = Animation(duration=0.2, rgba=self.rgba_click)
#             an.start(self.color_click)
#             self.end_fade = True
#
#     """ Propierties -------------------------------------------------"""
#     # --- Radius -----
#     def _get_radius(self):
#         return self._radius
#
#     def _set_radius(self, value):
#         self._radius = value
#         self.update_geometry()
#
#     radius = property(_get_radius, _set_radius)
#
#     # --- State -----
#     def _get_state_btn(self):
#         return self._state_btn
#
#     def _set_state_btn(self, value):
#         if isinstance(value, str) and value in ['on', 'off']:
#             self._state_btn = value
#             if value == 'off':
#                 self.off_anim()
#             else:
#                 self.on_anim()
#             # self.graphic_switch = self._draw_switch()
#         else:
#             raise ValueError("Incorrect Value")
#
#     state_btn = property(_get_state_btn, _set_state_btn)
#
#
# class CheckButtonGraphic(BaseGraphics):
#     """Grafico de botones check
#     Properties:
#         pos (tuple): botton left position of the rectangle that contains the widget
#         size (tuple): size of graphic
#         width (float): width of border the widget
#         radius (tuple): border radius of widget
#         color_border (): color border of graphic
#         color_face (): color face of graphic
#         type (str): "check", "cross", "square", "radio", "plus", "minus"
#         scale (float): size of graphics
#     """
#     _types = ['check', 'cross', 'square', 'radio', 'plus', 'minus']
#
#     def __init__(self, theme, theme_color_face='widget_face', **kwargs):
#         """Constructor de la clase
#         Keyword arguments:
#             type (str): "check", "cross", "square", "radio", "plus", "minus"
#             scale (float): size of graphics
#         """
#         super().__init__(theme, **kwargs)
#         # Graphics Properties ------------------------------
#         self._border_width = self.theme.geometry['border']
#         self._radius = compose_dict(kwargs, "radius", tuple, None, acept_none=True)
#         self._type = compose_dict(kwargs, "type", str, default="check", acept_none=False)
#         self._scale = compose_dict(kwargs, "scale", int, default=1.0, acept_none=False)
#         # Colours and sizes --------------------------------
#         self._alfa_color = {"checked": 1.0, "unchecked": 0.15, "disabled": 0.15}
#         cc = self.theme.colors['accent_face']
#         cc[3] = self._alfa_color["unchecked"]
#         self.color_check = graphics.Color(rgba=cc)
#         # Graphic -----------------------------------------
#         self.graphic_check = self._change_type(self._type)
#         # self.size = (32*self.scale, 32*self.scale)
#         # Anim --------------------------------------------
#
#     """ Graphic Metods -----------------------------------------------"""
#     def _get_canvas_size(self):
#         # return self.graphic_size
#         return tuple(xx - self._border_width for xx in self._graphic_size)
#
#     def _get_canvas_pos(self):
#         # px, py = self._graphic_pos
#         # # py = py/2 - self.graphic_size[1]/2
#         # return (px, py)
#         return tuple(xx + self._border_width / 2 for xx in self._graphic_pos)
#
#     """ Update metods -----------------------------------------------"""
#     def update_colours(self):
#         pass
#
#     def update_geometry(self):
#         super().update_geometry()
#         self.graphic_check = self._change_type(self._type)
#
#     def redraw(self):
#         self.clear()
#         self.add(self.color_check)
#         self.add(self.graphic_check)
#
#     """ Draw Types --------------------------------------------------"""
#     def _change_type(self, type):
#         if type == "cross":  # "check", "cross", "square", "radio", "plus", "minus"
#             graphic_check = self._draw_cross()
#         elif type == "square":
#             graphic_check = self._draw_square()
#         elif type == "radio":
#             graphic_check = self._draw_radio()
#         elif type == "plus":
#             graphic_check = self._draw_plus()
#         elif type == "minus":
#             graphic_check = self._draw_minus()
#         else:  # "check"
#             graphic_check = self._draw_check()
#         return graphic_check
#
#     def _draw_check(self):
#         # print('draw check')
#         # print(self._layout_pos, self._layout_size)
#         # print(self._graphic_pos, self._graphic_size)
#         # print(self._get_canvas_pos(), self._get_canvas_size())
#         # print(self._halign)
#         sc = self._scale
#         px, py = self._get_canvas_pos()
#         x1 = px + 1 * sc
#         y1 = py + 22 * sc
#         x2 = x1 + 6 * sc
#         y2 = y1 - 1 * sc
#         x3 = x1 + 10 * sc
#         y3 = py + 7 * sc
#         lst = [x1, y1, x2, y2, x3, y3]
#         check_canvas1 = graphics.SmoothLine(bezier=lst, bezier_precision=25, width=4 * sc)
#         x1 = x1 + 10 * sc
#         y1 = py + 7 * sc
#         x2 = x1 + 12 * sc
#         y2 = y1 + 22 * sc
#         x3 = x2 + 10 * sc
#         y3 = py + 32 * sc
#         lst = [x1, y1, x2, y2, x3, y3]
#         check_canvas2 = graphics.SmoothLine(bezier=lst, bezier_precision=25, width=3 * sc)
#         graph = graphics.InstructionGroup()
#         graph.add(check_canvas1)
#         graph.add(check_canvas2)
#         return graph
#
#     def _draw_cross(self):
#         sc = self._scale
#         px, py = self._get_canvas_pos()
#         x1 = px + 8 * sc
#         y1 = py + 8 * sc
#         x2 = px + 22 * sc
#         y2 = py + 22 * sc
#         lst = [x1, y1, x2, y2]
#         check_canvas1 = graphics.Line(points=lst, width=3 * sc)
#         x1 = px + 8 * sc
#         y1 = py + 22 * sc
#         x2 = px + 22 * sc
#         y2 = py + 8 * sc
#         lst = [x1, y1, x2, y2]
#         check_canvas2 = graphics.Line(points=lst, width=3 * sc)
#         graph = graphics.InstructionGroup()
#         graph.add(check_canvas1)
#         graph.add(check_canvas2)
#         return graph
#
#     def _draw_square(self):
#         sc = self._scale
#         px, py = self._get_canvas_pos()
#         x1 = px + 15 * sc
#         y1 = py + 15 * sc
#         lst = [x1, y1]
#         return graphics.Point(points=lst, pointsize=8 * sc)
#
#     def _draw_radio(self):
#         sc = self._scale
#         px, py = self._get_canvas_pos()
#         x1 = px + 6 * sc
#         y1 = py + 6 * sc
#         lst = [x1, y1]
#         return graphics.Ellipse(pos=lst, size=[18*sc, 18*sc])
#
#     def _draw_plus(self):
#         sc = self._scale
#         px, py = self._get_canvas_pos()
#         x1 = px + 15 * sc
#         y1 = py + 8 * sc
#         x2 = px + 15 * sc
#         y2 = py + 22 * sc
#         lst = [x1, y1, x2, y2]
#         check_canvas1 = graphics.Line(points=lst, width=3 * sc)
#         x1 = px + 8 * sc
#         y1 = py + 15 * sc
#         x2 = px + 22 * sc
#         y2 = py + 15 * sc
#         lst = [x1, y1, x2, y2]
#         check_canvas2 = graphics.Line(points=lst, width=3 * sc)
#         graph = graphics.InstructionGroup()
#         graph.add(check_canvas1)
#         graph.add(check_canvas2)
#         return graph
#
#     def _draw_minus(self):
#         sc = self._scale
#         px, py = self._get_canvas_pos()
#         x1 = px + 8 * sc
#         y1 = py + 15 * sc
#         x2 = px + 22 * sc
#         y2 = py + 15 * sc
#         lst = [x1, y1, x2, y2]
#         return graphics.Line(points=lst, width=3 * sc)
#
#     """ Anim metods -------------------------------------------------"""
#     def on_anim(self):
#         cc = self.color_check.rgba[:]
#         cc[3] = self._alfa_color["checked"]
#         fade_check = Animation(rgba=cc, duration=0.4)
#         fade_check.start(self.color_check)
#
#     def off_anim(self):
#         cc = self.color_check.rgba[:]
#         cc[3] = self._alfa_color["unchecked"]
#         fade_check = Animation(rgba=cc, duration=0.4)
#         fade_check.start(self.color_check)
#
#     """ Propierties -------------------------------------------------"""
#     # --- Radius -----
#     def _get_radius(self):
#         return self._radius
#
#     def _set_radius(self, value):
#         self._radius = value
#         self.update_geometry()
#
#     radius = property(_get_radius, _set_radius)
#
#     # --- Scale -----
#     def _get_scale(self):
#         return self._scale
#
#     def _set_scale(self, value):
#         if isinstance(value, float) and 0.5<=value<=3.0:
#             self._scale = value
#             self.size = (32 * value, 32 * value)
#             self.graphic_check = self._change_type(value)
#         else:
#             raise ValueError("Incorrect Value")
#
#     scale = property(_get_scale, _set_scale)
#
#     # --- Type -----
#     def _get_type(self):
#         return self._type
#
#     def _set_type(self, value):
#         if isinstance(value, str) and value in self._types:
#             self._type = value
#             self.graphic_check = self._change_type(value)
#         else:
#             raise ValueError("Incorrect Value")
#
#     type = property(_get_type, _set_type)
#
#     # --- State -----
#     def _get_state_btn(self):
#         return self._state_btn
#
#     def _set_state_btn(self, value):
#         if isinstance(value, str) and value in ['on', 'off']:
#             self._state_btn = value
#             if value == 'off':
#                 self.off_anim()
#             else:
#                 self.on_anim()
#             # self.graphic_switch = self._draw_switch()
#         else:
#             raise ValueError("Incorrect Value")
#
#     state_btn = property(_get_state_btn, _set_state_btn)
#
#
# class SwitchAcentGraphic(BaseGraphics):
#     """Grafico de botones check
#     Properties:
#         pos (tuple): botton left position of the rectangle that contains the widget
#         size (tuple): size of graphic
#         width (float): width of border the widget
#         radius (tuple): border radius of widget
#         color_border (): color border of graphic
#         color_face (): color face of graphic
#         orientation (str): "horizontal", "vertical"
#     """
#     _orientations = ['horizontal', 'vertical']
#
#     def __init__(self, theme, theme_color_face='widget_face', **kwargs):
#         """Constructor de la clase
#         Keyword arguments:
#             orientation (str): "horizontal", "vertical"
#             scale (float): size of graphics
#         """
#         super().__init__(theme, **kwargs)
#         # Graphics Properties ------------------------------
#         self._border_width = self.theme.geometry['border']
#         self._radius = compose_dict(kwargs, 'radius', tuple, None, acept_none=True)
#         self._orientation = compose_dict(kwargs, 'orientation', str, default='horizontal', acept_none=False)
#         # self._scale = compose_dict(kwargs, 'scale', float, default=1.0, acept_none=False)
#         self._state_btn = compose_dict(kwargs, 'state', str, default='off', acept_none=False)
#         # Anim Vars ------ --------------------------------
#         self._alfa_color = {"on": 1.0, "off": 0.4, "disabled": 0.15}
#         self.color = graphics.Color(rgba=self.theme.colors['accent_face'])
#         self.color.rgba[3] = self._alfa_color["off"]
#         self._graphic_pos = self._get_canvas_pos()
#         self._switch_pos = self._calc_switch_pos()
#         # Graphic -----------------------------------------
#         self.graphic_switch = self._draw_switch()
#
#     """ Graphic Metods -----------------------------------------------"""
#     def _get_canvas_size(self):
#         return tuple(xx - self._border_width for xx in self._graphic_size)
#
#     def _get_canvas_pos(self):
#         return tuple(xx + self._border_width / 2 for xx in self._graphic_pos)
#
#     def _calc_switch_pos(self):
#         bx, by = self._get_canvas_pos()
#         bw, bh = self._get_canvas_size()
#         btnw, btnh = self._calc_switch_size()
#         bt = self.theme.geometry['border']
#         if self._state_btn == 'off':  #  Switch Apagado
#             x = bx + bt / 2 + 4
#             y = by + bt / 2 + 4
#         elif self.orientation == 'vertical':  #  Switch Enciendido Vertical
#             x = bx + bt / 2 + 4
#             y = by + bh - bt / 2 - 4 - btnh
#         else:  # Switch Enciendido Horizontal
#             x = bx + bw - bt / 2 - 4 - btnw
#             y = by + bt / 2 + 4
#         return [x, y]  # asign to self._switch_canvas.size
#
#     def _calc_switch_size(self):
#         bw, bh = self._get_canvas_size()
#         if self.orientation == 'vertical':
#             btnw = bw - self.theme.geometry['border'] - 8
#             btnh = btnw if bh > btnw else bh * 0.4
#         else:
#             btnh = bh - self.theme.geometry['border'] - 8
#             btnw = btnh if bw > btnh else bw * 0.4
#         return (btnw, btnh)  # asign to self._switch_canvas.size
#
#     """ Update metods -----------------------------------------------"""
#     def update_colours(self):
#         pass
#
#     def update_geometry(self):
#         super().update_geometry()
#         self.graphic_switch.size = self._calc_switch_size()
#         self.graphic_switch.pos = self._calc_switch_pos()
#
#     def _draw_switch(self):
#         sz = self._calc_switch_size()
#         pos = self._calc_switch_pos()
#         return graphics.RoundedRectangle(size=sz, radius=self._radius, pos=pos)
#
#     def redraw(self):
#         self.clear()
#         self.add(self.color)
#         self.add(self.graphic_switch)
#
#     """ Anim metods -------------------------------------------------"""
#     def on_anim(self):
#         new_col = self.color.rgba[:]
#         new_col[3] = self._alfa_color["on"]
#         new_pos = self._calc_switch_pos()
#         fade_check = Animation(rgba=new_col, duration=0.4)
#         move_btn = Animation(duration=0.4, pos=new_pos, t='in_out_quad')
#         fade_check.start(self.color)
#         move_btn.start(self.graphic_switch)
#
#     def off_anim(self):
#         new_col = self.color.rgba[:]
#         new_col[3] = self._alfa_color["off"]
#         new_pos = self._calc_switch_pos()
#         fade_check = Animation(rgba=new_col, duration=0.4)
#         move_btn = Animation(duration=0.4, pos=new_pos, t='in_out_quad')
#         fade_check.start(self.color)
#         move_btn.start(self.graphic_switch)
#
#
#     """ Propierties -------------------------------------------------"""
#     # --- Pos --------
#     # def _set_pos(self, value):
#     #     super()._set_pos(value)
#     #     self._switch_pos = self._calc_switch_pos()
#
#     # --- Radius -----
#     def _get_radius(self):
#         return self._radius
#
#     def _set_radius(self, value):
#         self._radius = value
#         self.graphic_switch.radius = value
#         # self.update_geometry()
#
#     radius = property(_get_radius, _set_radius)
#
#     # # --- Scale -----
#     # def _get_scale(self):
#     #     return self._scale
#     #
#     # def _set_scale(self, value):
#     #     if isinstance(value, float) and 0.5<=value<=3.0:
#     #         self._scale = value
#     #         # self._graphic_size = (32 * value, 32 * value)
#     #         self.graphic_switch = self._draw_switch()
#     #     else:
#     #         raise ValueError("Incorrect Value")
#     #
#     # scale = property(_get_scale, _set_scale)
#
#     # --- Orientation -----
#     def _get_orientation(self):
#         return self._orientation
#
#     def _set_orientation(self, value):
#         if isinstance(value, str) and value in self._orientations:
#             # if self._orientation != value:
#             self._orientation = value
#             self.graphic_switch = self._draw_switch()
#         else:
#             raise ValueError("Incorrect Value")
#
#     orientation = property(_get_orientation, _set_orientation)
#
#     # --- State -----
#     def _get_state_btn(self):
#         return self._state_btn
#
#     def _set_state_btn(self, value):
#         if isinstance(value, str) and value in ['on', 'off']:
#             self._state_btn = value
#             if value == 'off':
#                 self.off_anim()
#             else:
#                 self.on_anim()
#             # self.graphic_switch = self._draw_switch()
#         else:
#             raise ValueError("Incorrect Value")
#
#     state_btn = property(_get_state_btn, _set_state_btn)
#


"""TaskCheckButton -> Sin Iniciar[ ], En proceso [>], Paralizada [o], Finalizada [v], anulada[x]"""

