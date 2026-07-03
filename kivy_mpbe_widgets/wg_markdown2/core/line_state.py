#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LineState - Estado mutable de una línea del documento

Este módulo define la estructura de datos que representa el estado
completo de una línea en el editor de Markdown.

Características:
- Mutable con eventos de Kivy (EventDispatcher)
- Contiene referencia a MDLine + estado UI + geometría
- Dispara eventos on_<property> cuando cambian los valores
- MDDocumentLineEditor observa directamente su LineState

Fecha: 2026-01-12
Actualizado: 2026-02-01
Autor: Martin Pablo Bellanca
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Optional, Set

from kivy.event import EventDispatcher
from kivy.properties import (
    NumericProperty,
    BooleanProperty,
    ObjectProperty,
    OptionProperty,
)

# Importar MDLine y MD_LINE_TYPE de helpers_mpbe
from helpers_mpbe.markdown_document.md_document import MDLine
from helpers_mpbe.markdown_document import MD_LINE_TYPE
from kivy_mpbe_widgets.wg_markdown2.widgets.md_labels import MDTextLabel

# Constantes y enumeraciones del módulo
from .constants import WIDGETS_LABELS, LineGroup, AnimationType


# =============================================================================
# CLASE PRINCIPAL - LineState (Mutable con EventDispatcher)
# =============================================================================
class LineState(EventDispatcher):
    """
    Estado mutable de una línea del documento.

    Hereda de EventDispatcher para disparar eventos automáticamente
    cuando cambian las propiedades. MDDocumentLineEditor puede hacer
    bind directamente a estas propiedades.

    Properties (disparan eventos on_<name> al cambiar):
        # Identificación
        index (int): Índice de la línea en el documento (0-based)
        md_line (MDLine): Objeto MDLine con contenido y tipo

        # Estados de UI
        active (bool): Si la línea está activa
        editing (bool): Si la línea está en modo edición
        selected (bool): Si la línea está seleccionada
        hotlight (bool): Si el mouse está sobre la línea

        # Visibilidad
        visible (bool): Si la línea es visible después de aplicar filtros
        matched_search (bool): Si coincide con búsqueda actual
        group (str): Grupo de visibilidad ('visible', 'hidden', 'filtered')

        # Geometría
        height (float): Altura del widget en pixels
        y_position (float): Posición Y absoluta en el layout

        # Animaciones
        anim_type (str): Tipo de animación para transiciones. ESTO NO DEPENDE DEL ESTADO, SE DEBE PASAR COMO ARGUMENTO EN LOS MÉTODOS DE MDDocumentLineEditor
        alpha_background (float): Opacidad del fondo (0.0-1.0)

        # Cursor
        cursor_col (int): Columna del cursor
        cursor_row (int): Fila del cursor

        # Sub-widgets
        show_number_line (bool): Si se muestra el número de línea
        show_tree (bool): Si se muestra el árbol/jerarquía
        show_infobar (bool): Si se muestra la barra de información

    Example:
        >>> state = LineState(index=5, md_line=my_line)
        >>> state.bind(active=on_active_changed)
        >>> state.active = True  # Dispara on_active_changed
    """

    # ========================================================================
    # Identificación y datos
    # ========================================================================
    index = NumericProperty(0)
    md_line = ObjectProperty(None, allownone=True)

    # ========================================================================
    # Estados de UI
    # ========================================================================
    active = BooleanProperty(False)
    editing = BooleanProperty(False)
    selected = BooleanProperty(False)
    hotlight = BooleanProperty(False)
    # widget_type = ObjectProperty(None, allownone=True)  # Tipo de widget asociado a la línea (MDTextLabel, MDHeadLabel, etc)

    # ========================================================================
    # Cursor (separado en col y row para Kivy Properties)
    # ========================================================================
    cursor_col = NumericProperty(0)
    cursor_row = NumericProperty(0)

    # ========================================================================
    # Visibilidad y grupos
    # ========================================================================
    visible = BooleanProperty(True)
    matched_search = BooleanProperty(False)
    group = OptionProperty('visible', options=['visible', 'hidden', 'filtered'])

    # ========================================================================
    # Geometría
    # ========================================================================
    height = NumericProperty(30.0)
    y_position = NumericProperty(0.0)

    # ========================================================================
    # Animaciones y tema
    # ========================================================================
    # anim_type = OptionProperty(
    #     'fade',
    #     options=['none', 'fade', 'slide_up', 'slide_down', 'expand_up', 'expand_down']
    # )
    alpha_background = NumericProperty(0.0)

    # # ========================================================================
    # # Sub-widgets ESTO LO SACO Y LO PONGO EN StateManager POR QUE ES UN ESTADO GENERAL
    # # ========================================================================
    # show_number_line = BooleanProperty(True)
    # show_tree = BooleanProperty(False)
    # show_infobar = BooleanProperty(False)

    def __init__(self, index: int = 0, md_line: MDLine = None, **kwargs):
        """
        Inicializa el estado de la línea.

        Args:
            index: Índice de la línea en el documento
            md_line: Objeto MDLine con el contenido
            **kwargs: Valores iniciales para otras propiedades
        """
        super().__init__(**kwargs)
        self.register_event_type('on_type_changed')
        self.index = index
        self.widget_index = index  # Índice del widget asociado (puede ser diferente si hay líneas ocultas)
        self.md_line = md_line
        # Tipo de widget asociado a la línea según su tipo markdown
        # (MDTextLabel, MDSeparatorLabel, etc). Sin md_line, default a texto.
        if md_line is not None:
            self._widget_type = WIDGETS_LABELS.get(md_line.type, MDTextLabel)
        else:
            self._widget_type = MDTextLabel


    # ========================================================================
    # Propiedades de UI
    # ========================================================================
    @property
    def widget_type(self):
        """Tipo de widget asociado a la línea (MDTextLabel, MDHeadLabel, etc)"""
        return self._widget_type

    @widget_type.setter
    def widget_type(self, new_type):
        """Establece el tipo de widget y dispara on_type_changed si cambia."""
        old_type = self._widget_type
        if new_type != old_type:
            self._widget_type = new_type
            self.dispatch('on_type_changed', self.index, old_type, new_type)

    # ========================================================================
    # Propiedades de cursor (compatibilidad con tuple)
    # ========================================================================
    @property
    def cursor_pos(self) -> Tuple[int, int]:
        """Retorna la posición del cursor como tuple (col, row)."""
        return (self.cursor_col, self.cursor_row)

    @cursor_pos.setter
    def cursor_pos(self, value: Tuple[int, int]):
        """Establece la posición del cursor desde tuple (col, row)."""
        self.cursor_col, self.cursor_row = value

    # ========================================================================
    # Propiedades de grupo y animación (compatibilidad con Enum)
    # ========================================================================
    def get_group_enum(self) -> LineGroup:
        """Retorna el grupo como Enum."""
        return LineGroup(self.group)

    def set_group_enum(self, value: LineGroup):
        """Establece el grupo desde Enum."""
        self.group = value.value

    # def get_anim_type_enum(self) -> AnimationType:
    #     """Retorna el tipo de animación como Enum."""
    #     return AnimationType(self.anim_type)

    # def set_anim_type_enum(self, value: AnimationType):
    #     """Establece el tipo de animación desde Enum."""
    #     self.anim_type = value.value

    # ========================================================================
    # Métodos delegados a MDLine
    # ========================================================================
    # +- Generales ----------------------------------------------------------- 
    def get_md_text(self) -> str:
        """Obtiene el texto Markdown de la línea."""
        if self.md_line is None:
            return ''
        return self.md_line.md_text

    def update_type(self) -> Optional[MD_LINE_TYPE]:
        """Actualiza el tipo de línea basado en el contenido actual."""
        if self.md_line is None:
            return None
        old_type = self.md_line.update_type()

        if old_type != self.md_line.type:
            # old_widget_type = self.widget_type
            new_widget_type = WIDGETS_LABELS.get(self.md_line.type, MDTextLabel)
            self.widget_type = new_widget_type  # dispara on_type_changed via setter

        return old_type

    def get_line_type(self) -> MD_LINE_TYPE:
        """Obtiene el tipo de línea Markdown."""
        if self.md_line is None:
            return MD_LINE_TYPE.TEXT
        return self.md_line.type

    def get_markup_text(self) -> str:
        """Obtiene el texto convertido a formato Kivy Markup."""
        if self.md_line is None:
            return ''
        return self.md_line.get_markup_text()

    def get_number_line(self) -> int:
        """Obtiene el número de línea (índice + 1)."""
        if self.md_line is None:
            return -1
        return self.md_line.line_number

    # +- Titles -----------------------------------------------------------------
    def is_title(self) -> bool:
        """Retorna True si la línea es un título (nivel 1-6)."""
        if self.md_line is None:
            return False
        return self.md_line.is_title()

    def get_title_level(self) -> Optional[int]:
        """Si la línea es un título, retorna su nivel (1-6). Sino, retorna None."""
        if self.md_line is None:
            return None
        return self.md_line.get_title_level()

    def get_title_childs(self) -> list[MDLine]:
        """Devuelve los MDLine de los títulos hijos de esta línea."""
        if self.md_line is None:
            return []
        return self.md_line.get_title_childs()
    
    def get_title_first_child(self) -> Optional[MDLine]:
        """Devuelve el primer MDLine de título hijo de esta línea, o None si no tiene."""
        if self.md_line is None:
            return None
        return self.md_line.get_title_first_child()
    
    def get_title_parent(self) -> Optional[MDLine]:
        """Devuelve el MDLine del título padre de esta línea, o None si no tiene."""
        if self.md_line is None:
            return None
        return self.md_line.get_title_parent()
    
    def get_title_prev_same_level(self) -> Optional[MDLine]:
        """Devuelve el MDLine del título previo del mismo nivel, o None si no tiene."""
        if self.md_line is None:
            return None
        return self.md_line.get_title_prev_same_level()
    
    def get_title_next_same_level(self) -> Optional[MDLine]:
        """Devuelve el MDLine del título siguiente del mismo nivel, o None si no tiene."""
        if self.md_line is None:
            return None
        return self.md_line.get_title_next_same_level()
    
    def get_title_prev(self) -> Optional[MDLine]:
        """Devuelve el MDLine del título previo, o None si no tiene."""
        if self.md_line is None:
            return None
        return self.md_line.get_title_prev()
    
    def get_title_next(self) -> Optional[MDLine]:
        """Devuelve el MDLine del título siguiente, o None si no tiene."""
        if self.md_line is None:
            return None
        return self.md_line.get_title_next()
    
    def on_type_changed(self, index: int, old_type, new_type):
        """
        Handler por defecto de on_type_changed.

        Args:
            index: Índice de la línea
            old_type: Tipo de widget anterior
            new_type: Tipo de widget nuevo

        Note:
            Este es el handler requerido por register_event_type().
            Los componentes externos pueden hacer bind() a este evento.
        """
        pass

    # ========================================================================
    # Representación
    # ========================================================================
    def __repr__(self) -> str:
        """Representación legible del estado para debugging."""
        type_abbrev = {
            MD_LINE_TYPE.TEXT: 'TXT',
            MD_LINE_TYPE.TITLE: 'TIT',
            MD_LINE_TYPE.HEAD_TITLE: 'HTT',
            MD_LINE_TYPE.UNDERLINE_TITLE: 'ULT',
            MD_LINE_TYPE.SEPARATOR: 'SEP',
            MD_LINE_TYPE.LIST: 'LST',
            MD_LINE_TYPE.ORDER_LIST: 'ORD',
            MD_LINE_TYPE.TASK: 'TSK',
            MD_LINE_TYPE.TODO: 'TDO',
            MD_LINE_TYPE.TABLE: 'TBL',
            MD_LINE_TYPE.BLOCKQUOTE: 'BLQ',
            MD_LINE_TYPE.IMAGEN: 'IMG',
            MD_LINE_TYPE.CODE: 'COD',
            MD_LINE_TYPE.START_CODE: 'SC+',
            MD_LINE_TYPE.END_CODE: 'SC-',
        }

        parts = []

        # Tipo de línea
        line_type = self.get_line_type()
        type_str = type_abbrev.get(line_type, '???')
        parts.append(type_str)

        # Estados de UI
        if self.active:
            parts.append('ACT')
        if self.editing:
            parts.append('EDIT')
        if self.selected:
            parts.append('SEL')
        if self.hotlight:
            parts.append('HOT')

        # Visibilidad
        if not self.visible:
            parts.append('HIDDEN')
        if self.matched_search:
            parts.append('MATCH')

        flags_str = '|'.join(parts)

        # Texto preview
        md_text = self.get_md_text()
        text_preview = md_text[:20] + '...' if len(md_text) > 20 else md_text
        text_preview = text_preview.replace('\n', '↵')

        return (
            f"LineState[{self.index}]({flags_str}|{self.group}, "
            f"h={self.height:.0f}, y={self.y_position:.0f}) "
            f"'{text_preview}'"
        )

