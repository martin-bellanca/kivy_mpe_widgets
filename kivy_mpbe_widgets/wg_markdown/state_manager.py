#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  state_manager.py
#
#  Copyright 2025 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

"""
State Manager Pattern Implementation

Centraliza la gestión de estados de las líneas del documento,
eliminando la fragmentación del estado entre múltiples componentes.

Created on 25/12/2024
@author: mpbe
"""

from typing import Dict, Set, Optional, Callable, Tuple, List
from dataclasses import dataclass, replace
from kivy.logger import Logger


@dataclass(frozen=True)
class LineState:
    """
    Estado inmutable de una línea del documento.

    Usando dataclass frozen=True garantiza inmutabilidad,
    lo que previene modificaciones accidentales y facilita
    el rastreo de cambios de estado.

    Attributes:
        index (int): Índice de la línea en la lista de datos
        selected (bool): Si la línea está seleccionada
        active (bool): Si la línea está activa (solo una puede estar activa)
        editing (bool): Si la línea está en modo edición
        hotlight (bool): Si el mouse está sobre la línea
        visible (bool): Si la línea es visible (después de filtros)
        cursor_pos (Tuple[int, int]): Posición del cursor (col, row) para animaciones

        # Variables de visibilidad de sub-widgets (reemplazan DataShow)
        show_number_line (bool): Si se muestra el número de línea
        show_tree (bool): Si se muestra el gancho de árbol
        show_infobar (bool): Si se muestra la barra de información

        # Variables de tema (reemplazan DataThemed)
        alpha_background (float): Opacidad del fondo (0.0-1.0) para efectos visuales

        # Variables de animación
        anim_type (str): Tipo de animación para transiciones visuales
            - 'fade': Transición suave con opacidad (default, para clicks)
            - 'slide_up': Desplazamiento hacia arriba (flecha arriba)
            - 'slide_down': Desplazamiento hacia abajo (flecha abajo)
            - 'expand_up': Expansión de selección hacia arriba (Shift+Arriba)
            - 'expand_down': Expansión de selección hacia abajo (Shift+Abajo)
    """

    index: int
    selected: bool = False
    active: bool = False
    editing: bool = False
    hotlight: bool = False
    visible: bool = True
    cursor_pos: Tuple[int, int] = (0, 0)

    # Visibilidad de sub-widgets (DataShow)
    show_number_line: bool = True
    show_tree: bool = False
    show_infobar: bool = False

    # Tema (DataThemed)
    alpha_background: float = 0.0

    # Animación (para transiciones visuales)
    anim_type: str = 'fade'  # 'fade', 'slide_up', 'slide_down', 'expand_up', 'expand_down'


    def with_changes(self, **kwargs) -> 'LineState':
        """
        Retorna un nuevo estado con los cambios especificados.

        Al ser inmutable, no podemos modificar el estado existente.
        En su lugar, creamos uno nuevo con las modificaciones.

        Args:
            **kwargs: Atributos a modificar

        Returns:
            LineState: Nuevo estado con los cambios aplicados

        Example:
            >>> old_state = LineState(index=5, selected=False)
            >>> new_state = old_state.with_changes(selected=True, active=True)
            >>> new_state.selected
            True
            >>> old_state.selected  # El original no cambia
            False
        """
        return replace(self, **kwargs)

    def __repr__(self) -> str:
        """Representación legible del estado."""
        flags = []
        if self.selected:
            flags.append('SEL')
        if self.active:
            flags.append('ACT')
        if self.editing:
            flags.append('EDIT')
        if self.hotlight:
            flags.append('HOT')
        if not self.visible:
            flags.append('HIDDEN')

        # Mostrar configuración de sub-widgets solo si difiere de los defaults
        if not self.show_number_line:  # Default es True
            flags.append('NO_NUM')
        if self.show_tree:  # Default es False
            flags.append('TREE')
        if self.show_infobar:  # Default es False
            flags.append('INFO')
        if self.alpha_background > 0.0:  # Default es 0.0
            flags.append(f'BG:{self.alpha_background:.1f}')

        flags_str = '|'.join(flags) if flags else 'NONE'
        return f"LineState[{self.index}]({flags_str})"


