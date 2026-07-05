#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MDDocumentEditor - Widget principal del editor de Markdown

Este es el widget coordinador principal que integra todos los componentes:
- ScrollView para navegación
- FocusBehavior para eventos de teclado
- ThemableBehavior para temas visuales
- StateManager para lógica
- RecycleBoxLayout para rendering

Responsabilidades:
1. Coordinar StateManager y RecycleBoxLayout
2. Manejar eventos de usuario (scroll, teclado, mouse)
3. Cargar y mostrar documentos
4. Activar/desactivar líneas (Etapa I: básico)

Fecha: 2026-01-12
Autor: Martin Pablo Bellanca
"""

from typing import Optional
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import FocusBehavior
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

# Importar ThemableBehavior
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.wg_markdown2.widgets.md_labels import MDTextLabel
from kivy_mpbe_widgets.wg_markdown2.widgets.md_document_line import (
    MDDocumentLine, EDITOR_PLACEMENT_OVERLAY, EDITOR_PLACEMENT_BELOW,
)

# Importar componentes core
from ..core.state_manager import DocumentStateManager as StateManager
from ..core.recycle_box_layout import RecycleBoxLayout  # Version a Futuro
# from ..core.list_box_layout import ListBoxLayout  # Voy a usar BoxLayout por ahora para simplificar (Etapa I)

# Importar MDDocument
from helpers_mpbe.markdown_document.md_document import MDDocument, MDLine


class MDDocumentEditor(FocusBehavior, ScrollView, ThemableBehavior):
    """
    Editor de documento Markdown con reciclaje inteligente.

    Este es el widget principal que el usuario instancia en su app.
    Coordina todos los componentes internos.

    Attributes:
        state_manager (StateManager): Gestor de estados
        recycle_layout (RecycleBoxLayout): Layout con reciclaje
        active_line_widget (MDDocumentLineEditor): Widget activo actual
        md_document (MDDocument): Documento cargado

    Properties:
        theme (ObjectProperty): Tema visual (de ThemableBehavior)

    Example:
        >>> editor = MDDocumentEditor()
        >>> editor.load_document(md_document)
        >>> # Usuario puede scrollear, click en líneas, etc.

    Note:
        Etapa I implementa funcionalidad básica:
        - Cargar documento
        - Mostrar con reciclaje
        - Scroll fluido
        - Click para activar (sin edición todavía)
    """

    # Kivy properties
    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        """
        Inicializa el MDDocumentEditor.

        Crea todos los componentes necesarios y los conecta.
        """
        # ====================================================================
        # Referencias (inicializar ANTES de super para evitar errores)
        # ====================================================================
        self.state_manager = StateManager()
        self.doc_lines_layout = None
        self.active_line_widget = None
        # Config: ubicación del editor en modo edición ('overlay' | 'below').
        # Honrada como kwarg: MDDocumentEditor(editor_placement='below'|'overlay').
        #   'overlay' (default) = input translúcido SOBRE el label: sin reflow y
        #       deslizamiento suave entre líneas en ambos sentidos.
        #   'below' = input opaco DEBAJO del label: funcional, pero al saltar de
        #       línea editando parpadea (el gráfico de selección no acompaña al
        #       widget cuando la fila reflowea). Queda como opción.
        # Debe fijarse antes de populate_md_lines (cada fila lo toma al crearse).
        self.editor_placement = kwargs.pop('editor_placement',
                                           EDITOR_PLACEMENT_OVERLAY)
        # self.md_document: Optional[MDDocument] = None  md_document esta en state_manager?
        self.last_scroll_y = 1.0
        # Columna objetivo del cursor en edición (goal column): se mantiene al
        # saltar ↑/↓ por líneas cortas y se reubica al moverse horizontal.
        # _edit_last_placed = columna real donde quedó el cursor (para detectar
        # movimiento horizontal del usuario entre saltos verticales).
        self._edit_goal_col = None
        self._edit_last_placed = None
        # Selección múltiple contigua (Inc 3e): índices con verde y ancla del
        # rango (donde arrancó la selección con Shift).
        self._selected_set = set()
        self._selection_anchor = None
        # Clipboard interno estructurado (Inc 3e.4): lista de md_text por línea
        # (preserva líneas multilínea a futuro: tablas/mermaid). _clipboard_sig
        # = firma de lo puesto en el clipboard del sistema, para detectar si el
        # contenido lo cambió otra app.
        self._clipboard_lines = None
        self._clipboard_sig = None

        # ====================================================================
        # Configuración de ScrollView (ANTES de super().__init__)
        # ====================================================================
        kwargs.setdefault('do_scroll_x', False)
        kwargs.setdefault('do_scroll_y', True)
        kwargs.setdefault('scroll_type', ['bars', 'content'])
        kwargs.setdefault('bar_width', 10)

        # Inicializar ScrollView y behaviors
        super().__init__(**kwargs)

        # ====================================================================
        # Inicialización diferida (después de que ScrollView esté listo)
        # ====================================================================
        # Clock.schedule_once(self._init_components, 0)
        self._init_components(0)


    def _init_components(self, dt):
        """
        Inicializa componentes después de que ScrollView esté completamente listo.

        Se llama con Clock.schedule_once para evitar problemas de inicialización
        con herencia múltiple (FocusBehavior, ThemableBehavior, ScrollView).
        """
        # ====================================================================
        # StateManager (lógica)
        # ====================================================================
        # self.state_manager = StateManager()

        # ====================================================================
        # RecycleBoxLayout (rendering)
        # ====================================================================
        # self.doc_lines_layout = RecycleBoxLayout(  # Versión Futura
        #     state_manager=self.state_manager
        # )

        # self.doc_lines_layout = ListBoxLayout(  # Versión Actual
        #     state_manager=self.state_manager
        # )
        self.doc_lines_layout = BoxLayout(  # Versión Actual
            orientation='vertical', size_hint_y=None, spacing=0, padding=0
        )
        # El layout crece con su contenido para que el ScrollView pueda desplazarlo.
        self.doc_lines_layout.bind(
            minimum_height=self.doc_lines_layout.setter('height')
        )

        # Lista de MDDocumentLine en orden del documento (índice == posición).
        # Lista (no dict) para que insertar/borrar/mover corran los índices
        # solos (Inc 3c). Poblada en populate_md_lines.
        self._line_widgets = []

        self.add_widget(self.doc_lines_layout)

        # ====================================================================
        # Bind eventos
        # ====================================================================
        self.bind(scroll_y=self._on_scroll)
        self.bind(size=self._on_size_changed)

        # Eventos estructurales del StateManager: el editor mantiene sus filas
        # y el layout en sync con inserciones/borrados/movimientos (Inc 3c).
        self.state_manager.bind(
            on_line_added=self._on_line_added,
            on_line_removed=self._on_line_removed,
            on_line_moved=self._on_line_moved,
        )

        # Teclado a nivel Window (enfoque robusto, como el editor viejo): así la
        # navegación no depende de que el widget tenga el foco de Kivy (evita que
        # se rompa al salir de edición con Escape/Enter). Gateado por _kbd_active
        # (documento en uso) y por NO estar editando.
        self._kbd_active = False
        Window.bind(on_key_down=self._on_window_key_down)

        Logger.info("MDDocumentEditor: Initialized")


        # ==========================================================================
    
    # ==========================================================================
    # CORE: Gestión de Documento
    # ==========================================================================

    def _release_line_widgets(self):
        """
        Descarta todas las filas de línea: desbindea sus eventos globales
        (Window.mouse_pos del hover, Window.on_key_down de la edición) y
        limpia el layout, el mapa y la referencia a la fila activa.
        Evita fugas de binds al repoblar el documento.
        """
        for line_widget in self._line_widgets:
            line_widget.release()
        if self.doc_lines_layout:
            self.doc_lines_layout.clear_widgets()
        self._line_widgets = []
        self.active_line_widget = None
        self._selected_set = set()
        self._selection_anchor = None

    def initialize_document(self):
        """
        Inicializa/resetea el documento a estado vacío.

        Limpia:
        - Filas de líneas (widgets) y su mapa (desbindeando eventos globales)
        - StateManager
        - Referencia a la línea activa
        """
        # Limpiar widgets de línea (desbindea eventos globales)
        self._release_line_widgets()

        # Limpiar estado
        if self.state_manager:
            self.state_manager._clear_all()

        Logger.info("MDDocumentEditorV2: Document initialized")

    def populate_md_lines(self, md_document:MDDocument):  # md_lines: list[MDLine]
        """
        Carga el documento desde un MDDocument.

        Esta es la función principal para cargar contenido en el editor.

        Args:
            md_lines: Lista de líneas del documento markdown

        Side Effects:
            - Inicializa estados en StateManager
            - Crea services
            - Popula RecycleView.data con estados
        """
        if not md_document:
            Logger.warning("MDDocumentEditorV2: populate_from_md_lines with empty list")
            self.initialize_document()
            return

        md_lines = md_document.md_lines

        # FASE 1: Inicializar estados en el StateManager (crea un LineState por línea)
        self.state_manager.set_document(md_document)
        Logger.info(f"MDDocumentEditorV2: Initialized {len(md_lines)} line states")

        # FASE 2: Construir las filas UNA sola vez, atadas a su LineState.
        # Descartar lo anterior (desbindea eventos globales; no duplicar, Inc 0).
        self._release_line_widgets()
        # El teclado del documento se re-activa al activar una línea del nuevo doc
        self._kbd_active = False

        for line_state in self.state_manager.get_line_states():
            line_widget = self._create_line_widget(line_state)
            self.doc_lines_layout.add_widget(line_widget)
            self._line_widgets.append(line_widget)

        Logger.info(f"MDDocumentEditorV2: Document populated with {len(md_lines)} lines")

    def _create_line_widget(self, line_state):
        """
        Crea una fila MDDocumentLine para `line_state` y le cablea los callbacks
        del coordinador (navegación entre líneas en edición y tipeo en vivo).
        No la agrega al layout ni a _line_widgets (eso lo hace quien llama).
        """
        line_widget = MDDocumentLine(line_state, placement=self.editor_placement)
        line_widget.on_edit_nav = self._on_line_edit_nav
        line_widget.on_edit_text = self._on_line_edit_text
        line_widget.on_edit_split = self._on_line_edit_split
        line_widget.on_edit_merge = self._on_line_edit_merge
        line_widget.on_edit_move_line = self._on_line_edit_move_line
        line_widget.on_edit_insert_above = self._on_line_edit_insert_above
        line_widget.on_edit_title_nav = self._on_line_edit_title_nav
        line_widget.on_edit_select = self._on_line_edit_select
        return line_widget

    def _on_line_edit_select(self, direction: int):
        """
        Shift+↑↓ en edición (3e.1): sale de edición a visualización y extiende
        la selección desde la línea activa.
        """
        idx = self.state_manager.get_active_index()
        if idx is not None:
            self.state_manager.update_state(idx, editing=False)  # sale de edición
        self.extend_selection(direction)

    def _on_line_edit_text(self, index: int, text: str):
        """Embudo de mutación de texto en vivo: pasa por el StateManager."""
        self.state_manager.update_line_text(index, text)

    def _on_line_edit_split(self, index: int, cursor_col: int):
        """
        Parte la línea `index` en la columna del cursor (Enter en edición, 3c.1):
        la línea actual conserva el texto anterior al cursor y una línea nueva
        debajo se lleva el posterior; la edición pasa a la nueva (cursor al inicio).
        La línea que se deja confirma al desactivarse.
        """
        md_line = self.state_manager.get_md_line(index)
        if md_line is None:
            return
        text = md_line.md_text
        col = max(0, min(cursor_col, len(text)))
        before, after = text[:col], text[col:]

        # La línea actual conserva 'before' (por el embudo del StateManager)
        self.state_manager.update_line_text(index, before)
        # Nueva línea debajo con 'after' → on_line_added crea su fila
        new_md_line = MDLine(after, None, None)
        new_md_line.update_type()
        self.state_manager.insert_line(index + 1, new_md_line)
        # Editar la nueva línea con el cursor al inicio
        self.edit_line(index + 1, cursor_col=0)

    def _on_line_edit_insert_above(self, index: int):
        """
        Inserta una línea vacía ARRIBA de `index` y pasa a editarla (Shift+Enter,
        3c.1). La línea actual baja sin cambios; la edición va a la nueva (índice
        `index`) con el cursor al inicio.
        """
        new_md_line = MDLine('', None, None)
        new_md_line.update_type()
        self.state_manager.insert_line(index, new_md_line)  # empuja la actual abajo
        self.edit_line(index, cursor_col=0)

    def _on_line_edit_merge(self, index: int, direction: int):
        """
        Une líneas en edición (Inc 3c.2):
        - direction -1 (Backspace al inicio): une la línea `index` con la de
          arriba; el texto se agrega al final de la anterior, `index` se borra
          y la edición pasa a la anterior con el cursor en el punto de unión.
        - direction +1 (Delete al final): une la de abajo con `index`; el texto
          de la siguiente se agrega al final de la actual, la siguiente se borra
          y la edición sigue en `index` con el cursor en el punto de unión.
        """
        if direction < 0:
            # Backspace: unir con la línea de arriba
            if index <= 0:
                return
            prev = index - 1
            prev_text = self.state_manager.get_md_line(prev).md_text
            cur_text = self.state_manager.get_md_line(index).md_text
            join_col = len(prev_text)
            self.state_manager.update_line_text(prev, prev_text + cur_text)
            self.state_manager.remove_line(index)   # borra la actual (en edición)
            # La anterior no estaba en edición → edit_line arranca su editor
            # con el texto ya unido y el cursor en el punto de unión.
            self.edit_line(prev, cursor_col=join_col)
        else:
            # Delete: unir con la línea de abajo
            if index >= self.state_manager.get_total_lines() - 1:
                return
            nxt = index + 1
            cur_text = self.state_manager.get_md_line(index).md_text
            next_text = self.state_manager.get_md_line(nxt).md_text
            join_col = len(cur_text)
            self.state_manager.remove_line(nxt)      # borra la de abajo
            # La actual ya está en edición → refresco su editor con el texto
            # unido (setear .text persiste vía embudo y re-renderiza el label).
            line_widget = self.get_line_widget(index)
            if line_widget is not None and line_widget.editor is not None:
                line_widget.editor.text = cur_text + next_text
                line_widget.editor.cursor = (join_col, 0)

    def _layout_kivy_index(self, doc_index: int) -> int:
        """
        Convierte un índice de documento (0 = arriba) al índice de `add_widget`
        del BoxLayout (los children están en orden inverso al visual).
        """
        return len(self.doc_lines_layout.children) - doc_index

    # ========================================================================
    # CARGA DE DOCUMENTO
    # ========================================================================

    def load_document(self, md_document: MDDocument):
        """
        Cargar documento de Markdown.

        Pasos:
        1. Guardar referencia al documento
        2. Cargar líneas en StateManager
        3. Renderizar viewport inicial

        Args:
            md_document: Instancia de MDDocument con el documento cargado

        Example:
            >>> md_doc = MDDocument()
            >>> md_doc.load_doc('/path', 'file.md')
            >>> editor.load_document(md_doc)
        """
        Logger.info(
            f"MDDocumentEditor: Loading document '{md_document.doc_name}' "
            f"with {md_document.can_lines} lines"
        )

        # Guardar referencia
        self.md_document = md_document

        # Cargar en StateManager
        self.state_manager._load_document(md_document.md_lines)

        # Resetear scroll al top
        self.scroll_y = 1.0

        # Renderizar viewport inicial
        self._refresh_visible_widgets()

        Logger.info("MDDocumentEditor: Document loaded successfully")

    # ========================================================================
    # EVENTOS DE SCROLL
    # ========================================================================

    def _on_scroll(self, instance, value):
        """
        Evento disparado cuando cambia scroll_y.

        Throttling: Solo procesa si el cambio es significativo.

        Args:
            instance: self
            value: Nuevo scroll_y (0.0-1.0)
        """
        # Throttling: Ignorar cambios muy pequeños
        if abs(value - self.last_scroll_y) < 0.001:
            return

        self.last_scroll_y = value

        # Actualizar widgets visibles
        self._refresh_visible_widgets()

    def _on_size_changed(self, instance, value):
        """
        Evento disparado cuando cambia el tamaño de la ventana.

        Recalcula widgets visibles porque viewport_height cambió.

        Args:
            instance: self
            value: Nuevo size (width, height)
        """
        Logger.debug(f"MDDocumentEditor: Size changed to {value}")

        # Recalcular widgets visibles (viewport_height cambió)
        self._refresh_visible_widgets()

    # ========================================================================
    # ACTUALIZACIÓN DE VIEWPORT
    # ========================================================================

    def _refresh_visible_widgets(self):
        """
        FUNCIÓN ÚNICA que actualiza widgets visibles.

        Llamada en:
        - Scroll
        - Resize de ventana
        - Carga de documento
        - Insert/Delete línea (Etapa II)
        - Aplicar filtro (Etapa II)

        Pasos:
        1. Obtener scroll_y y viewport_height actuales
        2. Preguntar a StateManager qué líneas renderizar
        3. Delegar actualización a RecycleBoxLayout
        """
        # Inc 0: todas las filas viven en el BoxLayout y el ScrollView las
        # desplaza; no hace falta crear/recrear widgets al scrollear (eso era lo
        # que duplicaba las líneas). El reciclaje real por viewport (mostrar sólo
        # las visibles) queda como optimización para un incremento posterior.
        #
        # TODO (post Etapa II): usar state_manager.get_visible_in_viewport(...)
        # para mostrar/ocultar o reciclar sólo las filas dentro del viewport.
        return

    # ========================================================================
    # EVENTOS DE MOUSE / ACTIVACIÓN POR CLICK (Inc 1)
    # ========================================================================

    # Umbral (px) para distinguir un tap de un arrastre-scroll
    _TAP_THRESHOLD = dp(8)

    def on_touch_down(self, touch):
        """
        Registra el inicio del touch para distinguir tap de scroll.

        En edición NO deja que el FocusBehavior del ScrollView robe el foco
        del input (cerraba la edición al clickear dentro del texto): saltea
        FocusBehavior en la cadena y marca el touch como 'ignorado' para que
        el desfoque global de Kivy tampoco actúe. El destino real del click
        lo decide on_touch_up (mover cursor / cambiar de línea en edición).
        """
        if self.collide_point(*touch.pos):
            touch.ud['md_down_pos'] = touch.pos
            if self._is_editing():
                FocusBehavior.ignored_touch.append(touch)
                return ScrollView.on_touch_down(self, touch)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """
        Si el touch fue un tap (se movió poco) sobre una línea:
        - línea NO seleccionada → la selecciona (activa);
        - línea YA seleccionada → entra en modo edición.
        Si hubo arrastre, se trata como scroll y no activa nada.
        La rueda del mouse (que Kivy emite como touch) se ignora para no
        seleccionar la línea al scrollear.
        """
        handled = super().on_touch_up(touch)

        # Ignorar la rueda del mouse (scroll), que no debe seleccionar
        if getattr(touch, 'button', None) in ('scrollup', 'scrolldown',
                                              'scrollleft', 'scrollright'):
            return handled

        start = touch.ud.get('md_down_pos')
        if start is not None and self.collide_point(*touch.pos):
            moved = abs(touch.pos[0] - start[0]) + abs(touch.pos[1] - start[1])
            if moved <= self._TAP_THRESHOLD:
                line = self._line_at(touch.pos)
                if line is not None:
                    editing = self._is_editing()
                    if 'shift' in Window.modifiers:
                        # Shift+Click extiende la selección hasta la línea
                        # clickeada (3e.2). Desde edición, sale a visualización.
                        if editing:
                            idx = self.state_manager.get_active_index()
                            if idx is not None:
                                self.state_manager.update_state(idx, editing=False)
                        self.extend_selection_to(line.index)
                    elif line.index == self.state_manager.get_active_index():
                        if not editing:
                            # click en la línea ya seleccionada → editar
                            # (cursor en el punto del click)
                            self.edit_line(line.index, click_pos=touch.pos)
                        # ya en edición: el TextInput recibe el touch y
                        # mueve el cursor solo
                    elif editing:
                        # click en otra línea estando en edición → mantener
                        # el modo: la actual confirma, la nueva entra a editar
                        self.edit_line(line.index, click_pos=touch.pos)
                    else:
                        # click en otra línea → seleccionar (fade)
                        self.activate_line(line.index)
        return handled

    def _line_at(self, window_pos):
        """Devuelve el MDDocumentLine bajo la posición (coords de ventana)."""
        for child in self.doc_lines_layout.children:
            if child.collide_point_to_window(*window_pos):
                return child
        return None

    def get_line_widget(self, index: int):
        """
        Devuelve el widget MDDocumentLine de la línea `index`.

        Punto único de acceso a los widgets de línea (groundwork para el
        reciclado del Inc 5): hoy devuelve de la lista `_line_widgets`; en el
        futuro, si la línea no está realizada, hará scroll + la creará.
        """
        if 0 <= index < len(self._line_widgets):
            return self._line_widgets[index]
        return None

    # ========================================================================
    # SINCRONIZACIÓN CON EVENTOS ESTRUCTURALES DEL STATEMANAGER (Inc 3c)
    # ========================================================================

    def _on_line_added(self, state_manager, event):
        """
        Una línea nueva se insertó en el StateManager: crea su fila y la agrega
        al layout y a `_line_widgets` en la posición correcta. El StateManager
        ya reindexó los line_states; las filas siguientes ajustan su índice solas
        (MDDocumentLine.index está bindeado a line_state.index).
        """
        index = event.index
        line_widget = self._create_line_widget(event.line_state)
        self.doc_lines_layout.add_widget(
            line_widget, index=self._layout_kivy_index(index))
        self._line_widgets.insert(index, line_widget)
        Logger.debug(f"MDDocumentEditor: line widget added at {index}")

    def _on_line_removed(self, state_manager, event):
        """
        Una línea se eliminó del StateManager: saca su fila del layout y de
        `_line_widgets`, y la libera (desbindea eventos globales).
        """
        index = event.index
        if not (0 <= index < len(self._line_widgets)):
            return
        line_widget = self._line_widgets.pop(index)
        self.doc_lines_layout.remove_widget(line_widget)
        line_widget.release()
        if self.active_line_widget is line_widget:
            self.active_line_widget = None
        Logger.debug(f"MDDocumentEditor: line widget removed at {index}")

    def _on_line_moved(self, state_manager, event):
        """
        Una línea se movió: reubica su fila en `_line_widgets` y en el layout.
        """
        from_index = event.old_index
        to_index = event.index
        if not (0 <= from_index < len(self._line_widgets)):
            return
        line_widget = self._line_widgets.pop(from_index)
        self._line_widgets.insert(to_index, line_widget)
        # Reordenar en el layout: quitar y re-agregar en la posición destino
        self.doc_lines_layout.remove_widget(line_widget)
        self.doc_lines_layout.add_widget(
            line_widget, index=self._layout_kivy_index(to_index))
        Logger.debug(
            f"MDDocumentEditor: line widget moved {from_index} -> {to_index}")

    # ========================================================================
    # ACTIVACIÓN DE LÍNEA
    # ========================================================================

    def activate_line(self, index: int, enter_edit_mode: bool = False, direction='fade'):
        """
        Activar una línea (Inc 1).

        Anima la des-selección de la línea previa y la selección de la nueva.
        Actualiza el estado en el StateManager (fuente de verdad del flag active).

        Args:
            index: Índice de la línea a activar
            enter_edit_mode: Si debe entrar en modo edición (Inc 2)
            direction: Animación de selección: 'fade' (click) o 'up'/'down'
                (navegación con flechas, deslizamiento).
        """
        old_index = self.state_manager.get_active_index()
        if old_index == index and self._selected_set == {index}:
            return  # ya está activa y es la única seleccionada

        # Selección simple: limpiar el verde de TODO el bloque seleccionado
        # anterior (para single es sólo la vieja activa; colapsa una multi-sel).
        for i in self._selected_set:
            if i != index:
                w = self.get_line_widget(i)
                if w is not None:
                    w.unselect(direction)

        # Actualizar estado (fuente de verdad)
        ok = self.state_manager.activate_line(index, enter_edit=enter_edit_mode)
        if not ok:
            return

        # Animar entrada de la nueva línea (si no estaba ya en verde)
        new_widget = self.get_line_widget(index)
        if new_widget is not None and index not in self._selected_set:
            new_widget.select(direction)
        self.active_line_widget = new_widget

        # Selección = {index}; sin ancla de multi-selección
        self._selected_set = {index}
        self._selection_anchor = None
        self._sync_selected_flags()

        # Marca este documento como destino del teclado para que las flechas
        # naveguen (el handler está a nivel Window). Foco fino entre paneles = Inc 4.
        self._kbd_active = True

        Logger.debug(f"MDDocumentEditor: Activated line {index}")

    # ========================================================================
    # SELECCIÓN MÚLTIPLE CONTIGUA (Shift+↑↓ / Shift+Click — Inc 3e)
    # ========================================================================

    def _sync_selected_flags(self):
        """Refleja `_selected_set` en los flags `selected` del StateManager."""
        self.state_manager.clear_selection()
        for i in self._selected_set:
            self.state_manager.select_line(i, multi=True)

    def extend_selection(self, direction: int) -> bool:
        """Extiende la selección contigua con Shift+↑↓ (mueve el extremo ±1)."""
        active = self.state_manager.get_active_index()
        if active is None:
            return False
        total = self.state_manager.get_total_lines()
        new_active = active + direction
        if not (0 <= new_active < total):
            return False  # borde del documento
        return self.extend_selection_to(new_active)

    def extend_selection_to(self, target: int) -> bool:
        """
        Extiende la selección contigua hasta `target` (Shift+↑↓ y Shift+Click).
        La primera vez fija el ancla en la línea activa; el bloque queda
        [min(ancla, target) .. max(ancla, target)] y el extremo activo va a target.
        """
        if not (0 <= target < self.state_manager.get_total_lines()):
            return False
        active = self.state_manager.get_active_index()
        if self._selection_anchor is None:
            self._selection_anchor = active if active is not None else target

        lo = min(self._selection_anchor, target)
        hi = max(self._selection_anchor, target)
        new_set = set(range(lo, hi + 1))

        # Diff visual del verde (fade para el bloque)
        for i in self._selected_set - new_set:
            w = self.get_line_widget(i)
            if w is not None:
                w.unselect('fade')
        for i in new_set - self._selected_set:
            w = self.get_line_widget(i)
            if w is not None:
                w.select('fade')
        self._selected_set = new_set

        # Mover el extremo activo (sin rehacer el verde de selección simple)
        self.state_manager.activate_line(target)
        self.active_line_widget = self.get_line_widget(target)
        self._sync_selected_flags()
        self._scroll_to_line(target)
        self._kbd_active = True
        return True

    def clear_multi_selection(self):
        """Escape: colapsa la selección múltiple a la línea activa."""
        active = self.state_manager.get_active_index()
        for i in self._selected_set:
            if i != active:
                w = self.get_line_widget(i)
                if w is not None:
                    w.unselect('fade')
        self._selected_set = {active} if active is not None else set()
        self._selection_anchor = None
        self._sync_selected_flags()

    def edit_line(self, index: int, click_pos=None, cursor_col=None,
                  reset_goal=True, direction='fade'):
        """
        Entrar en modo edición de una línea (Inc 2).

        Se asegura de que la línea esté activa (seleccionada) y luego pone
        editing=True en el LineState; el MDDocumentLine reacciona mostrando
        el editor en overlay.

        Args:
            index: Índice de la línea a editar.
            click_pos: posición (coords de ventana) del click que originó la
                edición; el cursor se ubica ahí (prioridad).
            cursor_col: columna destino del cursor (saltos de línea en edición).
            reset_goal: si True (edición nueva por click/F2/Enter), olvida la
                columna objetivo; los saltos ↑/↓ la manejan con reset_goal=False.
            Ambos hints None → cursor al final.
        """
        if reset_goal:
            self._edit_goal_col = None
            self._edit_last_placed = None
        line_widget = self.get_line_widget(index)
        if line_widget is not None:
            line_widget.set_edit_cursor_hint(click_pos, cursor_col)
        self.activate_line(index, direction=direction)  # fade (click) o slide (nav)
        self.state_manager.update_state(index, editing=True)
        Logger.debug(f"MDDocumentEditor: Editing line {index}")

    def _on_line_edit_nav(self, from_index: int, delta: int, cursor_col) -> bool:
        """
        Mueve la edición `delta` líneas desde `from_index` (callback de
        MDDocumentLine en edición). La línea que se deja confirma sus cambios
        (al desactivarse, editing=False → commit). Devuelve True si se movió.

        Args:
            cursor_col: columna destino — int (columna actual del cursor, para
                ↑/↓ con columna objetivo), 'end' (final de la línea destino,
                para ← en el borde) o 'start' (inicio, para → en el borde).
        """
        target = from_index + delta
        total = self.state_manager.get_total_lines()
        if not (0 <= target < total):
            return False  # borde del documento: no hace nada

        md_line = self.state_manager.get_md_line(target)
        tlen = len(md_line.md_text) if md_line is not None else 0

        if cursor_col == 'end':
            # ← en el borde: movimiento horizontal → reubica la columna objetivo
            col = tlen
            self._edit_goal_col = col
        elif cursor_col == 'start':
            # → en el borde: ídem
            col = 0
            self._edit_goal_col = col
        else:
            # ↑/↓: columna objetivo. Si el cursor actual difiere de donde lo
            # dejamos, el usuario se movió horizontal → reubica el objetivo;
            # si coincide, se mantiene (las líneas cortas no lo pisan).
            current = int(cursor_col)
            if self._edit_goal_col is None or current != self._edit_last_placed:
                self._edit_goal_col = current
            col = min(self._edit_goal_col, tlen)

        self._edit_last_placed = col
        # Slide direccional del gráfico de selección, como en modo selección
        direction = 'down' if delta > 0 else 'up'
        self.edit_line(target, cursor_col=col, reset_goal=False,
                       direction=direction)
        self._scroll_to_line(target)
        return True

    # ========================================================================
    # MOVER LÍNEA (Alt+↑↓, Inc 3c.3)
    # ========================================================================

    def _move_line(self, index, delta: int) -> bool:
        """
        Mueve la línea `index` `delta` posiciones (± clampado a los bordes).
        La línea movida conserva su estado (active/editing viajan con el
        LineState). Devuelve True si se movió.
        """
        if index is None:
            return False
        target = index + delta
        total = self.state_manager.get_total_lines()
        if not (0 <= target < total):
            return False  # borde del documento: no hace nada
        self.state_manager.move_line(index, target)  # reordena filas (on_line_moved)
        self._scroll_to_line(target)
        return True

    def move_selection(self, direction: int) -> bool:
        """
        Mueve el bloque seleccionado (1..n líneas contiguas) una posición
        (modo selección, Alt+↑↓, 3c.3/3e.3). Técnica: mover la línea del borde
        opuesto al otro lado del bloque (subir = la de arriba va abajo del
        bloque). La selección y el ancla se corren con el bloque.
        """
        if not self._selected_set:
            return False
        lo = min(self._selected_set)
        hi = max(self._selected_set)
        total = self.state_manager.get_total_lines()
        if direction < 0:
            if lo == 0:
                return False
            self.state_manager.move_line(lo - 1, hi)  # borde sup → debajo del bloque
            shift = -1
        else:
            if hi == total - 1:
                return False
            self.state_manager.move_line(hi + 1, lo)  # borde inf → arriba del bloque
            shift = 1

        # Corrimiento lógico del bloque (el verde acompaña a los widgets solos)
        self._selected_set = {i + shift for i in self._selected_set}
        if self._selection_anchor is not None:
            self._selection_anchor += shift
        active = self.state_manager.get_active_index()  # move_line ya lo repuso
        self.active_line_widget = self.get_line_widget(active)
        self._sync_selected_flags()
        self._scroll_to_line(active)
        return True

    def delete_selection(self) -> bool:
        """
        Borra las líneas del bloque seleccionado (Delete, 3e.3). Tras borrar,
        selecciona la línea que queda en la posición del borde superior.
        """
        if not self._selected_set:
            return False
        lo = min(self._selected_set)
        hi = max(self._selected_set)
        # Borrar de abajo hacia arriba para no correr los índices bajo los pies
        for i in range(hi, lo - 1, -1):
            self.state_manager.remove_line(i)
        self._selected_set = set()
        self._selection_anchor = None
        total = self.state_manager.get_total_lines()
        if total > 0:
            self.activate_line(min(lo, total - 1))
        else:
            self.active_line_widget = None
        return True

    # ------------------------------------------------------ portapapeles (3e.4)
    def _select_block(self, lo: int, hi: int):
        """Fija el bloque seleccionado [lo..hi] (verde), ancla en lo y activa hi."""
        new_set = set(range(lo, hi + 1))
        for i in self._selected_set - new_set:
            w = self.get_line_widget(i)
            if w is not None:
                w.unselect('fade')
        for i in new_set - self._selected_set:
            w = self.get_line_widget(i)
            if w is not None:
                w.select('fade')
        self._selected_set = new_set
        self._selection_anchor = lo
        self.state_manager.activate_line(hi)
        self.active_line_widget = self.get_line_widget(hi)
        self._sync_selected_flags()
        self._scroll_to_line(hi)
        self._kbd_active = True

    def _selection_texts(self):
        """md_text de las líneas seleccionadas, en orden."""
        return [self.state_manager.get_md_line(i).md_text
                for i in sorted(self._selected_set)]

    def copy_selection(self) -> bool:
        """
        Ctrl+C: copia el bloque. Guarda un clipboard interno estructurado
        (una entrada por línea, preserva md_text multilínea a futuro) y también
        el clipboard del sistema (unido por \\n) para interoperar con otras apps.
        """
        if not self._selected_set:
            return False
        from kivy.core.clipboard import Clipboard
        self._clipboard_lines = self._selection_texts()
        self._clipboard_sig = '\n'.join(self._clipboard_lines)
        Clipboard.copy(self._clipboard_sig)
        return True

    def cut_selection(self) -> bool:
        """Ctrl+X: copia el bloque y lo borra."""
        if not self._selected_set:
            return False
        self.copy_selection()
        self.delete_selection()
        return True

    def paste_clipboard(self) -> bool:
        """
        Ctrl+V: pega las líneas del portapapeles. Usa el clipboard interno
        (estructura exacta) si el del sistema no cambió; si vino de otra app,
        parsea su texto por líneas. Con **una** línea seleccionada inserta
        debajo de la activa; con **varias** reemplaza el bloque. Selecciona lo
        pegado.
        """
        from kivy.core.clipboard import Clipboard
        system_text = Clipboard.paste()
        if (self._clipboard_lines is not None
                and system_text == self._clipboard_sig):
            lines = list(self._clipboard_lines)   # estructura interna exacta
        else:
            if not system_text:
                return False
            lines = system_text.splitlines()       # texto externo
        if not lines:
            return False

        if len(self._selected_set) > 1:
            # Reemplazar el bloque: borrar y pegar en su posición
            lo = min(self._selected_set)
            hi = max(self._selected_set)
            for i in range(hi, lo - 1, -1):
                self.state_manager.remove_line(i)
            # Las líneas borradas ya no existen: limpiar el set (sus índices
            # apuntarían a otras líneas y _select_block des-seleccionaría mal).
            self._selected_set = set()
            insert_at = lo
        else:
            # Insertar debajo de la línea activa (o al final si no hay activa)
            active = self.state_manager.get_active_index()
            insert_at = (active + 1) if active is not None \
                else self.state_manager.get_total_lines()

        for offset, txt in enumerate(lines):
            new_md_line = MDLine(txt, None, None)
            new_md_line.update_type()
            self.state_manager.insert_line(insert_at + offset, new_md_line)

        self._select_block(insert_at, insert_at + len(lines) - 1)
        return True

    def _on_line_edit_move_line(self, index: int, delta: int):
        """
        Mueve la línea en edición (Alt+↑↓ con el input enfocado). Tras reordenar,
        re-enfoca el editor de la línea movida: el remove/add del widget en el
        layout le quita el foco (texto y cursor se conservan).
        """
        if not self._move_line(index, delta):
            return
        target = index + delta
        line_widget = self.get_line_widget(target)
        if line_widget is not None and line_widget.editor is not None:
            line_widget.editor.focus = True

    # ========================================================================
    # NAVEGACIÓN POR TÍTULOS (Ctrl+↑↓, etc. — Inc 3d)
    # ========================================================================

    def _go_to_title(self, direction: int, kind: str = 'any',
                     cursor_col=None) -> bool:
        """
        Mueve la selección al título anterior/siguiente. `direction` ±1.
        `kind`: 'any' (cualquier nivel), 'same' (mismo nivel que el título de
        referencia), 'parent' (nivel superior en la jerarquía).

        Conserva el modo: si `cursor_col` viene (veníamos de edición) edita el
        título destino manteniendo la columna del cursor (clampada a su largo);
        si es None (selección) lo selecciona. Devuelve True si se movió.
        """
        active = self.state_manager.get_active_index()
        if kind == 'any':
            predicate = None
        else:
            ref = self.state_manager.get_reference_title_level(active)
            if kind == 'same':
                predicate = lambda lvl: lvl == ref
            else:  # 'parent': primer título de nivel menor (más arriba en jerarquía)
                predicate = lambda lvl: 0 < lvl < ref
        target = self.state_manager.find_title_index(active, direction, predicate)
        if target is None:
            return False
        slide = 'down' if direction > 0 else 'up'
        if cursor_col is not None:
            # Conservar edición y columna del cursor (clampada en _place_cursor)
            self.edit_line(target, cursor_col=cursor_col, direction=slide)
        else:
            self.activate_line(target, direction=slide)
        self._scroll_to_line(target)
        return True

    def _on_line_edit_title_nav(self, direction: int, kind: str, cursor_col: int):
        """Navegación por títulos desde edición: edita el título manteniendo la columna."""
        self._go_to_title(direction, kind, cursor_col=cursor_col)

    def deactivate_current_line(self):
        """Desactivar la línea activa actual (delegado al StateManager)."""
        active_index = self.state_manager.get_active_index()
        if active_index is not None:
            self.state_manager.deactivate_line(active_index)
            self.active_line_widget = None
            Logger.debug(f"MDDocumentEditor: Deactivated line {active_index}")

    # ========================================================================
    # EVENTOS DE TECLADO (Etapa II)
    # ========================================================================

    # Key codes de Kivy para navegación
    _K_UP, _K_DOWN = 273, 274
    _K_PAGEUP, _K_PAGEDOWN = 280, 281
    _K_HOME, _K_END = 278, 279
    _K_ENTER, _K_NUMPAD_ENTER = 13, 271
    _K_F2 = 283
    _K_ESCAPE = 27
    _K_DELETE = 127
    _K_C, _K_X, _K_V = 99, 120, 118  # copiar / cortar / pegar (con Ctrl)

    def _is_editing(self) -> bool:
        """True si la línea activa está en modo edición."""
        idx = self.state_manager.get_active_index()
        if idx is None:
            return False
        state = self.state_manager.get_state(idx)
        return bool(state and state.editing)

    def _on_window_key_down(self, window, key, scancode, codepoint, modifiers):
        """
        Navegación por teclado a nivel Window (Inc 3a).

        No depende de que el widget tenga el foco de Kivy (por eso sobrevive a
        salir de edición con Escape/Enter). Sólo responde si el documento está
        en uso (`_kbd_active`) y NO se está editando (en edición las teclas van
        al MDLineTextInput).

        Args:
            key: código entero de la tecla.
            modifiers: lista de modificadores ('ctrl', 'shift', 'alt').

        Returns:
            bool: True si se manejó el evento.
        """
        if not self._kbd_active or self._is_editing():
            return False
        mods = modifiers or []

        if key == self._K_UP:
            if 'ctrl' in mods:  # Ctrl+↑ título (3d): +Shift mismo nivel
                return self._go_to_title(-1, 'same' if 'shift' in mods else 'any')
            if 'alt' in mods:            # Alt+Shift+↑ título padre (3d.3) / Alt+↑ mover (3c.3/3e.3)
                if 'shift' in mods:
                    return self._go_to_title(-1, 'parent')
                return self.move_selection(-1)
            if 'shift' in mods:          # Shift+↑ extiende la selección (3e.1)
                return self.extend_selection(-1)
            return self._navigate(-1)
        elif key == self._K_DOWN:
            if 'ctrl' in mods:  # Ctrl+↓ título (3d): +Shift mismo nivel
                return self._go_to_title(1, 'same' if 'shift' in mods else 'any')
            if 'alt' in mods:            # Alt+Shift+↓ título padre (3d.3) / Alt+↓ mover (3c.3/3e.3)
                if 'shift' in mods:
                    return self._go_to_title(1, 'parent')
                return self.move_selection(1)
            if 'shift' in mods:          # Shift+↓ extiende la selección (3e.1)
                return self.extend_selection(1)
            return self._navigate(1)
        elif key == self._K_PAGEUP:
            return self._navigate(-self._page_size())
        elif key == self._K_PAGEDOWN:
            return self._navigate(self._page_size())
        elif key == self._K_HOME and 'ctrl' in mods:
            self._go_to_line(0, 'up')
            return True
        elif key == self._K_END and 'ctrl' in mods:
            self._go_to_line(self.state_manager.get_total_lines() - 1, 'down')
            return True
        elif key in (self._K_ENTER, self._K_NUMPAD_ENTER, self._K_F2):
            # Enter o F2 sobre la línea activa → entrar en edición (Inc 3b).
            # F2 para salir de edición (toggle) y las flechas en edición son 3b.2.
            return self._edit_active_line()
        elif key == self._K_ESCAPE and len(self._selected_set) > 1:
            # Escape colapsa la selección múltiple a la línea activa (3e.1)
            self.clear_multi_selection()
            return True
        elif key == self._K_DELETE and self._selected_set:
            # Delete borra el bloque seleccionado (3e.3)
            return self.delete_selection()
        elif key == self._K_C and 'ctrl' in mods and self._selected_set:
            return self.copy_selection()          # Ctrl+C (3e.4)
        elif key == self._K_X and 'ctrl' in mods and self._selected_set:
            return self.cut_selection()           # Ctrl+X (3e.4)
        elif key == self._K_V and 'ctrl' in mods:
            return self.paste_clipboard()         # Ctrl+V (3e.4)
        return False

    def _edit_active_line(self) -> bool:
        """
        Entra en edición de la línea activa (cursor al final). Devuelve True si
        había línea activa (evento consumido), False si no.
        """
        index = self.state_manager.get_active_index()
        if index is None:
            return False
        self.edit_line(index)
        return True

    def _navigate(self, delta: int) -> bool:
        """
        Mueve la línea activa `delta` posiciones (+ abajo, - arriba), clampando
        a los bordes. Devuelve True (evento consumido).
        """
        total = self.state_manager.get_total_lines()
        if total == 0:
            return False

        current = self.state_manager.get_active_index()
        if current is None:
            target = 0 if delta > 0 else total - 1
        else:
            target = current + delta

        direction = 'down' if delta > 0 else 'up'
        self._go_to_line(target, direction)
        return True

    def _go_to_line(self, target: int, direction: str = 'fade'):
        """
        Activa la línea `target` (clampada a [0, total-1]) y la mantiene visible.
        Si ya es la activa, sólo asegura que esté a la vista.
        """
        total = self.state_manager.get_total_lines()
        if total == 0:
            return
        target = max(0, min(target, total - 1))
        if target != self.state_manager.get_active_index():
            self.activate_line(target, direction=direction)
        self._scroll_to_line(target)

    def _page_size(self) -> int:
        """
        Cantidad de líneas por 'página' ≈ alto del viewport / alto de línea,
        con un solapamiento de una línea. Mínimo 1.
        """
        ref_h = 30.0
        active = self.state_manager.get_active_index()
        widget = self.get_line_widget(active if active is not None else 0)
        if widget is not None and widget.height > 0:
            ref_h = widget.height
        return max(1, int(self.height / ref_h) - 1)

    def _scroll_to_line(self, index: int):
        """Scrollea para que la línea `index` quede visible en el viewport."""
        # Si el contenido entra completo en el viewport, no hay nada que
        # scrollear. Además scroll_to con contenido más chico que el viewport
        # divide por (alto_contenido - alto_viewport) < 0 y salta el documento.
        if self.doc_lines_layout.height <= self.height:
            return
        widget = self.get_line_widget(index)
        if widget is not None:
            self.scroll_to(widget, padding=dp(10), animate=True)

    # ========================================================================
    # UTILIDADES
    # ========================================================================

    def get_active_line_index(self) -> Optional[int]:
        """
        Obtener índice de la línea activa actual.

        Returns:
            int | None: Índice de línea activa o None
        """
        if self.active_line_widget:
            return self.active_line_widget.index
        return None

    def scroll_to_top(self):
        """Scrollear al top del documento."""
        self.scroll_y = 1.0

    def scroll_to_bottom(self):
        """Scrollear al bottom del documento."""
        self.scroll_y = 0.0

    def __repr__(self) -> str:
        """Representación string del editor."""
        # Protección: __repr__ puede ser llamado antes de __init__ completo
        if not hasattr(self, 'md_document') or not hasattr(self, 'state_manager'):
            return "MDDocumentEditor(initializing...)"

        doc_name = self.md_document.doc_name if self.md_document else 'None'
        active_index = self.get_active_line_index()
        lines = self.state_manager.get_total_lines()

        return (
            f"MDDocumentEditor("
            f"document={doc_name}, "
            f"lines={lines}, "
            f"active_line={active_index}"
            f")"
        )
