#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MDDocumentLine - Widget de una línea del documento, asociado a su LineState.

Etapa II · Incremento 0:
    - Contenedor liviano por línea, atado a un LineState.
    - Renderiza el label markdown según line_state.widget_type (solo lectura).

Etapa II · Incremento 1 (hover + selección, estilo cuadro de archivos):
    - Hover: GHotlightItem (2 líneas verticales azules).
    - Selección: GSelectItem (relleno verde animado desde el click).

Etapa II · Incremento 2 (edición en overlay translúcido):
    - Al pasar line_state.editing=True se superpone un MDLineTextInput
      semi-transparente SOBRE el label (mismo lugar). Al tipear, el label
      se re-renderiza en vivo y el texto se persiste en el MDLine.
    - Enter o perder el foco confirma; Escape cancela (restaura el texto).

Autor: Martin Pablo Bellanca
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty

from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.graphics.items_graphics import GHotlightItem
from kivy_mpbe_widgets.graphics.markdown_graphics import GSelectItem
from kivy_mpbe_widgets.wg_markdown2.widgets.md_labels import MDTextLabel
from kivy_mpbe_widgets.wg_markdown2.widgets.md_inputs import MDLineTextInput


# Ubicación del editor en modo edición (opción de configuración)
EDITOR_PLACEMENT_OVERLAY = 'overlay'  # input translúcido SOBRE el label
EDITOR_PLACEMENT_BELOW = 'below'      # input opaco DEBAJO del label
# Alpha del fondo del input en modo overlay (sólo el fondo es translúcido;
# el texto va negro y opaco para que se lea bien).
OVERLAY_BG_ALPHA = 0.35


