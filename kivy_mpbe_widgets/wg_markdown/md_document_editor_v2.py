#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_document_editor_v2.py
#
#  MDDocumentEditor V2 - Refactorizado con StateManager y Service Layer
#
#  Created on 25/12/2024
#  @author: mpbe
#

# VERSION ULTIMA 2025-12-25 OPTIMIZADO POR CLAUDE


"""
MDDocumentEditorV2 - Editor de Documentos Markdown Refactorizado

Versión completamente refactorizada con:
- ✅ StateManager para gestión centralizada de estado (Fase 1)
- ✅ Service Layer para lógica de negocio (Fase 2)
- ✅ Código limpio sin comentarios obsoletos
- ✅ Arquitectura clara y mantenible

Diferencias con versión anterior (MDDocumentEditor):
- NO tiene variables de estado fragmentadas (_active_index, _selected_indexs, etc.)
- NO tiene código comentado masivo
- SÍ tiene estado centralizado en StateManager
- SÍ tiene lógica de negocio en Services
- SÍ tiene métodos simples y claros
"""

# Imports del sistema
import sys
from pathlib import Path
from typing import Optional, List, Dict, Set, Tuple

# Configurar paths
project_root = Path(__file__).parent
helpers_root = Path.home() / 'Documentos' / 'Programacion' / 'Programacion_lin' / 'Visual_Studio_Code' / 'helpers_mpbe_prj'
widgets_root = Path.home() / 'Documentos' / 'Programacion' / 'Programacion_lin' / 'Visual_Studio_Code' / 'kivy_mpe_widgets_prj'

for path in [project_root, helpers_root, widgets_root]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Imports del proyecto
from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager, StateChangeEvent, LineState
from kivy_mpbe_widgets.wg_markdown.services.line_service import LineService
from kivy_mpbe_widgets.wg_markdown.services.selection_service import SelectionService
from kivy_mpbe_widgets.wg_markdown.services.navigation_service import NavigationService
from kivy_mpbe_widgets.wg_markdown.services.filter_service import FilterService

# Imports de helpers_mpbe
from helpers_mpbe.markdown_document.md_document import MDDocument, MDLine
from helpers_mpbe.markdown_document import MD_LINE_TYPE

# Imports de Kivy
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
from kivy.logger import Logger

# Imports de kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.wg_undo.undo_manager import UndoManager
from kivy_mpbe_widgets.graphics.widget_graphics import GBorder, GFocus
from kivy_mpbe_widgets.wg_markdown.md_line_editors_v2 import MDDocumentLineEditor

# Define KV layout
kv = """
<MDDocumentEditor>:
    viewclass: 'MDDocumentLineEditor'
    SelectableRecycleBoxLayout:
        id: srblayout
        default_size: None, dp(30)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
"""
Builder.load_string(kv)


