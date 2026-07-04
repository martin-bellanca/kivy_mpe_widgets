#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DocumentStateManager - Gestor centralizado de estados (Single Source of Truth)

Este módulo implementa el DocumentStateManager, que es la única fuente de verdad
para todos los estados de líneas del documento.

Arquitectura V6:
- Hereda de EventDispatcher de Kivy
- Emite eventos estructurales via dispatch() (on_line_added, on_line_removed, on_line_moved, on_line_state_changed)
- Los LineState son mutables y disparan eventos automáticamente via Properties
- MDDocumentEditor hace bind() a eventos estructurales
- MDDocumentLineEditor hace bind() directo a su LineState

Responsabilidades:
1. Almacenar todos los LineState
2. Gestionar estados de activación, selección, hotlight
3. Gestionar geometría (posiciones Y, alturas)
4. Emitir eventos estructurales para add/remove/move
5. Operaciones de documento delegadas a MDDocument

Fecha: 2026-02-01
Autor: Martin Pablo Bellanca
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Set, List, Optional, Tuple, Any

from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.logger import Logger

# Importar LineState y Enums
from .line_state import LineState, LineGroup  #, AnimationType

# Importar MDLine y MDDocument de helpers_mpbe
from helpers_mpbe.markdown_document.md_document import MDDocument, MDLine
from helpers_mpbe.markdown_document import MD_LINE_TYPE


# =============================================================================
# ENUMERACIÓN - Tipos de evento estructural
# =============================================================================
class EventType(Enum):
    """
    Tipos de evento emitidos por DocumentStateManager.

    Valores:
        CHANGED: El estado de una línea existente cambió (emitido por update_state)
        ADDED: Se agregó una nueva línea al documento
        REMOVED: Se eliminó una línea del documento
        MOVED: Una línea se movió de posición
        BATCH: Múltiples cambios en una sola operación (reservado para uso futuro)
    """
    CHANGED = 'changed'
    ADDED = 'added'
    REMOVED = 'removed'
    MOVED = 'moved'
    BATCH = 'batch'  # Reservado para operaciones que afectan múltiples líneas (ej. aplicar filtro)


# =============================================================================
# DATACLASS - Evento estructural
# =============================================================================
@dataclass
class LineStateEvent:
    """
    Evento emitido por DocumentStateManager para cambios estructurales.

    Este evento se usa para notificar cambios que afectan la estructura
    del documento (agregar, eliminar, mover líneas). Para cambios de estado
    individual, MDDocumentLineEditor observa directamente su LineState.

    Attributes:
        index (int): Índice de la línea afectada
        line_state (Optional[LineState]): Estado de la línea (None si fue removida)
        event_type (EventType): Tipo de evento estructural
        old_index (Optional[int]): Índice anterior (para MOVED)
        changed_attributes (Set[str]): Atributos que cambiaron (para CHANGED)
        old_values (Dict[str, Any]): Valores anteriores de los atributos cambiados (para CHANGED)
    """
    index: int
    line_state: Optional[LineState] = None
    event_type: EventType = EventType.CHANGED
    old_index: Optional[int] = None
    changed_attributes: Set[str] = field(default_factory=set)
    old_values: Dict[str, Any] = field(default_factory=dict)

    def is_structural_change(self) -> bool:
        """Verifica si el evento es un cambio estructural (add/remove/move)."""
        return self.event_type in {EventType.ADDED, EventType.REMOVED, EventType.MOVED}

    def is_state_change(self) -> bool:
        """Verifica si el evento es un cambio de estado."""
        return self.event_type == EventType.CHANGED

    def __repr__(self) -> str:
        """Representación legible del evento."""
        return f"LineStateEvent[{self.index}]({self.event_type.name})"


