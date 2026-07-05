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

import re

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty

from helpers_mpbe.markdown_document.md_translate import title_font_size

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
OVERLAY_BG_ALPHA = 0.5
# Opacidad del label mientras se edita en overlay: tenue (fantasma del render
# detrás del texto de edición), pero sin ocultarlo del todo.
OVERLAY_LABEL_ALPHA = 0.35


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
        # Hint del cursor al entrar en edición. Se consumen al posicionarse:
        # - _edit_click_pos: coords de ventana del click (prioridad).
        # - _edit_cursor_col: columna destino (saltos de línea en edición).
        # Ambos None → cursor al final.
        self._edit_click_pos = None
        self._edit_cursor_col = None
        # Callbacks del coordinador (los setea MDDocumentEditor):
        # - on_edit_nav(index, delta, cursor_col) -> bool: salto de línea en edición.
        # - on_edit_text(index, text): embudo de mutación de texto (StateManager).
        # - on_edit_split(index, cursor_col): parte la línea en el cursor (Enter).
        # - on_edit_merge(index, direction): une con la línea de arriba (-1,
        #   Backspace) o de abajo (+1, Delete).
        # - on_edit_move_line(index, delta): mueve la línea (Alt+↑↓ en edición).
        # - on_edit_insert_above(index): inserta línea vacía arriba (Shift+Enter).
        # - on_edit_title_nav(direction, kind): navega por títulos (Ctrl+↑↓, etc.).
        # - on_edit_select(direction): sale de edición y extiende selección (Shift+↑↓).
        self.on_edit_nav = None
        self.on_edit_text = None
        self.on_edit_split = None
        self.on_edit_merge = None
        self.on_edit_move_line = None
        self.on_edit_insert_above = None
        self.on_edit_title_nav = None
        self.on_edit_select = None

        # Observa el modo edición, cambios de tipo y de índice del LineState.
        # El índice sigue al del estado (el StateManager lo reindexa al
        # insertar/borrar/mover líneas, Inc 3c).
        self.line_state.bind(editing=self._on_editing,
                             on_type_changed=self._on_type_changed,
                             index=self._on_state_index)

    def _on_state_index(self, line_state, value):
        """El índice de la fila sigue al del LineState (reindexado estructural)."""
        self.index = value

    def release(self):
        """
        Desbindea los eventos globales de la fila (Window y LineState).
        Llamar antes de descartar el widget (repoblado/limpieza) para evitar
        fugas: el hover bindea Window.mouse_pos y la edición Window.on_key_down.
        """
        self.graphic_hotlight.release()
        Window.unbind(on_key_down=self._on_key_down)
        self.line_state.unbind(editing=self._on_editing,
                               on_type_changed=self._on_type_changed,
                               index=self._on_state_index)

    # ------------------------------------------------------- tipo de línea
    def _on_type_changed(self, line_state, index, old_type, new_type):
        """
        Reemplaza el label por el del nuevo tipo de línea (p. ej. al tipear
        '# ' en edición la línea pasa a título). Mantiene posición y z-order
        (si el editor está montado, el label queda debajo de él).
        """
        old_label = self.label
        old_label.unbind(height=self._on_label_height)
        self._cell.remove_widget(old_label)

        self.label = new_type(md_text=self.line_state.get_md_text())
        self.label.size_hint = (1, None)
        self.label.pos_hint = dict(old_label.pos_hint)
        self.label.opacity = old_label.opacity  # conserva el tenue de edición
        if self.editor is not None and self.editor.parent is self._cell:
            # Insertar al fondo del orden de dibujo (el editor sigue arriba)
            self._cell.add_widget(self.label, index=len(self._cell.children))
        else:
            self._cell.add_widget(self.label)
        self.label.bind(height=self._on_label_height)
        self._apply_row_height()

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
            # Intercepta teclas de edición (F2; flechas entre líneas en 3b.3)
            self.editor.nav_handler = self._on_editor_nav

        if self.placement == EDITOR_PLACEMENT_BELOW:
            # Input opaco, DEBAJO del label (label arriba, input abajo)
            self.editor.background_color = (1, 1, 1, 1)
            self.editor.pos_hint = {'x': 0, 'y': 0}
            self.label.pos_hint = {'x': 0, 'top': 1}
        else:  # overlay
            # Input SOBRE el label; fondo translúcido, texto negro. El label
            # queda tenue detrás (fantasma del render) para que el texto de
            # edición no se confunda con el renderizado.
            self.editor.background_color = (1, 1, 1, OVERLAY_BG_ALPHA)
            self.editor.pos_hint = {'x': 0, 'y': 0}
            self.label.opacity = OVERLAY_LABEL_ALPHA
            # Fuente y altura del input = las del label: el texto de edición no
            # se ve chico y la fila no crece al editar (reflow ~cero). Padding
            # vertical 0 para que la fuente entre en el alto del label.
            self.editor.font_size = self.label.font_size
            self.editor.padding = [self.editor.padding[0], 0,
                                   self.editor.padding[2], 0]
            self.editor.height = self.label.height

        self.editor.text = self.line_state.md_line.md_text

        if self.editor.parent is None:
            self._cell.add_widget(self.editor)

        # Ajusta la altura de la fila según el modo
        self._apply_row_height()

        # Foco + cursor (diferido para que el editor esté montado y posicionado)
        self.editor.focus = True
        Clock.schedule_once(self._place_cursor, 0)

        # Escape para cancelar
        Window.bind(on_key_down=self._on_key_down)

    def set_edit_cursor_hint(self, window_pos, cursor_col=None):
        """
        Fija dónde ubicar el cursor al entrar en edición.

        Args:
            window_pos: posición (x, y) en coords de ventana del click que
                origina la edición (prioridad si viene).
            cursor_col: columna destino (para saltos de línea en edición).
            Ambos None → cursor al final del texto.
        """
        self._edit_click_pos = window_pos
        self._edit_cursor_col = cursor_col

    def _place_cursor(self, dt):
        """
        Posiciona el cursor al entrar en edición: en el punto del click si
        hay hint (como la V1 con get_cursor_from_xy), o al final del texto.
        El hint se consume (una edición posterior no hereda un click viejo).

        El input conserva su fuente chica; el mapeo compensa las diferencias
        con el render: la distancia del click al inicio del texto se escala
        por (fuente input / fuente render) y se le suma el padding izquierdo
        del input (el label no tiene) y el ancho del prefijo markdown oculto
        (p. ej. '## ' en títulos). Queda una deriva chica en títulos (el
        render es negrita, el input no).
        """
        if self.editor is None:
            return
        click_pos, self._edit_click_pos = self._edit_click_pos, None
        col, self._edit_cursor_col = self._edit_cursor_col, None
        if click_pos is not None:
            x, y = self.editor.to_widget(*click_pos)
            # Distancia al inicio del texto renderizado (label e input
            # comparten x), llevada a la escala de la fuente del input
            scale = self.editor.font_size / float(self._render_font_size())
            cx = (x - self.editor.x) * scale
            x = (self.editor.x + cx + self.editor.padding[0]
                 + self._hidden_prefix_width())
            self.editor.cursor = self.editor.get_cursor_from_xy(x, y)
        elif col is not None:
            self.editor.cursor = (max(0, min(col, len(self.editor.text))), 0)
        else:
            self.editor.cursor = (len(self.editor.text), 0)

    def _render_font_size(self):
        """
        Tamaño de fuente con que se ve el render de la línea (para escalar el
        X del click a la fuente del input): títulos según su nivel
        (title_font_size, la misma fórmula del traductor); el resto, la del label.
        """
        level = self.line_state.get_title_level()
        if level:
            return title_font_size(level)
        return getattr(self.label, 'font_size', self.editor.font_size)

    def _hidden_prefix_width(self):
        """
        Ancho (px) del prefijo markdown que el render oculta (p. ej. '## '),
        medido con la fuente del input. 0 si la línea no tiene prefijo oculto.
        """
        match = re.match(r'^#{1,6}\s', self.editor.text)
        if not match:
            return 0.0
        core = CoreLabel(font_size=self.editor.font_size,
                         font_name=self.editor.font_name)
        return core.get_extents(match.group(0))[0]

    # Key codes de las teclas de edición interceptadas en el input
    _K_F2 = 283
    _K_UP, _K_DOWN = 273, 274
    _K_LEFT, _K_RIGHT = 276, 275
    _K_ENTER, _K_NUMPAD_ENTER = 13, 271
    _K_BACKSPACE, _K_DELETE = 8, 127
    _K_SPACE = 32
    _BOX_RE = re.compile(r'\[[ xX]\]')

    def _on_editor_nav(self, keycode, modifiers):
        """
        Intercepta teclas de edición mientras el input tiene el foco
        (callback de MDLineTextInput.nav_handler). Devuelve True si consume
        la tecla (no la procesa el TextInput).

        Inc 3b.2: F2 sale de edición (confirma, como Enter/foco-fuera).
        Inc 3b.3: saltos de línea en edición —
          ↑/↓ mueven la edición manteniendo la columna del cursor;
          ←/→ en el borde de la línea pasan a la anterior/siguiente
          (cursor al final/inicio). Si no está en el borde, ←/→ mueven
          el cursor dentro del input (no se consumen).
        """
        key = keycode[0]
        if key == self._K_F2:
            self._commit()
            return True
        if key == self._K_SPACE and 'ctrl' in modifiers:
            # Ctrl+Espacio togglea el checkbox de la tarea en edición (3e.7)
            return self._toggle_task_in_editor()
        if key in (self._K_ENTER, self._K_NUMPAD_ENTER):
            if 'shift' in modifiers:
                # Shift+Enter inserta una línea vacía arriba (Inc 3c.1)
                return self._request_edit_insert_above()
            # Enter parte la línea en el cursor (Inc 3c.1)
            return self._request_edit_split()
        if key == self._K_UP:
            if 'ctrl' in modifiers:  # Ctrl+↑ título (3d): +Shift mismo nivel
                return self._request_edit_title_nav(
                    -1, 'same' if 'shift' in modifiers else 'any')
            if 'alt' in modifiers:       # Alt+Shift+↑ título padre (3d.3) / Alt+↑ mover (3c.3)
                if 'shift' in modifiers:
                    return self._request_edit_title_nav(-1, 'parent')
                return self._request_edit_move_line(-1)
            if 'shift' in modifiers:     # Shift+↑ sale de edición y selecciona (3e.1)
                return self._request_edit_select(-1)
            return self._request_edit_move(-1, self.editor.cursor_col)
        if key == self._K_DOWN:
            if 'ctrl' in modifiers:  # Ctrl+↓ título (3d): +Shift mismo nivel
                return self._request_edit_title_nav(
                    1, 'same' if 'shift' in modifiers else 'any')
            if 'alt' in modifiers:       # Alt+Shift+↓ título padre (3d.3) / Alt+↓ mover (3c.3)
                if 'shift' in modifiers:
                    return self._request_edit_title_nav(1, 'parent')
                return self._request_edit_move_line(1)
            if 'shift' in modifiers:     # Shift+↓ sale de edición y selecciona (3e.1)
                return self._request_edit_select(1)
            return self._request_edit_move(1, self.editor.cursor_col)
        if key == self._K_LEFT and self.editor.cursor_index() == 0:
            return self._request_edit_move(-1, 'end')
        if key == self._K_RIGHT and self.editor.cursor_index() == len(self.editor.text):
            return self._request_edit_move(1, 'start')
        # Backspace al inicio (no primera) → une con la línea de arriba (Inc 3c.2)
        if (key == self._K_BACKSPACE and self.editor.cursor_index() == 0
                and self.index > 0):
            return self._request_edit_merge(-1)
        # Delete al final → une con la de abajo (el borde 'última' lo ve el coord)
        if (key == self._K_DELETE
                and self.editor.cursor_index() == len(self.editor.text)):
            return self._request_edit_merge(1)
        return False

    def _request_edit_move(self, delta, cursor_col):
        """
        Pide al coordinador mover la edición `delta` líneas, con la columna
        destino `cursor_col` (int, 'end' o 'start'). Consume la tecla.

        Diferido un frame: estamos dentro del keyboard callback del input
        actual, que se destruye al cambiar de línea; hacer el cambio de foco
        acá mismo reentraría el manejo de foco/teclado.
        """
        if self.on_edit_nav is None:
            return False
        index = self.index
        Clock.schedule_once(
            lambda dt: self.on_edit_nav(index, delta, cursor_col), 0)
        return True

    def _request_edit_split(self):
        """
        Pide al coordinador partir la línea en la columna del cursor (Enter en
        edición). Consume la tecla. Diferido un frame (misma razón que
        _request_edit_move: estamos dentro del keyboard callback del input).
        """
        if self.on_edit_split is None:
            return False
        index = self.index
        cursor_col = self.editor.cursor_col
        Clock.schedule_once(
            lambda dt: self.on_edit_split(index, cursor_col), 0)
        return True

    def _request_edit_merge(self, direction):
        """
        Pide al coordinador unir esta línea con la de arriba (direction -1,
        Backspace) o con la de abajo (direction +1, Delete). Consume la tecla.
        Diferido un frame (misma razón que _request_edit_move/_split).
        """
        if self.on_edit_merge is None:
            return False
        index = self.index
        Clock.schedule_once(
            lambda dt: self.on_edit_merge(index, direction), 0)
        return True

    def _request_edit_insert_above(self):
        """
        Pide al coordinador insertar una línea vacía arriba de esta y editarla
        (Shift+Enter). Consume la tecla. Diferido un frame (como split/merge).
        """
        if self.on_edit_insert_above is None:
            return False
        index = self.index
        Clock.schedule_once(
            lambda dt: self.on_edit_insert_above(index), 0)
        return True

    def _request_edit_move_line(self, delta):
        """
        Pide al coordinador mover esta línea `delta` posiciones (Alt+↑↓ en
        edición). Consume la tecla. Diferido un frame (el reordenamiento de
        widgets toca el input enfocado).
        """
        if self.on_edit_move_line is None:
            return False
        index = self.index
        Clock.schedule_once(
            lambda dt: self.on_edit_move_line(index, delta), 0)
        return True

    def _request_edit_title_nav(self, direction, kind):
        """
        Pide al coordinador navegar por títulos desde edición (Ctrl+↑↓, etc.):
        edita el título destino manteniendo la columna del cursor. Consume la
        tecla. Diferido un frame (cambia activación/foco).
        """
        if self.on_edit_title_nav is None:
            return False
        cursor_col = self.editor.cursor_col
        Clock.schedule_once(
            lambda dt: self.on_edit_title_nav(direction, kind, cursor_col), 0)
        return True

    def _toggle_task_in_editor(self):
        """
        Ctrl+Espacio en edición: si la línea es tarea, togglea su checkbox
        (`[ ]`↔`[x]`) en el input (persiste + re-renderiza), sin mover el cursor.
        """
        text = self.editor.text
        m = self._BOX_RE.search(text)
        if not m:
            return False  # no es tarea: no consumir
        checked = text[m.start() + 1] in 'xX'
        box = '[ ]' if checked else '[x]'
        col = self.editor.cursor_col
        self.editor.text = text[:m.start()] + box + text[m.end():]
        self.editor.cursor = (col, 0)
        return True

    def _request_edit_select(self, direction):
        """
        Shift+↑↓ en edición: sale de edición a visualización y extiende la
        selección `direction`. Consume la tecla. Diferido un frame.
        """
        if self.on_edit_select is None:
            return False
        Clock.schedule_once(
            lambda dt: self.on_edit_select(direction), 0)
        return True

    def _exit_edit(self):
        """Quita el editor y deja el label con el texto actual re-renderizado."""
        Window.unbind(on_key_down=self._on_key_down)
        self._edit_click_pos = None
        self._edit_cursor_col = None
        if self.editor is not None and self.editor.parent is not None:
            self.editor.focus = False
            self._cell.remove_widget(self.editor)
        # Restaurar posición y opacidad del label (overlay lo dejó tenue)
        self.label.pos_hint = {'x': 0, 'y': 0}
        self.label.opacity = 1
        self.label.md_text = self.line_state.md_line.md_text
        # La fila vuelve a la altura del label
        self._apply_row_height()

    def _on_editor_text(self, instance, value):
        """Cada cambio de texto persiste (vía StateManager) y re-renderiza en vivo."""
        self._persist_text(value)
        self.label.md_text = value  # render en tiempo real

    def _persist_text(self, value):
        """
        Embudo de mutación de texto: rutea por el coordinador (StateManager) si
        está cableado; si no (uso sin coordinador), cae al LineState directo.
        En ambos casos actualiza el tipo (on_type_changed → swap del label).
        """
        if self.on_edit_text is not None:
            self.on_edit_text(self.index, value)
        else:
            self.line_state.md_line.md_text = value
            self.line_state.update_type()

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
        # Si el input recuperó el foco en el interín (p. ej. el click cayó
        # dentro del texto en edición), no hay nada que commitear.
        if self.editor is not None and self.editor.focus:
            return
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
            # Restaura el texto original por el mismo embudo (repone tipo/label)
            self._persist_text(self._edit_original)
            self.label.md_text = self._edit_original
            if self.editor is not None:
                self.editor.text = self._edit_original
            self.line_state.editing = False
            return True
        return False
