#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MDDocumentLine - Widget de una línea del documento, asociado a su LineState.

Etapa II · Incremento 0:
    - Contenedor liviano por línea, atado a un LineState.
    - Renderiza el label markdown según line_state.widget_type (solo lectura).
    - Mantiene su altura sincronizada con la del label.

Incrementos siguientes (preparado, aún no implementado):
    - Inc 1: reaccionar a line_state.active (highlight visual).
    - Inc 2: embeber MDLineEditor y reaccionar a line_state.editing (edición).

Autor: Martin Pablo Bellanca
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty

from kivy_mpbe_widgets.wg_markdown2.widgets.md_labels import MDTextLabel


class MDDocumentLine(BoxLayout):
    """
    Fila de documento asociada a un LineState.

    Args:
        line_state (LineState): Estado de la línea que esta fila representa.

    Attributes:
        line_state (LineState): Referencia al estado observado.
        index (int): Índice de la línea (espejo de line_state.index).
        label: Widget de render (subclase de BaseMDLabel) según widget_type.
    """

    index = NumericProperty(0)
    line_state = ObjectProperty(None, allownone=True)

    def __init__(self, line_state, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        super().__init__(**kwargs)

        self.line_state = line_state
        self.index = line_state.index

        # Label de render según el tipo de línea (solo lectura por ahora)
        widget_type = line_state.widget_type or MDTextLabel
        self.label = widget_type(md_text=line_state.get_md_text())
        self.add_widget(self.label)

        # La altura de la fila sigue a la del label (que se autodimensiona por texture_size)
        self.height = self.label.height
        self.label.bind(height=self._on_label_height)

        # TODO Inc 1: self.line_state.bind(on_active=self._on_active) -> highlight
        # TODO Inc 2: self.line_state.bind(on_editing=self._on_editing) -> show_editor

    def _on_label_height(self, instance, value):
        """Mantiene la altura de la fila igual a la del label."""
        self.height = value