class MDDocumentLine(ThemableBehavior, BoxLayout):
    """
    Fila de documento asociada a un LineState.

    Args:
        line_state (LineState): Estado de la línea que esta fila representa.
        placement (str): Ubicación del editor en edición ('overlay' o 'below').
    """

    index = NumericProperty(0)
    line_state = ObjectProperty(None, allownone=True)

    def __init__(self, line_state, placement=EDITOR_PLACEMENT_OVERLAY, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        BoxLayout.__init__(self, **kwargs)
        ThemableBehavior.__init__(self)

        self.line_state = line_state
        self.index = line_state.index
        self.placement = placement

        # Gráficos de selección (verde animado) y hover (líneas verticales azules).
        with self.canvas.before:
            self.graphic_select = GSelectItem(self)
        with self.canvas.after:
            self.graphic_hotlight = GHotlightItem(self)

        # Celda de texto: FloatLayout que permite superponer el editor sobre el label.
        self._cell = FloatLayout(size_hint_y=None)
        widget_type = line_state.widget_type or MDTextLabel
        self.label = widget_type(md_text=line_state.get_md_text())
        self.label.size_hint = (1, None)
        # pos_hint es imprescindible: sin él, el FloatLayout deja el label en
        # (0,0) absoluto y todas las filas se superponen.
        self.label.pos_hint = {'x': 0, 'y': 0}
        self._cell.add_widget(self.label)
        self.add_widget(self._cell)

        # La altura de la fila/celda sigue a la del label
        self.height = self.label.height
        self._cell.height = self.label.height
        self.label.bind(height=self._on_label_height)

        # Editor (se crea perezosamente al entrar en edición)
        self.editor = None
        self._edit_original = None

        # Observa el modo edición del LineState
        self.line_state.bind(editing=self._on_editing)

    # ------------------------------------------------------------------ altura
    def _on_label_height(self, instance, value):
        """Recalcula la altura de la fila cuando cambia la del label."""
        self._apply_row_height()

    def _apply_row_height(self, *args):
        """
        Altura de la fila según el modo:
        - Sin editar: alto del label.
        - Editando 'overlay': max(label, input) (el input no se corta).
        - Editando 'below': label + input (entran los dos apilados).
        """
        h = self.label.height
        if (self.line_state is not None and self.line_state.editing
                and self.editor is not None):
            if self.placement == EDITOR_PLACEMENT_BELOW:
                h = self.label.height + self.editor.height
            else:  # overlay
                h = max(self.label.height, self.editor.height)
        self.height = h
        self._cell.height = h

    # ------------------------------------------------------------ hover (Inc 1)
    def _hotlight_event(self, state, mp):
        """Callback de GHotlightItem al entrar/salir el mouse."""
        if self.line_state is not None:
            self.line_state.hotlight = state

    # -------------------------------------------------------- selección (Inc 1)
    def select(self, direction='fade'):
        """
        Anima la selección de la línea.

        Args:
            direction: 'fade' (click, aparición por fade), 'up' o 'down'
                (navegación con flechas, deslizamiento hacia arriba/abajo).
        """
        if direction == 'up':
            self.graphic_select.animate_up(True)
        elif direction == 'down':
            self.graphic_select.animate_down(True)
        else:
            self.graphic_select.animate_fade(True)

    def unselect(self, direction='fade'):
        """Anima la des-selección de la línea (misma dirección que la selección)."""
        if direction == 'up':
            self.graphic_select.animate_up(False)
        elif direction == 'down':
            self.graphic_select.animate_down(False)
        else:
            self.graphic_select.animate_fade(False)

    # --------------------------------------------------------- edición (Inc 2)
    def _on_editing(self, instance, value):
        """Reacciona al cambio de line_state.editing (entra/sale de edición)."""
        if value:
            self._enter_edit()
        else:
            self._exit_edit()

    def _enter_edit(self):
        """Superpone el editor translúcido sobre el label y le da foco."""
        self._edit_original = self.line_state.md_line.md_text

        if self.editor is None:
            self.editor = MDLineTextInput(size_hint=(1, None))
            self.editor.foreground_color = (0, 0, 0, 1)  # texto negro (legible)
            self.editor.bind(text=self._on_editor_text,
                             focus=self._on_editor_focus,
                             on_text_validate=self._on_editor_validate,
                             height=self._apply_row_height)

        if self.placement == EDITOR_PLACEMENT_BELOW:
            # Input opaco, DEBAJO del label (label arriba, input abajo)
            self.editor.background_color = (1, 1, 1, 1)
            self.editor.pos_hint = {'x': 0, 'y': 0}
            self.label.pos_hint = {'x': 0, 'top': 1}
        else:  # overlay
            # Input SOBRE el label; sólo el fondo translúcido, texto negro
            self.editor.background_color = (1, 1, 1, OVERLAY_BG_ALPHA)
            self.editor.pos_hint = {'x': 0, 'y': 0}

        self.editor.text = self.line_state.md_line.md_text

        if self.editor.parent is None:
            self._cell.add_widget(self.editor)

        # Ajusta la altura de la fila según el modo
        self._apply_row_height()

        # Foco + cursor al final (diferido para que el editor esté montado)
        self.editor.focus = True
        Clock.schedule_once(self._place_cursor_end, 0)

        # Escape para cancelar
        Window.bind(on_key_down=self._on_key_down)

    def _place_cursor_end(self, dt):
        if self.editor is not None:
            self.editor.cursor = (len(self.editor.text), 0)

    def _exit_edit(self):
        """Quita el editor y deja el label con el texto actual re-renderizado."""
        Window.unbind(on_key_down=self._on_key_down)
        if self.editor is not None and self.editor.parent is not None:
            self.editor.focus = False
            self._cell.remove_widget(self.editor)
        # Restaurar posición del label (por si estaba en modo 'below')
        self.label.pos_hint = {'x': 0, 'y': 0}
        self.label.md_text = self.line_state.md_line.md_text
        # La fila vuelve a la altura del label
        self._apply_row_height()

    def _on_editor_text(self, instance, value):
        """Cada cambio de texto persiste en el MDLine y re-renderiza el label en vivo."""
        self.line_state.md_line.md_text = value
        self.line_state.md_line.update_type()
        self.label.md_text = value  # render en tiempo real

    def _on_editor_focus(self, instance, value):
        """
        Al perder el foco, cierra la edición — pero DIFERIDO un frame.

        Se difiere para que, si la salida es por Escape, el handler síncrono de
        Escape corra primero (cancela + devuelve el foco) y este commit quede
        sin efecto. Si la salida es por click en otro panel, el commit diferido
        cierra la edición normalmente.
        """
        if not value:
            Clock.schedule_once(self._commit_on_focus_loss, 0)

    def _commit_on_focus_loss(self, dt):
        if self.line_state.editing:
            self._commit()

    def _on_editor_validate(self, instance):
        """Enter confirma la edición (input multiline=False)."""
        self._commit()

    def _commit(self):
        """Confirma la edición (el texto ya está persistido)."""
        self.line_state.editing = False

    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        """Escape cancela y restaura el texto original."""
        if key == 27 and self.line_state.editing:  # Escape
            self.line_state.md_line.md_text = self._edit_original
            self.line_state.md_line.update_type()
            self.label.md_text = self._edit_original
            if self.editor is not None:
                self.editor.text = self._edit_original
            self.line_state.editing = False
            return True
        return False
