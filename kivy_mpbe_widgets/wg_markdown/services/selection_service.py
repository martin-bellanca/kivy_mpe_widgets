#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  selection_service.py
#
#  Servicio para operaciones de selección de líneas
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
SelectionService - Servicio para Operaciones de Selección

Encapsula toda la lógica de negocio relacionada con:
- Selección simple y múltiple
- Selección de rangos
- Toggle de selección
- Consultas sobre selección

Desacopla la lógica de negocio de la UI (widgets).
"""

from typing import List, Set, Optional
from kivy.logger import Logger

# Imports relativos dentro del proyecto
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager
from helpers_mpbe.markdown_document.md_document import MDLine


class SelectionService:
    """
    Servicio para operaciones de selección de líneas.

    Este servicio encapsula toda la lógica de negocio relacionada
    con la selección de líneas, tanto simple como múltiple.

    Responsibilities:
        - Selección simple (reemplaza anteriores)
        - Selección múltiple (agrega a existentes)
        - Selección de rangos
        - Toggle de selección
        - Limpiar selección
        - Consultar estado de selección

    Dependencies:
        - DocumentStateManager: Para gestión de estado de selección
        - md_lines: Lista de MDLine del documento
    """

    def __init__(self,
                 state_manager: DocumentStateManager,
                 md_lines: List[MDLine]):
        """
        Inicializa el servicio de selección.

        Args:
            state_manager: Gestor de estados del documento
            md_lines: Lista de líneas del documento
        """
        self.state_manager = state_manager
        self.md_lines = md_lines

        Logger.info("SelectionService: Initialized")

    # ==========================================================================
    # Selección Simple
    # ==========================================================================

    def select_single(self, index: int) -> bool:
        """
        Selecciona una única línea, limpiando la selección anterior.

        Args:
            index: Índice de la línea a seleccionar

        Returns:
            bool: True si se seleccionó correctamente

        Side Effects:
            - Limpia selección anterior
            - Marca la línea como seleccionada
            - Notifica a observadores

        Example:
            >>> service.select_single(5)
            >>> # Ahora solo la línea 5 está seleccionada
        """
        # Validar índice
        if not self._is_valid_index(index):
            Logger.warning(f"SelectionService: Invalid index {index}")
            return False

        # Seleccionar (automáticamente limpia anteriores)
        self.state_manager.select_line(index, multi=False)

        Logger.info(f"SelectionService: Single selection -> {index}")

        return True

    # ==========================================================================
    # Selección Múltiple
    # ==========================================================================

    def select_multi(self, index: int) -> bool:
        """
        Agrega una línea a la selección actual (multi-selección).

        Args:
            index: Índice de la línea a agregar a la selección

        Returns:
            bool: True si se agregó correctamente

        Side Effects:
            - Marca la línea como seleccionada
            - No afecta otras selecciones
            - Notifica a observadores

        Example:
            >>> service.select_multi(5)
            >>> service.select_multi(7)
            >>> service.select_multi(10)
            >>> # Ahora líneas 5, 7, 10 están seleccionadas
        """
        # Validar índice
        if not self._is_valid_index(index):
            Logger.warning(f"SelectionService: Invalid index {index}")
            return False

        # Agregar a selección
        self.state_manager.select_line(index, multi=True)

        Logger.info(f"SelectionService: Multi selection added -> {index}")

        return True

    def select_range(self, start: int, end: int) -> int:
        """
        Selecciona un rango de líneas (inclusivo).

        Args:
            start: Índice inicial del rango
            end: Índice final del rango (inclusivo)

        Returns:
            int: Cantidad de líneas seleccionadas

        Side Effects:
            - Limpia selección anterior
            - Selecciona todas las líneas en el rango
            - Notifica a observadores

        Example:
            >>> service.select_range(3, 8)
            >>> # Líneas 3, 4, 5, 6, 7, 8 están seleccionadas
        """
        # Normalizar rango (start debe ser menor que end)
        if start > end:
            start, end = end, start

        # Validar índices
        if not self._is_valid_index(start):
            Logger.warning(f"SelectionService: Invalid start index {start}")
            return 0
        if not self._is_valid_index(end):
            Logger.warning(f"SelectionService: Invalid end index {end}")
            return 0

        # Usar método del StateManager
        self.state_manager.select_range(start, end)

        count = end - start + 1
        Logger.info(f"SelectionService: Range selected [{start}..{end}] ({count} lines)")

        return count

    # ==========================================================================
    # Toggle de Selección
    # ==========================================================================

    def toggle_selection(self, index: int) -> bool:
        """
        Alterna el estado de selección de una línea.

        Si está seleccionada, la deselecciona.
        Si no está seleccionada, la selecciona (multi).

        Args:
            index: Índice de la línea

        Returns:
            bool: True si ahora está seleccionada, False si fue deseleccionada

        Side Effects:
            - Alterna estado de selección
            - Notifica a observadores

        Example:
            >>> service.toggle_selection(5)  # Selecciona
            True
            >>> service.toggle_selection(5)  # Deselecciona
            False
        """
        # Validar índice
        if not self._is_valid_index(index):
            Logger.warning(f"SelectionService: Invalid index {index}")
            return False

        # Usar método del StateManager
        self.state_manager.toggle_selection(index)

        # Obtener estado final
        state = self.state_manager.get_state(index)

        Logger.info(
            f"SelectionService: Toggled selection {index} -> {state.selected}"
        )

        return state.selected

    # ==========================================================================
    # Deselección
    # ==========================================================================

    def unselect(self, index: int) -> bool:
        """
        Deselecciona una línea específica.

        Args:
            index: Índice de la línea a deseleccionar

        Returns:
            bool: True si se deseleccionó

        Side Effects:
            - Marca línea como no seleccionada
            - Notifica a observadores
        """
        # Validar índice
        if not self._is_valid_index(index):
            Logger.warning(f"SelectionService: Invalid index {index}")
            return False

        # Deseleccionar
        self.state_manager.unselect_line(index)

        Logger.info(f"SelectionService: Unselected {index}")

        return True

    def clear_selection(self) -> int:
        """
        Limpia toda la selección.

        Returns:
            int: Cantidad de líneas que fueron deseleccionadas

        Side Effects:
            - Deselecciona todas las líneas
            - Notifica a observadores

        Example:
            >>> count = service.clear_selection()
            >>> print(f"{count} lines deselected")
        """
        # Obtener cantidad antes de limpiar
        count = len(self.state_manager.get_selected_indices())

        # Limpiar
        self.state_manager.clear_selection()

        Logger.info(f"SelectionService: Selection cleared ({count} lines)")

        return count

    # ==========================================================================
    # Selección Inteligente
    # ==========================================================================

    def select_all(self) -> int:
        """
        Selecciona todas las líneas del documento.

        Returns:
            int: Cantidad de líneas seleccionadas

        Side Effects:
            - Selecciona todas las líneas
            - Notifica a observadores
        """
        count = len(self.md_lines)

        if count > 0:
            self.select_range(0, count - 1)

        Logger.info(f"SelectionService: All lines selected ({count})")

        return count

    def select_visible(self) -> int:
        """
        Selecciona todas las líneas visibles (no ocultas por filtros).

        Returns:
            int: Cantidad de líneas seleccionadas

        Side Effects:
            - Limpia selección anterior
            - Selecciona líneas visibles
            - Notifica a observadores
        """
        # Limpiar selección actual
        self.clear_selection()

        count = 0

        # Seleccionar solo líneas visibles
        for index in range(len(self.md_lines)):
            state = self.state_manager.get_state(index)
            if state.visible:
                self.state_manager.select_line(index, multi=True)
                count += 1

        Logger.info(f"SelectionService: Visible lines selected ({count})")

        return count

    def invert_selection(self) -> int:
        """
        Invierte la selección actual.

        Las líneas seleccionadas se deseleccionan.
        Las líneas no seleccionadas se seleccionan.

        Returns:
            int: Cantidad de líneas ahora seleccionadas

        Side Effects:
            - Invierte estado de selección de todas las líneas
            - Notifica a observadores
        """
        # Obtener selección actual
        currently_selected = self.state_manager.get_selected_indices()

        # Invertir
        for index in range(len(self.md_lines)):
            if index in currently_selected:
                self.state_manager.unselect_line(index)
            else:
                self.state_manager.select_line(index, multi=True)

        new_count = len(self.state_manager.get_selected_indices())

        Logger.info(
            f"SelectionService: Selection inverted ({new_count} now selected)"
        )

        return new_count

    # ==========================================================================
    # Extensión de Selección
    # ==========================================================================

    def extend_selection_to(self, target_index: int) -> int:
        """
        Extiende la selección desde la línea activa hasta el índice objetivo.

        Si no hay línea activa, selecciona solo la línea objetivo.

        Args:
            target_index: Índice al que extender la selección

        Returns:
            int: Cantidad de líneas ahora seleccionadas en el rango

        Side Effects:
            - Selecciona rango entre línea activa y objetivo
            - Mantiene selecciones anteriores
            - Notifica a observadores
        """
        # Validar índice objetivo
        if not self._is_valid_index(target_index):
            Logger.warning(f"SelectionService: Invalid target index {target_index}")
            return 0

        # Obtener línea activa
        active_index = self.state_manager.get_active_index()

        if active_index is None:
            # No hay línea activa, seleccionar solo objetivo
            self.select_single(target_index)
            return 1

        # Determinar rango
        start = min(active_index, target_index)
        end = max(active_index, target_index)

        # Seleccionar rango (mantiene selecciones previas con multi=True)
        for index in range(start, end + 1):
            self.state_manager.select_line(index, multi=True)

        count = end - start + 1

        Logger.info(
            f"SelectionService: Extended selection [{start}..{end}] ({count} lines)"
        )

        return count

    # ==========================================================================
    # Consultas
    # ==========================================================================

    def is_selected(self, index: int) -> bool:
        """
        Verifica si una línea está seleccionada.

        Args:
            index: Índice de la línea

        Returns:
            bool: True si está seleccionada
        """
        if not self._is_valid_index(index):
            return False

        state = self.state_manager.get_state(index)
        return state.selected

    def get_selected_indices(self) -> Set[int]:
        """
        Obtiene el conjunto de índices seleccionados.

        Returns:
            Set[int]: Conjunto de índices seleccionados
        """
        return self.state_manager.get_selected_indices()

    def get_selected_count(self) -> int:
        """
        Obtiene la cantidad de líneas seleccionadas.

        Returns:
            int: Cantidad de líneas seleccionadas
        """
        return len(self.state_manager.get_selected_indices())

    def has_selection(self) -> bool:
        """
        Verifica si hay líneas seleccionadas.

        Returns:
            bool: True si hay al menos una línea seleccionada
        """
        return self.state_manager.has_selection()

    def get_selected_lines(self) -> List[MDLine]:
        """
        Obtiene la lista de líneas seleccionadas.

        Returns:
            List[MDLine]: Lista de objetos MDLine seleccionados
        """
        selected_indices = self.get_selected_indices()

        return [
            self.md_lines[index]
            for index in sorted(selected_indices)
            if self._is_valid_index(index)
        ]

    def get_selection_range(self) -> Optional[tuple[int, int]]:
        """
        Obtiene el rango de la selección (índice mínimo y máximo).

        Returns:
            tuple[int, int]: (min_index, max_index) o None si no hay selección
        """
        selected = self.get_selected_indices()

        if not selected:
            return None

        return (min(selected), max(selected))

    # ==========================================================================
    # Utilidades Privadas
    # ==========================================================================

    def _is_valid_index(self, index: int) -> bool:
        """Valida que un índice esté dentro del rango."""
        return 0 <= index < len(self.md_lines)

    # ==========================================================================
    # Representación
    # ==========================================================================

    def __repr__(self) -> str:
        """Representación legible del servicio."""
        count = self.get_selected_count()
        return f"SelectionService(lines={len(self.md_lines)}, selected={count})"
