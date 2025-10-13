#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_recycleview_line_editors.py
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
Created on 21/09/2025
@author: mpbe
'''

# imports del sistema -------------------------------------------------------


# helpers_mpbe --------------------------------------------------------------

# Kivy imports --------------------------------------------------------------

# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.wg_markdown.md_doc_line_widgets import MDLine
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import BaseDataDic


# Clases para Data dict -------------------------------------------------------
class DataThemed:    # Nuevo
    def __init__(self, alpha_background:float=0.0, anim:bool=False, anim_type:str="point"):
        """Define las variables del tema del widget

        Args:
            alpha_background (float, optional): _description_. Defaults to 0.0.
            anim (bool, optional): Indica si la activacion se anima. Defaults to False.
            anim_type (str, optional): Tipo de Animacion a implementar en la activación. Defaults to "point".
        """
        self.alpha_background = alpha_background
        # self.anim = anim
        # self.anim_type = anim_type
        # ESTE PAQUETE HACE FALTA?


class DataShow:    # Nuevo
    def __init__(self, show_number_line:bool=True, show_infobar:bool=False, show_tree:bool=False):
        self.number_line = show_number_line
        self.tree = show_tree
        self.infobar = show_infobar


class DataState:  # Nuevo
    def __init__(self, selectable:bool=True, selected:bool=False,
                 editable:bool=True, focused:bool=True, active:bool=False,
                 mode_editor:bool=False, cursor_pos:tuple=(0,0), hide:bool=False):
        # self.index = index              # Indice de la linea en Data. En layout.children el indice es inverso
        # self.focused = focused          # Define si el item puede tener el foco
        self.editable = editable                # Define si el item se puede editar
        self.selectable = selectable            # Define si el item se puede seleccionar
        self.selected = selected                # Define si el item esta seleccionado (puede haber muchos items selecionados)
        self.active = active                    # Define si el item esta activo
        self.mode_editor = mode_editor          # Define si esta en modo edicion
        self.editor_cursor_pos = cursor_pos     # Posicion del cursor en el editor
        self.hide = hide                        # Indica si la linea esta oculta


# Clase Data Item -------------------------------------------------------------
class DataItemLineMDD():  # Modificado

    def __init__(self, md_line:MDLine, data_themed:DataThemed, data_show:DataShow, data_state:DataState):
        """Devuelve el diccionario de MDDocumentEditor
        **Dict Parameters:**
            md_line (MDLine): Clase que guarda la información de la linea
            data_themed (DataThemed): Varialbes relacionadas con el tema guardadas en data
            data_show (DataShow): Varialbes relacionadas con la visibilidad guardadas en data
            data_state (DataState): Varialbes relacionadas con el estado del item guardadas en data
        """
        self.md_line = md_line
        self.data_themed = data_themed
        self.data_show = data_show
        self.data_state = data_state

    def to_dict(self):
        """Devuelve el diccionario de MDDocumentEditor
        **Dict Parameters:**
            index (int): De class BaseDic. Indica la posicion del item en la lista data.
            MDLine: Clase que maneja la linea en formato markdown
            active (bool): Indica si el item esta activo
            selected (bool): De class BaseDic. Indica si el item esta seleccionado
            mode_editor (bool): De class BaseDic. Indica si esta en modo edicion
            
            cursor (list): Define la posicion del cursor para la animacion
            start_anim (bool): De class BaseDic. Indica si se anima la seleccion o des-selección
            state_background (bool): De class BaseDic. Indica si se sombrea el fondo. Es para el pintado intercalado.

            show_number_line (bool): Muestra el numero de lineas
            show_tree (bool): Muestra el arbol
            show_infobar (bool): Muestra la barra de información
        """
        return {'md_line': self.md_line,
                'themed': self.data_themed, 
                'show': self.data_show,
                'state':self.data_state
                }
    