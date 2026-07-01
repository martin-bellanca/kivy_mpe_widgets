#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MDDocumentLine - Widget de una línea del documento, asociado a su LineState.

Etapa II · Incremento 0:
    - Contenedor liviano por línea, atado a un LineState.
    - Renderiza el label markdown según line_state.widget_type (solo lectura).
    - Mantiene su altura sincronizada con la del label.

Etapa II · Incremento 1 (hover + selección, estilo cuadro de archivos):
    - Hover: GHotlightItem dibuja 2 líneas verticales (izq/der) en azul
      (hotlight_border) al pasar el mouse; se autogestiona con Window.mouse_pos.
    - Selección: GSelectItem pinta la línea (pressed_face, verde en el tema)
      con animación que se expande desde la posición del click. La activación
      la dispara el coordinador (select/unselect) para pasarle el origen.

Incrementos siguientes (preparado, aún no implementado):
    - Inc 2: embeber MDLineEditor y reaccionar a line_state.editing (edición).

Autor: Martin Pablo Bellanca
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty

from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.graphics.items_graphics import GSelectItem, GHotlightItem
from kivy_mpbe_widgets.wg_markdown2.widgets.md_labels import MDTextLabel


class MDDocumentLine(ThemableBehavior, BoxLayout):
    """
    Fila de documento asociada a un LineState.

    Args:
        line_state (LineState): Estado de la línea que esta fila representa.

    Attributes:
        line_state (LineState): Referencia al estado observado.
        index (int): Índice de la línea (espejo de line_state.index).
        label: Widget de render (subclase de BaseMDLabel) según widget_type.
        graphic_select (GSelectItem): Gráfico de selección animada (verde).
        graphic_hotlight (GHotlightItem): Gráfico de hover (2 líneas verticales azules).
    """

    index = NumericProperty(0)
    line_state = ObjectProperty(None, allownone=True)

    def __init__(self, line_state, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        BoxLayout.__init__(self, **kwargs)
        ThemableBehavior.__init__(self)

        self.line_state = line_state
        self.index = line_state.index

        # Gráficos de selección (verde animado) y hover (líneas verticales azules).
        # Mismo sistema que los ítems del cuadro de archivos (BaseItem).
        with self.canvas.before:
            self.graphic_select = GSelectItem(self)
        with self.canvas.after:
            self.graphic_hotlight = GHotlightItem(self)

        # Label de render según el tipo de línea (solo lectura por ahora)
        widget_type = line_state.widget_type or MDTextLabel
        self.label = widget_type(md_text=line_state.get_md_text())
        self.add_widget(self.label)

        # La altura de la fila sigue a la del label (que se autodimensiona por texture_size)
        self.height = self.label.height
        self.label.bind(height=self._on_label_height)

        # TODO Inc 2: self.line_state.bind(editing=self._on_editing) -> show_editor

    # ------------------------------------------------------------------ altura
    def _on_label_height(self, instance, value):
        """Mantiene la altura de la fila igual a la del label."""
        self.height = value

    # ------------------------------------------------------------ hover (Inc 1)
    def _hotlight_event(self, state, mp):
        """Callback de GHotlightItem al entrar/salir el mouse. Sincroniza estado."""
        if self.line_state is not None:
            self.line_state.hotlight = state

    # -------------------------------------------------------- selección (Inc 1)
    def select(self, anim_from=None):
        """Anima la selección (verde) expandiéndose desde anim_from (o el centro)."""
        pos = anim_from if anim_from is not None else self.center
        self.graphic_select.animate_select(True, pos)

    def unselect(self, anim_from=None):
        """Anima la des-selección de la línea."""
        pos = anim_from if anim_from is not None else self.center
        self.graphic_select.animate_select(False, pos)