# =============================================================================
# CLASE PRINCIPAL - DocumentStateManager
# =============================================================================
class DocumentStateManager(EventDispatcher):
    """
    Gestor centralizado de estados de líneas del documento.

    Este es el "Single Source of Truth" para el estado de todas las líneas.
    Hereda de EventDispatcher para emitir eventos estructurales via dispatch().

    Attributes:
        md_document (MDDocument): Referencia al documento (ObjectProperty)
        _line_states (List[LineState]): Estados de todas las líneas (índice == posición)
        _active_index (Optional[int]): Índice de la línea activa
        _selected_indices (Set[int]): Índices de líneas seleccionadas
        _visible_indices (Set[int]): Índices de líneas visibles
        _filtered_indices (Set[int]): Índices de líneas filtradas (ocultas)

    Events:
        on_line_added: Disparado cuando se agrega una línea
        on_line_removed: Disparado cuando se elimina una línea
        on_line_moved: Disparado cuando se mueve una línea
        on_line_state_changed: Disparado cuando cambia el estado de una línea existente

    Example:
        >>> manager = DocumentStateManager()
        >>> manager.bind(on_line_added=self._on_line_added)
        >>> manager.load_document(md_lines)
        >>> manager.activate_line(5, enter_edit=True)
    """

    # ========================================================================
    # Properties de Kivy
    # ========================================================================
    md_document = ObjectProperty(None, allownone=True)
    total_height = NumericProperty(0.0)

    # ========================================================================
    # Sub-widgets
    # ========================================================================
    show_number_line = BooleanProperty(True)
    show_tree = BooleanProperty(False)
    show_infobar = BooleanProperty(False)


    def __init__(self, **kwargs):
        """
        Inicializa el DocumentStateManager.

        Registra los eventos estructurales y crea las estructuras de datos.
        """
        super().__init__(**kwargs)

        # ====================================================================
        # Registrar eventos estructurales
        # ====================================================================
        self.register_event_type('on_line_added')
        self.register_event_type('on_line_removed')
        self.register_event_type('on_line_moved')
        self.register_event_type('on_line_state_changed')

        # ====================================================================
        # Almacenamiento de estados
        # ====================================================================
        self._line_states: List[LineState] = []

        # ====================================================================
        # Estado de activación y selección
        # ====================================================================
        self._active_index: Optional[int] = None
        self._selected_indices: Set[int] = set()

        # ====================================================================
        # Índices por grupo de visibilidad
        # ====================================================================
        self._visible_indices: Set[int] = set()
        self._filtered_indices: Set[int] = set()

        # ====================================================================
        # Índices de búsqueda
        # ====================================================================
        self._search_matches: Set[int] = set()

        # ====================================================================
        # Geometría
        # ====================================================================
        self._line_y_positions: List[float] = []

        # ====================================================================
        # Configuración
        # ====================================================================
        self._viewport_buffer: int = 5  # Líneas extra arriba/abajo del viewport

        Logger.info("DocumentStateManager: Initialized")

    # ========================================================================
    # EVENTOS - Handlers por defecto (requeridos por register_event_type)
    # ========================================================================

    def on_line_added(self, event: LineStateEvent):
        """Handler por defecto para on_line_added."""
        pass

    def on_line_removed(self, event: LineStateEvent):
        """Handler por defecto para on_line_removed."""
        pass

    def on_line_moved(self, event: LineStateEvent):
        """Handler por defecto para on_line_moved."""
        pass

    def on_line_state_changed(self, event: LineStateEvent):
        """Handler por defecto para on_line_state_changed."""
        pass

    # ========================================================================
    # INICIALIZACIÓN Y CARGA
    # ========================================================================

    def set_document(self, md_document: MDDocument):
        """
        Establecer el documento y cargar sus líneas.

        Args:
            md_document: Instancia de MDDocument
        """
        self.md_document = md_document

        if md_document is not None and hasattr(md_document, 'md_lines'):
            self._load_document()
        else:
            self._clear_all()

    def _load_document(self):
        """
        Cargar documento completo desde lista de MDLine.

        Crea un LineState mutable para cada MDLine.

        Args:
            md_lines: Lista de MDLine del documento
        """
        Logger.info(f"DocumentStateManager: Loading document with {len(self.md_document.md_lines)} lines")

        # Limpiar estado anterior
        self._clear_all()

        # Crear LineState para cada MDLine
        for i, md_line in enumerate(self.md_document.md_lines):
            # Estimar altura inicial basada en tipo de línea
            estimated_height = self._estimate_line_height(md_line)

            # Crear estado mutable
            md_line.set_num_line(i+1)  # Asigna sin actualizar las lineas siguientes.
            state = LineState(
                index=i,
                md_line=md_line,
                visible=True,
                group=LineGroup.VISIBLE.value,
                height=estimated_height,
                y_position=0.0
            )

            # NOTA: para propiedades de Kivy se bindea por nombre (active=...);
            # bind(on_active=...) sólo aplica a eventos registrados y Kivy lo
            # ignora en silencio si no existen.
            state.bind(
                # UI State Changes
                active=self._on_line_state_active,
                selected=self._on_line_state_selected,
                hotlight=self._on_line_state_hotlight,
                editing=self._on_line_state_editing,
                # Visibility & Group Changes
                visible=self._on_line_state_visible,
                matched_search=self._on_line_state_matched_search,
                group=self._on_line_group_changed,
                # Geometry Changes
                height=self._on_line_height_changed,
                # Type Changes (custom event)
                on_type_changed=self._on_line_type_changed
            )

            self._line_states.append(state)
            self._visible_indices.add(i)

        # Calcular geometría inicial
        self._recalculate_geometry()

        Logger.info(
            f"DocumentStateManager: Loaded {len(self._line_states)} lines, "
            f"total height: {self.total_height:.0f}px"
        )

    def _clear_all(self):
        """
        Limpiar todos los estados.

        Resetea el manager a estado vacío.
        """
        self._line_states.clear()
        self._active_index = None
        self._selected_indices.clear()
        self._visible_indices.clear()
        self._filtered_indices.clear()
        self._search_matches.clear()
        self._line_y_positions.clear()
        self.total_height = 0.0

        Logger.info("DocumentStateManager: Cleared all states")

    # ========================================================================
    # ACCESO A ESTADOS
    # ========================================================================

    # @property
    def get_line_states(self) -> List[LineState]:
        """Acceso a los estados de líneas (read-only)."""
        return self._line_states

    def get_state(self, index: int) -> Optional[LineState]:
        """
        Obtener estado de una línea por su índice.

        Args:
            index: Índice de la línea

        Returns:
            LineState o None si no existe
        """
        if 0 <= index < len(self._line_states):
            return self._line_states[index]
        return None

    def get_md_line(self, index: int) -> Optional[MDLine]:
        """
        Obtener MDLine de una línea por su índice.

        Args:
            index: Índice de la línea

        Returns:
            MDLine o None si no existe
        """
        if 0 <= index < len(self._line_states):
            return self._line_states[index].md_line
        return None

    def get_active_index(self) -> Optional[int]:
        """
        Obtener índice de la línea activa.

        Returns:
            Índice de la línea activa o None
        """
        return self._active_index

    def get_active_state(self) -> Optional[LineState]:
        """
        Obtener estado de la línea activa.

        Returns:
            LineState de la línea activa o None
        """
        if self._active_index is not None and 0 <= self._active_index < len(self._line_states):
            return self._line_states[self._active_index]
        return None

    def get_selected_indices(self) -> Set[int]:
        """
        Obtener conjunto de índices seleccionados.

        Returns:
            Set de índices seleccionados (copia)
        """
        return self._selected_indices.copy()

    def get_total_lines(self) -> int:
        """
        Obtener número total de líneas.

        Returns:
            Número total de líneas
        """
        return len(self._line_states)

    def get_visible_lines_count(self) -> int:
        """
        Obtener número de líneas visibles (no filtradas).

        Returns:
            Número de líneas visibles
        """
        return len(self._visible_indices)

    # @property
    def get_visible_indices(self) -> Set[int]:
        """Acceso a índices visibles (read-only)."""
        return self._visible_indices

    # ========================================================================
    # MODIFICACIÓN DE ESTADOS
    # ========================================================================

    def update_state(self, index: int, **changes):
        """
        Actualizar estado de una línea y emitir evento CHANGED.

        Como LineState es mutable con EventDispatcher, modificamos
        directamente las propiedades. Cada cambio dispara automáticamente
        el evento on_<property> correspondiente, y además emitimos un
        evento CHANGED consolidado a nivel de documento.

        Args:
            index: Índice de la línea
            **changes: Cambios a aplicar (nombres de propiedades y valores)

        Example:
            >>> manager.update_state(5, active=True, editing=True)
        """
        if not (0 <= index < len(self._line_states)):
            Logger.warning(f"DocumentStateManager: Line {index} out of range")
            return

        state = self._line_states[index]
        changed_attrs = set()
        old_values = {}

        # Capturar valores anteriores y aplicar cambios
        for prop_name, value in changes.items():
            if hasattr(state, prop_name):
                old_value = getattr(state, prop_name)
                # Solo registrar si realmente cambió
                if old_value != value:
                    old_values[prop_name] = old_value
                    setattr(state, prop_name, value)
                    changed_attrs.add(prop_name)
            else:
                Logger.warning(
                    f"DocumentStateManager: Unknown property '{prop_name}'"
                )

        # Emitir evento CHANGED solo si hubo cambios reales
        if changed_attrs:
            event = LineStateEvent(
                index=index,
                line_state=state,
                event_type=EventType.CHANGED,
                changed_attributes=changed_attrs,
                old_values=old_values
            )
            self.dispatch('on_line_state_changed', event)

        Logger.debug(f"DocumentStateManager: Updated state for line {index}: {changes}")

    def activate_line(
        self,
        index: int,
        enter_edit: bool = False,
        cursor_pos: Tuple[int, int] = (0, 0)
    ) -> bool:
        """
        Activar una línea (y opcionalmente entrar en modo edición).

        Desactiva la línea anterior si existe.

        Args:
            index: Índice de la línea a activar
            enter_edit: Si True, también entra en modo edición
            cursor_pos: Posición del cursor (col, row)

        Returns:
            True si se activó correctamente
        """
        if not (0 <= index < len(self._line_states)):
            Logger.warning(f"DocumentStateManager: Cannot activate line {index}")
            return False

        # Desactivar línea anterior
        if self._active_index is not None and self._active_index != index:
            self.deactivate_line(self._active_index)

        # Activar nueva línea
        state = self._line_states[index]
        state.active = True

        if enter_edit:
            state.editing = True
            state.cursor_pos = cursor_pos

        self._active_index = index

        Logger.debug(
            f"DocumentStateManager: Activated line {index}, "
            f"edit={enter_edit}, cursor={cursor_pos}"
        )

        return True

    def deactivate_line(self, index: int) -> bool:
        """
        Desactivar una línea.

        Args:
            index: Índice de la línea a desactivar

        Returns:
            True si se desactivó correctamente
        """
        if not (0 <= index < len(self._line_states)):
            return False

        state = self._line_states[index]
        state.active = False
        state.editing = False

        if self._active_index == index:
            self._active_index = None

        Logger.debug(f"DocumentStateManager: Deactivated line {index}")

        return True

    def select_line(self, index: int, multi: bool = False) -> bool:
        """
        Seleccionar una línea.

        Args:
            index: Índice de la línea
            multi: Si True, agrega a la selección existente

        Returns:
            True si se seleccionó correctamente
        """
        if not (0 <= index < len(self._line_states)):
            return False

        if not multi:
            # Limpiar selección anterior
            self.clear_selection()

        # Seleccionar línea
        state = self._line_states[index]
        state.selected = True
        self._selected_indices.add(index)

        Logger.debug(f"DocumentStateManager: Selected line {index}, multi={multi}")

        return True

    def select_range(self, start: int, end: int) -> int:
        """
        Seleccionar un rango de líneas.

        Args:
            start: Índice inicial (inclusive)
            end: Índice final (inclusive)

        Returns:
            Número de líneas seleccionadas
        """
        # Normalizar rango
        if start > end:
            start, end = end, start

        count = 0
        for index in range(start, end + 1):
            if 0 <= index < len(self._line_states):
                state = self._line_states[index]
                state.selected = True
                self._selected_indices.add(index)
                count += 1

        Logger.debug(f"DocumentStateManager: Selected range [{start}, {end}], count={count}")

        return count

    def clear_selection(self) -> int:
        """
        Limpiar toda la selección.

        Returns:
            Número de líneas deseleccionadas
        """
        count = len(self._selected_indices)

        for index in self._selected_indices:
            if 0 <= index < len(self._line_states):
                self._line_states[index].selected = False

        self._selected_indices.clear()

        Logger.debug(f"DocumentStateManager: Cleared selection, count={count}")

        return count

    def toggle_selection(self, index: int) -> bool:
        """
        Alternar selección de una línea.

        Args:
            index: Índice de la línea

        Returns:
            True si ahora está seleccionada, False si no
        """
        if not (0 <= index < len(self._line_states)):
            return False

        state = self._line_states[index]
        state.selected = not state.selected

        if state.selected:
            self._selected_indices.add(index)
        else:
            self._selected_indices.discard(index)

        Logger.debug(f"DocumentStateManager: Toggled selection {index} -> {state.selected}")

        return state.selected

    def set_hotlight(self, index: int, value: bool):
        """
        Establecer hotlight (mouse hover) de una línea.

        Args:
            index: Índice de la línea
            value: True para activar hotlight
        """
        if 0 <= index < len(self._line_states):
            self._line_states[index].hotlight = value

    def set_visibility(self, index: int, visible: bool):
        """
        Establecer visibilidad de una línea.

        Args:
            index: Índice de la línea
            visible: True para hacer visible
        """
        if not (0 <= index < len(self._line_states)):
            return

        state = self._line_states[index]
        state.visible = visible

        if visible:
            self._visible_indices.add(index)
            self._filtered_indices.discard(index)
            state.group = LineGroup.VISIBLE.value
        else:
            self._visible_indices.discard(index)
            self._filtered_indices.add(index)
            state.group = LineGroup.FILTERED.value

    def update_line_height(self, index: int, new_height: float):
        """
        Actualizar altura de una línea.

        Args:
            index: Índice de la línea
            new_height: Nueva altura en pixels
        """
        if not (0 <= index < len(self._line_states)):
            return

        state = self._line_states[index]
        old_height = state.height

        # Solo recalcular si cambió significativamente
        if abs(new_height - old_height) > 1.0:
            state.height = new_height
            self._recalculate_geometry()

            Logger.debug(
                f"DocumentStateManager: Updated height for line {index}: "
                f"{old_height:.0f}px → {new_height:.0f}px"
            )

    # ========================================================================
    # OPERACIONES DE DOCUMENTO (dispatch eventos)
    # ========================================================================

    def insert_line(self, index: int, md_line: MDLine) -> Optional[LineState]:
        """
        Insertar una nueva línea en el documento.

        Crea LineState, reindexta líneas posteriores, y dispara on_line_added.

        Args:
            index: Índice donde insertar
            md_line: MDLine a insertar

        Returns:
            LineState creado o None si falla
        """
        Logger.info(f"DocumentStateManager: Inserting line at index {index}")

        # Crear nuevo LineState
        estimated_height = self._estimate_line_height(md_line)
        new_state = LineState(
            index=index,
            md_line=md_line,
            visible=True,
            group=LineGroup.VISIBLE.value,
            height=estimated_height
        )

        # Bindear eventos del LineState (propiedades por nombre; ver _load_document)
        new_state.bind(
            active=self._on_line_state_active,
            selected=self._on_line_state_selected,
            hotlight=self._on_line_state_hotlight,
            editing=self._on_line_state_editing,
            visible=self._on_line_state_visible,
            matched_search=self._on_line_state_matched_search,
            group=self._on_line_group_changed,
            height=self._on_line_height_changed,
            on_type_changed=self._on_line_type_changed
        )

        # Insertar en lista en la posición correcta
        self._line_states.insert(index, new_state)

        # Reindexar líneas posteriores (actualizar sus índices internos)
        for i in range(index + 1, len(self._line_states)):
            self._line_states[i].index = i

        # Actualizar sets de índices (incrementar los >= index)
        self._visible_indices = {i if i < index else i + 1 for i in self._visible_indices}
        self._visible_indices.add(index)

        self._filtered_indices = {i if i < index else i + 1 for i in self._filtered_indices}
        self._selected_indices = {i if i < index else i + 1 for i in self._selected_indices}
        self._search_matches = {i if i < index else i + 1 for i in self._search_matches}

        # Actualizar _active_index si es necesario
        if self._active_index is not None and self._active_index >= index:
            self._active_index += 1

        # Sincronizar el documento (lista guardable + links) y geometría
        self._sync_md_lines()
        self._recalculate_geometry()

        # Disparar evento
        event = LineStateEvent(
            index=index,
            line_state=new_state,
            event_type=EventType.ADDED
        )
        self.dispatch('on_line_added', event)

        Logger.debug(f"DocumentStateManager: Dispatched on_line_added for index {index}")

        return new_state

    def remove_line(self, index: int) -> bool:
        """
        Eliminar una línea del documento.

        Reindexta líneas posteriores y dispara on_line_removed.

        Args:
            index: Índice de la línea a eliminar

        Returns:
            True si se eliminó correctamente
        """
        if not (0 <= index < len(self._line_states)):
            Logger.warning(f"DocumentStateManager: Cannot remove line {index}")
            return False

        Logger.info(f"DocumentStateManager: Removing line at index {index}")

        # Obtener estado antes de eliminar
        removed_state = self._line_states.pop(index)

        # Reindexar líneas posteriores (actualizar sus índices internos)
        for i in range(index, len(self._line_states)):
            self._line_states[i].index = i

        # Actualizar sets de índices (decrementar los > index)
        self._visible_indices = {i if i < index else i - 1 for i in self._visible_indices if i != index}
        self._filtered_indices = {i if i < index else i - 1 for i in self._filtered_indices if i != index}
        self._selected_indices = {i if i < index else i - 1 for i in self._selected_indices if i != index}
        self._search_matches = {i if i < index else i - 1 for i in self._search_matches if i != index}

        # Si era la línea activa, desactivar
        if self._active_index == index:
            self._active_index = None
        elif self._active_index is not None and self._active_index > index:
            self._active_index -= 1

        # Sincronizar el documento (lista guardable + links) y geometría
        self._sync_md_lines()
        self._recalculate_geometry()

        # Disparar evento
        event = LineStateEvent(
            index=index,
            line_state=None,  # Ya no existe
            event_type=EventType.REMOVED
        )
        self.dispatch('on_line_removed', event)

        Logger.debug(f"DocumentStateManager: Dispatched on_line_removed for index {index}")

        return True

    def move_line(self, from_index: int, to_index: int) -> bool:
        """
        Mover una línea de una posición a otra.

        Args:
            from_index: Índice origen
            to_index: Índice destino

        Returns:
            True si se movió correctamente
        """
        if not (0 <= from_index < len(self._line_states)):
            return False

        if not (0 <= to_index < len(self._line_states)):
            return False

        if from_index == to_index:
            return True

        Logger.info(f"DocumentStateManager: Moving line {from_index} -> {to_index}")

        was_active = self._active_index == from_index

        # Mover en la lista (pop + insert)
        state_to_move = self._line_states.pop(from_index)
        self._line_states.insert(to_index, state_to_move)

        # Reindexar todas las líneas afectadas
        if from_index < to_index:
            # Mover hacia abajo: actualizar índices desde from hasta to
            for i in range(from_index, to_index + 1):
                self._line_states[i].index = i
        else:
            # Mover hacia arriba: actualizar índices desde to hasta from
            for i in range(to_index, from_index + 1):
                self._line_states[i].index = i

        # Reconstruir los sets de índices desde los estados (a prueba de balas:
        # el movimiento corre los índices de todas las líneas intermedias, no
        # sólo la movida). Los flags viven en cada LineState (fuente de verdad).
        self._rebuild_index_sets()
        if was_active:
            self._active_index = to_index

        # Sincronizar el documento (lista guardable + links) y geometría
        self._sync_md_lines()
        self._recalculate_geometry()

        # Disparar evento
        event = LineStateEvent(
            index=to_index,
            line_state=state_to_move,
            event_type=EventType.MOVED,
            old_index=from_index
        )
        self.dispatch('on_line_moved', event)

        Logger.debug(
            f"DocumentStateManager: Dispatched on_line_moved "
            f"{from_index} -> {to_index}"
        )

        return True

    def update_line_text(self, index: int, text: str) -> bool:
        """
        Actualizar el texto de una línea (embudo único de mutación de texto).

        Rutea por LineState.update_type() para que, si cambia el tipo de línea,
        se dispare on_type_changed (y los widgets reemplacen el label). Es la
        vía correcta en vez de escribir md_line.md_text directo desde la UI.

        Args:
            index: Índice de la línea
            text: Nuevo texto

        Returns:
            True si se actualizó correctamente
        """
        if not (0 <= index < len(self._line_states)):
            return False

        state = self._line_states[index]
        if state.md_line is None:
            return False

        # Actualizar texto y detectar nuevo tipo (vía LineState → on_type_changed)
        state.md_line.md_text = text
        state.update_type()

        Logger.debug(
            f"DocumentStateManager: Updated text for line {index}, "
            f"type={state.md_line.type.name}"
        )

        return True

    def _rebuild_index_sets(self):
        """
        Reconstruye los sets de índices (visible/filtered/selected/search) desde
        los flags de cada LineState. Para usar tras operaciones que corren muchos
        índices a la vez (p. ej. move_line), donde la aritmética por-índice es
        propensa a errores. Los flags viven en el LineState (fuente de verdad).
        """
        self._visible_indices = {s.index for s in self._line_states if s.visible}
        self._filtered_indices = {s.index for s in self._line_states if not s.visible}
        self._selected_indices = {s.index for s in self._line_states if s.selected}
        self._search_matches = {s.index for s in self._line_states if s.matched_search}

    def _sync_md_lines(self):
        """
        Sincroniza md_document._md_lines con el orden actual de _line_states
        (fuente de verdad del orden). Tras insertar/borrar/mover, deja el
        documento guardable y repone los links de cada MDLine (prev/next) y el
        num_line por posición. O(n), pero se llama en acciones de usuario.

        La mutación estructural la orquesta este StateManager (MDDocument ya no
        tiene API estructural propia).
        """
        if self.md_document is None:
            return
        md_lines = [s.md_line for s in self._line_states]
        self.md_document._md_lines = md_lines
        n = len(md_lines)
        for i, ml in enumerate(md_lines):
            ml.prev_line = md_lines[i - 1] if i > 0 else None
            ml.next_line = md_lines[i + 1] if i < n - 1 else None
            ml.set_num_line(i + 1)

    # ========================================================================
    # GEOMETRÍA
    # ========================================================================

    def _recalculate_geometry(self):
        """
        Recalcular posiciones Y de todas las líneas visibles.

        Actualiza y_position de cada LineState y el total_height.
        """
        # Redimensionar lista de posiciones Y para que coincida con _line_states
        self._line_y_positions = [0.0] * len(self._line_states)

        current_y = 0.0

        # Recorrer líneas visibles en orden
        for index in sorted(self._visible_indices):
            if not (0 <= index < len(self._line_states)):
                continue

            state = self._line_states[index]

            # Actualizar posición Y directamente (mutable)
            state.y_position = current_y
            self._line_y_positions[index] = current_y

            # Avanzar Y con altura de esta línea
            current_y += state.height

        # Guardar altura total
        self.total_height = current_y

        Logger.debug(
            f"DocumentStateManager: Geometry recalculated, "
            f"total_height={self.total_height:.0f}px"
        )

    def get_visible_in_viewport(
        self,
        scroll_y: float,
        viewport_height: float
    ) -> List[int]:
        """
        Calcular qué líneas deben renderizarse en el viewport actual.

        Args:
            scroll_y: Posición de scroll (0.0=bottom, 1.0=top)
            viewport_height: Altura del viewport en pixels

        Returns:
            Lista ordenada de índices a renderizar (incluye buffer)
        """
        if not self._visible_indices:
            return []

        # Convertir scroll_y a posición absoluta
        scroll_pos = self.total_height * (1.0 - scroll_y)

        # Calcular rango del viewport con buffer
        buffer_height = self._viewport_buffer * 30.0

        viewport_start = max(0, scroll_pos - buffer_height)
        viewport_end = min(
            self.total_height,
            scroll_pos + viewport_height + buffer_height
        )

        # Encontrar líneas que intersectan con viewport
        visible_in_viewport = []

        for index in sorted(self._visible_indices):
            state = self._line_states[index]
            line_top = state.y_position
            line_bottom = state.y_position + state.height

            if line_bottom >= viewport_start and line_top <= viewport_end:
                visible_in_viewport.append(index)

        return visible_in_viewport

    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================

    def _estimate_line_height(self, md_line: MDLine) -> float:
        """
        Estimar altura inicial de una línea basándose en su tipo.

        Args:
            md_line: Línea de Markdown

        Returns:
            Altura estimada en pixels
        """
        base_heights = {
            MD_LINE_TYPE.TITLE: 40.0,
            MD_LINE_TYPE.HEAD_TITLE: 45.0,
            MD_LINE_TYPE.TEXT: 25.0,
            MD_LINE_TYPE.LIST: 28.0,
            MD_LINE_TYPE.ORDER_LIST: 28.0,
            MD_LINE_TYPE.TASK: 30.0,
            MD_LINE_TYPE.TODO: 30.0,
            MD_LINE_TYPE.CODE: 22.0,
            MD_LINE_TYPE.BLOCKQUOTE: 30.0,
            MD_LINE_TYPE.TABLE: 35.0,
            MD_LINE_TYPE.SEPARATOR: 20.0,
            MD_LINE_TYPE.IMAGEN: 100.0,
        }

        base = base_heights.get(md_line.type, 25.0)

        # Ajustar por longitud de texto
        text_length = len(md_line.md_text)
        if text_length > 80:
            extra_lines = (text_length - 80) // 80
            base += extra_lines * 20.0

        return base

    # ========================================================================
    # HANDLERS DE EVENTOS DE LineState
    # ========================================================================
    # Estos métodos capturan eventos individuales de cada LineState y los
    # re-emiten como eventos LineStateEvent a nivel de documento

    def _on_line_state_active(self, line_state: LineState, value: bool):
        """
        Handler para cambios en la propiedad 'active' de LineState.

        Args:
            line_state: El LineState que cambió
            value: Nuevo valor de 'active'
        """
        event = LineStateEvent(
            index=line_state.index,
            line_state=line_state,
            event_type=EventType.CHANGED,
            changed_attributes={'active'},
            old_values={'active': not value}  # El valor anterior es el opuesto
        )
        self.dispatch('on_line_state_changed', event)

        Logger.debug(f"DocumentStateManager: Line {line_state.index} active changed to {value}")

    def _on_line_state_selected(self, line_state: LineState, value: bool):
        """
        Handler para cambios en la propiedad 'selected' de LineState.

        Args:
            line_state: El LineState que cambió
            value: Nuevo valor de 'selected'
        """
        event = LineStateEvent(
            index=line_state.index,
            line_state=line_state,
            event_type=EventType.CHANGED,
            changed_attributes={'selected'},
            old_values={'selected': not value}
        )
        self.dispatch('on_line_state_changed', event)

        Logger.debug(f"DocumentStateManager: Line {line_state.index} selected changed to {value}")

    def _on_line_state_hotlight(self, line_state: LineState, value: bool):
        """
        Handler para cambios en la propiedad 'hotlight' de LineState.

        Args:
            line_state: El LineState que cambió
            value: Nuevo valor de 'hotlight'
        """
        event = LineStateEvent(
            index=line_state.index,
            line_state=line_state,
            event_type=EventType.CHANGED,
            changed_attributes={'hotlight'},
            old_values={'hotlight': not value}
        )
        self.dispatch('on_line_state_changed', event)

        Logger.debug(f"DocumentStateManager: Line {line_state.index} hotlight changed to {value}")

    def _on_line_state_editing(self, line_state: LineState, value: bool):
        """
        Handler para cambios en la propiedad 'editing' de LineState.

        Args:
            line_state: El LineState que cambió
            value: Nuevo valor de 'editing'
        """
        event = LineStateEvent(
            index=line_state.index,
            line_state=line_state,
            event_type=EventType.CHANGED,
            changed_attributes={'editing'},
            old_values={'editing': not value}
        )
        self.dispatch('on_line_state_changed', event)

        Logger.debug(f"DocumentStateManager: Line {line_state.index} editing changed to {value}")

    def _on_line_state_visible(self, line_state: LineState, value: bool):
        """
        Handler para cambios en la propiedad 'visible' de LineState.

        Args:
            line_state: El LineState que cambió
            value: Nuevo valor de 'visible'
        """
        event = LineStateEvent(
            index=line_state.index,
            line_state=line_state,
            event_type=EventType.CHANGED,
            changed_attributes={'visible'},
            old_values={'visible': not value}
        )
        self.dispatch('on_line_state_changed', event)

        Logger.debug(f"DocumentStateManager: Line {line_state.index} visible changed to {value}")

    def _on_line_state_matched_search(self, line_state: LineState, value: bool):
        """
        Handler para cambios en la propiedad 'matched_search' de LineState.

        Args:
            line_state: El LineState que cambió
            value: Nuevo valor de 'matched_search'
        """
        event = LineStateEvent(
            index=line_state.index,
            line_state=line_state,
            event_type=EventType.CHANGED,
            changed_attributes={'matched_search'},
            old_values={'matched_search': not value}
        )
        self.dispatch('on_line_state_changed', event)

        Logger.debug(f"DocumentStateManager: Line {line_state.index} matched_search changed to {value}")

    def _on_line_group_changed(self, line_state: LineState, value: str):
        """
        Handler para cambios en la propiedad 'group' de LineState.

        Args:
            line_state: El LineState que cambió
            value: Nuevo valor de 'group'
        """
        # Para 'group' no podemos determinar fácilmente el valor anterior,
        # así que lo dejamos como cadena vacía
        event = LineStateEvent(
            index=line_state.index,
            line_state=line_state,
            event_type=EventType.CHANGED,
            changed_attributes={'group'},
            old_values={'group': ''}  # Valor anterior desconocido
        )
        self.dispatch('on_line_state_changed', event)

        Logger.debug(f"DocumentStateManager: Line {line_state.index} group changed to {value}")

    def _on_line_height_changed(self, line_state: LineState, new_height: float):
        """
        Handler para cambios en la altura de LineState (NumericProperty).

        Args:
            line_state: El LineState que cambió
            new_height: Nueva altura
        """
        # Para NumericProperty no tenemos el valor anterior directamente,
        # pero podemos usar 0.0 como placeholder o calcularlo si es necesario
        event = LineStateEvent(
            index=line_state.index,
            line_state=line_state,
            event_type=EventType.CHANGED,
            changed_attributes={'height'},
            old_values={'height': 0.0}  # Valor anterior no disponible
        )
        self.dispatch('on_line_state_changed', event)

        Logger.debug(
            f"DocumentStateManager: Line {line_state.index} height changed to {new_height:.0f}px"
        )

    def _on_line_type_changed(self, line_state: LineState, index: int, old_type, new_type):
        """
        Handler para cambios en el tipo de línea de LineState (evento custom).

        Args:
            line_state: El LineState que cambió
            index: Índice de la línea (pasado por el dispatch)
            old_type: Tipo anterior (MD_LINE_TYPE)
            new_type: Nuevo tipo (MD_LINE_TYPE)
        """
        event = LineStateEvent(
            index=line_state.index,
            line_state=line_state,
            event_type=EventType.CHANGED,
            changed_attributes={'widget_type'},
            old_values={'widget_type': old_type}
        )
        self.dispatch('on_line_state_changed', event)

        Logger.debug(
            f"DocumentStateManager: Line {line_state.index} widget_type changed "
            f"from {old_type.__name__ if old_type else 'None'} to {new_type.__name__ if new_type else 'None'}"
        )

    # ========================================================================
    # REPRESENTACIÓN
    # ========================================================================

    def __repr__(self) -> str:
        """Representación string del DocumentStateManager."""
        total = len(self._line_states) if hasattr(self, '_line_states') else 0
        visible = len(self._visible_indices) if hasattr(self, '_visible_indices') else 0
        height = self.total_height if hasattr(self, 'total_height') else 0.0
        active = self._active_index if hasattr(self, '_active_index') else None

        return (
            f"DocumentStateManager("
            f"total={total}, "
            f"visible={visible}, "
            f"active={active}, "
            f"height={height:.0f}px"
            f")"
        )
