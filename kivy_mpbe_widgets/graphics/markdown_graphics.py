# -*- coding: utf-8 -*-
#
#  items_graphics.py
#
#  Copyright 2024 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
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
Base Items Graphics Package to create widgets of kivy_dkw
Created on 03/11/2024

@author: mpbe
@note:
'''

# kivy imports --------------------------------------------------------------
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.behaviors import FocusBehavior
from kivy.graphics import InstructionGroup, Color, Line, Rectangle
from kivy.animation import Animation
# mpbe imports --------------------------------------------------------------
from helpers_mpbe.python import compose_dict
# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy.event import EventDispatcher
from kivy_mpbe_widgets.theming import ThemableBehavior, Theme
from kivy.properties import OptionProperty
from kivy_mpbe_widgets.events.widgets_events import StartAnimEventDispatcher, EndAnimEventDispatcher
from kivy.properties import NumericProperty


 
class GHotlightItem(InstructionGroup):
    """Clase que maneja la gráfica del hotlight del item"""

    def __init__(self, widget):
        super().__init__()
        # Variable del widget
        self._widget = widget
        # Variables de Animación
        # self._alpha_color = 0  ACA ESTA EL PROBLEMA, HAY QUE USAR UNA properti que cambie el valor de alpha
        self.duration = 0.5
        self._active = False
        # Variables de posición
        self._pos_lx = 0  # Pos line left x
        self._pos_rx = 0  # Pos line right x
        self._pos_by = 0  # Pos line bottom y
        self._pos_ty = 0  # Pos line top y
        # Variables de graficos
        self._color = Color(rgba=self._widget.theme.colors['hotlight_border'])
        self._color.a = 0
        self._width = 1  # self._widget.theme.geometry['hotlight_width']
        self._gr_hl_sup = None
        self._gr_hl_inf = None
        # Inicializacion del grafico
        self._draw_graphics()
        # Eventos
        # self._widget.bind(pos=self.update_graphics, size=self.update_graphics)
        # if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
        #     Window.bind(mouse_pos=self.on_mouse_move)

    # Propiedades de Activacion ---------------------------------------------------------
    def _get_active(self):
        return self._active
    active = property(_get_active)

    # Propiedades de la animacion -------------------------------------------------------
    def _set_alpha_color(self, value):
        """Callback que se activa cuando la propiedad _alpha_color cambia."""
        # self._alpha_color = value
        self._color.a = value
    def _get_alpha_color(self):
        return self._color.a
    _alpha_color = property(_get_alpha_color, _set_alpha_color)


    # Funciones de Dibujo y Actualización -----------------------------------------------
    def _draw_graphics(self):
        self._color.a = self._alpha_color
        self._calc_pos_lines()
        self._gr_hl_sup = Line(points=(self._pos_lx, self._pos_ty, self._pos_rx, self._pos_ty), width=self._width, cap='none')
        self._gr_hl_inf = Line(points=(self._pos_lx, self._pos_by, self._pos_rx, self._pos_by), width=self._width, cap='none')
        self.add(self._color)
        self.add(self._gr_hl_sup)
        self.add(self._gr_hl_inf)

    def _calc_pos_lines(self):
        ww, wh = self._widget.size
        wx, wy = self._widget.pos
        self._pos_lx = wx  # Pos line left x
        self._pos_rx = wx + ww  # Pos line right x
        self._pos_by = wy
        self._pos_ty = wy + wh

    def update_graphics(self, *args):
        self._calc_pos_lines()
        self._gr_hl_sup.points = (self._pos_lx, self._pos_ty, self._pos_rx, self._pos_ty)
        self._gr_hl_inf.points = (self._pos_lx, self._pos_by, self._pos_rx, self._pos_by)

    # Funciones de Animación -------------------------------------------------
    def show(self, active:bool):
        '''Muestra el o Esconde el rectangulo sin animacion'''
        self._alpha_color = 1.0 if active else 0.0
        self._active = active

    def animate(self, active:bool):
        alpha = 1.0 if active else 0.0
        # Animation.cancel_all(self, '_alpha_color') # Cancelar animaciones previas
        # Inicia la animacion
        anim = Animation(_alpha_color=alpha, d=self.duration, t='out_quad')
        anim.start(self)
        self._active = active

    # Eventos del mouse -------------------------------------------------------
    # def on_mouse_move(self, instance, mp):
    #     hla = self._widget.collide_point_to_window(*mp)
    #     # print(f"+- GHotlightItem.on_mouse_move(): active:{self._active} collide {hla} widget: {self._widget.md_line.num_line}")
    #     if self._active != hla and not self._widget.disabled and self._widget.level_render == self._widget.theme.level_render:
    #         self._active = hla
    #         if hla:  # enciende el hotlight
    #             self.animate(1.0)
    #             # self.show(1.0)
    #         else:  # apaga el hotlight
    #             self.animate(0.0)
    #         self._widget._handle_hotlight_event(hla)



class GActiveItem(InstructionGroup):
    """Clase que maneja la gráfica de la activación del item"""
    def __init__(self, widget):
        super().__init__()
        # Variable del widget
        self._widget = widget
        # Variables de animación
        self._alpha_color = 0
        self.duration = 3
        # Variables de posición
        self._pos_lx = 0  # Pos line left x
        self._pos_rx = 0  # Pos line right x
        self._pos_by = 0  # Pos line bottom y
        self._pos_ty = 0  # Pos line top y
        # Variables de graficos
        self._color = Color(rgba=self._widget.theme.colors['focus_border'])
        self._width = self._widget.theme.geometry['hotlight_width'] * 3
        self._gr_vl = None
        # Inicializacion del grafico
        self._draw()
        # Eventos
        # self._widget.bind(pos=self.update_graphics, size=self.update_graphics)

    # Funciones de Dibujo y Actualización -----------------------------------------------
    def _draw(self):
        self._color.a = self._alpha_color
        self._calc_pos_lines()
        self._gr_vl = Line(points=(self._pos_lx, self._pos_by, self._pos_lx, self._pos_ty),
                           width=self._width, cap='none')
        self.add(self._color)
        self.add(self._gr_vl)

    def _calc_pos_lines(self):
        ww, wh = self._widget.size
        wx, wy = self._widget.pos
        self._pos_lx = wx  # Pos line left x
        self._pos_rx = wx + ww  # Pos line right x
        self._pos_by = wy
        self._pos_ty = wy + wh

    def update_graphics(self, *args):
        self._calc_pos_lines()
        self._gr_vl.points = (self._pos_lx, self._pos_by, self._pos_lx, self._pos_ty)

    # Funciones de Animación -------------------------------------------------
    def show(self, value):
        '''Muestra el o Esconde el rectangulo sin animacion'''
        self._alpha_color = 1.0 if value is True else 0.0

    def animate(self, value):
        alpha = 1.0 if value is True else 0.0
        # Animation.cancel_all(self, '_alpha_color') # Cancelar animaciones previas
        # Inicia la animacion
        anim = Animation(_alpha_color=alpha, d=self.duration, t='out_quad')
        anim.start(self)

    # Poner on_activate aca? creo que no
    


class GSelectItem(InstructionGroup):
    """Clase que maneja la gráfica de la selección del item"""
    def __init__(self, widget):
        super().__init__()
        # Variable del widget
        self._widget = widget
        # Variables de animación
        self.duration = 1
        # Variables de posición
        self._pos_x = 0 
        # self._pos_y = 0  # Definida como propiedad
        self._size_w = 0
        # self._size_h = 0  # Definida como propiedad
        # Variables de graficos
        self._color = Color(rgba=self._widget.theme.colors['pressed_face'])
        self._color.a = 0
        self._gr_rectangle = None
        # Inicializacion del grafico
        self._draw()
        # Eventos
        # self._widget.bind(pos=self.update_graphics, size=self.update_graphics)

    # Propiedades de la animacion -------------------------------------------------------
    def _set_alpha_color(self, value):
        """Callback que se activa cuando la propiedad _alpha_color cambia."""
        self._color.a = value
    def _get_alpha_color(self):
        return self._color.a
    _alpha_color = property(_get_alpha_color, _set_alpha_color)

    def _set_size_h(self, value):
        self._gr_rectangle.size = (self._widget.width, value)
    def _get_size_h(self):
        return self._gr_rectangle.size[1]
    _size_h = property(_get_size_h, _set_size_h)

    def _set_pos_y(self, value):
        self._gr_rectangle.pos = (self._widget.y, value)
    def _get_pos_y(self):
        return self._gr_rectangle.pos[1]
    _pos_y = property(_get_pos_y, _set_pos_y)



    # Funciones de Dibujo y Actualización -----------------------------------------------
    def _draw(self):
        self._color.a = self._alpha_color
        # self._calc_pos_rect()
        self._gr_rectangle = Rectangle(size=self._widget.size,
                               pos=self._widget.pos)
        self.add(self._color)
        self.add(self._gr_rectangle)

    def _calc_pos_rect(self):
        self._size_w, self._size_h = self._widget.size
        self._pos_x, self._pos_y = self._widget.pos

    def update_graphics(self, *args):
        self._calc_pos_rect()
        self._gr_rectangle.pos = (self._pos_x, self._pos_y)
        self._gr_rectangle.size = (self._size_w, self._size_h)

    # Funciones de Animación -------------------------------------------------
    def show(self, value):
        '''Muestra el o Esconde el rectangulo sin animacion'''
        self._gr_rectangle.size = self._widget.size
        self._alpha_color = 1.0 if value else 0.0

    def animate_fade(self, selected:bool):
        """
        Anima el rectangulo de selcción con un fade.
        Se usa para seleccionar con click y des-seleccionar
        Args:
            selected(bool): Indica el estado de la seleccion
        """
        alpha = 1.0 if selected else 0.0
        # Animation.cancel_all(self, '_alpha_color', '_size_h') # Cancelar animaciones previas
        # Inicia la animacion
        self._gr_rectangle.size = self._widget.size
        self._gr_rectangle.pos = self._widget.pos
        anim = Animation(_alpha_color=alpha, d=self.duration, t='out_quad')
        anim.start(self)

    def animate_up(self):
        """
        Anima la selección desde abajo hacia arriba.
        """
        # Animation.cancel_all(self, '_alpha_color', '_size_h') # Cancelar animaciones previas
        # Define las variables de base
        self._size_h = 0
        self._alpha_color = 1
        # Anima la altura
        anim = Animation(_size_h=self._widget.height, d=self.duration, t='out_quad')
        anim.start(self)

    def animate_down(self):
        """
        Anima la selección desde arriba hacia abajo.
        """
        # Animation.cancel_all(self, '_alpha_color', '_size_h') # Cancelar animaciones previasAnimation.cancel_all(self, 'alpha_color') # Cancelar animaciones previas
        # Define las variables de base
        self._pos_y = self._pos_y + self._size_h
        self._size_h = 0
        self._alpha_color = 1
        # Anima la altura y la posicion y
        anim = Animation(_size_h=self._widget.height, _pos_y=self._widget.y, d=self.duration, t='out_quad')
        anim.start(self)

