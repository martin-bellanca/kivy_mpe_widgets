#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_line_editors_v2.py
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
MDDocumentLineEditor V2 - Widget para edición de líneas de documento Markdown

Versión 2.0 con integración al StateManager.
Reemplaza el uso de DataShow, DataThemed y DataState por LineState inmutable.

Created on 27/12/2024
@author: mpbe
"""

# imports del sistema -------------------------------------------------------
from enum import Enum
from statistics import linear_regression

# helpers_mpbe --------------------------------------------------------------
from helpers_mpbe.python import compose_dict, compose, check_list
from helpers_mpbe.markdown_document.md_labels import BaseMDLabel,MDTextLabel, MDTableLabel, MDSeparatorLabel
from helpers_mpbe.markdown_document.md_labels import MDCodeLabel, MDHeadLabel, MDToDoLabel, MDTaskLabel, MDImageLabel
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
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
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty, BoundedNumericProperty
from kivy.clock import Clock

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.events.widgets_events import HotlightEventDispatcher, StartAnimEventDispatcher, EndAnimEventDispatcher
from kivy_mpbe_widgets.wg_undo.undo_manager import UndoManager, Command
from kivy_mpbe_widgets.base_widgets import FrameUnfocused, FrameFocused
from kivy_mpbe_widgets.wg_markdown.md_doc_line_widgets import *
from helpers_mpbe.markdown_document.md_document import MDDocument
from helpers_mpbe.markdown_document import MD_LINE_TYPE
from helpers_mpbe.markdown_document.md_document import MDLine
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import BaseItem, BaseDataDic
from kivy_mpbe_widgets.events.recycle_view_events import SelectItemEventDispatcher, UnSelectItemEventDispatcher
from kivy_mpbe_widgets.events.recycle_view_events import ActivateItemEventDispatcher, UnActivateItemEventDispatcher
from kivy_mpbe_widgets.graphics.widget_graphics import GFace, GBorder, GFocus, GHotLight
from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager, LineState
from kivy_mpbe_widgets.graphics.markdown_graphics import GHotlightItem, GActiveItem, GSelectItem


# from kivy_dkw.wg_markdown.render_markdown_to_widgets import render_line_markdown_to_widget

# Define el archivo KV en un string (V2 - con StateManager)
kv = """
<MDDocumentLineEditor>:
    size_hint_y: None

    canvas.before:
        # Fondo base del item (usa alpha_background del LineState)
        Color:
            rgba: self._background_color
        Rectangle:
            pos: self.pos
            size: self.size

        # Rectángulo de selección para la animación
        Color:
            rgba: root._selected_color
        Rectangle:
            pos: root.fill_sel_pos
            size: root.fill_sel_size

    canvas.after:
        # Línea de Active Item (lado izquierdo)
        Color:
            rgba: self._active_color if self.active else (1, 1, 1, 0)
        Line:
            width: 4
            points: self.x, self.y, self.x, self.top

        # Líneas de Hotlight (superior e inferior)
        Color:
            rgba: self._hotlight_color if self.hotlight else (1, 1, 1, 0)
        Line:
            width: 1
            points: self.x, self.top-1, self.right, self.top-1
        Line:
            width: 1
            points: self.x, self.y+1, self.right, self.y+1
