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
# mpbe imports --------------------------------------------------------------
from helpers_mpbe.python import compose_dict
# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import ThemableBehavior, Theme
from kivy.properties import OptionProperty







# TODO: No codificado
class GHotlightItem(InstructionGroup):

    def __init__(self, widget):
        super().__init__()
        self._widget = widget
        self._active = False
        self.alpha_color = 0
        self._draw()
        self._widget.bind(pos=self._update_graphics, size=self._update_graphics)
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)

    # Funciones de Dibujo y Actualización -----------------------------------------------
    def _draw(self):
        cc = self._widget.theme.colors['hotlight_border']
        cc[3] = self.alpha_color
        self._color = Color(rgba=cc)
        ee = self._widget.theme.geometry['hotlight_width']
        self._calc_pos_lines()
        self._hl_rect_l = Line(points=(self._pos_lx, self._pos_by, self._pos_lx, self._pos_ty), width=ee, cap='none')
        self._hl_rect_r = Line(points=(self._pos_rx, self._pos_by, self._pos_rx, self._pos_ty), width=ee, cap='none')
        self.add(self._color)
        self.add(self._hl_rect_l)
        self.add(self._hl_rect_r)

    def _calc_pos_lines(self):
        ww, wh = self._widget.size
        wx, wy = self._widget.pos
        lhw = self._widget.theme.geometry['hotlight_width']
        wbw = self._widget.theme.geometry['border_width']
        hl = wh - wbw * 2
        self._pos_lx = wx + wbw + lhw  # Pos line left x
        self._pos_rx = wx + ww - wbw - lhw  # Pos line right x
        self._pos_by = wy
        self._pos_ty = wy + wh

    def _update_graphics(self, *args):
        self._calc_pos_lines()
        self._hl_rect_l.points = (self._pos_lx, self._pos_by, self._pos_lx, self._pos_ty)
        self._hl_rect_r.points = (self._pos_rx, self._pos_by, self._pos_rx, self._pos_ty)

    # Funciones de Animación -------------------------------------------------
    def show(self, value):
        '''Muestra el o Esconde el rectangulo sin animacion'''
        # print(f'Show - {value}')
        if value == True:
            self.alpha_color = 1.0
            # self._color.a = self.alpha_color
        else:
            self.alpha_color = 0.0
            # self._color.a = self.alpha_color

    def animate_hotlight(self, alpha):
        self.alpha_color = alpha
        # self._color.a = self.alpha_color
        # Reiniciar el tiempo y programar la actualización de la animación
        self.elapsed_time = 0
        Clock.schedule_interval(self.update_animation, 1 / 60)  # 60 FPS

    def update_animation(self, dt):
        # Aumentar el tiempo transcurrido
        self.elapsed_time += dt
        duracion = 0.6
        progress = min(1, self.elapsed_time / duracion)  # Normalizar entre 0 y 1

        # Actualiza Alpha
        if self.alpha_color == 1:
            new_alpha = self.alpha_color * progress
        else:
            new_alpha = 1 - 1 * progress
        self._color.a = new_alpha

        # Detener la animación cuando alcance el tamaño objetivo
        if progress >= 1:
            Clock.unschedule(self.update_animation)
            return False  # Detener el `Clock`

    # Eventos del mouse -------------------------------------------------------
    def on_mouse_move(self, instance, mp):
        hla = self._widget.collide_point_to_window(mp[0], mp[1])
        if self._active != hla and not self._widget.disabled and self._widget.level_render == self._widget.theme.level_render:
            self._active = hla
            if hla:  # enciende el hotlight
                self.animate_hotlight(1.0)
                self._widget._hotlight_event(True, mp)
            else:  # apaga el hotlight
                self.animate_hotlight(0.0)
                self._widget._hotlight_event(False, mp)


