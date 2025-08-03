#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_editors.py
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
Created on 04/08/2024
@author: mpbe
'''

# imports del sistema -------------------------------------------------------
from enum import Enum
# helpers_mpbe --------------------------------------------------------------
from helpers_mpbe.python import compose_dict, compose, check_list
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window, WindowBase
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import BooleanProperty, StringProperty, OptionProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import FrameUnfocused, FrameFocused
from kivy_mpbe_widgets.wg_markdown.md_doc_line_widgets import *
from kivy_mpbe_widgets.wg_markdown.md_document import MDDocument
from kivy_mpbe_widgets.wg_markdown import MD_LINE_TYPE
from kivy_mpbe_widgets.wg_markdown.md_labels import MDTextLabel, MDTableLabel, MDSeparatorLabel
from kivy_mpbe_widgets.wg_markdown.md_labels import BaseMDLabel, MDCodeLabel, MDHeadLabel, MDToDoLabel, MDTaskLabel, MDImageLabel
from kivy_mpbe_widgets.wg_markdown.md_document import MDLine
# from kivy_dkw.wg_markdown.render_markdown_to_widgets import render_line_markdown_to_widget

# Define el archivo KV en un string
kv = """
<MDDocumentLineEditor>:
    size_hint_y: None
    
    canvas:
        # Dibuja lineas si 'highlight' es True, dibujar la línea superior
        Color:
            rgba: self._hotlight_color if self.hotlight else (1, 1, 1, 0)  # Fondo verde si tiene foco
        Line:
            width: 1
            points: self.x, self.top-1, self.right, self.top-1
        Line:
            width: 1
            points: self.x, self.y+1, self.right, self.y+1
    
        # Dibuja lineas si 'focused' es True, dibujar la línea superior
        Color:
            rgba: self._focused_color if self.focused else (1, 1, 1, 0)  # Fondo verde si tiene foco
        Line:
            width: 1
            points: self.x, self.top, self.right, self.top
        Line:
            width: 1
            points: self.x, self.y, self.right, self.y
    
"""
Builder.load_string(kv)



# AGREGAR VARIABLE PARA INDICAR FOCO QUE PUEDA MOVERSE CON FLECHAS Y TAB FUERA DE EDICION (hightlight)
class MDDocumentLineEditor(BoxLayout, ThemableBehavior):
    line = ObjectProperty(baseclass=MDLine, defaultvalue=MDLine(md_text='', prev_line=None, next_line=None))
    num_line = NumericProperty(defaultvalue=0)  # Numero de la linea en la lista
    hidden_line = BooleanProperty(defaultvalue=False)  # Indica si el renglon no es visible en el arbol (nodo padre cerrado)
    hotlight = BooleanProperty(defaultvalue=False)  # indica la linea que tiene el cursor ensima
    focused = BooleanProperty(defaultvalue=False)  # indica si la linea en modo render es linea actual para edición

    def __init__(self, mdline, **kwargs):
        """
        Keyword arguments:
            show_number_line (bool): muestra el numero de linea
            show_tree_hook (bool): muestra el arbol del documento
            show_info_bar (bool): muestra la barra de informacion
        """


        BoxLayout.__init__(self, orientation='horizontal')
        ThemableBehavior.__init__(self)
        # colors -----------------------------------------
        self._hotlight_color = self.theme.colors['hotlight_border']
        self._focused_color = self.theme.colors['focus_border']
        # line -------------------------------------------
        self.line = compose(mdline, MDLine, False)
        self.line.bind(md_text=self.on_line_md_text)
        self.line.bind(type=self.on_line_type)
        # Drag Hook --------------------------------------
        self.wg_drag_hook = MDDLDrag()
        self.add_widget(self.wg_drag_hook)
        # Number Line ------------------------------------
        sw = compose_dict(kwargs, 'show_number_line', bool, True)
        nl = compose_dict(kwargs, 'num_line', int, 0)
        if sw:
            self.wg_number_line = MDDLNumberLine(text=f"{nl:04d}")
            self.add_widget(self.wg_number_line)
            self.num_line = nl
        else:
            self.wg_number_line = None
        # Tree Hook --------------------------------------
        sw = compose_dict(kwargs, 'show_tree_hook', bool, False)
        if sw:
            self.wg_tree_hook = MDDLTree_hook()
            self.add_widget(self.wg_tree_hook)
        else:
            self.wg_tree_hook = None
        # Info Bar ---------------------------------------
        sw = compose_dict(kwargs, 'show_info_bar', bool, False)
        if sw:
            self.wg_info_bar = MDDLInfoBar()
            self.add_widget(self.wg_info_bar)
        else:
            self.wg_info_bar = None
        # Espacio ----------------------------------------
        self.wg_space = MDDLSpace()
        self.add_widget(self.wg_space)
        # Line Editor ------------------------------------
        self.wg_line_editor = MDLineEditor(line=self.line, non_focus=True)
        self.add_widget(self.wg_line_editor)
        self.wg_line_editor.bind(size=self.on_resize_self)
        # Actualiza la Altura ----------------------------
        self._update_height()
        # Eventos ----------------------------------------
        self.wg_line_editor.bind(mode_editor=self.on_mode_editor)
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)

    # Properties -----------------------------------------------
    def _set_md_text(self, md_text):
        '''
        Notas:
            -self.line y self.active_label se actualizan de on_txt_change de self.md_editor
        '''
        # print('MDDocumentLineEditor->on_line')
        self.line.md_text = md_text
        # self.md_editor.text = md_text
        # self.active_label.md_text = md_text
        # self.line.md_text = md_text
    def _get_md_text(self):
        return self.line.md_text
    md_text = property(_get_md_text, _set_md_text)

    def _set_type(self, type):
        self.line.type = type
    def _get_type(self):
        return self.line.type
    type = property(_get_type, _set_type)

    def _set_mode_editor(self, value):
        self.wg_line_editor.mode_editor = value
    def _get_mode_editor(self):
        return self.wg_line_editor.mode_editor
    mode_editor = property(_get_mode_editor, _set_mode_editor)

    # Private Functions ----------------------------------------
    def _update_height(self):
        if self.wg_line_editor:
            self.height = self.wg_line_editor.height
            self.wg_drag_hook.height = self.wg_line_editor.height
            if self.wg_number_line:
                self.wg_number_line.height = self.wg_line_editor.height
            if self.wg_tree_hook:
                self.wg_tree_hook.height = self.wg_line_editor.height
            if self.wg_info_bar:
                self.wg_info_bar.height = self.wg_line_editor.height
            self.wg_space.height = self.wg_line_editor.height
        else:
            self.height = 16

    # Public Funtions ------------------------------------------
    def collide_point(self, x, y):  # on windows coordinates
        try:
            # Check the position of the point
            # bpx, bpy = self.to_window(self.pos[0], self.pos[1], True)
            bpx, bpy = self.to_window(self.pos[0], self.pos[1], True)
            bwidth, bheight = self.size
            # Direction X
            bpw = bpx + bwidth
            inx = True if bpx <= x <= bpw else False
            # Direction Y
            bph = bpy + bheight
            iny = True if bpy <= y <= bph else False
            # Collide
            return inx and iny
        except:
            return False

    def show_number_line(self, value:bool, number:int):
        if value and not self.wg_number_line:  # muestra
            self.wg_number_line = MDDLNumberLine(text=f"{self.num_line:04d}")
            self.add_widget(self.wg_number_line, index=1)
        elif not value and self.wg_number_line:  # oculta
            self.remove_widget(self.wg_number_line)
            self.wg_number_line = None

    def show_tree_hook(self, value: bool):
        if value and not self.wg_tree_hook:  # muestra
            self.wg_tree_hook = MDDLTree_hook()
            self.add_widget(self.wg_tree_hook, index=2)
        elif not value and self.wg_tree_hook:  # oculta
            self.remove_widget(self.wg_tree_hook)
            self.wg_tree_hook = None

    def show_info_bar(self, value: bool):
        if value and not self.wg_info_bar:  # muestra
            self.wg_info_bar = MDDLInfoBar()
            self.add_widget(self.wg_info_bar, index=2)
        elif not value and self.wg_info_bar:  # oculta
            self.remove_widget(self.wg_info_bar)
            self.wg_info_bar = None

    # Funtions events ---------------------------------------------------
    def on_resize_self(self, instance, value):
        self._update_height()

    def on_num_line(self, instance, value):
        self.num_line = value
        if self.wg_number_line:
            self.wg_number_line.text = f"{value:04d}"

    def on_line(self, instance, value):
        # print('MDDocumentLineEditor->on_line')
        pass

    def on_line_type(self, instance, value):
        # print('MDDocumentLineEditor->on_line_type')
        pass

    def on_line_md_text(self, instance, value):
        # print('MDDocumentLineEditor->on_line_md_text')
        pass

    def on_mouse_move(self, instance, mp):
        # print("MDDocumentLineEditor->on_mouse_move")
        if self.collide_point(mp[0], mp[1]):
            self.hotlight = True
        else:
            self.hotlight = False

    def on_mode_editor(self, instance, value):
        # print("MDDocumentLineEditor->on_mode_editor")
        if value:
            self.focused = value


class MDDocumentEditor(FrameFocused):  # , FocusBehavior
    # markdown_text = StringProperty()
    # usar listado de lineas

    # AGREGAR TAMBIEN SEGUIMIENTO DEL TECLADO PARA MOVER EL FOCUS CON LAS FLECHAS
    md_document = ObjectProperty(defaultvalue=None)

    def __init__(self, dm_document, **kwargs):
        # FocusBehavior.__init__(self, **kwargs)
        self.scroll = ScrollView(size_hint=(1, 1), size=(400, 600))
        super(MDDocumentEditor, self).__init__(container=self.scroll, radius=(0,0,0,0), hotlight=False,  **kwargs)
        self.graphic_face._color.rgba = self.theme.colors['panel_face']
        self.graphic_border._width = 1
        self.container_lines = BoxLayout(orientation='vertical', size_hint_y=None)
        # self.transparent = True

        self.container_lines.bind(minimum_height=self.container_lines.setter('height'))
        self.scroll.add_widget(self.container_lines)
        # self.add_widget(self.scroll)
        self.md_document = dm_document
        # self.populate_md_editor()
        self._id_focus = -1  # Guarda el ID de la linea que tiene el foco
        # self.widget_focus = None  # widget que tiene el foco a nivel App
        # Window.bind(on_key_up=self._on_keyboard_up)
        Window.bind(on_key_down=self._on_keyboard_down)
        Clock.schedule_once(self.update_geometry, 0.5)

    """ UI Functions ------------------------------------------------"""
    def update_geometry(self, dt=0):
        # super().update_geometry()
        self.scroll.center = self.center
        pd = (self.theme.geometry['padding'] + 2) * 2
        self.scroll.size = (xx-pd for xx in self.size)

    def redraw(self, instance, args):
        super().redraw(instance, args)
        self.update_geometry()


    # Privates -------------------------------------------------------------
    def _numl_to_index(self, num_line):
        return len(self.container_lines.children) - num_line

    def _index_to_numl(self, index):
        return len(self.container_lines.children) - index

    def _index_mdline_to_index_mdeditor(self, index):
        return len(self.container_lines.children) - index - 1

    def _index_mdeditor_to_index_mdline(self, index):
        return len(self.container_lines.children) - index - 1

    def _update_scroll_pos(self, md_line_ed):
        """Actualiza la posicion del scroll a md_line_ed"""
        if self.scroll.height < self.container_lines.height:
            self.scroll.scroll_to(md_line_ed)

    # Line manipulation functions ------------------------------------------
    def populate_md_editor(self):
        '''Limpia el editor y agrega las md_line de md_document'''
        self.container_lines.clear_widgets()
        if self.md_document:
            num_line = 0
            for line in self.md_document.md_lines:
                num_line += 1
                eline = MDDocumentLineEditor(mdline=line, num_line=num_line, show_info_bar=False, show_tree_hook=False)
                eline.bind(focused=self.on_line_focused)
                self.container_lines.add_widget(eline)

    def append_line(self, md_txt_line):

        num_line = len(self.container_lines.children)
        new_line = self.md_document.append_line(md_txt_line)
        eline = MDDocumentLineEditor(mdline=new_line, num_line=num_line, show_info_bar=False, show_tree_hook=False)
        eline.bind(focused=self.on_line_focused)
        self.container_lines.add_widget(eline)
        return eline

    def append_lines(self, md_txt_lines):
        check_list(md_txt_lines, str, False)
        for txt_line in md_txt_lines:
            self.append_line(txt_line)

    def insert_line(self, num_line, md_txt_line):
        new_line = self.md_document.insert_line(num_line, md_txt_line)
        eline = MDDocumentLineEditor(mdline=new_line, num_line=num_line, show_info_bar=False, show_tree_hook=False)
        eline.bind(focused=self.on_line_focused)
        self.container_lines.add_widget(eline, index=self._numl_to_index(num_line))
        self.update_num_line(num_line_init=num_line)
        self._update_scroll_pos(eline)  # Actualiza la posicion del scroll

    def insert_lines(self, num_line, md_txt_lines):
        pass
        # TODO: Codificar

    def remove_line(self, ed_line):
        self.md_document.remove_line(ed_line.line)
        self.container_lines.remove_widget(ed_line)
        self.update_num_line(num_line_init=ed_line.num_line)

    def remove_lines(self, ed_lines):  # Lista de objetos MDDocumentLines a Remover
        for line in ed_lines:
            self.remove_line(line)

    def clear_lines(self):
        self._lines_doc = []
        self.container_lines.clear_widgets()

    def move_line_up(self, ed_line):
        self.md_document.move_line_up(ed_line.line)
        ch = self.container_lines.children
        id = ch.index(ed_line)
        ch[id], ch[id + 1] = ch[id + 1], ch[id]
        # Actualiza el nro de lines y foco
        ch[id+1].num_line -= 1
        ch[id].num_line += 1
        self._id_focus += 1
        self._update_scroll_pos(ed_line)  # Actualiza la posicion del scroll

    def move_up_lines(self, ed_line, cant_lines):
        """
        Parameters:
            ed_line (MDEditorLine): Primer linea de la seleccion
            cant_lines (int): Cantidad de lineas selccionadas debajo de ed_line.
        """
        # TODO: Sin Codificar
        pass



    def move_line_down(self, ed_line):
        self.md_document.move_line_down(ed_line.line)
        ch = self.container_lines.children
        id = ch.index(ed_line)
        ch[id], ch[id - 1] = ch[id - 1], ch[id]
        # Actualiza el nro de lines y foco
        ch[id].num_line -= 1
        ch[id-1].num_line += 1
        self._id_focus -= 1
        self._update_scroll_pos(ed_line)  # Actualiza la posicion del scroll

    def move_down_lines(self, ed_line, cant_lines):
        """
        Parameters:
            ed_line (MDEditorLine): Primer linea de la seleccion
            cant_lines (int): Cantidad de lineas selccionadas debajo de ed_line.
        """
        # TODO: Sin Codificar
        pass

    def move_line_to(self, num_line, ed_line):
        '''Mueve ed_line a la poscion num_line'''
        # TODO: Sin Codificar
        pass


    def move_lines_to(self, num_line, ed_line, cant_lines):
        """
        Parameters:
            num_line (int): Numero de linea destino de la seleccion
            ed_line (MDEditorLine): Primer linea de la seleccion
            cant_lines (int): Cantidad de lineas selccionadas debajo de ed_line.
        """
        # TODO: Sin Codificar
        pass


    # Line Functions -----------------------------------------------------
    def focus_line(self):
        return self.container_lines.children[self._id_focus]

    def next_line(self, num_line, hidden=True):
        index = self._numl_to_index(num_line)
        if not hidden:
            return self._lines_doc[index - 1]
        else:
            for ii in range(index-1, -1, -1):
                if not self.container_lines.children[ii].hidden_line:
                    return self.container_lines.children[ii]
            return self.container_lines.children[0]

    def previus_line(self, num_line, hidden=True):
        index = self._numl_to_index(num_line)
        if not hidden:
            return self.container_lines.children[index + 1]
        else:
            for ii in range(index+1, len(self.container_lines.children)):
                if not self.container_lines.children[ii].hidden_line:
                    return self.container_lines.children[ii]
            return self.container_lines.children[len(self.container_lines.children) - 1]

    def update_num_line(self, num_line_init):
        '''Actuliza el indice y numero de linea desde index al final'''
        cl = len(self.container_lines.children)
        for nl in range(num_line_init, cl+1):
        # for lineed in self._lines_editor[index:]:
            id = cl - nl
            self.container_lines.children[id].num_line = nl

    # Private Functions -------------------------------------------------
    pass

    # Funtions events ---------------------------------------------------
    def on_line_doc_type(self, instance, value):
        pass

    # def on_markdown_text(self, instance, markdown_text):  # OBSOLETO. Esto se hace en MDDocument
    #     self.container.clear_widgets()
    #     widgets = render_markdown_to_widgets(markdown_text)
    #     for widget in widgets:
    #         self.container.add_widget(widget)

    def on_line_focused(self, instance, value):
        # print("MDDocumentEditor->on_line_focused")
        if value:
            index = self._numl_to_index(instance.num_line)
            if self._id_focus > -1 and self._id_focus != index:
                self.container_lines.children[self._id_focus].focused = False
            # instance.focused = True
            # instance.focused = True
            # cl = len(self.container.children)
            self._id_focus = index
        # elif instance.index == self._id_focus:
        #     self._id_focus = -1

    # def init_cursor(self):
    #     self._lines_editor[self._id_focus].wg_line_editor.md_editor.cursor = (0, 0)

    # def _on_keyboard_down(self, window, keycode, modifier, char, special_key):
    #     "Retienen la presion de ctrl, alt, shift o meta"
    #     print(char, special_key)
    #     if keycode in [305, 306]:
    #         self._special_key = 'ctrl'
    #     elif keycode in [307, 308]:
    #         self._special_key = 'alt'
    #     elif keycode in [303, 304]:
    #         self._special_key = 'shift'
    #     elif keycode == 1073742055:
    #         self._special_key = 'meta'
    #     elif keycode == 1073741925:
    #         self._special_key = 'menu'

    def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
        print("MDDocumentEditor->_on_keyboard_down", "Codigo de Teclas", keycode, modifier)
        # Variables Internas
        if not self.focus:
            return False
        if len(self.container_lines.children) == 0:
            return False
        cursor_pos = self.container_lines.children[self._id_focus].wg_line_editor.md_editor.cursor  # Posicion del cursor actual
        in_edition = self.container_lines.children[self._id_focus].mode_editor  # TextInput actual en Edicion
        can_lines = len(self.container_lines.children)
        # Variables de Lineas
        focus_line_ed = self.container_lines.children[self._id_focus]
        previus_line_ed = self.previus_line(focus_line_ed.num_line)
        next_line_ed = self.next_line(focus_line_ed.num_line)


        # not in_edition and 'ctrl' in special_keys and 'shift' in special_keys and keycode == 273 and self._id_focus > 0:

        # Mueve la linea hacia arriba con Ctrl+Shift+Up -----------------------------------------
        if keycode == 273 and 'ctrl' in special_keys and 'shift' in special_keys and self._id_focus < can_lines-1:
            self.move_line_up(focus_line_ed)

        # Mueve la linea hacia abajo con Ctrl+Shift+Down ----------------------------------------
        elif keycode == 274 and 'ctrl' in special_keys and 'shift' in special_keys and self._id_focus > 0:
            self.move_line_down(focus_line_ed)

        # Ctrl+Up Salta al titulo anterior --------------------------------------------
        elif keycode == 273 and 'ctrl' in special_keys and self._id_focus < can_lines - 1:
            # Busca el titulo
            line = focus_line_ed.line.get_title_prev()
            id = self._index_mdline_to_index_mdeditor(self.md_document.md_lines.index(line))
            ed_line = self.container_lines.children[id]
            # Tratamiento en modo edicion
            if focus_line_ed.mode_editor == True:
                focus_line_ed.mode_editor = False
                ed_line.focused = True
                ed_line.mode_editor = True
                ed_line.wg_line_editor.md_editor.cursor = cursor_pos
            else:
                # Lleva el foco al titulo
                ed_line.focused = True
            self._update_scroll_pos(ed_line)  # Actualiza la posicion del scroll

        # Ctrl+Down Salta al titulo siguiente ----------------------------------------
        elif keycode == 274 and 'ctrl' in special_keys and self._id_focus > 0:
            # Busca el titulo
            line = focus_line_ed.line.get_title_next()
            id = self._index_mdline_to_index_mdeditor(self.md_document.md_lines.index(line))
            ed_line = self.container_lines.children[id]
            # Tratamiento en modo edicion
            if focus_line_ed.mode_editor == True:
                focus_line_ed.mode_editor = False
                ed_line.mode_editor = True
                ed_line.wg_line_editor.md_editor.cursor = cursor_pos
            # Lleva el foco al titulo
            ed_line.focused = True
            self._update_scroll_pos(ed_line)  # Actualiza la posicion del scroll


        # Deshacer ctrl+Z ---------------------------------------------------------------
        elif keycode == 122 and 'ctrl' in special_keys:
            print("MDDocumentEditor->_on_keyboard_down: DESHACER Ctrl+Z")
            pass

        # Rehacer ctrl+Y ---------------------------------------------------------------
        elif keycode == 121 and 'ctrl' in special_keys:
            print("MDDocumentEditor->_on_keyboard_down: REHACER Ctrl+Y")
            pass

        # Termina la ejecucion si esta presionada ctrl, alt, shift o meta --------------
        elif 'ctrl' in special_keys or 'alt' in special_keys or 'shift' in special_keys or 'meta' in special_keys:
            return False


        # Flecha Arriba ----------------------------------------------------------------
        elif keycode == 273:  # Flecha Arriba --------------------------------------------
            previus_line_ed.focused = True
            if in_edition:
                focus_line_ed.wg_line_editor.mode_editor = False
                previus_line_ed.wg_line_editor.mode_editor = True
                previus_line_ed.wg_line_editor.md_editor.cursor = cursor_pos
            self._update_scroll_pos(previus_line_ed)
            return True
        # Flecha abajo -----------------------------------------------------------------
        elif keycode in [274]:  # Flecha abajo -----------------------------------------
            next_line_ed.focused = True
            if in_edition:
                focus_line_ed.wg_line_editor.mode_editor = False
                next_line_ed.wg_line_editor.mode_editor = True
                next_line_ed.wg_line_editor.md_editor.cursor = cursor_pos
            self._update_scroll_pos(next_line_ed)
            return True
        # Return y Enter de Teclado Numerico --------------------------------------------
        elif keycode in [13, 271]:  # Return y Enter de Teclado Numerico ----------------
            if not in_edition:
                focus_line_ed.mode_editor = True
            else:
                txt_focus = focus_line_ed.wg_line_editor.md_text[:cursor_pos[0]]
                txt_new_line = focus_line_ed.wg_line_editor.md_text[cursor_pos[0]:]
                focus_line_ed.md_text = txt_focus
                focus_line_ed.mode_editor = False
                focus_line_ed.focused = False
                if len(self.container_lines.children) > focus_line_ed.num_line:
                    self.insert_line(focus_line_ed.num_line, txt_new_line)  # MDLine next y prev se actualiza en insert
                else:
                    eline = self.append_line(txt_new_line)
                    print(eline.md_text, self._id_focus)
                    # self._id_focus += 1
                    self.container_lines.children[0].focused = True  # NO FUNCIONA
                self.container_lines.children[self._id_focus].mode_editor = True
                def init_cursor(dt):
                    self.container_lines.children[self._id_focus].wg_line_editor.md_editor.cursor = (0, 0)
                Clock.schedule_once(init_cursor, 0.1)
                self._update_scroll_pos(self.container_lines.children[self._id_focus])
            return True
        # F2 ------------------------------------------------------------------------------
        elif keycode == 283:  # F2 --------------------------------------------------------
            if not in_edition:
                focus_line_ed.mode_editor = True
                # focus_line.wg_line_editor.md_editor.cursor = (0, 0)
            else:
                focus_line_ed.mode_editor = False
            return True
        # Backspace -----------------------------------------------------------------------
        elif keycode == 8:  # Backspace ---------------------------------------------------
            index = self._numl_to_index(focus_line_ed.num_line)
            if in_edition and index < can_lines-1 and cursor_pos == (0, 0):  # ESTA EN MODO EDICION
                txt_focus = focus_line_ed.md_text
                self.remove_line(focus_line_ed)
                self._id_focus += 1
                cursor_pos = len(previus_line_ed.md_text)
                previus_line_ed.md_text += txt_focus
                previus_line_ed.wg_line_editor.mode_editor = True
                previus_line_ed.wg_line_editor.md_editor.cursor = (cursor_pos, 0)
                return True
            elif not in_edition:  # NO ESTA EN MODO EDICION
                self.remove_line(focus_line_ed)
                if self._id_focus > 0:
                    next_line_ed.focused = True
                else:
                    self._id_focus += 1
                    previus_line_ed.focused = True
        # Delete -------------------------------------------------------------------------
        elif keycode == 127:  # Delete ---------------------------------------------------
            ltxt = len(focus_line_ed.md_text)
            if in_edition and self._id_focus > 0 and cursor_pos==(ltxt, 0):
                txt_next = next_line_ed.md_text
                self.remove_line(next_line_ed)
                focus_line_ed.md_text += txt_next
                focus_line_ed.wg_line_editor.md_editor.cursor = (ltxt, 0)
                self._id_focus -= 1
                return True
            elif not in_edition:  # NO ESTA EN MODO EDICION
                self.remove_line(focus_line_ed)
                if self._id_focus < can_lines:
                    next_line_ed.focused = True
                else:
                    self._id_focus -= 1
                    previus_line_ed.focused = True
        # Flecha Izquierda ---------------------------------------------------------------
        elif keycode == 276:  # Flecha Izquierda -----------------------------------------
            index = self._numl_to_index(focus_line_ed.num_line)
            if in_edition and index < can_lines-1 and cursor_pos == (0, 0):  # ESTA EN MODO EDICION
                focus_line_ed.wg_line_editor.mode_editor = False
                previus_line_ed.wg_line_editor.mode_editor = True
                cursor_pos = len(previus_line_ed.md_text)
                previus_line_ed.wg_line_editor.md_editor.cursor = (cursor_pos, 0)
                return True
        # Flecha Derecha -----------------------------------------------------------------
        elif keycode == 275:  # Flecha Derecha -------------------------------------------
            ltxt = len(focus_line_ed.md_text)
            if in_edition and self._id_focus > 0 and cursor_pos == (ltxt, 0):
                focus_line_ed.wg_line_editor.mode_editor = False
                next_line_ed.wg_line_editor.mode_editor = True
                next_line_ed.wg_line_editor.md_editor.cursor = (0, 0)
                return True

    # Properties events ------------------------------------------------
    def on_md_document(self, instance, value):
        self.md_document = compose(value, MDDocument, True, True, None)
        self.populate_md_editor()