class SelectableRecycleBoxLayout(RecycleBoxLayout):
    """Layout para RecycleView de líneas de documento."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MDDocumentEditor(FocusBehavior, ThemableBehavior, RecycleView):
    """
    Editor de documentos Markdown refactorizado con StateManager y Services.

    Esta versión reemplaza completamente la arquitectura antigua de
    gestión de estado con una arquitectura limpia y moderna.

    Características:
    - ✅ FASE 1: Estado centralizado en DocumentStateManager
    - ✅ FASE 2: Lógica de negocio en Services (Line, Selection, Navigation)
    - ✅ FASE 3: Sistema de filtrado completo con FilterService
    - Código limpio sin deuda técnica
    - API pública clara y simple
    - Fácil de testear y mantener

    Attributes:
        state_manager (DocumentStateManager): Gestor de estado centralizado
        line_service (LineService): Servicio para operaciones de líneas
        selection_service (SelectionService): Servicio para selección
        navigation_service (NavigationService): Servicio para navegación
        filter_service (FilterService): Servicio para filtrado (FASE 3)
        undo_manager (UndoManager): Gestor de undo/redo
        filter (bool): Si hay filtro activo
        filter_txt (str): Texto del filtro
        filter_up (bool): Si incluye padres en filtro (títulos jerárquicos)
    """

    # Properties de Kivy
    filter = BooleanProperty(False)
    filter_txt = StringProperty('')
    filter_up = BooleanProperty(False)

    def __init__(self, activate_background=True, flat=False, **kwargs):
        """
        Inicializa el editor de documentos V2.

        Args:
            activate_background: Si activa cambio de tonalidad en fondo
            flat: Si usa diseño plano (sin bordes)
            **kwargs: Argumentos adicionales para RecycleView
        """
        # Inicializar clases base
        FocusBehavior.__init__(self)
        ThemableBehavior.__init__(self)
        RecycleView.__init__(self, **kwargs)

        # Configuración visual
        self.flat = flat
        self.activate_background = activate_background

        # ✅ FASE 1: StateManager
        self.state_manager = DocumentStateManager(enable_history=False)
        self.state_manager.subscribe(self._on_line_state_changed)

        # ✅ FASE 2: Services (se inicializan al cargar documento)
        self.line_service: Optional[LineService] = None
        self.selection_service: Optional[SelectionService] = None
        self.navigation_service: Optional[NavigationService] = None

        # ✅ FASE 3: FilterService
        self.filter_service: Optional[FilterService] = None

        # UndoManager
        self.undo_manager = UndoManager()

        # Data del documento
        self._md_lines: Optional[List[MDLine]] = None
        self.data_items: Dict = {}

        # Referencias UI
        self.layout = None  # Se asigna después del build

        # Gráficos (borde y foco)
        with self.canvas.after:
            if not self.flat:
                self.graphic_border = GBorder(self)
            self.graphic_focus = GFocus(self)

        # Bind keyboard
        Window.bind(on_key_down=self._on_keyboard_down)

        Logger.info("MDDocumentEditorV2: Initialized")

    def on_kv_post(self, base_widget):
        """Llamado después de que el KV se ha construido."""
        super().on_kv_post(base_widget)
        self.layout = self.ids.srblayout

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
        self._md_lines = None

        # Limpiar undo
        self.undo_manager.clear_stack()

        # Limpiar estado
        if self.state_manager:
            self.state_manager.clear_all()

        # Resetear services
        self.line_service = None
        self.selection_service = None
        self.navigation_service = None

        Logger.info("MDDocumentEditorV2: Document initialized")

    def populate_from_md_lines(self, md_lines: List[MDLine]):
        """
        Carga el documento desde una lista de MDLine.

        Esta es la función principal para cargar contenido en el editor.

        Args:
            md_lines: Lista de líneas del documento markdown

        Side Effects:
            - Inicializa estados en StateManager
            - Crea services
            - Popula RecycleView.data con estados
        """
        if not md_lines:
            Logger.warning("MDDocumentEditorV2: populate_from_md_lines with empty list")
            self.initialize_document()
            return

        # Guardar referencia a md_lines
        self._md_lines = md_lines

        # ✅ FASE 1: Inicializar estados
        self.state_manager.initialize_states(len(md_lines))
        Logger.info(f"MDDocumentEditorV2: Initialized {len(md_lines)} line states")

        # ✅ FASE 2: Crear services
        self._initialize_services()

        # Crear data_items (para filtros)
        self._create_data_items()

        # Aplicar filtros y actualizar RecycleView.data
        self.apply_data_items()

        # NO ESTA CREANDO LOS MDDocumentLineEditor

        Logger.info(f"MDDocumentEditorV2: Document populated with {len(md_lines)} lines")

    def _initialize_services(self):
        """Crea instancias de los services."""
        if not self._md_lines:
            Logger.warning("MDDocumentEditorV2: Cannot initialize services without md_lines")
            return

        self.line_service = LineService(
            state_manager=self.state_manager,
            md_lines=self._md_lines
        )

        self.selection_service = SelectionService(
            state_manager=self.state_manager,
            md_lines=self._md_lines
        )

        self.navigation_service = NavigationService(
            state_manager=self.state_manager,
            md_lines=self._md_lines
        )

        self.filter_service = FilterService(
            state_manager=self.state_manager,
            md_lines=self._md_lines
        )

        Logger.info("MDDocumentEditorV2: Services initialized (including FilterService)")

    def _create_data_items(self):
        """
        Crea data_items (diccionario completo antes de filtros).

        data_items es la fuente de verdad, self.data es la vista filtrada.
        """
        if not self._md_lines:
            return

        self.data_items = {}

        for index, md_line in enumerate(self._md_lines):
            # ✅ Obtener estado del StateManager
            state = self.state_manager.get_state(index)

            # Crear data item
            data_item = {
                'index': index,
                'md_line': md_line,
                'state': state,
                # Aquí se pueden agregar más propiedades
                # show, themed, etc.
                # TODO: agregar propiedades faltantes. show y themed
            }

            self.data_items[index] = data_item
        pass

    def apply_data_items(self):
        """
        Aplica filtros y actualiza RecycleView.data usando FilterService.

        Si hay filtro activo, usa FilterService para filtrar.
        Si no, muestra todos los data_items.
        """
        if not self.data_items or not self.filter_service:
            self.data = []
            return

        if self.filter and self.filter_txt.strip():
            # ✅ FASE 3: Usar FilterService para filtrar
            matching_indices = self.filter_service.filter_by_text(
                filter_text=self.filter_txt,
                case_sensitive=False,
                include_parents=self.filter_up  # ✅ Incluir títulos padre si está activado
            )

            # Aplicar filtro al StateManager (actualizar visibilidad)
            visible_count = self.filter_service.apply_filter(
                matching_indices=matching_indices,
                hide_non_matching=True
            )

            # Construir self.data solo con líneas visibles
            filtered_data = []
            for index in matching_indices:
                if index in self.data_items:
                    data_item = self.data_items[index]
                    # Actualizar estado en data_item
                    data_item['state'] = self.state_manager.get_state(index)
                    filtered_data.append(data_item)

            self.data = filtered_data
            Logger.info(
                f"MDDocumentEditorV2: Filter applied via FilterService, "
                f"{visible_count} lines visible (filter_up={self.filter_up})"
            )

        else:
            # ✅ Sin filtro: limpiar filtro y mostrar todo
            if self.filter_service:
                self.filter_service.clear_filter()

            # Copiar todos los data_items a self.data
            self.data = list(self.data_items.values())
            Logger.debug(f"MDDocumentEditorV2: All {len(self.data)} lines visible")

    # ==========================================================================
    # FASE 1: Callbacks de StateManager
    # ==========================================================================

    def _on_line_state_changed(self, event: StateChangeEvent):
        """
        Callback ejecutado cuando cambia el estado de una línea.

        Actualiza tanto data_items como RecycleView.data para que
        los widgets se refresquen automáticamente.

        OPTIMIZACIÓN: Si solo cambió hotlight, NO actualizar RecycleView.data
        porque eso causa refresh innecesarios en cada movimiento del mouse.
        El hotlight se maneja localmente en el widget.

        Args:
            event: Evento con información del cambio
        """
        Logger.debug(
            f"MDDocumentEditorV2: State changed for line {event.index}: "
            f"{event.changed_attributes}"
        )

        # 1. Actualizar data_item (diccionario completo - siempre)
        if event.index in self.data_items:
            self.data_items[event.index]['state'] = event.new_state

        # 2. Verificar si solo cambió hotlight
        # Si solo cambió hotlight, NO actualizar RecycleView.data
        # para evitar refresh innecesarios
        if event.changed_attributes == {'hotlight'}:
            Logger.debug(
                f"MDDocumentEditorV2: Hotlight changed for line {event.index}, "
                f"skipping RecycleView.data update (handled locally)"
            )
            return

        # 3. Actualizar RecycleView.data (lista filtrada visible)
        # Solo para cambios importantes (active, editing, selected, visible, etc.)
        updated = False
        for i, item in enumerate(self.data):
            if item.get('index') == event.index:
                # Crear nuevo diccionario con estado actualizado
                # IMPORTANTE: Crear nuevo dict para que RecycleView detecte el cambio
                updated_item = {
                    'index': event.index,
                    'md_line': self.data_items[event.index]['md_line'],
                    'state': event.new_state
                }

                # Reemplazar en self.data
                self.data[i] = updated_item
                updated = True

                Logger.info(
                    f"MDDocumentEditorV2: Updated RecycleView.data[{i}] for line {event.index}"
                )
                break

        if not updated:
            Logger.debug(
                f"MDDocumentEditorV2: Line {event.index} not in visible data "
                f"(may be filtered out)"
            )

    def _get_widget_at_index(self, index: int) -> Optional[MDDocumentLineEditor]:
        """
        Obtiene el widget en el índice especificado.

        Args:
            index: Índice de la línea

        Returns:
            Widget o None si no está visible
        """
        if not self.layout or not self.layout.children:
            return None

        for child in self.layout.children:
            if hasattr(child, 'index') and child.index == index:
                return child

        return None

    # ==========================================================================
    # FASE 2: Eventos con Services
    # ==========================================================================

    def handle_touch_left_up_event(self, index: int, view, touch):
        """
        Maneja click izquierdo en una línea.

        Args:
            index: Índice de la línea
            view: Widget clickeado
            touch: Evento de touch
        """
        if not self.line_service:
            Logger.warning("MDDocumentEditorV2: LineService not initialized")
            return

        # Calcular cursor desde touch
        cursor_pos = (0, 0)
        try:
            if hasattr(view, 'wg_line_editor'):
                local_pos = view.to_local(*touch.pos)
                cursor_pos = view.wg_line_editor.md_editor.get_cursor_from_xy(*local_pos)
        except Exception as e:
            Logger.debug(f"MDDocumentEditorV2: Could not get cursor: {e}")

        # ✅ Usar LineService
        # Click siempre usa animación 'fade'
        success = self.line_service.activate_line(
            index=index,
            enter_edit=True,
            cursor_pos=cursor_pos,
            anim_type='fade'
        )

        if not success:
            Logger.info(f"MDDocumentEditorV2: Line {index} is not editable")

    def handle_hotlight_event(self, index: int, state: bool):
        """
        Maneja evento de hotlight (mouse over).

        Args:
            index: Índice de la línea
            state: True si entra, False si sale
        """
        if not self.state_manager:
            return

        self.state_manager.set_hotlight(index, state)

    def _on_keyboard_down(self, window, key, scancode, codepoint, modifiers):
        """
        Maneja eventos de teclado.

        Args:
            window: Ventana de Kivy
            key: Código de tecla
            scancode: Scancode
            codepoint: Codepoint
            modifiers: Modificadores (ctrl, shift, alt)
        """
        # Solo procesar si tiene el foco
        if not self.focus:
            return False

        # Tecla Enter: Insertar línea abajo
        if key == 13:  # Enter
            return self._on_keyboard_enter()

        # Tecla Delete: Eliminar línea
        if key == 127:  # Delete
            return self._on_keyboard_delete()

        # Flecha abajo: Navegar abajo
        if key == 274:  # Down arrow
            return self._on_keyboard_arrow_down(modifiers)

        # Flecha arriba: Navegar arriba
        if key == 273:  # Up arrow
            return self._on_keyboard_arrow_up(modifiers)

        return False

    def _on_keyboard_enter(self) -> bool:
        """Maneja tecla Enter."""
        if not self.line_service:
            return False

        active_index = self.state_manager.get_active_index()
        if active_index is None:
            return False

        # Insertar línea abajo
        new_index = self.line_service.insert_line_below(
            index=active_index,
            text="",
            line_type=MD_LINE_TYPE.TEXT
        )

        # Actualizar data
        self._create_data_items()
        self.apply_data_items()

        # Activar nueva línea
        self.line_service.activate_line(new_index, enter_edit=True)

        Logger.info(f"MDDocumentEditorV2: Inserted new line at {new_index}")
        return True

    def _on_keyboard_delete(self) -> bool:
        """Maneja tecla Delete."""
        if not self.line_service:
            return False

        active_index = self.state_manager.get_active_index()
        if active_index is None:
            return False

        # Eliminar línea
        success = self.line_service.delete_line(active_index)

        if success:
            # Actualizar data
            self._create_data_items()
            self.apply_data_items()

            Logger.info(f"MDDocumentEditorV2: Deleted line {active_index}")

        return success

    def _on_keyboard_arrow_down(self, modifiers) -> bool:
        """Maneja flecha abajo."""
        if not self.navigation_service or not self.line_service:
            return False

        # Ctrl+Down: Ir a siguiente título
        if 'ctrl' in modifiers:
            next_title = self.navigation_service.navigate_to_next_title()
            if next_title is not None:
                self.line_service.activate_line(next_title)
                return True
            return False

        # Down simple: Siguiente línea
        next_index = self.navigation_service.navigate_to_next_line()
        if next_index is not None:
            self.line_service.activate_line(next_index, enter_edit=True)
            return True

        return False

    def _on_keyboard_arrow_up(self, modifiers) -> bool:
        """Maneja flecha arriba."""
        if not self.navigation_service or not self.line_service:
            return False

        # Ctrl+Up: Ir a título anterior
        if 'ctrl' in modifiers:
            prev_title = self.navigation_service.navigate_to_previous_title()
            if prev_title is not None:
                self.line_service.activate_line(prev_title)
                return True
            return False

        # Up simple: Línea anterior
        prev_index = self.navigation_service.navigate_to_previous_line()
        if prev_index is not None:
            self.line_service.activate_line(prev_index, enter_edit=True)
            return True

        return False

    # ==========================================================================
    # Callbacks de Properties
    # ==========================================================================

    def on_filter(self, instance, value):
        """Callback cuando cambia el estado del filtro."""
        Logger.info(f"MDDocumentEditorV2: Filter changed to {value}")
        self.apply_data_items()

    def on_filter_txt(self, instance, value):
        """Callback cuando cambia el texto del filtro."""
        Logger.info(f"MDDocumentEditorV2: Filter text changed to '{value}'")
        if self.filter:
            self.apply_data_items()

    def on_filter_up(self, instance, value):
        """Callback cuando cambia incluir padres en filtro."""
        Logger.info(f"MDDocumentEditorV2: Filter include parents changed to {value}")
        if self.filter:
            self.apply_data_items()

    # ==========================================================================
    # API Pública - Filtrado
    # ==========================================================================

    def apply_filter(self, filter_text: str = '', include_parents: bool = False):
        """
        Aplica filtro al documento.

        Args:
            filter_text: Texto a buscar
            include_parents: Si True, incluye títulos padre en resultados

        Side Effects:
            Actualiza filter, filter_txt y filter_up, lo que dispara apply_data_items()
        """
        self.filter = bool(filter_text.strip())
        self.filter_txt = filter_text
        self.filter_up = include_parents
        # Los on_filter callbacks se encargan de llamar apply_data_items()

    def clear_filter(self):
        """
        Limpia el filtro activo.

        Side Effects:
            Resetea filter, filter_txt y filter_up, mostrando todas las líneas
        """
        self.filter = False
        self.filter_txt = ''
        self.filter_up = False
        # El on_filter callback se encarga de llamar apply_data_items()

    # ==========================================================================
    # API Pública
    # ==========================================================================

    def scroll_to_index(self, index: int):
        """
        Hace scroll para mostrar la línea en el índice.

        Args:
            index: Índice de la línea
        """
        if self.layout:
            self.scroll_to_index(index)

    def validate_state(self) -> bool:
        """
        Valida el estado del documento.

        Returns:
            bool: True si todos los invariantes son válidos
        """
        if not self.state_manager:
            return True

        return self.state_manager.validate_invariants()

    def print_state_summary(self):
        """Imprime resumen del estado (debug)."""
        if self.state_manager:
            self.state_manager.print_state_summary()

    def __repr__(self) -> str:
        """
        Representación legible del editor.

        Usa getattr con defaults para evitar AttributeError durante
        la inicialización cuando Kivy hace logging/trace antes de que
        todas las variables estén inicializadas.
        """
        # Usar getattr con defaults para evitar AttributeError durante inicialización
        md_lines = getattr(self, '_md_lines', None)
        state_manager = getattr(self, 'state_manager', None)
        filter_val = getattr(self, 'filter', False)

        lines = len(md_lines) if md_lines else 0
        active = state_manager.get_active_index() if state_manager else None
        selected = len(state_manager.get_selected_indices()) if state_manager else 0

        return (
            f"MDDocumentEditorV2("
            f"lines={lines}, "
            f"active={active}, "
            f"selected={selected}, "
            f"filter={filter_val}"
            f")"
        )
