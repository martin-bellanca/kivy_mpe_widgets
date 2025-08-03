# -*- coding: utf-8 -*-
#
#  base_widgets.py
#
#  Copyright 2018 Martin Pablo Bellanca <mbellanca@gmail.com>
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
Base Package to create widgets of kivy_dkw \n
Created on 02/05/2020

@author: mpbe
@note:
'''

# kivy imports --------------------------------------------------------------
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import OptionProperty
# mpbe imports --------------------------------------------------------------
from helpers_mpbe.python import compose_dict
# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets as MPW
from kivy_mpbe_widgets.theming import ThemableBehavior, Theme
from kivy_mpbe_widgets.graphics.widget_graphics import GFace, GBorder, GFocus, GHotLight
from kivy_mpbe_widgets.events.widgets_events import HotlightEventDispatcher


# Works Dirs ----------------------------------------------------------------
# KV_DIRECTORY = MPW.DIR_BASE + '/wg_labels/'
# Builder.load_file(KV_DIRECTORY+'text_labels.kv')


class ThemeWidget(ThemableBehavior, Widget):
    """
    Clase base para la creacion de widgets con el uso de temas
    **Arguments:**
    - container (BoxLayout): Contenedor base para insertar sub widgets.
    """
    process_event = None  # Guarda el widget que esta procesando el evento. Es para que un widget pueda bloquear un evento, depende de que este codificado en todos los widgets.
    level_render = OptionProperty('low', options=['low', 'medium', 'high'])

    def __init__(self, transparent=None, flat=None, container=None, **kwargs):
        """Class Constuctor
        **Parameters:**
        - transparent (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        - flat (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        - opposite_colors (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        """
        ThemableBehavior.__init__(self, transparent, flat)
        Widget.__init__(self, **kwargs)
        if container:
            self.container = container  # BoxLayout(orientation='vertical')
        else:
            self.container = BoxLayout(orientation='vertical')
        self.add_widget(self.container)
        self.bind(pos=self._update_geometry, size=self._update_geometry)

    def _update_geometry(self, instance, value):
        self.container.size = self.size
        self.container.pos = self.pos

    # def collide_point_to_window(self, x, y):  # on windows coordinates
    #     try:
    #         # Check the position of the point
    #         bpx, bpy = self.to_window(self.pos[0], self.pos[1], True)
    #         bwidth, bheight = self.size
    #         # Direction X
    #         bpw = bpx + bwidth
    #         inx = True if bpx <= x <= bpw else False
    #         # Direction Y
    #         bph = bpy + bheight
    #         iny = True if bpy <= y <= bph else False
    #         # Collide
    #         return inx and iny
    #     except:
    #         return False


class FocusedWidget(FocusBehavior, ThemeWidget):
    """
    Clase base para widgets que necesitan recibir el foco
    **Attributes:**

    **FocusBehavior Derived:**
    - **Attributes:**
        - focus (bool): define si la instancia tiene el foco.
        - focused (bool): alias de focus. Obsoleto, NO USAR.
        - focus_next y previus (ObjectProperty): Guarda el proximo widget a recibir el foco. Si es None no se cambia el foco.
    """
    actual_focus = None

    def __init__(self, transparent=None, flat=None, container=None,**kwargs):
        FocusBehavior.__init__(self, **kwargs)
        ThemeWidget.__init__(self, transparent=transparent, flat=flat, container=container, **kwargs)
        pass

    def on_focus(self, instance, value, *largs):
        # print(f'FocusedWidget.on_focus {self.uid}-{value}')
        if value:
            FocusedWidget.actual_focus = self
        else:
            FocusedWidget.actual_focus = None
        return False


class FrameUnfocused(ThemeWidget):
    """
    Cuadro base para crear widgets sin foco. Ofrece el gráfico del fondo y borde.
    """

    def __init__(self, transparent=None, flat=None, container=None, radius=None, draw_borders=(True,)*4, **kwargs):
        """
        Constuctor of the class
        **Parameters:**
        **Keyword arguments:**
        - radius (list float): Denife radios diferentes para cada vertice
        - draw_borders (list bool):  Define si se dibujan los bordes (l, t, r, b)
        - transparent (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        - flat (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        """
        ThemeWidget.__init__(self, transparent, flat, container=container, **kwargs)
        # Canvas ---------------------------------------------
        with self.canvas.before:
            if not self.transparent: self.graphic_face = GFace(self, radius=radius)
            self.graphic_border = GBorder(self, radius=radius, draw_borders=draw_borders)
        # with self.canvas.after:


class FrameFocused(FocusedWidget, HotlightEventDispatcher):
    """
    Cuadro base para crear widgets con foco. Ofrece el gráfico del fondo, borde, resaltado de foco y resaltado de hotlight.
    """

    def __init__(self, transparent=None, flat=None, container=None, hotlight=True, radius=None, draw_borders=(True,)*4, **kwargs):
        """
        Constuctor of the class
        **Parameters:**
        **Keyword arguments:**
        - radius (list float): Denife radios diferentes para cada vertice
        - draw_borders (list bool):  Define si se dibujan los bordes (l, t, r, b)
        - transparent (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        - flat (bool)None: Definida en ThemeableBehavior. Si es None asigna el valor del tema.
        """
        HotlightEventDispatcher.__init__(self)
        FocusedWidget.__init__(self, transparent=transparent, flat=flat, container=container, **kwargs)
        # Canvas ---------------------------------------------
        with self.canvas.before:
            if not self.transparent and not self.flat: self.graphic_face = GFace(self, radius=radius)
        with self.canvas.after:
            if not self.flat: self.graphic_border = GBorder(self, radius=radius, draw_borders=draw_borders)
            self.graphic_focus = GFocus(self, radius=radius, draw_borders=draw_borders)
            if hotlight: self.graphic_hotlight = GHotLight(self, radius=radius)


    # def keyboard_on_key_down(self, windows, keycode, text, modifiers):
    #     self._special_key = modifiers
    #
    # def keyboard_on_key_up(self, window, keycode):
    #     # FocusBehavior.keyboard_on_key_up(self, window, keycode)
    #     # print("keyboard Base Widget")
    #     ne = None
    #     # if keycode[0] in [274, 275]:  # Flechas
    #     #     ne = self.get_focus_next()
    #     # elif keycode[0] in [273, 276]:  # Flechas
    #     #     ne = self.get_focus_previous()
    #     if keycode[0] in [9] and not ('shift' in self._special_key):
    #         ne = self.get_focus_next()
    #     elif keycode[0] in [9] and 'shift' in self._special_key:
    #         ne = self.get_focus_previous()
    #     if ne:
    #         ne.focus = True
    #         if isinstance(ne, FocusedWidget):
    #             ne.widget_graphic.state = 'focused'
    #         #             ne.widget_graphic.color_border.rgba = self.theme.colors['focus_border']
    #         x, y = window.window.mouse_pos
    #         # self._update_state()
    #         return True