class StateChangeEvent:
    """
    Evento de cambio de estado.

    Encapsula la información sobre un cambio de estado
    para notificar a los observadores.
    """

    def __init__(self, index: int, old_state: LineState, new_state: LineState):
        """
        Inicializa un evento de cambio de estado.

        Args:
            index: Índice de la línea que cambió
            old_state: Estado anterior
            new_state: Estado nuevo
        """
        self.index = index
        self.old_state = old_state
        self.new_state = new_state

    @property
    def changed_attributes(self) -> Set[str]:
        """Retorna conjunto de atributos que cambiaron."""
        changed = set()
        # Atributos de estado básicos
        for attr in ['selected', 'active', 'editing', 'hotlight', 'visible', 'cursor_pos']:
            if getattr(self.old_state, attr) != getattr(self.new_state, attr):
                changed.add(attr)

        # Atributos de visibilidad de sub-widgets
        for attr in ['show_number_line', 'show_tree', 'show_infobar']:
            if getattr(self.old_state, attr) != getattr(self.new_state, attr):
                changed.add(attr)

        # Atributos de tema
        if self.old_state.alpha_background != self.new_state.alpha_background:
            changed.add('alpha_background')

        return changed

    def __repr__(self) -> str:
        """Representación legible del evento."""
        changes = ', '.join(f"{attr}: {getattr(self.old_state, attr)} → {getattr(self.new_state, attr)}"
                           for attr in self.changed_attributes)
        return f"StateChange[{self.index}]({changes})"


