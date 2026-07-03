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

from logging import ERROR
from typing import Optional
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import FocusBehavior
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from pygments.unistring import No

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
        # Config: ubicación del editor en modo edición ('overlay' | 'below')
        self.editor_placement = EDITOR_PLACEMENT_BELOW
        # self.md_document: Optional[MDDocument] = None  md_document esta en state_manager?
        self.last_scroll_y = 1.0

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

        # Mapa index -> MDDocumentLine (poblado en populate_md_lines)
        self._line_widgets = {}

        self.add_widget(self.doc_lines_layout)

        # ====================================================================
        # Bind eventos
        # ====================================================================
        self.bind(scroll_y=self._on_scroll)
        self.bind(size=self._on_size_changed)

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

    def initialize_document(self):
        """
        Inicializa/resetea el documento a estado vacío.

        Limpia:
        - Filas de líneas (widgets) y su mapa
        - StateManager
        - Referencia a la línea activa
        """
        # Limpiar widgets de línea
        if self.doc_lines_layout:
            self.doc_lines_layout.clear_widgets()
        self._line_widgets = {}

        # Limpiar estado
        if self.state_manager:
            self.state_manager._clear_all()

        # Resetear referencia a línea activa
        self.active_line_widget = None

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
        # Limpiar lo anterior para no duplicar (Inc 0).
        self.doc_lines_layout.clear_widgets()
        self._line_widgets = {}

        for line_state in self.state_manager.get_line_states():
            line_widget = MDDocumentLine(line_state, placement=self.editor_placement)
            self.doc_lines_layout.add_widget(line_widget)
            self._line_widgets[line_state.index] = line_widget

        Logger.info(f"MDDocumentEditorV2: Document populated with {len(md_lines)} lines")

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
        """Registra el inicio del touch para distinguir tap de scroll."""
        if self.collide_point(*touch.pos):
            touch.ud['md_down_pos'] = touch.pos
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """
        Si el touch fue un tap (se movió poco) sobre una línea, la activa.
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
                    if getattr(touch, 'is_double_tap', False):
                        self.edit_line(line.index)
                    else:
                        self.activate_line(line.index)  # click -> fade
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
        reciclado del Inc 5): hoy devuelve del mapa `_line_widgets`; en el
        futuro, si la línea no está realizada, hará scroll + la creará.
        """
        return self._line_widgets.get(index)

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
        if old_index == index:
            return  # ya está activa

        # Animar salida de la línea previa
        if old_index is not None:
            old_widget = self.get_line_widget(old_index)
            if old_widget is not None:
                old_widget.unselect(direction)

        # Actualizar estado (fuente de verdad)
        ok = self.state_manager.activate_line(index, enter_edit=enter_edit_mode)
        if not ok:
            return

        # Animar entrada de la nueva línea
        new_widget = self.get_line_widget(index)
        if new_widget is not None:
            new_widget.select(direction)
        self.active_line_widget = new_widget

        # Marca este documento como destino del teclado para que las flechas
        # naveguen (el handler está a nivel Window). Foco fino entre paneles = Inc 4.
        self._kbd_active = True

        Logger.debug(f"MDDocumentEditor: Activated line {index}")

    def edit_line(self, index: int):
        """
        Entrar en modo edición de una línea (Inc 2).

        Se asegura de que la línea esté activa (seleccionada) y luego pone
        editing=True en el LineState; el MDDocumentLine reacciona mostrando
        el editor en overlay.
        """
        self.activate_line(index)  # selecciona si no lo estaba (fade)
        self.state_manager.update_state(index, editing=True)
        Logger.debug(f"MDDocumentEditor: Editing line {index}")

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
            return self._navigate(-1)
        elif key == self._K_DOWN:
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
        return False

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
