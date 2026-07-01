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
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from pygments.unistring import No

# Importar ThemableBehavior
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.wg_markdown2.widgets.md_labels import MDTextLabel
from kivy_mpbe_widgets.wg_markdown2.widgets.md_document_line import MDDocumentLine

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
            line_widget = MDDocumentLine(line_state)
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
                    self.activate_line(line.index, anim_from=touch.pos)
        return handled

    def _line_at(self, window_pos):
        """Devuelve el MDDocumentLine bajo la posición (coords de ventana)."""
        for child in self.doc_lines_layout.children:
            if child.collide_point_to_window(*window_pos):
                return child
        return None

    # ========================================================================
    # ACTIVACIÓN DE LÍNEA
    # ========================================================================

    def activate_line(self, index: int, enter_edit_mode: bool = False, anim_from=None):
        """
        Activar una línea (Inc 1).

        Anima la des-selección de la línea previa y la selección de la nueva
        (verde, expandiéndose desde anim_from). Actualiza el estado en el
        StateManager (fuente de verdad del flag active).

        Args:
            index: Índice de la línea a activar
            enter_edit_mode: Si debe entrar en modo edición (Inc 2)
            anim_from: Posición (coords de ventana) desde donde expandir la
                animación de selección. Si es None, se anima desde el centro.
        """
        old_index = self.state_manager.get_active_index()
        if old_index == index:
            return  # ya está activa

        # Animar salida de la línea previa
        if old_index is not None:
            old_widget = self._line_widgets.get(old_index)
            if old_widget is not None:
                old_widget.unselect(anim_from)

        # Actualizar estado (fuente de verdad)
        ok = self.state_manager.activate_line(index, enter_edit=enter_edit_mode)
        if not ok:
            return

        # Animar entrada de la nueva línea
        new_widget = self._line_widgets.get(index)
        if new_widget is not None:
            new_widget.select(anim_from)
        self.active_line_widget = new_widget

        Logger.debug(f"MDDocumentEditor: Activated line {index}")

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

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        Manejo de eventos de teclado.

        Etapa I: Placeholder (no funcional todavía)
        Etapa II: Arrow Up/Down, Page Up/Down, etc.

        Args:
            window: Ventana de Kivy
            keycode: Código de tecla (int, str)
            text: Texto de la tecla
            modifiers: Modificadores (Shift, Ctrl, Alt)

        Returns:
            bool: True si se manejó el evento, False si no
        """
        # TODO Etapa II: Implementar navegación con teclado
        return False

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