class DocumentStateManager:
    """
    Gestor centralizado de estados de líneas del documento.

    Este gestor es la única fuente de verdad para el estado de
    las líneas. Implementa el patrón Observer para notificar
    cambios a los interesados.

    Features:
        - Single Source of Truth para estados
        - Estados inmutables (LineState frozen)
        - Sistema de observadores para cambios
        - Validación automática de invariantes
        - Historial de cambios opcional (debug)

    Example:
        >>> manager = DocumentStateManager()
        >>> manager.activate_line(5, enter_edit_mode=True)
        >>> state = manager.get_state(5)
        >>> print(state)
        LineState[5](SEL|ACT|EDIT)
    """

    def __init__(self, enable_history: bool = False):
        """
        Inicializa el gestor de estados.

        Args:
            enable_history: Si True, mantiene historial de cambios (útil para debug)
        """
        # Almacenamiento de estados
        self._states: Dict[int, LineState] = {}

        # Estado global del documento
        self._active_index: Optional[int] = None
        self._selected_indices: Set[int] = set()

        # Sistema de observadores
        self._observers: List[Callable[[StateChangeEvent], None]] = []

        # Historial de cambios (opcional, para debugging)
        self._enable_history = enable_history
        self._history: List[StateChangeEvent] = [] if enable_history else None

        Logger.info("DocumentStateManager: Initialized")

    # ============================================================================
    # Public API - Acceso a Estados
    # ============================================================================

    def get_state(self, index: int) -> LineState:
        """
        Obtiene el estado de una línea.

        Si no existe estado para el índice, retorna un estado
        por defecto (no seleccionado, no activo, visible).

        Args:
            index: Índice de la línea

        Returns:
            LineState: Estado de la línea
        """
        return self._states.get(index, LineState(index=index))

    def get_all_states(self) -> Dict[int, LineState]:
        """
        Retorna copia de todos los estados.

        Returns:
            Dict con índice → estado
        """
        return self._states.copy()

    def get_active_index(self) -> Optional[int]:
        """
        Retorna el índice de la línea activa.

        Returns:
            int o None si no hay línea activa
        """
        return self._active_index

    def get_selected_indices(self) -> Set[int]:
        """
        Retorna conjunto de índices seleccionados.

        Returns:
            Set de índices
        """
        return self._selected_indices.copy()

    def has_selection(self) -> bool:
        """Retorna True si hay líneas seleccionadas."""
        return len(self._selected_indices) > 0

    def has_active_line(self) -> bool:
        """Retorna True si hay una línea activa."""
        return self._active_index is not None

    # ============================================================================
    # Public API - Modificación de Estados
    # ============================================================================

    def update_state(self, index: int, **changes):
        """
        Actualiza el estado de una línea.

        Este es el método fundamental para cambiar estados.
        Todos los demás métodos lo utilizan internamente.

        Args:
            index: Índice de la línea
            **changes: Atributos a cambiar

        Example:
            >>> manager.update_state(5, selected=True, hotlight=False)
        """
        old_state = self.get_state(index)
        new_state = old_state.with_changes(**changes)

        # Solo actualizar si realmente cambió algo
        if old_state != new_state:
            self._states[index] = new_state
            self._notify_observers(index, old_state, new_state)

            Logger.debug(f"DocumentStateManager: State updated - {StateChangeEvent(index, old_state, new_state)}")

    def activate_line(self, index: int, enter_edit_mode: bool = False, cursor_pos: Optional[Tuple[int, int]] = None, anim_type: str = 'fade'):
        """
        Activa una línea (solo una puede estar activa a la vez).

        Automáticamente:
        - Desactiva la línea previamente activa
        - Selecciona la nueva línea activa
        - Opcionalmente entra en modo edición

        Args:
            index: Índice de la línea a activar
            enter_edit_mode: Si True, entra en modo edición
            cursor_pos: Posición del cursor para animaciones
            anim_type: Tipo de animación ('fade', 'slide_up', 'slide_down', 'expand_up', 'expand_down')

        Example:
            >>> manager.activate_line(10, enter_edit_mode=True, cursor_pos=(5, 0), anim_type='fade')
        """
        # Desactivar línea anterior si existe
        if self._active_index is not None and self._active_index != index:
            self.deactivate_line(self._active_index, anim_type=anim_type)

        # Activar nueva línea
        self._active_index = index
        self._selected_indices.add(index)

        changes = {
            'active': True,
            'selected': True,
            'editing': enter_edit_mode,
            'anim_type': anim_type
        }

        if cursor_pos is not None:
            changes['cursor_pos'] = cursor_pos

        self.update_state(index, **changes)

        Logger.info(f"DocumentStateManager: Line {index} activated (edit={enter_edit_mode})")

    def deactivate_line(self, index: int, anim_type: str = 'fade'):
        """
        Desactiva una línea.

        Args:
            index: Índice de la línea a desactivar
            anim_type: Tipo de animación para la desactivación
        """
        if self._active_index == index:
            self._active_index = None

        self.update_state(index, active=False, editing=False, anim_type=anim_type)

        Logger.debug(f"DocumentStateManager: Line {index} deactivated (anim={anim_type})")

    def deactivate_all(self):
        """Desactiva todas las líneas."""
        if self._active_index is not None:
            self.deactivate_line(self._active_index)

    def select_line(self, index: int, multi: bool = False):
        """
        Selecciona una línea.

        Args:
            index: Índice de la línea
            multi: Si False, deselecciona todas las demás líneas primero
        """
        if not multi:
            self.clear_selection()

        self._selected_indices.add(index)
        self.update_state(index, selected=True)

        Logger.debug(f"DocumentStateManager: Line {index} selected (multi={multi})")

    def unselect_line(self, index: int):
        """
        Des-selecciona una línea.

        Args:
            index: Índice de la línea
        """
        self._selected_indices.discard(index)
        self.update_state(index, selected=False)

        Logger.debug(f"DocumentStateManager: Line {index} unselected")

    def toggle_selection(self, index: int):
        """
        Alterna la selección de una línea.

        Args:
            index: Índice de la línea
        """
        state = self.get_state(index)
        if state.selected:
            self.unselect_line(index)
        else:
            self.select_line(index, multi=True)

    def select_range(self, start: int, end: int):
        """
        Selecciona un rango de líneas.

        Args:
            start: Índice de inicio
            end: Índice de fin (inclusive)
        """
        self.clear_selection()

        begin = min(start, end)
        finish = max(start, end)

        for i in range(begin, finish + 1):
            self._selected_indices.add(i)
            self.update_state(i, selected=True)

        Logger.info(f"DocumentStateManager: Range selected [{begin}:{finish}]")

    def clear_selection(self):
        """Limpia toda la selección."""
        for index in list(self._selected_indices):
            self.update_state(index, selected=False)

        self._selected_indices.clear()

        Logger.debug("DocumentStateManager: Selection cleared")

    def toggle_edit_mode(self, index: int):
        """
        Alterna el modo edición para la línea activa.

        Solo funciona si la línea está activa.

        Args:
            index: Índice de la línea
        """
        if index == self._active_index:
            state = self.get_state(index)
            self.update_state(index, editing=not state.editing)

            Logger.debug(f"DocumentStateManager: Edit mode toggled for line {index}")

    def set_hotlight(self, index: int, value: bool):
        """
        Establece el estado de hotlight (hover del mouse).

        Args:
            index: Índice de la línea
            value: True para activar, False para desactivar
        """
        self.update_state(index, hotlight=value)

    def set_visibility(self, index: int, visible: bool):
        """
        Establece la visibilidad de una línea (filtros).

        Args:
            index: Índice de la línea
            visible: True para visible, False para oculta
        """
        self.update_state(index, visible=visible)

    # ============================================================================
    # Public API - Visibilidad de Sub-widgets (DataShow)
    # ============================================================================

    def set_show_number_line(self, index: int, value: bool):
        """
        Establece la visibilidad del número de línea para una línea específica.

        Args:
            index: Índice de la línea
            value: True para mostrar, False para ocultar
        """
        self.update_state(index, show_number_line=value)

    def set_show_number_line_all(self, value: bool):
        """
        Establece la visibilidad del número de línea para TODAS las líneas.

        Útil para cambios globales de configuración de UI.

        Args:
            value: True para mostrar, False para ocultar

        Example:
            >>> manager.set_show_number_line_all(False)  # Oculta números en todo el documento
        """
        for index in self._states.keys():
            self.update_state(index, show_number_line=value)

        Logger.info(f"DocumentStateManager: show_number_line set to {value} for all lines")

    def set_show_tree(self, index: int, value: bool):
        """
        Establece la visibilidad del gancho de árbol para una línea específica.

        Args:
            index: Índice de la línea
            value: True para mostrar, False para ocultar
        """
        self.update_state(index, show_tree=value)

    def set_show_tree_all(self, value: bool):
        """
        Establece la visibilidad del gancho de árbol para TODAS las líneas.

        Útil para cambios globales de configuración de UI.

        Args:
            value: True para mostrar, False para ocultar

        Example:
            >>> manager.set_show_tree_all(True)  # Muestra árbol en todo el documento
        """
        for index in self._states.keys():
            self.update_state(index, show_tree=value)

        Logger.info(f"DocumentStateManager: show_tree set to {value} for all lines")

    def set_show_infobar(self, index: int, value: bool):
        """
        Establece la visibilidad de la barra de información para una línea específica.

        Args:
            index: Índice de la línea
            value: True para mostrar, False para ocultar
        """
        self.update_state(index, show_infobar=value)

    def set_show_infobar_all(self, value: bool):
        """
        Establece la visibilidad de la barra de información para TODAS las líneas.

        Útil para cambios globales de configuración de UI.

        Args:
            value: True para mostrar, False para ocultar

        Example:
            >>> manager.set_show_infobar_all(True)  # Muestra infobar en todo el documento
        """
        for index in self._states.keys():
            self.update_state(index, show_infobar=value)

        Logger.info(f"DocumentStateManager: show_infobar set to {value} for all lines")

    # ============================================================================
    # Public API - Tema (DataThemed)
    # ============================================================================

    def set_alpha_background(self, index: int, alpha: float):
        """
        Establece la opacidad del fondo para una línea específica.

        Args:
            index: Índice de la línea
            alpha: Valor de opacidad (0.0 = transparente, 1.0 = opaco)
        """
        # Validar rango
        alpha = max(0.0, min(1.0, alpha))
        self.update_state(index, alpha_background=alpha)

    def set_alpha_background_all(self, alpha: float):
        """
        Establece la opacidad del fondo para TODAS las líneas.

        Útil para cambios globales de tema.

        Args:
            alpha: Valor de opacidad (0.0 = transparente, 1.0 = opaco)

        Example:
            >>> manager.set_alpha_background_all(0.5)  # 50% opacidad en todas las líneas
        """
        # Validar rango
        alpha = max(0.0, min(1.0, alpha))

        for index in self._states.keys():
            self.update_state(index, alpha_background=alpha)

        Logger.info(f"DocumentStateManager: alpha_background set to {alpha} for all lines")

    def set_alpha_background_zebra(self, alpha_even: float = 0.0, alpha_odd: float = 0.1):
        """
        Aplica un patrón zebra (cebra) alternando opacidad de fondo entre líneas pares e impares.

        Útil para mejorar la legibilidad en documentos largos.

        Args:
            alpha_even: Opacidad para líneas pares (default: 0.0 = transparente)
            alpha_odd: Opacidad para líneas impares (default: 0.1 = ligeramente visible)

        Example:
            >>> manager.set_alpha_background_zebra(0.0, 0.15)  # Patrón zebra sutil
        """
        # Validar rangos
        alpha_even = max(0.0, min(1.0, alpha_even))
        alpha_odd = max(0.0, min(1.0, alpha_odd))

        for index in self._states.keys():
            alpha = alpha_even if index % 2 == 0 else alpha_odd
            self.update_state(index, alpha_background=alpha)

        Logger.info(f"DocumentStateManager: Zebra pattern applied (even={alpha_even}, odd={alpha_odd})")

    # ============================================================================
    # Public API - Operaciones de Documento
    # ============================================================================

    def initialize_states(self, count: int):
        """
        Inicializa estados para un documento con 'count' líneas.

        Crea estados por defecto para todas las líneas.

        Args:
            count: Número de líneas en el documento
        """
        self._states.clear()
        self._active_index = None
        self._selected_indices.clear()

        for i in range(count):
            self._states[i] = LineState(index=i)

        Logger.info(f"DocumentStateManager: Initialized {count} line states")

    def shift_indices(self, start_index: int, delta: int):
        """
        Desplaza índices de estados (para insert/delete).

        Cuando se inserta o elimina una línea, los índices
        posteriores deben ajustarse.

        Args:
            start_index: Índice desde donde desplazar
            delta: Desplazamiento (+1 para insert, -1 para delete)

        Example:
            >>> # Después de insertar línea en índice 5
            >>> manager.shift_indices(start_index=5, delta=1)
        """
        # Crear nuevo diccionario con índices ajustados
        new_states = {}

        for index, state in self._states.items():
            if index < start_index:
                # Antes del punto de inserción/eliminación: no cambiar
                new_states[index] = state
            else:
                # Después: ajustar índice
                new_index = index + delta
                if new_index >= 0:  # Solo si el nuevo índice es válido
                    new_states[new_index] = state.with_changes(index=new_index)

        self._states = new_states

        # Ajustar índice activo
        if self._active_index is not None and self._active_index >= start_index:
            self._active_index += delta
            if self._active_index < 0:
                self._active_index = None

        # Ajustar índices seleccionados
        new_selected = set()
        for index in self._selected_indices:
            if index < start_index:
                new_selected.add(index)
            else:
                new_index = index + delta
                if new_index >= 0:
                    new_selected.add(new_index)

        self._selected_indices = new_selected

        Logger.debug(f"DocumentStateManager: Indices shifted from {start_index} by {delta}")

    def remove_state(self, index: int):
        """
        Elimina el estado de una línea.

        Args:
            index: Índice de la línea a eliminar
        """
        if index in self._states:
            del self._states[index]

        if self._active_index == index:
            self._active_index = None

        self._selected_indices.discard(index)

        Logger.debug(f"DocumentStateManager: State removed for index {index}")

    def clear_all(self):
        """Limpia todos los estados."""
        self._states.clear()
        self._active_index = None
        self._selected_indices.clear()

        if self._enable_history:
            self._history.clear()

        Logger.info("DocumentStateManager: All states cleared")

    # ============================================================================
    # Public API - Sistema de Observadores
    # ============================================================================

    def subscribe(self, observer: Callable[[StateChangeEvent], None]):
        """
        Suscribe un observador a cambios de estado.

        El observador será llamado cada vez que cambie el estado
        de cualquier línea.

        Args:
            observer: Función que recibe StateChangeEvent

        Example:
            >>> def on_state_changed(event):
            ...     print(f"Line {event.index} changed: {event.changed_attributes}")
            >>> manager.subscribe(on_state_changed)
        """
        if observer not in self._observers:
            self._observers.append(observer)
            Logger.debug(f"DocumentStateManager: Observer subscribed ({len(self._observers)} total)")

    def unsubscribe(self, observer: Callable):
        """
        Des-suscribe un observador.

        Args:
            observer: Función a des-suscribir
        """
        if observer in self._observers:
            self._observers.remove(observer)
            Logger.debug(f"DocumentStateManager: Observer unsubscribed ({len(self._observers)} total)")

    def _notify_observers(self, index: int, old_state: LineState, new_state: LineState):
        """
        Notifica a todos los observadores de un cambio de estado.

        Args:
            index: Índice de la línea que cambió
            old_state: Estado anterior
            new_state: Estado nuevo
        """
        event = StateChangeEvent(index, old_state, new_state)

        # Guardar en historial si está habilitado
        if self._enable_history:
            self._history.append(event)

        # Notificar a todos los observadores
        for observer in self._observers:
            try:
                observer(event)
            except Exception as e:
                Logger.error(f"DocumentStateManager: Error in observer: {e}")

    # ============================================================================
    # Public API - Debug y Utilidades
    # ============================================================================

    def get_history(self) -> List[StateChangeEvent]:
        """
        Retorna el historial de cambios (si está habilitado).

        Returns:
            Lista de eventos de cambio
        """
        if not self._enable_history:
            Logger.warning("DocumentStateManager: History is not enabled")
            return []

        return self._history.copy()

    def print_state_summary(self):
        """Imprime un resumen del estado actual (útil para debug)."""
        print("\n" + "="*80)
        print("DOCUMENT STATE SUMMARY")
        print("="*80)
        print(f"Total states: {len(self._states)}")
        print(f"Active line: {self._active_index}")
        print(f"Selected lines: {sorted(self._selected_indices)}")
        print(f"Observers: {len(self._observers)}")

        if self._enable_history:
            print(f"History entries: {len(self._history)}")

        print("\nState breakdown:")
        selected = sum(1 for s in self._states.values() if s.selected)
        active = sum(1 for s in self._states.values() if s.active)
        editing = sum(1 for s in self._states.values() if s.editing)
        hotlight = sum(1 for s in self._states.values() if s.hotlight)
        hidden = sum(1 for s in self._states.values() if not s.visible)

        print(f"  Selected: {selected}")
        print(f"  Active: {active}")
        print(f"  Editing: {editing}")
        print(f"  Hotlight: {hotlight}")
        print(f"  Hidden: {hidden}")

        print("\nSub-widget visibility:")
        show_num = sum(1 for s in self._states.values() if s.show_number_line)
        show_tree = sum(1 for s in self._states.values() if s.show_tree)
        show_info = sum(1 for s in self._states.values() if s.show_infobar)

        print(f"  show_number_line: {show_num}")
        print(f"  show_tree: {show_tree}")
        print(f"  show_infobar: {show_info}")

        print("\nTheme:")
        if self._states:
            avg_alpha = sum(s.alpha_background for s in self._states.values()) / len(self._states)
            non_zero_alpha = sum(1 for s in self._states.values() if s.alpha_background > 0.0)
            print(f"  avg alpha_background: {avg_alpha:.2f}")
            print(f"  lines with alpha > 0: {non_zero_alpha}")

        print("="*80 + "\n")

    def validate_invariants(self) -> bool:
        """
        Valida invariantes del estado (para testing/debug).

        Invariantes:
        - Solo una línea puede estar activa
        - Toda línea activa debe estar seleccionada
        - _active_index debe corresponder a una línea con active=True
        - _selected_indices debe corresponder a líneas con selected=True

        Returns:
            True si todos los invariantes son válidos
        """
        errors = []

        # 1. Solo una línea activa
        active_lines = [idx for idx, state in self._states.items() if state.active]
        if len(active_lines) > 1:
            errors.append(f"Multiple active lines: {active_lines}")

        # 2. Línea activa está seleccionada
        for idx in active_lines:
            if not self._states[idx].selected:
                errors.append(f"Active line {idx} is not selected")

        # 3. _active_index coherente
        if self._active_index is not None:
            if self._active_index not in self._states:
                errors.append(f"Active index {self._active_index} has no state")
            elif not self._states[self._active_index].active:
                errors.append(f"Active index {self._active_index} state is not active")

        # 4. _selected_indices coherente
        for idx in self._selected_indices:
            if idx not in self._states:
                errors.append(f"Selected index {idx} has no state")
            elif not self._states[idx].selected:
                errors.append(f"Selected index {idx} state is not selected")

        # 5. Estados con selected=True en _selected_indices
        for idx, state in self._states.items():
            if state.selected and idx not in self._selected_indices:
                errors.append(f"Line {idx} is selected but not in _selected_indices")

        if errors:
            Logger.error("DocumentStateManager: Invariant validation failed:")
            for error in errors:
                Logger.error(f"  - {error}")
            return False

        return True

    def __repr__(self) -> str:
        """Representación legible del gestor."""
        return (f"DocumentStateManager(states={len(self._states)}, "
                f"active={self._active_index}, "
                f"selected={len(self._selected_indices)})")
