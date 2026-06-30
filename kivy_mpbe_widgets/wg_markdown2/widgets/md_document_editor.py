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
from kivy.uix.boxlayout import BoxLayout
from pygments.unistring import No

# Importar ThemableBehavior
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.wg_markdown2.widgets.md_labels import MDTextLabel

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
            orientation='vertical', size_hint_min_y=None, spacing=0, padding=0
        )

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
        Inicializa/resetea el documento.

        Limpia:
        - Data del RecycleView
        - Undo manager
        - StateManager
        - Services
        """
        self.data_items = {}
        self.data = []
        # self._md_lines = None

        # Limpiar undo
        self.undo_manager.clear_stack()

        # Limpiar estado
        if self.state_manager:
            self.state_manager._clear_all()

        # Resetear services
        self.line_service = None
        self.selection_service = None
        self.navigation_service = None

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

        # Guardar referencia a md_lines
        # self._md_lines = md_lines
        md_lines = md_document.md_lines

        # ✅ FASE 1: Inicializar estados
        self.state_manager.set_document(md_document)
        Logger.info(f"MDDocumentEditorV2: Initialized {len(md_lines)} line states")

        # TODO: SEGUIR Y VER DONDE ASIGNA LAS LINEAS AL WIDGET

        # # ✅ FASE 2: Crear services
        # TODO: Aplicar Filtros o limpiar filtros existentes?

        # Crea y agrega los Labels doc_lines_layout

        # TODO: Deberia estar en self._refresh_visible_widgets y usar lineas visibles

        for line_state in self.state_manager.get_line_states():
            
            print(f"Creating widget for line {line_state.index}: {line_state.get_md_text()[:30]}...")
            
            widget_lbl = line_state.widget_type(md_text=line_state.get_md_text())
            if widget_lbl is None:
                Logger.warning(f"MDDocumentEditorV2: No widget type for line {line_state.index}, using default MDTextLabel")
                widget_lbl = MDTextLabel(md_text=line_state.get_md_text())

            self.doc_lines_layout.add_widget(widget_lbl)


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
        # Obtener dimensiones actuales
        scroll_y = self.scroll_y
        viewport_height = self.height

        # Preguntar al StateManager QUÉ mostrar
        visible_indices = self.state_manager.get_visible_in_viewport(
            scroll_y=scroll_y,
            viewport_height=viewport_height
        )

        # Delegar actualización al layout


        # TODO: Traer desde state_manager las líneas visibles, y luego iterar sobre los widgets en doc_lines_layout para mostrar/ocultar según corresponda. Esto se puede hacer comparando los índices de las líneas con los índices de los widgets actualmente en doc_lines_layout, y mostrando solo aquellos que estén en visible_indices.
        # self.doc_lines_layout.update_visible_range(visible_indices)  No existe esta funcion. 
        # Buscar en StateManager qué líneas deberían estar visibles, y luego iterar sobre los widgets en doc_lines_layout para mostrar/ocultar según corresponda. Esto se puede hacer comparando los índices de las líneas con los índices de los widgets actualmente en doc_lines_layout, y mostrando solo aquellos que estén en visible_indices.

        # No se si hacer aca o llamar a populate pasando las lineas a mostar
        for line_state in self.state_manager.get_line_states():
            
            print(f"Creating widget for line {line_state.index}: {line_state.get_md_text()[:30]}...")
            
            widget_lbl = line_state.widget_type(md_text=line_state.get_md_text())
            if widget_lbl is None:
                Logger.warning(f"MDDocumentEditorV2: No widget type for line {line_state.index}, using default MDTextLabel")
                widget_lbl = MDTextLabel(md_text=line_state.get_md_text())

            self.doc_lines_layout.add_widget(widget_lbl)

    # ========================================================================
    # ACTIVACIÓN DE LÍNEA (Etapa I - Básico)
    # ========================================================================

    def activate_line(self, index: int, enter_edit_mode: bool = False):
        """
        Activar una línea.

        Etapa I: Solo visual, sin modo edición funcional.

        Args:
            index: Índice de la línea a activar
            enter_edit_mode: Si debe entrar en modo edición (Etapa II)

        Note:
            En Etapa I, enter_edit_mode se ignora. Solo activa visualmente.
        """
        Logger.info(f"MDDocumentEditor: Activating line {index}")

        # 1. Desactivar línea anterior
        if self.active_line_widget:
            old_index = self.active_line_widget.index

            # Desactivar visualmente
            self.active_line_widget.active = False
            if hasattr(self.active_line_widget, 'graphic_select'):
                self.active_line_widget.graphic_select.show(False)

            # Actualizar estado en StateManager
            self.state_manager.update_state(
                old_index,
                active=False,
                editing=False
            )

            Logger.debug(f"MDDocumentEditor: Deactivated line {old_index}")

        # 2. Obtener widget de nueva línea
        widget = self.doc_lines_layout.get_widget(index)

        if not widget:
            Logger.warning(
                f"MDDocumentEditor: Cannot activate line {index}, "
                f"widget not in viewport"
            )
            # TODO Etapa II: Forzar scroll y creación de widget
            return

        # 3. Activar visualmente
        widget.active = True
        if hasattr(widget, 'graphic_select'):
            widget.graphic_select.show(True)

        # 4. Actualizar estado en StateManager
        self.state_manager.update_state(
            index,
            active=True,
            editing=enter_edit_mode
        )

        # 5. Guardar referencia
        self.active_line_widget = widget

        Logger.debug(f"MDDocumentEditor: Activated line {index}")

    def deactivate_current_line(self):
        """
        Desactivar la línea activa actual.
        """
        if self.active_line_widget:
            old_index = self.active_line_widget.index

            # Desactivar visualmente
            self.active_line_widget.active = False
            if hasattr(self.active_line_widget, 'graphic_select'):
                self.active_line_widget.graphic_select.show(False)

            # Actualizar estado
            self.state_manager.update_state(
                old_index,
                active=False,
                editing=False
            )

            self.active_line_widget = None

            Logger.debug(f"MDDocumentEditor: Deactivated line {old_index}")

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