class GFocusItem(InstructionGroup):

    def __init__(self, widget):
        super().__init__()
        self._widget = widget
        self.alpha_color = 0
        self._draw()
        # Eventos -------------------------------------------------
        # self._widget.parent.bind(focus=self._on_focus)

        self._widget.bind(pos=self._update_graphics, size=self._update_graphics)

    # Funciones de Dibujo y Actualización -----------------------------------------------
    def _draw(self):
        cc = self._widget.theme.colors['focus_border']
        cc[3] = self.alpha_color
        self._color = Color(rgba=cc)
        ee = self._widget.theme.geometry['focus_width']
        self._calc_pos_lines()
        self._f_rect_t = Line(points=(self._pos_lx, self._pos_ty, self._pos_rx, self._pos_ty), width=ee,
                               cap='none')
        self._f_rect_b = Line(points=(self._pos_lx, self._pos_by, self._pos_rx, self._pos_by), width=ee,
                               cap='none')
        self.add(self._color)
        self.add(self._f_rect_t)
        self.add(self._f_rect_b)

    def show(self, value):
        '''Muestra el o Esconde el rectangulo sin animacion'''
        # print(f'Show - {value}')
        if value == True:
            self.alpha_color = 1.0
            self._color.a = self.alpha_color
        else:
            self.alpha_color = 0.0
            self._color.a = self.alpha_color

    def _calc_pos_lines(self):
        ww, wh = self._widget.size
        wx, wy = self._widget.pos
        lhw = self._widget.theme.geometry['focus_width']
        wbw = self._widget.theme.geometry['border_width']
        hl = wh - wbw * 2
        self._pos_lx = wx + wbw + lhw  #+ 2  # Pos line left x
        self._pos_rx = wx + ww - wbw - lhw  #- 2  # Pos line right x
        self._pos_by = wy
        self._pos_ty = wy + wh

    def _update_graphics(self, *args):
        self._calc_pos_lines()
        self._f_rect_t.points = (self._pos_lx, self._pos_ty, self._pos_rx, self._pos_ty)
        self._f_rect_b.points = (self._pos_lx, self._pos_by, self._pos_rx, self._pos_by)

    # Funciones de Animación -------------------------------------------------
    def animate_focus(self, value):
        if value:
            self.alpha_color = 1.0
        else:
            self.alpha_color = 0.0
        # Reiniciar el tiempo y programar la actualización de la animación
        self.elapsed_time = 0
        Clock.schedule_interval(self.update_animation, 1 / 60)  # 60 FPS

    def update_animation(self, dt):
        # Aumentar el tiempo transcurrido
        self.elapsed_time += dt
        duracion = 1.0
        progress = min(1, self.elapsed_time / duracion)  # Normalizar entre 0 y 1

        # Actualiza Alpha
        if self.alpha_color == 1:
            new_alpha = self.alpha_color * progress
        else:
            new_alpha = 1 - 1 * progress
        self._color.a = new_alpha

        # Detener la animación cuando alcance el tamaño objetivo
        if progress >= 1:
            Clock.unschedule(self.update_animation)
            return False  # Detener el `Clock`

    # '''Eventos del widget -----------------------------------------------------------------'''
    # def _on_focus(self, instance, value):
    #     # print(f'GFocus._on_focus {value}')
    #     self.animate_focus(value)