"""
# Builder.load_string(kv)


class MDDocumentLineEditor(RecycleDataViewBehavior, ThemeWidget, HotlightEventDispatcher):
    """
    Widget editor de línea de documento Markdown - Versión 2 con StateManager.

    Utiliza LineState inmutable en lugar de DataShow/DataThemed/DataState.
    Se integra con DocumentStateManager para gestión centralizada de estados.

    Properties:
        num_line: Número de la línea en el documento
        hotlight: Indica si el mouse está sobre la línea
        active: Indica si la línea está activa (desde LineState)
        selected: Indica si la línea está seleccionada (desde LineState)
        fill_sel_pos: Posición del rectángulo de selección animado
        fill_sel_size: Tamaño del rectángulo de selección animado
    """

    # Properties
    num_line = NumericProperty(defaultvalue=0)
    hotlight = BooleanProperty(defaultvalue=False)
    active = BooleanProperty(defaultvalue=False)  # Sincronizado con LineState
    selected = BooleanProperty(defaultvalue=False)  # Sincronizado con LineState
    fill_sel_pos = ListProperty([0, 0])
    fill_sel_size = ListProperty([0, 0])

    def __init__(self):
        """
        Inicializa el widget editor de línea.

        El estado de la línea (show_number_line, show_tree, show_infobar, alpha_background)
        se obtiene del LineState en refresh_view_attrs().
        """
        # Call Super Constructors
        RecycleDataViewBehavior.__init__(self)
        ThemeWidget.__init__(self)
        HotlightEventDispatcher.__init__(self)

        # Variables internas
        self.index = -1
        self._touch_pos = (0, 0)
        self.old_text_line = None  # Backup del texto de la línea

        # Línea de markdown (será actualizada en refresh_view_attrs)
        self.md_line = MDLine(md_text="", prev_line=None, next_line=None)

        # Estado de la línea (LineState inmutable - será actualizado en refresh_view_attrs)
        self.line_state = LineState(index=-1)

        # Colores del tema (calculados con alpha_background)
        self._background_color = [1, 1, 1, 0]  # Actualizado desde LineState
        self._selected_color = self.theme.colors['pressed_face']
        self._selected_color[3] = 0.6
        self._active_color = self.theme.colors['focus_border']
        self._active_color[3] = 1.0
        self._hotlight_color = self.theme.colors['hotlight_border']

        # Bind mouse events para desktop
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)


        # Construcción del Widget
        self.size_hint_y = None

        # Layout principal (horizontal)
        self._layout = BoxLayout(orientation="horizontal")
        self.add_widget(self._layout)

        # Sub-widgets (visibilidad controlada por LineState)
        self.wg_space = MDDLSpace()
        self._layout.add_widget(self.wg_space)

        self.wg_drag_hook = MDDLDrag()
        self._layout.add_widget(self.wg_drag_hook)

        self.wg_number_line = None  # Creado dinámicamente según LineState.show_number_line
        self.wg_tree_hook = None    # Creado dinámicamente según LineState.show_tree
        self.wg_info_bar = None     # Creado dinámicamente según LineState.show_infobar

        # Line Editor principal
        self.wg_line_editor = MDLineEditor(line=self.md_line, non_focus=True)
        self._layout.add_widget(self.wg_line_editor)
        self.wg_line_editor.bind(size=self.on_resize_self)

        self._update_height()

        # Graphics (selection, active, hotlight)
        with self.canvas.before:
            self.graphic_select = GSelectItem(self)
        with self.canvas.after:
            self.graphic_active = GActiveItem(self)
            self.graphic_hotlight = GHotlightItem(self)

        # Bind eventos de geometría
        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)

    # +- Widget Update Functions --------------------------------------------------------
    def _on_update_geometry(self, instance, value):
        self._layout.pos = self.pos
        self._layout.size = self.size
        self.graphic_hotlight.update_graphics()
        self.graphic_select.update_graphics()
        self.graphic_active.update_graphics()

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

    def on_resize_self(self, instance, value):
        self._update_height()

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


    # Show/Hide Sub-widgets (controlado por LineState)
    def show_number_line(self, value: bool, num_line: int):
        """
        Muestra u oculta el widget de número de línea.

        Args:
            value: True para mostrar, False para ocultar
            num_line: Número de línea a mostrar
        """
        if value:
            if not self.wg_number_line:
                self.wg_number_line = MDDLNumberLine()
                self._layout.add_widget(self.wg_number_line, index=1)
                self.wg_space_number_line = MDDLSpace()
                self._layout.add_widget(self.wg_space_number_line, index=1)
            self.num_line = num_line
        else:
            if self.wg_number_line:
                self._layout.remove_widget(self.wg_number_line)
                self._layout.remove_widget(self.wg_space_number_line)
                self.wg_number_line = None

    def show_tree_hook(self, value: bool):
        """
        Muestra u oculta el gancho de árbol.

        Args:
            value: True para mostrar, False para ocultar
        """
        if value and not self.wg_tree_hook:
            self.wg_tree_hook = MDDLTree_hook()
            self._layout.add_widget(self.wg_tree_hook, index=2)
        elif not value and self.wg_tree_hook:
            self._layout.remove_widget(self.wg_tree_hook)
            self.wg_tree_hook = None

    def show_info_bar(self, value: bool):
        """
        Muestra u oculta la barra de información.

        Args:
            value: True para mostrar, False para ocultar
        """
        if value and not self.wg_info_bar:
            self.wg_info_bar = MDDLInfoBar()
            self._layout.add_widget(self.wg_info_bar, index=2)
        elif not value and self.wg_info_bar:
            self._layout.remove_widget(self.wg_info_bar)
            self.wg_info_bar = None




    # +- Eventos de MDLineEditor --------------------------------------------------------
    def on_num_line(self, instance, value):
        self.num_line = value
        if self.wg_number_line:
            self.wg_number_line.text = f"{value:04d}"

    # +- Properties ---------------------------------------------------------------------
    # +--- md_text ------------------------------
    def _set_md_text(self, md_text):
        '''
        Notas:
            -self.line y self.active_label se actualizan de on_txt_change de self.md_editor
        '''
        # print('MDDocumentLineEditor->on_line')
        # self.md_line.md_text = md_text
        self.wg_line_editor.md_text = md_text
        # self.active_label.md_text = md_text
        # self.line.md_text = md_text
    def _get_md_text(self):
        return self.md_line.md_text
    md_text = property(_get_md_text, _set_md_text)

    # +--- md_line type  ------------------------
    def _set_line_type(self, type):
        self.md_line.type = type
    def _get_line_type(self):
        return self.md_line.type
    line_type = property(_get_line_type, _set_line_type)

    # +--- cursor_pos type  ------------------------
    def _set_cursor_pos(self, value:tuple):
        self.wg_line_editor.md_editor.cursor = value
    def _get_cursor_pos(self):
        return self.wg_line_editor.md_editor.cursor  #.editor_cursor_pos
    editor_cursor_pos = property(_get_cursor_pos, _set_cursor_pos)


    # Funciones de visualización
    def show_editor(self, show: bool, anim: bool, cursor: tuple = None):
        """
        Muestra u oculta el editor de texto.

        Args:
            show: True para mostrar editor, False para mostrar label
            anim: True para animar la transición
            cursor: Posición del cursor (col, row)

        Note:
            El estado editing se sincroniza con LineState a través del
            RecycleView parent (DocumentStateManager).
        """
        if anim:
            self.wg_line_editor.show_anim_editor(show, cursor)
        else:
            self.wg_line_editor.show_editor(show, cursor)

    def select(self, value: bool, anim: bool, anim_type: str = 'fade'):
        """
        Selecciona o des-selecciona el widget.

        Args:
            value: True para seleccionar, False para deseleccionar
            anim: True para animar la transición
            anim_type: Tipo de animación ('fade', 'up', 'down')

        Note:
            self.selected se sincroniza con LineState.selected en refresh_view_attrs.
        """
        self.selected = value

        if anim:
            if anim_type == 'up':
                self.graphic_select.animate_up(value)
            elif anim_type == 'down':
                self.graphic_select.animate_down(value)
            else:
                self.graphic_select.animate_fade(value)
        else:
            self.graphic_select.show(value)

    def activate(self, value: bool, show_editor: bool = False, cursor: tuple = None,
                 anim: bool = True, anim_type: str = 'fade'):
        """
        Activa o desactiva el widget.

        Args:
            value: True para activar, False para desactivar
            show_editor: True para entrar en modo edición
            cursor: Posición del cursor en el editor
            anim: True para animar las transiciones
            anim_type: Tipo de animación para la selección

        Note:
            self.active se sincroniza con LineState.active en refresh_view_attrs.
        """
        # Seleccionar
        self.select(value, anim, anim_type)

        # Modo edición
        self.show_editor(show_editor, anim, cursor)

        # Activar
        self.active = value
        if anim:
            self.graphic_active.animate(value)
        else:
            self.graphic_active.show(value)
    

    # RecycleDataViewBehavior interface
    def refresh_view_attrs(self, rv, index, data):
        """
        Actualiza el widget cuando cambian los datos del RecycleView.

        Args:
            rv: RecycleView parent
            index: Índice del item en la lista de datos
            data: Diccionario con los datos del item

        Data keys (V2 con StateManager):
            md_line (MDLine): Línea de markdown
            line_state (LineState): Estado inmutable de la línea con:
                - show_number_line, show_tree, show_infobar (visibilidad)
                - alpha_background (opacidad del fondo)
                - selected, active, editing (estados)
                - hotlight, visible, cursor_pos
                - anim_type (tipo de animación)

        Note:
            Este método es llamado por RecycleView cada vez que:
            1. Se actualiza data en el RecycleView
            2. Se hace scroll y se reciclan widgets
            3. Se cambia el estado de una línea (vía StateManager)
        """
        self.index = index

        # Obtener md_line
        self.md_line = data.get('md_line')
        self.wg_line_editor.line = self.md_line

        # Obtener LineState (reemplaza DataThemed/DataShow/DataState)
        self.line_state = data.get('line_state', LineState(index=index))

        # Aplicar visibilidad de sub-widgets (desde LineState)
        self.show_number_line(self.line_state.show_number_line, self.md_line.num_line)
        self.show_tree_hook(self.line_state.show_tree)
        self.show_info_bar(self.line_state.show_infobar)

        # Aplicar alpha_background (tema)
        base_color = self.theme.colors.get('background', [1, 1, 1])
        self._background_color = [*base_color[:3], self.line_state.alpha_background]

        # Aplicar estado (selected, active, editing)
        # Solo actualizar si realmente cambió algo importante (no hotlight)
        # El hotlight se maneja localmente en on_mouse_move() para fluidez

        # IMPORTANTE: Bloquear actualizaciones de hotlight durante refresh
        # para evitar que on_mouse_move() interfiera con las animaciones
        self._refreshing = True
        saved_hotlight = self.hotlight

        # Verificar si hay cambios en active/editing
        state_changed = (
            self.active != self.line_state.active or
            self.line_state.editing != (hasattr(self, '_editing_state') and self._editing_state)
        )

        if state_changed:
            # Guardar estado de edición actual
            self._editing_state = self.line_state.editing

            # Aplicar cambios con animación
            if self.line_state.active and self.line_state.editing:
                # Activar con animación
                self.activate(
                    value=True,
                    show_editor=True,
                    cursor=self.line_state.cursor_pos,
                    anim=True,
                    anim_type=self.line_state.anim_type
                )
            elif self.line_state.active and not self.line_state.editing:
                # Activar sin editor
                self.activate(
                    value=True,
                    show_editor=False,
                    anim=True,
                    anim_type=self.line_state.anim_type
                )
            else:
                # Desactivar
                self.activate(
                    value=False,
                    show_editor=False,
                    anim=True,
                    anim_type=self.line_state.anim_type
                )
        else:
            # Si no cambió active/editing, actualizar solo selección
            # (evita llamar activate() innecesariamente)
            self.selected = self.line_state.selected
            self.graphic_select.show(self.line_state.selected)

        # Restaurar hotlight (on_mouse_move() no pudo modificarlo durante _refreshing)
        self.hotlight = saved_hotlight

        # Desbloquear actualizaciones de hotlight
        self._refreshing = False

        return super(MDDocumentLineEditor, self).refresh_view_attrs(rv, index, data)
    

    # Eventos del Widget
    def on_mouse_move(self, instance, mp):
        """
        Handler de movimiento del mouse para hotlight.

        Args:
            instance: Window instance
            mp: Mouse position (x, y)

        Note:
            El hotlight se maneja localmente para fluidez.
            Durante refresh_view_attrs() se bloquea para evitar interferencias.
        """
        # Si estamos en medio de refresh_view_attrs(), ignorar eventos de mouse
        # para evitar que el hotlight "salte" durante las animaciones
        if hasattr(self, '_refreshing') and self._refreshing:
            return

        hla = self.collide_point_to_window(*mp)

        if self.hotlight != hla and not self.disabled and self.level_render == self.theme.level_render:
            self.graphic_hotlight.animate(hla)
            self.hotlight = hla

            # Notificar al parent (RecycleView) del evento hotlight
            if self.parent:
                self.parent.parent.handle_hotlight_event(index=self.index, state=hla)  # view=self,

    def on_touch_down(self, touch):
        """
        Handler de touch down para capturar el evento.

        Args:
            touch: Touch event

        Returns:
            bool: True si el evento fue manejado
        """
        if self.collide_point(*(self.to_window(*touch.pos))):
            touch.grab(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """
        Handler de touch up para selección y activación.

        Args:
            touch: Touch event

        Returns:
            bool: True si el evento fue manejado

        Note:
            Notifica al RecycleView parent para actualizar el StateManager.
        """
        if touch.grab_current is self:
            if touch.button == 'left' and self.parent:
                # Notificar al RecycleView parent del evento de selección
                # El flujo es:
                # 1. MDDocumentEditor.handle_touch_left_up_event()
                # 2. LineService.activate_line()
                # 3. StateManager.activate_line()
                # 4. StateManager emite StateChangeEvent
                # 5. MDDocumentEditor._on_line_state_changed()
                # 6. RecycleView.data se actualiza
                # 7. RecycleView llama a refresh_view_attrs()
                # 8. Widget se actualiza automáticamente
                self.parent.parent.handle_touch_left_up_event(
                    index=self.index,
                    view=self,
                    touch=touch
                )

                return True

            touch.ungrab(self)



