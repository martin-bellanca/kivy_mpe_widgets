#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wg_markdown
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
Created on 12/09/2024
@author: mpbe
Note: Widgets the markdown package
"""

# imports del sistema -------------------------------------------------------
from enum import Enum

class MD_LINE_TYPE(Enum):
    TEXT = 0
    TITLE = 1
    HEAD_TITLE = 2
    UNDERLINE_TITLE = 3
    SEPARATOR = 4
    LIST = 5
    ORDER_LIST = 6
    TASK = 7
    TODO = 8
    TABLE = 9
    BLOCKQUOTE = 10
    IMAGEN = 11
    CODE = 12
    START_CODE = 13
    END_CODE = 14

    # Expresiones regulares para detectar diferentes tipos de párrafos
class TYPE_PATTERNS ():
    table = r'^\|.*\|$'  # Para detectar cualquier fila de una tabla
    list = r'^\s*- [^\[].*'  # Para listas regulares  ^\s*[-*+]\s+.*
    ordered_list = r'^\d{1,2}\.\s.+$'  # Para listas numeradas
    task = r'^\s*-\s\[[x\s]\].*'  # Para listas de tareas (checkbox)  ^\s*[-*+] \[.\]\s+.*
    todo = r'^\s*-\[[xo>\-\s].*'  # Para tareas tipo ToDo    ^\s*-\[\s\]\s+.*
    title = r'^#{1,6}\s+.*$'  # Para títulos con #
    underlined_title = r'^===[=\s]*$'  # Para títulos subrayados con ===   ^.*\n=+$
    separator = r'^---[-\s]*$'  # Para separador horizontal (linea horizontal)
    image = r'^!\[.*?\]\(.*?\)$'  # Imagen

    def get_mu_widget(self):
        return (MDTextLabel,  # TEXT
                MDTextLabel,  # TITLE
                MDTextLabel,  # HEAD_TITLE      MDHeadLabel
                MDSeparatorLabel,  # UNDERLINE_TITLE
                MDSeparatorLabel,  # SEPARATOR
                MDTextLabel,  # LIST
                MDTextLabel,  # ORDER_LIST
                MDTaskLabel,  # TASK            MDTaskLabel
                MDToDoLabel,  # TODO            MDToDoLabel
                MDTableLabel,  # TABLE
                MDBlockQuoteLabel,  # BLOCKQUOTE      MDBlockQuoteLabel
                MDImagenLabel,  # IMAGEN          MDImageLabel
                MDCodeLabel,  # CODE            MDCodeLabel
                MDCodeLabel,  # START_CODE      MDCodeLabel
                MDCodeLabel,  # END_CODE        MDCodeLabel
                )[self.value]


    @classmethod
    def get_name_list(cls):
        return [member.name for member in cls]

    @classmethod
    def get_value_list(cls):
        return [member.value for member in cls]