class GSelectItem(InstructionGroup):

    def __init__(self, widget):
        super().__init__()
        self._widget = widget
        self.alpha_color = 0
        self.sel_vertical_pos = 0
        self.sel_vertical_size = 30
        self.sel_horizontal_pos = 0
        self.sel_horizontal_size = 0
        # self.sel_click_x = 0
        # self.Sel_click_y = 0
        self._delta_x = 0
        self._delta_y = 0
        self._delta_w = 0
        self._delta_h = 0

        self._draw()
        self._widget.bind(pos=self._update_size, size=self._update_size)

    # Funciones de Dibujo y Actualización -----------------------------------------------
    def _draw(self):
        cc = self._widget.theme.colors['pressed_face']
        cc[3] = self.alpha_color
        self._color = Color(rgba=cc)
        bo = self._widget.theme.geometry['border_width']
        hl = self._widget.theme.geometry['hotlight_width']
        self._rect = Rectangle(size=(self.sel_horizontal_size, self.sel_vertical_size),
                               pos=(self.sel_horizontal_pos, self.sel_vertical_pos))
        self._initialize_select_anim(self._widget.center)
        self.add(self._color)
        self.add(self._rect)

    def show(self, value):
        '''Muestra el o Esconde el rectangulo sin animacion'''
        # print(f'Show')
        # if not self.play:
        if value == True:
            self.alpha_color = 1.0
            self._color.a = self.alpha_color
            self._update_size(self, None)
        elif value == False:
            # print('  off')
            self.alpha_color = 0.0
            self._color.a = self.alpha_color

    def _initialize_select_anim(self, mouse_pos):
        # print('GSelectItem._initialize_select_anim')
        sip = 6  # size initial point
        mx, my = mouse_pos
        # mx, my = self._widget.center
        ww, wh = self._widget.size
        wx, wy = self._widget.pos
        # lhw = self._widget.theme.geometry['focus_width']
        wbw = self._widget.theme.geometry['border_width']
        # Vertical
        self.sel_vertical_pos = my - sip/2
        self.sel_vertical_size = sip
        self._delta_h = wh - sip
        self._delta_y = self.sel_vertical_pos - wy
        # Horizontal
        self.sel_horizontal_pos = mx - sip/2
        self.sel_horizontal_size = sip
        self._delta_w = ww - sip - wbw * 2
        self._delta_x = self.sel_horizontal_pos - wx

    def _initialize_unselect_anim(self):
        # print('GSelectItem._initialize_unselect_anim')
        sip = 4  # size initial point
        mx, my = self._widget.center
        ww, wh = self._widget.size
        wx, wy = self._widget.pos
        # lhw = self._widget.theme.geometry['focus_width']
        wbw = self._widget.theme.geometry['border_width']
        # Vertical
        self.sel_vertical_pos = my - sip / 2
        self.sel_vertical_size = sip
        self._delta_h = wh - sip
        self._delta_y = self.sel_vertical_pos - wy
        # Horizontal
        self.sel_horizontal_pos = wx + wbw  #+ 3
        self.sel_horizontal_size = ww - wbw * 2 - sip
        self._delta_w = ww - sip - wbw * 2
        self._delta_x = self.sel_horizontal_size/2

    def _update_size(self, instance, value):
        # print(f'GSelectItem._update_size, ac={self.alpha_color}')
        if self._color.a == 1.0:
            sip = 4  # size initial point
            mx, my = self._widget.pos
            ww, wh = self._widget.size
            wx, wy = self._widget.pos
            # lhw = self._widget.theme.geometry['focus_width']
            wbw = self._widget.theme.geometry['border_width']
            # Vertical
            self.sel_vertical_pos = my
            self.sel_vertical_size = wh
            # Horizontal
            self.sel_horizontal_pos = mx + wbw  #+ 3
            self.sel_horizontal_size = ww - wbw * 2  #- 6
            self._update_graphics()

    def _update_graphics(self, *args):
        # self._calc_pos()
        self._rect.pos = (self.sel_horizontal_pos, self.sel_vertical_pos)
        self._rect.size = (self.sel_horizontal_size, self.sel_vertical_size)

    # Funciones de Animación -------------------------------------------------
    def animate_select(self, value, mouse_pos):
        # print(f'GSelectItem.animate_select, value={value} alpha={self.alpha_color}')
        self.play = True
        if value:
            # print(f"animate_Select->Selecciona {self._widget.uid}")
            wwp = self._widget.to_window(*self._widget.pos)
            mouse_pos = (mouse_pos[0]-wwp[0], self._widget.center[1])
            self.alpha_color = 1.0
            self._initialize_select_anim(mouse_pos)
            # print(f'sel v pos={self.sel_vertical_pos}')
            self._elapsed_time = 0  # Reinicia el tiempo
            Clock.schedule_interval(self._sel_v_anim, 1 / 60)  # 60 FPS - Ejecuta la animacion
        elif not value:
            # print(f"animate_Select->Deselecciona {self._widget.uid}")
            self.alpha_color = 0.0
            self._color.a = 1.0
            self._initialize_unselect_anim()
            # print(f'des sel v pos={self.sel_vertical_pos}')
            self._elapsed_time = 0  # Reinicia el tiempo
            Clock.schedule_interval(self._unsel_v_anim, 1 / 60)  # 60 FPS - Ejecuta la animacion

    def _sel_v_anim(self, dt):
        # Aumentar el tiempo transcurrido
        self._elapsed_time += dt
        duracion = 0.2
        progress = min(1, self._elapsed_time / duracion)  # Normalizar entre 0 y 1
        # Actualiza Alpha
        new_alpha = self.alpha_color * progress
        self._color.a = new_alpha
        # Vertical
        self.sel_vertical_pos = self._widget.y + self._delta_y * (1 - progress)
        self.sel_vertical_size = self._widget.height - self._delta_h * (1 - progress)
        # print(f'  sel V(pos, size)={self.sel_vertical_pos, self.sel_vertical_size}, delta={self._delta_y}')
        self._update_graphics()
        # Detener la animación cuando alcance el tamaño objetivo
        if progress >= 1:
            self._elapsed_time = 0
            Clock.unschedule(self._sel_v_anim)
            Clock.schedule_interval(self._sel_h_anim, 1 / 60)  # 60 FPS - Ejecuta la animacion

    def _sel_h_anim(self, dt):
        # Aumentar el tiempo transcurrido
        self._elapsed_time += dt
        duracion = 0.4
        progress = min(1, self._elapsed_time / duracion)  # Normalizar entre 0 y 1
        # Horizontal
        wbw = self._widget.theme.geometry['border_width']
        self.sel_horizontal_pos = self._widget.x + wbw + self._delta_x * (1 - progress)  #+ 3
        self.sel_horizontal_size = self._widget.width - wbw * 2 - self._delta_w * (1 - progress)  #- 6
        self._update_graphics()
        # Detener la animación cuando alcance el tamaño objetivo
        if progress >= 1:
            Clock.unschedule(self._sel_h_anim)

    def _unsel_v_anim(self, dt):
        # Aumentar el tiempo transcurrido
        # print(f'GSelectItem._unsel_v_anim')
        # print(f'  H(pos, size)={self.sel_horizontal_pos, self.sel_horizontal_size}, delta={self._delta_y}')


        self._elapsed_time += dt
        # print(f'unsel time={self._elapsed_time}')
        duracion = 0.2
        progress = min(1, self._elapsed_time / duracion)  # Normalizar entre 0 y 1
        # Vertical
        self.sel_vertical_pos = self._widget.y + self._delta_y * progress
        self.sel_vertical_size = self._widget.height - self._delta_h * progress
        self._update_graphics()
        # Detener la animación cuando alcance el tamaño objetivo
        if progress >= 1:
            self._elapsed_time = 0
            Clock.unschedule(self._unsel_v_anim)
            Clock.schedule_interval(self._unsel_h_anim, 1 / 60)  # 60 FPS - Ejecuta la animacion

    def _unsel_h_anim(self, dt):
        # Aumentar el tiempo transcurrido
        self._elapsed_time += dt
        # print(f'unsel, time={self._elapsed_time}')
        duracion = 0.4
        progress = min(1, self._elapsed_time / duracion)  # Normalizar entre 0 y 1
        # Horizontal
        wbw = self._widget.theme.geometry['border_width']
        self.sel_horizontal_pos = self._widget.x + wbw + 3 + self._delta_x * progress
        self.sel_horizontal_size = self._widget.width - wbw * 2 - 6 - self._delta_w * progress
        self._update_graphics()

        # Detener la animación cuando alcance el tamaño objetivo
        if progress >= 1:
            Clock.unschedule(self._unsel_h_anim)
            self._color.a = 0.0