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
import kivy_dkw
from kivy_dkw.theming import ThemableBehavior
from kivy_dkw.base_widget import UnfocusedWidget
from kivy_dkw.wg_markdown import MD_LINE_TYPE
from kivy_dkw.wg_markdown.md_labels import MDTextLabel, MDTableLabel, MDSeparatorLabel
from kivy_dkw.wg_markdown.md_labels import BaseMDLabels, MDCodeLabel, MDHeadLabel, MDToDoLabel, MDTaskLabel, MDImageLabel
from kivy_dkw.wg_markdown.md_document import MDLine
# from kivy_dkw.wg_markdown.render_markdown_to_widgets import render_line_markdown_to_widget

# Define el archivo KV en un string
kv = """
<MDLineTextInput@TextInput>:
    multiline: False
    size_hint_y: None
    font_size: 14
    height: self.font_size * 2.0
    # background_color: (0, 0, 0, 0.1)

<MarkdownRowTextInputWLabel_OBSOLETO@FloatLayout>:
    size_hint_y: 1
    # height: md_label.font_size+8

    canvas.before:
        Color:
            rgba: 0.1, 0.6, 0.8, 1  # RGB + Alpha (transparencia)
        Rectangle:
            pos: self.pos
            size: self.size


<MDLineEditor>:
    size_hint_y: None
    # height: md_label.font_size+8

    # canvas.before:
    #     Color:
    #         rgba: 0.1, 0.6, 0.8, 1  # RGB + Alpha (transparencia)
    #     Rectangle:
    #         pos: self.pos
    #         size: self.size


<MDDLDrag>:
    size_hint_x: None
    width: 10
    size_hint_y: None
    canvas.before:
        # Dibuja el borde
        Color:
            rgba: 0, 0, 0, 1  # Color Negro
        Line:
            width: 1  # Grosor del borde
            rectangle: self.x, self.y, self.width, self.height
        # Dibuja el Centro
        Color:
            rgba: 0.5, 0.5, 0.5, 1
        Rectangle:
            size: (self.width-6, self.height-6)
            pos: (self.x+3, self.y+3)


<MDDLNumberLine>
    size_hint_x: None
    width: 38
    size_hint_y: None
    color: 0, 0, 0, 1
    canvas.before:
        # # Dibuja el Centro
        # Color:
        #     rgba: 0.5, 0.5, 0.5, 1
        # Rectangle:
        #     size: self.size
        #     pos: self.pos

        # Dibuja el borde
        Color:
            rgba: 0, 0, 0, 1  # Color Negro
        # Línea en el borde izquierdo
        Line:
            width: 1
            points: self.x, self.y, self.x, self.top  # Desde el fondo hasta la parte superior en el borde izquierdo

        # Línea en el borde derecho
        Line:
            points: self.right, self.y, self.right, self.top  # Desde el fondo hasta la parte superior en el borde derecho
           
    
        
<MDDLTree_hook>
    size_hint_x: None
    width: 16
    size_hint_y: None
    canvas.before:
        # # Dibuja el Centro
        # Color:
        #     rgba: 0.5, 0.5, 0.5, 1
        # Rectangle:
        #     size: self.size
        #     pos: self.pos

        # Dibuja el borde
        Color:
            rgba: 0, 0, 0, 1  # Color Negro
        # Línea en el borde izquierdo
        Line:
            width: 1
            points: self.x, self.y, self.x, self.top  # Desde el fondo hasta la parte superior en el borde izquierdo

        # Línea en el borde derecho
        Line:
            points: self.right, self.y, self.right, self.top  # Desde el fondo hasta la parte superior en el borde derecho
            
        # Line:
        #     width: 1  # Grosor del borde
        #     rectangle: self.x, self.y, self.width, self.height


<MDDLInfoBar>
    size_hint_x: None
    width: 80
    size_hint_y: None
    canvas.before:
        # # Dibuja el Centro
        # Color:
        #     rgba: 0.5, 0.5, 0.5, 1
        # Rectangle:
        #     size: self.size
        #     pos: self.pos

        # Dibuja el borde
        Color:
            rgba: 0, 0, 0, 1  # Color Negro
        Line:
            width: 1  # Grosor del borde
            rectangle: self.x, self.y, self.width, self.height


<MDDLSpace>
    size_hint_x: None
    width: 6
    size_hint_y: None


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




class MDLineTextInput(TextInput):
    def __init__(self, **kwargs):
        super(MDLineTextInput, self).__init__(**kwargs)
        self.multiline = False
        self._pairs = {
            '*': '**',
            '"': '""',
            '(': '()',
            '[': '[]',
            '{': '{}',
            '_': '__',
        }
        self._start_with = {
            '[ ': '[ ] ',
            '-[': '- [ ] ',
            '- [': '- [ ] ',
            '-x': '- [x] ',
            '[>': '[>] ',
            '[<': '[>] ',
            '[o': '[o] ',
            '[0': '[o] ',
            '[O': '[o] ',
            '[x': '[x] ',
            '[-': '[-] '
        }

    def insert_text(self, substring, from_undo=False):
        # Reemplaza el tab por 4 espacios
        if substring == '\t':  # Detectar tabulador
            substring = ' ' * 4  # Reemplazar con 4 espacios
        # Reemplaza los inicios -------------------------
        cc = self.cursor_col-1
        if -1< cc < 2: # menos de 4 caracteres
            autext = self.text[:cc+1] + substring
            if autext in self._start_with:
                new_txt = self._start_with[autext]
                if len(self.text) >= len(new_txt):
                    if self.text[:len(new_txt)] != new_txt:
                        self.do_replace_start(new_txt, autext)
                    else:
                        return super().insert_text(substring, from_undo=from_undo)
                else:
                    self.do_replace_start(new_txt, autext)
            else:
                return super().insert_text(substring, from_undo=from_undo)
        # Reemplaza los caracteres de par
        elif substring in self._pairs:
            pair = self._pairs[substring]
            self.do_insert_pair(pair, len(substring))
        else:
            return super().insert_text(substring, from_undo=from_undo)


        # AGREGAR EVENTO DE CAMBIO DE TEXTO
        return None

    def do_insert_pair(self, pair, offset):
        # Insert the pair and move cursor to middle
        cursor_pos = self.cursor_index()
        self.text = self.text[:cursor_pos] + pair + self.text[cursor_pos:]
        self.cursor = (cursor_pos + offset, 0)

    def do_replace_start(self, new_txt, old_txt):
        if new_txt[0] in self._pairs:
            cc = len(old_txt)
        else:
            cc = len(old_txt)-1
        self.text = new_txt + self.text[cc:]
        self.cursor = (len(new_txt), 0)


class MarkdownRowTextInputWLabel_OBSOLETO(FloatLayout):  # ToDo: Esta se reemplaza por MDLineEditor
    mode_editor = BooleanProperty(defaultvalue=False)
    # type_editor = Lista o con 'Label, Image, Sepator, Table, etc.'

    def __init__(self, **kwargs):
        super(MarkdownRowTextInputWLabel_OBSOLETO, self).__init__(size_hint_y=None)
        self.md_label = MDTextLabel(pos_hint={'x': 0, 'center_y': 0.5})
        self.md_label.bind(size=self.update_height)
        self.add_widget(self.md_label)
        self.md_editor = MDLineTextInput(background_color = (0.8, 0.8, 0.8, 0.80),
                                         size_hint_y = None,
                                         pos_hint = {'x': 0, 'center_y': 0.5},
                                         opacity=0)
        self.md_editor.bind(text=self.on_txt_change)
        self.md_editor.bind(focus=self.on_focus)
        self.add_widget(self.md_editor)
        self.md_text = compose_dict(kwargs,'md_text',str,'')
        Window.bind(on_key_up=self.on_key_up)
    # Properties --------------------------------------------------------
    def _get_md_text(self):
        return self.md_label.md_text
    def _set_md_text(self, value):
        self.md_label.md_text = value
        self.md_editor.text = value
    md_text = property(_get_md_text, _set_md_text)

    # funtions events ---------------------------------------------------
    def on_mode_editor(self, instance, value):
        if value and value == self.mode_editor:
            self.md_editor.opacity = 1
            # self.md_editor.cursor = (2,0)
            # self.md_editor.select_all()
            self.md_editor.focus = True
        else:
            self.md_editor.opacity = 0

    def on_txt_change(self, instance, value):
        self.md_label.md_text = value

    def update_height(self, instance, value):
        if self.md_label.height > 0:
            self.height = self.md_label.height
        else:
            self.height = self.md_label.font_size+4

    def on_touch_up(self, touch):
        if touch.button == 'left':
            if self.collide_point(touch.x, touch.y):
                self.mode_editor = True
            else:
                self.mode_editor = False
            return False
        # super().on_touch_up(touch)

    def on_key_up(self, window, keycode, scancode):
        # Detectar si se presionó la tecla Escape
        if self.mode_editor == True:
            if keycode == 27:
                self.mode_editor=False
                return False  # True Evitar que otros controladores manejen la tecla
        return False  # Permitir que otros controladores manejen la tecla

    def on_focus(self, instance, value):
        if not value:  # Cuando pierde el foco
            self.mode_editor = False
            return True
        else:  # Cuando gana el foco
            pass


class MDLineEditor(FloatLayout):
    mode_editor = BooleanProperty(defaultvalue=False)
    line = ObjectProperty(baseclass=MDLine, defaultvalue=MDLine(md_text='', prev_line=None, next_line=None))
    # md_text = StringProperty(defaultvalue="**Texto en Negrita**")


    def __init__(self, **kwargs):
        super(MDLineEditor, self).__init__()
        # self.editor_on_return = False
        # Editor de texto -----------------------------------
        self.md_editor = MDLineTextInput(background_color=(0.8, 0.8, 0.8, 0.80),
                                          size_hint_y=None, pos_hint={'x': 0, 'y': 0},
                                          opacity=1)  # , font_size=12
        self.md_editor.text = self.line.md_text
        # print(self.md_editor.font_size)
        self.md_editor.bind(text=self.on_txt_change)
        non_focus = compose_dict(kwargs, 'non_focus', bool, False)
        if not non_focus:
            self.md_editor.bind(focus=self.on_focus)
        # Label -----------------------------------------------
        self.active_label = None
        Window.bind(on_key_up=self.on_key_up)
        self.update_type()
        # Asigna md_text --------------------------------------
        self.line = compose_dict(kwargs, 'line', MDLine, False)
        self.line.bind(md_text=self.on_line_md_text)
        self.line.bind(type=self.on_line_type)
        self.md_editor.text = self.line.md_text

    # Properties -----------------------------------------------
    def _set_md_text(self, md_text):
        self.line.md_text = md_text
    def _get_md_text(self):
        return self.line.md_text
    md_text = property(_get_md_text, _set_md_text)

    def _set_type(self, type):
        self.line.type = type
        self.update_type()
    def _get_type(self):
        return self.line.type
    type = property(_get_type, _set_type)


    # Private Functions ----------------------------------------
    def _md_editor_focus(self):
        self.md_editor.focus = True

    def _update_height(self):
        if self.active_label and self.active_label.height > 0:
            self.height = self.active_label.height
        else:
            self.height = 16  # self.active_label.font_size + 4

    def update_type(self):  # TODO: CODIFICAR
        type = self.line.type
        if isinstance(self.active_label, BaseMDLabels):
            self.remove_widget(self.active_label)
        if type == MD_LINE_TYPE.TEXT:
            self.active_label = MDTextLabel(md_text=self.line.md_text)
        elif type == MD_LINE_TYPE.SEPARATOR:
            self.active_label = MDSeparatorLabel()
        elif type == MD_LINE_TYPE.TABLE:
            self.active_label = MDTableLabel(md_text=self.line.md_text)



        self.active_label.pos_hint = {'x': 0, 'y': 0}
        self.add_widget(self.active_label, index=1)
        self.active_label.bind(size=self.on_resize_self)
        # self._update_height()

    # funtions events ---------------------------------------------------
    def on_resize_self(self, instance, value):
        self._update_height()

    def on_line_md_text(self, instance, value):
        self.md_editor.text = value
        self.update_type()

    def on_line_type(self, instance, value):
        self.update_type()

    def on_mode_editor(self, instance, value):
        if value and value == self.mode_editor:
            self.add_widget(self.md_editor)
            Clock.schedule_once(lambda dt: self._md_editor_focus(), 0.15)
            # self.editor_on_return = True
        else:
            self.remove_widget(self.md_editor)

    def on_txt_change(self, instance, value):
        self.active_label.md_text = value
        self.line.md_text = value  # TODO: la funcion on_md_text de MDLine deberia actualizar el tipo

    def on_touch_up(self, touch):
        if touch.button == 'left':
            if self.collide_point(touch.x, touch.y):
                self.mode_editor = True
            else:
                self.mode_editor = False
            return False
        # super().on_touch_up(touch)

    def on_key_up(self, window, keycode, scancode):
        # print("MDLineEditor->_on_keyboard_up")
        # Detectar si se presionó la tecla Escape
        if self.mode_editor == True:
            if keycode == 27:  # Escape
                self.mode_editor=False
                return False  # True Evitar que otros controladores manejen la tecla
        return False  # Permitir que otros controladores manejen la tecla

    def on_focus(self, instance, value):
        print("MDLineEditor->on_focus")
        if not value:  # Cuando pierde el foco
            self.mode_editor = False
            # return True
        else:  # Cuando gana el foco
            # self.editor_on_return = True
            pass


class MDDLDrag(Widget):
    _widgets_drag = []
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._widgets_drag.append(self.uid)
        self._is_mouseover = False
        Window.bind(mouse_pos=self.on_mouseover)

    def on_mouseover(self, instance, pos):
        # Verificar si el mouse está sobre este widget
        if self.collide_point(*self.to_widget(*pos)) and self.uid in self._widgets_drag:
            self._is_mouseover = True
            Window.set_system_cursor('hand')
        elif self._is_mouseover:
            Window.set_system_cursor('arrow')
            self._is_mouseover = False

    def on_remove(self):
        """Asegurarse de desvincular el evento cuando el widget es destruido."""
        Window.unbind(mouse_pos=self.on_mouseover)
        self._widgets_drag.remove(self.uid)


class MDDLNumberLine(Label):
    pass


class MDDLTree_hook(Widget):
    pass


class MDDLInfoBar(StackLayout):
    pass


class MDDLSpace(Widget):
    pass


# AGREGAR VARIABLE PARA INDICAR FOCO QUE PUEDA MOVERSE CON FLECHAS Y TAB FUERA DE EDICION (hightlight)
class MDDocumentLineEditor(BoxLayout, ThemableBehavior):
    line = ObjectProperty(baseclass=MDLine, defaultvalue=MDLine(md_text='', prev_line=None, next_line=None))
    index = NumericProperty(defaultvalue=0)  # indice de la linea en la lista
    hidden_line = BooleanProperty(defaultvalue=False)  # Indica si el renglon no es visible en el arbol (nodo padre cerrado)
    hotlight = BooleanProperty(defaultvalue=False)  # indica la linea que tiene el cursor ensima
    focused = BooleanProperty(defaultvalue=False)  # indica si la linea en modo render es linea actual para edición

    def __init__(self, mdline, index=0, **kwargs):
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
        if sw:
            self.wg_number_line = MDDLNumberLine(text=f"{self.index+1:04d}")
            self.add_widget(self.wg_number_line)
            self.index = index
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
        if kivy_dkw.DEVICE_TYPE == 'desktop':
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
            self.wg_number_line = MDDLNumberLine(text=f"{self.index:04d}")
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

    def on_index(self, instance, value):
        if self.wg_number_line:
            self.wg_number_line.text = f"{self.index+1:04d}"

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
        print("MDDocumentLineEditor->on_mode_editor")
        if value:
            self.focused = value


class MDDocumentEditor(UnfocusedWidget):  # , FocusBehavior
    # markdown_text = StringProperty()
    # usar listado de lineas

    # AGREGAR TAMBIEN SEGUIMIENTO DEL TECLADO PARA MOVER EL FOCUS CON LAS FLECHAS

    def __init__(self, lines=[], **kwargs):
        # FocusBehavior.__init__(self, **kwargs)
        self.scroll = ScrollView(size_hint=(1, 1), size=(400, 600))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None)
        super(MDDocumentEditor, self).__init__(radius=(0,0,0,0),  **kwargs)
        self.widget_graphic.border_width = 1
        # self.transparent = True

        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.add_widget(self.scroll)
        lines = compose(lines, list, False)
        self._lines_doc = []
        self._lines_editor = []
        self.append_lines(lines)  # Agrega las lineas al widget
        self._id_focus = -1  # Guarda el ID de la linea que tiene el foco
        self.widget_focus = None  # widget que tiene el foco a nivel App
        # Window.bind(on_key_up=self._on_keyboard_up)
        Window.bind(on_key_down=self._on_keyboard_down)

    """ UI Functions ------------------------------------------------"""
    def update_geometry(self):
        super().update_geometry()
        self.scroll.center = self.center
        pd = (self.theme.geometry['padding'] + 2) * 2
        self.scroll.size = (xx-pd for xx in self.size)

    def redraw(self, instance, args):
        super().redraw(instance, args)
        self.update_geometry()


    # Properties --------------------------------------------------------
    pass

    # Functions for manipulating lines -------------------------------------

    def append_line(self, line):
        index = len(self._lines_editor)
        eline = MDDocumentLineEditor(mdline=line, index=index, show_info_bar=False, show_tree_hook=False)
        eline.bind(focused=self.on_line_focused)
        self.container.add_widget(eline)
        self._lines_editor.append(eline)
        self._lines_doc.append(line)

    def append_lines(self, lines):
        check_list(lines, MDLine, False)
        self._lines_doc += lines
        index = len(self._lines_editor)
        for line in lines:
            eline = MDDocumentLineEditor(mdline=line, index=index, show_info_bar=False, show_tree_hook=False)
            eline.bind(focused=self.on_line_focused)
            self.container.add_widget(eline)
            self._lines_editor.append(eline)
            index +=1

    def insert_line(self, index, line):  # hay que insertar iterando o partiendo la lista
        eline = MDDocumentLineEditor(mdline=line, index=index, show_info_bar=False, show_tree_hook=False)
        eline.bind(focused=self.on_line_focused)
        cc = len(self._lines_editor)
        self.container.add_widget(eline, index=cc-index-1)
        self._lines_editor.insert(index+1, eline)
        self._lines_doc.insert(index+1, line)
        self.update_index(index=index)

    def insert_lines(self, index, lines):
        pass

    def remove_line(self, line):
        index = self._lines_editor.index(line)
        self.container.remove_widget(line)
        self._lines_editor.remove(line)
        self._lines_doc.remove(line.line)
        self.update_index(index=index-1)

    def remove_lines(self, lines):  # Lista de objetos MDDocumentLines a Remover
        pass

    def clear_lines(self):
        self._lines_editor = []
        self.container.clear_widgets()

    def next_line(self, index, hidden=True):
        if not hidden:
            return self._lines_editor[index+1]
        else:
            for ii in range(index+1, len(self._lines_editor)):
                if not self._lines_editor[ii].hidden_line:
                    return self._lines_editor[ii]
            return self._lines_editor[0]

    def previus_line(self, index, hidden=True):
        if not hidden:
            return self._lines_editor[index - 1]
        else:
            for ii in range(index-1, -1, -1):
                if not self._lines_editor[ii].hidden_line:
                    return self._lines_editor[ii]
            return self._lines_editor[len(self._lines_editor)-1]

    def update_index(self, index):
        '''Actuliza el indice y numero de linea desde index al final'''
        for ii in range(index, len(self._lines_editor)):
        # for lineed in self._lines_editor[index:]:
            self._lines_editor[ii].index = ii

    # Private Functions -------------------------------------------------
    pass

    # Funtions events ---------------------------------------------------
    def on_line_doc_type(self, instance, value):
        pass

    def on_markdown_text(self, instance, markdown_text):  # OBSOLETO. Esto se hace en MDDocument
        self.container.clear_widgets()
        widgets = render_markdown_to_widgets(markdown_text)
        for widget in widgets:
            self.container.add_widget(widget)

    def on_line_focused(self, instance, value):
        # print("MDDocumentEditor->on_line_focused")
        if value:
            print(instance.index)
            if self._id_focus > -1 and self._id_focus != instance.index:
                self._lines_editor[self._id_focus].focused = False
            # instance.focused = True
            # instance.focused = True
            self._id_focus = instance.index
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
        # CODIFICAR LA PRESION DE LA TECLA RETURN (13)
        # print("MDDocumentEditor->_on_keyboard_down", "Codigo de Teclas", keycode, modifier)
        # Variables Internas
        cursor_pos = self._lines_editor[self._id_focus].wg_line_editor.md_editor.cursor  # Posicion del cursor actual
        in_edition = self._lines_editor[self._id_focus].wg_line_editor.mode_editor  # TextInput actual en Edicion
        # Variables de Lineas
        previus_line = self.previus_line(self._id_focus)
        focus_line = self._lines_editor[self._id_focus]
        next_line = self.next_line(self._id_focus)
        # Termina la ejecucion si esta presionada ctrl, alt, shift o meta --------------

        # if 'ctrl' in special_keys or 'alt' in special_keys or 'shift' in special_keys or 'meta' in special_keys:
        #     return False

        # not in_edition and 'ctrl' in special_keys and 'shift' in special_keys and keycode == 273 and self._id_focus > 0:
        if not(in_edition) and keycode == 273 and 'ctrl' in special_keys and 'shift' in special_keys and self._id_focus > 0:
            print("MDDocumentEditor->_on_keyboard_down: SUBIR LINEA")



        if not(in_edition) and keycode == 274 and 'ctrl' in special_keys and 'shift' in special_keys and self._id_focus > 0:
            print("MDDocumentEditor->_on_keyboard_down: Bajar LINEA")
            print(self._id_focus)
            # self.container.remove_widget(focus_line)
            # # self.container.remove_widget(next_line)
            # self.container.add_widget(focus_line, index=self._id_focus)
            # focus_line.index += 1
            # next_line.index -= 1
            # id = self._id_focus
            # self._lines_editor[id], self._lines_editor[id + 1] = self._lines_editor[id + 1], self._lines_editor[id]
            # self._id_focus += 1

            id = self._id_focus
            ch = self.container.children
            ch[id], ch[id + 1] = ch[id + 1], ch[id]
            self._lines_doc[id], self._lines_doc[id+1] = self._lines_doc[id+1], self._lines_doc[id]
            focus_line.index +=1
            next_line.index -= 1
            self._id_focus += 1

        elif 'ctrl' in special_keys or 'alt' in special_keys or 'shift' in special_keys or 'meta' in special_keys:
            return False


        # Flecha Arriba ----------------------------------------------------------------
        elif keycode == 273:  # Flecha Arriba --------------------------------------------
            previus_line.focused = True
            if in_edition:
                focus_line.wg_line_editor.mode_editor = False
                previus_line.wg_line_editor.mode_editor = True
                previus_line.wg_line_editor.md_editor.cursor = cursor_pos
            if self.scroll.height < self.container.height:
                self.scroll.scroll_to(previus_line)
            return True
        # Flecha abajo -----------------------------------------------------------------
        elif keycode in [274]:  # Flecha abajo -----------------------------------------
            next_line.focused = True
            if in_edition:
                focus_line.wg_line_editor.mode_editor = False
                next_line.wg_line_editor.mode_editor = True
                next_line.wg_line_editor.md_editor.cursor = cursor_pos
            if self.scroll.height < self.container.height:
                self.scroll.scroll_to(next_line)
            return True
        # Return y Enter de Teclado Numerico --------------------------------------------
        elif keycode in [13, 271]:  # Return y Enter de Teclado Numerico ----------------
            if not in_edition:
                focus_line.mode_editor = True
                # focus_line.wg_line_editor.md_editor.cursor = (0, 0)
            else:
                # print("MDDocumentEditor->_on_keyboard_up - Return en Edicion")
                # print(cursor_pos)
                txt_focus = focus_line.wg_line_editor.md_text[:cursor_pos[0]]
                txt_new_line = focus_line.wg_line_editor.md_text[cursor_pos[0]:]
                # print("Actual line: " + txt_focus)
                # print("New Line: " + txt_new_line)
                focus_line.md_text = txt_focus
                focus_line.mode_editor = False
                focus_line.focused = False
                line = MDLine(md_text=txt_new_line, prev_line=None, next_line=None)
                self.insert_line(focus_line.index, line)
                self._id_focus += 1
                self._lines_editor[self._id_focus].mode_editor = True
                # self._lines_editor[self._id_focus].wg_line_editor.md_editor.cursor = (0, 0)
                def init_cursor(dt):
                    focus_line.wg_line_editor.md_editor.cursor = (0, 0)
                Clock.schedule_once(init_cursor, 0.1)
                if self.scroll.height < self.container.height:
                    self.scroll.scroll_to(self._lines_editor[self._id_focus])
            return True
        # F2 ------------------------------------------------------------------------------
        elif keycode == 283:  # F2 --------------------------------------------------------
            if not in_edition:
                focus_line.mode_editor = True
                # focus_line.wg_line_editor.md_editor.cursor = (0, 0)
            else:
                focus_line.mode_editor = False
            return True
        # Backspace -----------------------------------------------------------------------
        elif keycode == 8:  # Backspace ---------------------------------------------------
            # print("MDDocumentEditor->_on_keyboard_up - Backspace")
            if in_edition and focus_line.index > 1 and cursor_pos == (0, 0):  # ESTA EN MODO EDICION
                txt_focus = focus_line.md_text
                self.remove_line(focus_line)
                self._id_focus -= 1
                cursor_pos = len(previus_line.md_text)
                previus_line.md_text += txt_focus
                previus_line.wg_line_editor.mode_editor = True
                previus_line.wg_line_editor.md_editor.cursor = (cursor_pos, 0)
                return True
            elif not in_edition:  # NO ESTA EN MODO EDICION
                print("MDDocumentEditor->_on_keyboard_up - BackSpace in not edition")
                self.remove_line(focus_line)
                if self._id_focus < len(self._lines_editor):
                    next_line.focused = True
                else:
                    self._id_focus -= 1
                    previus_line.focused = True
        # Delete -------------------------------------------------------------------------
        elif keycode == 127:  # Delete ---------------------------------------------------
            ltxt = len(focus_line.md_text)
            clines = len(self._lines_editor)-1
            if in_edition and self._id_focus < clines and cursor_pos==(ltxt, 0):
                # print("MDDocumentEditor->_on_keyboard_up - DELETE")
                txt_next = next_line.md_text
                self.remove_line(next_line)
                focus_line.md_text += txt_next
                focus_line.wg_line_editor.md_editor.cursor = (ltxt, 0)
                return True
            elif not in_edition:  # NO ESTA EN MODO EDICION
                print("MDDocumentEditor->_on_keyboard_up - BackSpace in not edition")
                self.remove_line(focus_line)
                if self._id_focus < len(self._lines_editor):
                    next_line.focused = True
                else:
                    self._id_focus -= 1
                    previus_line.focused = True
        # Flecha Izquierda ---------------------------------------------------------------
        elif keycode == 276:  # Flecha Izquierda -----------------------------------------
            if in_edition and focus_line.index > 1 and cursor_pos == (0, 0):  # ESTA EN MODO EDICION
                focus_line.wg_line_editor.mode_editor = False
                previus_line.wg_line_editor.mode_editor = True
                cursor_pos = len(previus_line.md_text)
                previus_line.wg_line_editor.md_editor.cursor = (cursor_pos, 0)
                return True
        # Flecha Derecha -----------------------------------------------------------------
        elif keycode == 275:  # Flecha Derecha -------------------------------------------
            ltxt = len(focus_line.md_text)
            clines = len(self._lines_editor) - 1
            if in_edition and self._id_focus < clines and cursor_pos == (ltxt, 0):
                focus_line.wg_line_editor.mode_editor = False
                next_line.wg_line_editor.mode_editor = True
                next_line.wg_line_editor.md_editor.cursor = (0, 0)
                return True


