#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  behaviors.py
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
from kivy.uix.image import Image
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_font_icons.font_icon import FontIcon
# helpers_mpbe --------------------------------------------------------------
from helpers_mpbe.python import compose_dict, check_list, compose

# Labels Behaviors --------------------------------------------------
# -------------------------------------------------------------------
class ImageBehavior():  # (BaseImageBehavior)
    """Behavior class. Define comportamiento básico para componentes que utilizan imagenes."""
    def __init__(self, image_source, image_fit_mode='scale-down'):
        """
        Class Constructor
        **Parameters:**
        - image_source: str - Path hacia la imagen
        - image_fit_mode: ('scale-down', 'fill', 'contain', 'cover')
        **Keyword arguments:**
        """
        source = compose(image_source, str, False)
        fit = compose(image_fit_mode, str, False)
        self._image = Image(source=source, fit_mode=fit, size_hint=(None, None))

    def _get_source(self):
        return self._image.source
    def _set_source(self, source:str):
        self._image.source = source
    image_source = property(_get_source, _set_source)

    def _get_fit_mode(self):
        return self._image.fit_mode
    def _set_fit_mode(self, value:str):
        """
        Determine how the image should be resized to fit inside the widget box.
        Available options:
            - "scale-down": the image will be scaled down to fit inside the widget
            - "fill": the image is stretched to fill the widget
            - "contain": the image is resized to fit inside the widget box, maintaining its aspect ratio
            - "cover": the image will be stretched horizontally or vertically to fill the widget box, maintaining its aspect ratio.
        """
        if value in ('scale-down', 'fill', 'contain', 'cover'):
            self._image.fit_mode = value
        else:
            raise ValueError('%s is not available value') % (value)
    image_fit_mode = property(_get_fit_mode, _set_fit_mode)


class IconBehavior():  # (BaseImageBehavior)
    '''Behavior class. Define comportamiento básico para componentes que utilizan iconos de fuentes.'''
    def __init__(self, icon_name, icon_size=24, icon_family='materialdesignicons-webfont', **kwargs):
        """Constructor class.
        **Parameters:**
        - icon_name: str - Nombre del icono de la lista de iconos de fuentes del tema
        - icon_size: int - tamaño del icono
        - icon_family: str - Nombre del conjunto de iconos (nombre de la fuente) ['materialdesignicons-webfont']
        **Keyword arguments:**
        """
        name = compose(icon_name, str, None)
        size = compose(icon_size, int, None, True, 24)
        family = compose(icon_family, str, None, True, 'materialdesignicons-webfont')
        self._icon = FontIcon(icon_name=name, icon_size=size, icon_family=family)  # , size_hint=(1,1)

    def _get_name(self):
        return self._icon.icon_name
    def _set_name(self, icon_name:str):
        self._icon.icon_name = icon_name
    icon_name = property(_get_name, _set_name)

    def _get_size(self):
        return self._icon.icon_size
    def _set_size(self, icon_size:int):
        self._icon.icon_size = icon_size
    icon_size = property(_get_size, _set_size)

    def _get_family(self):
        return self._icon.icon_family
    def _set_family(self, icon_family:str):
        self._icon.icon_family = icon_family
    icon_family = property(_get_family, _set_family)

    def _get_color(self):
        return self._icon.color
    def _set_color(self, rgba_color:dict):
        self._icon.color = rgba_color
    icon_color = property(_get_color, _set_color)

    def _get_texture_size(self):
        return self._icon.texture_size
    icon_texture_size = property(_get_texture_size)


class TextLabelBehavior():
    '''Behavior class. Define comportamiento básico para componentes que utilizan la clase TextLabel.'''
    def __init__(self, text, text_style='body', text_halign='left', text_valign='center', **kwargs):
        """
        Constructor class.
        **Parameters:**
        - text (str): Texto a mostrar
        - text_style (str): Estilo del Texto. ["title", "subhead", "body", "body_bold", "caption", "button", "error", "secundary", "hint"]. Default "body"
        - text_halign (str): <KVLabel> auto,left, center, right
        - text_valign (str): <KVLabel> top, middle, bottom
        **Keyword arguments:**
        """
        text = compose(text, str, False)
        text_style = compose(text_style, str, False)
        text_halign = compose(text_halign, str, False)
        text_valign = compose(text_valign, str, False)
        self._text_label = TextLabel(text=text, style=text_style, halign=text_halign, valign=text_valign)

    def _set_text(self, value):
        self._text_label.text = value
    def _get_text(self):
        return self._text_label.text
    text = property(_get_text, _set_text)

    def _set_text_style(self, value):
        self._text_label.style = value
    def _get_text_style(self):
        return self._text_label.style
    text_style = property(_get_text_style, _set_text_style)

    def _set_text_halign(self, value):
        self._text_label.halign = value
    def _get_text_halign(self):
        return self._text_label.halign
    text_halign = property(_get_text_halign, _set_text_halign)

    def _set_text_valign(self, value):
        self._text_label.valign = value
    def _get_text_valign(self):
        return self._text_label.valign
    text_valign = property(_get_text_valign, _set_text_valign)


