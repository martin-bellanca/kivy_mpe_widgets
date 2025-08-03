#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  panels.py
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


"""
Created on 27/08/2023
@author: mpbe
"""


# imports del sistema -------------------------------------------------------
import kivy.uix.widget
# helpers imports ----------------------------------------------------------
from helpers_mpbe.python import compose
# Kivy imports -------------------------------------------------------------
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.properties import StringProperty
from kivy.properties import OptionProperty, ObjectProperty, VariableListProperty, NumericProperty, BooleanProperty
from kivy.graphics import InstructionGroup, Color

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.base_widgets import FrameUnfocused
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.graphics.panel_graphics import TitleGraphic

# Builder.load_file(kivy_mpbe_widgets.DIR_BASE+'/wg_panels/panels.kv')


class _PanelBase(FrameUnfocused):
    """
    Panel base para la creacion de paneles
    """
    padding = VariableListProperty(0)
    spacing = NumericProperty(0)

    def __init__(self, container, transparent=None, flat=None, padding=None, spacing=None):
        FrameUnfocused.__init__(self, transparent=transparent, flat=flat, container=container)
        self.graphic_face._color.rgba = self.theme.colors['panel_face']
        self.padding = self.theme.geometry['padding'] if padding == None else padding
        self.spacing = self.theme.geometry['spacing'] if spacing == None else spacing
        pass

    def on_padding(self, instance, value):
        self.container.padding = value

    def on_spacing(self, instance, value):
        self.container.spacing = value


class BoxPanel(_PanelBase):
    """
        Cuadro para agrupar componentes.
        Properties:
            container: Contenedor de Widgets
            orientation: Orientacion del container ['vertical', 'orizontal']
            padding: Separacion de los Widgets respecto al perimetro del container.
                        Puder ser: un entero, [sep_vert, sep_hor] o [sep_izq, sep_sup, sep_der , sep_inf]
            spacing: Separacion entre Widgets
    """
    orientation = OptionProperty('vertical', options=['vertical', 'horizontal'])

    def __init__(self, orientation='vertical', transparent=None, flat=None, padding=None, spacing=None):
        _PanelBase.__init__(self, transparent=transparent, flat=flat, container=BoxLayout(orientation=orientation),
                            padding=padding, spacing=spacing)
        self.orientation = orientation

    def on_orientation(self, instance, value):
        self.container.orientation = value


class GridPanel(_PanelBase):
    """
        Grilla para agrupar componentes.
        Properties:
            cols (int): Cantidad de columnas
            rows (int): Cantidad de filas
            row_default_height (int): Altura por defecto de la fila
            row_force_default (bool): Fuerza la altura de las celdas al valor por defecto
            col_default_width (int): Ancho por defecto de la columna
            col_force_default (bool): Fuerza el ancho de las columnas al valor por defecto
            orientation: Orientacion del container ['vertical', 'orizontal']
            padding: Separacion de los Widgets respecto al perimetro del container.
                        Puder ser: un entero, [sep_vert, sep_hor] o [sep_izq, sep_sup, sep_der , sep_inf]
            spacing: Separacion entre Widgets dentro de la celda.
                        Puder ser: un entero, [sep_vert, sep_hor] o [sep_izq, sep_sup, sep_der , sep_inf]
    """
    cols = NumericProperty(1)
    rows = NumericProperty(None)
    row_default_height = NumericProperty(14)
    row_force_default = BooleanProperty(False)
    col_default_width = NumericProperty (50)
    col_force_default = BooleanProperty(False)

    def __init__(self, rows=None, cols=None, row_default_height=0, row_force_default=False,
                 col_default_width=0, col_force_default=False,
                 transparent=None, flat=None, padding=None, spacing=None):
        grly = GridLayout(rows=rows, cols=cols,
                          row_default_height=row_default_height, row_force_default=row_force_default,
                          col_default_width=col_default_width, col_force_default=col_force_default)
        _PanelBase.__init__(self, transparent=transparent, flat=flat, container=grly, padding=padding, spacing=spacing)
        self.rows = rows
        self.cols = cols
        self.row_default_height = row_default_height
        self.row_force_default = row_force_default
        self.col_default_width = col_default_width
        self.col_force_default = col_force_default

    def on_rows(self, instance, value):
        self.container.rows = value

    def on_cols(self, instance, value):
        self.container.cols = value

    def on_row_default_height(self, instance, value):
        self.container.row_default_height = value

    def on_row_force_default(self, instance, value):
        self.container.row_force_default = value

    def on_col_default_width(self, instance, value):
        self.container.col_default_width = value

    def on_col_force_default(self, instance, value):
        self.container.col_force_default = value


class StackPanel(_PanelBase):
    """
        Pila para agrupar componentes.
        Properties:
            container: Contenedor de Widgets
            orientation: Orientacion del container ['lr-tb', 'tb-lr', 'lr-bt', 'bt-lr', 'rl-tb', 'tb-rl', 'rl-bt', 'bt-rl']
            padding: Separacion de los Widgets respecto al perimetro del container.
                        Puder ser: un entero, [sep_vert, sep_hor] o [sep_izq, sep_sup, sep_der , sep_inf]
            spacing: Separacion entre Widgets
    """
    orientation = OptionProperty('lr-tb', options=['lr-tb', 'tb-lr', 'lr-bt', 'bt-lr', 'rl-tb', 'tb-rl', 'rl-bt', 'bt-rl'])

    def __init__(self, orientation='lr-tb', transparent=None, flat=None, padding=None, spacing=None):
        _PanelBase.__init__(self, transparent=transparent, flat=flat, container=StackLayout(orientation=orientation),
                            padding=padding, spacing=spacing)
        self.orientation = orientation

    def on_orientation(self, instance, value):
        self.container.orientation = value


class TitlePanel(_PanelBase):
    """
    Cuadro para agrupar componentes.
    Properties:
        title (str): Texto del titulo del cuadro
        title_align (str option): Alineacion horizontal del titlulo. "left", "center", "right"
    """
    container = ObjectProperty(None)  # Propiedad para referenciar el contenedor
    padding = VariableListProperty(0)
    spacing = NumericProperty(0)
    title = StringProperty(defaultvalue="")
    title_align = OptionProperty("left", options=["left", "center", "right"])

    def __init__(self, title, title_align='center', transparent=None, flat=None, padding=None, spacing=None):

        self._title_label = TextLabel(text=title, style='title', halign=title_align, valign='top',
                                      shorten=True, size_hint=(1, None))
        self.title = title
        self.title_align = title_align
        self.padding = self.theme.geometry['padding'] if padding == None else padding
        self.spacing = self.theme.geometry['spacing'] if spacing == None else spacing
        bl = BoxLayout(orientation='vertical', padding=padding, spacing=spacing)
        bl.add_widget(self._title_label)
        _PanelBase.__init__(self, transparent=transparent, flat=flat, container=bl,
                            padding=padding, spacing=spacing)
        rr = list(self.graphic_border._radius)
        if self.title_align == "left":
            rr[0] = 1
            self.graphic_face._radius = rr
            self.graphic_border._radius = rr
        elif self.title_align == "right":
            rr[1] = 1
            self.graphic_face._radius = rr
            self.graphic_border._radius = rr

        self.graphic_line = TitleGraphic(self)
        self.canvas.after.add(self.graphic_line)

    def on_title(self, instance, value):
        self.title = value
        self._title_label.text = value

    def on_title_align(self, instance, value):
        self.title_align = value
        self._title_label.halign = value
