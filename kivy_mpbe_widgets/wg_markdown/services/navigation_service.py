#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  navigation_service.py
#
#  Servicio para navegación por el documento
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
NavigationService - Servicio para Navegación en el Documento

Encapsula toda la lógica de negocio relacionada con:
- Navegación línea por línea
- Navegación por títulos (jerarquía)
- Navegación por listas
- Scroll y visibilidad
- Búsqueda de líneas por criterio

Desacopla la lógica de negocio de la UI (widgets).
"""

from typing import Optional, List, Callable
from kivy.logger import Logger

# Imports relativos dentro del proyecto
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager
from helpers_mpbe.markdown_document import MD_LINE_TYPE
from helpers_mpbe.markdown_document.md_document import MDLine


class NavigationService:
    """
    Servicio para navegación por el documento.

    Este servicio encapsula toda la lógica de negocio relacionada
    con la navegación estructurada por el documento markdown.

    Responsibilities:
        - Navegación secuencial (arriba/abajo)
        - Navegación por títulos (jerarquía)
        - Navegación por listas
        - Encontrar líneas por criterio
        - Scroll y asegurar visibilidad
        - Saltar a posición específica

    Dependencies:
        - DocumentStateManager: Para obtener línea activa
        - md_lines: Lista de MDLine del documento
    """

    def __init__(self,
                 state_manager: DocumentStateManager,
                 md_lines: List[MDLine]):
        """
        Inicializa el servicio de navegación.

        Args:
            state_manager: Gestor de estados del documento
            md_lines: Lista de líneas del documento
        """
        self.state_manager = state_manager
        self.md_lines = md_lines

        Logger.info("NavigationService: Initialized")

    # ==========================================================================
    # Navegación Secuencial
    # ==========================================================================

    def navigate_to_next_line(self) -> Optional[int]:
        """
        Navega a la siguiente línea desde la línea activa.

        Returns:
            int: Índice de la siguiente línea, o None si no hay siguiente

        Side Effects:
            - No cambia la línea activa (solo retorna el índice)
            - El caller debe decidir si activar la línea

        Example:
            >>> next_idx = service.navigate_to_next_line()
            >>> if next_idx is not None:
            ...     line_service.activate_line(next_idx)
        """
        active_index = self.state_manager.get_active_index()

        if active_index is None:
            # No hay línea activa, retornar primera línea
            if len(self.md_lines) > 0:
                return 0
            return None

        # Siguiente línea
        next_index = active_index + 1

        if next_index < len(self.md_lines):
            Logger.debug(f"NavigationService: Next line -> {next_index}")
            return next_index

        # Ya estamos en la última línea
        Logger.debug("NavigationService: Already at last line")
        return None

    def navigate_to_previous_line(self) -> Optional[int]:
        """
        Navega a la línea anterior desde la línea activa.

        Returns:
            int: Índice de la línea anterior, o None si no hay anterior

        Side Effects:
            - No cambia la línea activa (solo retorna el índice)
        """
        active_index = self.state_manager.get_active_index()

        if active_index is None:
            # No hay línea activa, retornar última línea
            if len(self.md_lines) > 0:
                return len(self.md_lines) - 1
            return None

        # Línea anterior
        prev_index = active_index - 1

        if prev_index >= 0:
            Logger.debug(f"NavigationService: Previous line -> {prev_index}")
            return prev_index

        # Ya estamos en la primera línea
        Logger.debug("NavigationService: Already at first line")
        return None

    def navigate_to_first_line(self) -> Optional[int]:
        """
        Retorna el índice de la primera línea.

        Returns:
            int: 0 si hay líneas, None si documento vacío
        """
        if len(self.md_lines) > 0:
            return 0
        return None

    def navigate_to_last_line(self) -> Optional[int]:
        """
        Retorna el índice de la última línea.

        Returns:
            int: Índice de última línea, o None si documento vacío
        """
        if len(self.md_lines) > 0:
            return len(self.md_lines) - 1
        return None

    # ==========================================================================
    # Navegación por Títulos
    # ==========================================================================

    def navigate_to_next_title(self, from_index: Optional[int] = None) -> Optional[int]:
        """
        Navega al siguiente título desde el índice dado.

        Args:
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice del siguiente título, o None si no hay

        Example:
            >>> next_title = service.navigate_to_next_title()
            >>> if next_title is not None:
            ...     line_service.activate_line(next_title)
        """
        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                from_index = 0

        # Buscar siguiente título
        for index in range(from_index + 1, len(self.md_lines)):
            md_line = self.md_lines[index]
            if md_line.type == MD_LINE_TYPE.TITLE:
                Logger.debug(
                    f"NavigationService: Next title -> {index} ('{md_line.md_text[:30]}')"
                )
                return index

        Logger.debug("NavigationService: No more titles found")
        return None

    def navigate_to_previous_title(self, from_index: Optional[int] = None) -> Optional[int]:
        """
        Navega al título anterior desde el índice dado.

        Args:
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice del título anterior, o None si no hay
        """
        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                from_index = len(self.md_lines) - 1

        # Buscar título anterior
        for index in range(from_index - 1, -1, -1):
            md_line = self.md_lines[index]
            if md_line.type == MD_LINE_TYPE.TITLE:
                Logger.debug(
                    f"NavigationService: Previous title -> {index} ('{md_line.md_text[:30]}')"
                )
                return index

        Logger.debug("NavigationService: No previous titles found")
        return None

    def navigate_to_parent_title(self, from_index: Optional[int] = None) -> Optional[int]:
        """
        Navega al título padre (nivel superior) desde el índice dado.

        Usa la lógica de MDLine.get_title_parent().

        Args:
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice del título padre, o None si no hay
        """
        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                return None

        # Validar índice
        if not self._is_valid_index(from_index):
            return None

        # Obtener línea actual
        current_line = self.md_lines[from_index]

        # Obtener título padre usando método de MDLine
        parent_title = current_line.get_title_parent()

        if parent_title is None:
            Logger.debug("NavigationService: No parent title found")
            return None

        # Encontrar índice del padre
        try:
            parent_index = self.md_lines.index(parent_title)
            Logger.debug(
                f"NavigationService: Parent title -> {parent_index} "
                f"('{parent_title.md_text[:30]}')"
            )
            return parent_index
        except ValueError:
            Logger.warning("NavigationService: Parent title not found in list")
            return None

    def navigate_to_next_sibling_title(self, from_index: Optional[int] = None) -> Optional[int]:
        """
        Navega al siguiente título del mismo nivel desde el índice dado.

        Usa la lógica de MDLine.get_title_next().

        Args:
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice del siguiente título hermano, o None si no hay
        """
        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                return None

        # Validar índice
        if not self._is_valid_index(from_index):
            return None

        # Obtener línea actual
        current_line = self.md_lines[from_index]

        # Obtener siguiente título hermano
        next_sibling = current_line.get_title_next()

        if next_sibling is None:
            Logger.debug("NavigationService: No next sibling title found")
            return None

        # Encontrar índice
        try:
            sibling_index = self.md_lines.index(next_sibling)
            Logger.debug(
                f"NavigationService: Next sibling title -> {sibling_index} "
                f"('{next_sibling.md_text[:30]}')"
            )
            return sibling_index
        except ValueError:
            Logger.warning("NavigationService: Sibling title not found in list")
            return None

    # ==========================================================================
    # Navegación por Tipo de Línea
    # ==========================================================================

    def navigate_to_next_of_type(self,
                                  line_type: MD_LINE_TYPE,
                                  from_index: Optional[int] = None) -> Optional[int]:
        """
        Navega a la siguiente línea del tipo especificado.

        Args:
            line_type: Tipo de línea a buscar
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice de la siguiente línea del tipo, o None si no hay

        Example:
            >>> # Buscar siguiente lista
            >>> next_list = service.navigate_to_next_of_type(MD_LINE_TYPE.LIST)
        """
        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                from_index = 0

        # Buscar siguiente del tipo
        for index in range(from_index + 1, len(self.md_lines)):
            md_line = self.md_lines[index]
            if md_line.type == line_type:
                Logger.debug(
                    f"NavigationService: Next {line_type.name} -> {index}"
                )
                return index

        Logger.debug(f"NavigationService: No more {line_type.name} found")
        return None

    def navigate_to_previous_of_type(self,
                                     line_type: MD_LINE_TYPE,
                                     from_index: Optional[int] = None) -> Optional[int]:
        """
        Navega a la línea anterior del tipo especificado.

        Args:
            line_type: Tipo de línea a buscar
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice de la línea anterior del tipo, o None si no hay
        """
        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                from_index = len(self.md_lines) - 1

        # Buscar anterior del tipo
        for index in range(from_index - 1, -1, -1):
            md_line = self.md_lines[index]
            if md_line.type == line_type:
                Logger.debug(
                    f"NavigationService: Previous {line_type.name} -> {index}"
                )
                return index

        Logger.debug(f"NavigationService: No previous {line_type.name} found")
        return None

    # ==========================================================================
    # Búsqueda de Líneas
    # ==========================================================================

    def find_line_by_text(self,
                         search_text: str,
                         case_sensitive: bool = False,
                         from_index: Optional[int] = None) -> Optional[int]:
        """
        Busca la siguiente línea que contenga el texto especificado.

        Args:
            search_text: Texto a buscar
            case_sensitive: Si True, búsqueda sensible a mayúsculas
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice de la línea encontrada, o None si no se encuentra

        Example:
            >>> found = service.find_line_by_text("TODO", case_sensitive=True)
            >>> if found is not None:
            ...     line_service.activate_line(found)
        """
        if not search_text:
            return None

        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                from_index = 0

        # Preparar texto de búsqueda
        if not case_sensitive:
            search_text = search_text.lower()

        # Buscar
        for index in range(from_index + 1, len(self.md_lines)):
            md_line = self.md_lines[index]
            line_text = md_line.md_text

            if not case_sensitive:
                line_text = line_text.lower()

            if search_text in line_text:
                Logger.debug(
                    f"NavigationService: Found '{search_text}' at line {index}"
                )
                return index

        Logger.debug(f"NavigationService: Text '{search_text}' not found")
        return None

    def find_line_by_predicate(self,
                              predicate: Callable[[MDLine], bool],
                              from_index: Optional[int] = None) -> Optional[int]:
        """
        Busca la siguiente línea que cumpla con el predicado.

        Args:
            predicate: Función que recibe MDLine y retorna bool
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice de la línea encontrada, o None si no se encuentra

        Example:
            >>> # Buscar línea con más de 100 caracteres
            >>> long_line = service.find_line_by_predicate(
            ...     lambda line: len(line.md_text) > 100
            ... )
        """
        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                from_index = 0

        # Buscar
        for index in range(from_index + 1, len(self.md_lines)):
            md_line = self.md_lines[index]

            if predicate(md_line):
                Logger.debug(f"NavigationService: Predicate matched at line {index}")
                return index

        Logger.debug("NavigationService: No line matched predicate")
        return None

    def find_all_of_type(self, line_type: MD_LINE_TYPE) -> List[int]:
        """
        Encuentra todos los índices de líneas de un tipo específico.

        Args:
            line_type: Tipo de línea a buscar

        Returns:
            List[int]: Lista de índices de líneas del tipo

        Example:
            >>> all_titles = service.find_all_of_type(MD_LINE_TYPE.TITLE)
            >>> print(f"Found {len(all_titles)} titles")
        """
        result = []

        for index, md_line in enumerate(self.md_lines):
            if md_line.type == line_type:
                result.append(index)

        Logger.debug(f"NavigationService: Found {len(result)} lines of type {line_type.name}")

        return result

    # ==========================================================================
    # Navegación por Visibilidad
    # ==========================================================================

    def navigate_to_next_visible(self, from_index: Optional[int] = None) -> Optional[int]:
        """
        Navega a la siguiente línea visible (no oculta por filtros).

        Args:
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice de la siguiente línea visible, o None si no hay
        """
        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                from_index = 0

        # Buscar siguiente visible
        for index in range(from_index + 1, len(self.md_lines)):
            state = self.state_manager.get_state(index)
            if state.visible:
                Logger.debug(f"NavigationService: Next visible -> {index}")
                return index

        Logger.debug("NavigationService: No more visible lines")
        return None

    def navigate_to_previous_visible(self, from_index: Optional[int] = None) -> Optional[int]:
        """
        Navega a la línea visible anterior.

        Args:
            from_index: Índice desde donde buscar (None = línea activa)

        Returns:
            int: Índice de la línea visible anterior, o None si no hay
        """
        # Determinar índice de inicio
        if from_index is None:
            from_index = self.state_manager.get_active_index()
            if from_index is None:
                from_index = len(self.md_lines) - 1

        # Buscar anterior visible
        for index in range(from_index - 1, -1, -1):
            state = self.state_manager.get_state(index)
            if state.visible:
                Logger.debug(f"NavigationService: Previous visible -> {index}")
                return index

        Logger.debug("NavigationService: No previous visible lines")
        return None

    # ==========================================================================
    # Utilidades
    # ==========================================================================

    def get_line_at_index(self, index: int) -> Optional[MDLine]:
        """
        Obtiene la línea en el índice especificado.

        Args:
            index: Índice de la línea

        Returns:
            MDLine o None si índice inválido
        """
        if not self._is_valid_index(index):
            return None

        return self.md_lines[index]

    def get_visible_count(self) -> int:
        """
        Cuenta cuántas líneas están visibles (no ocultas).

        Returns:
            int: Cantidad de líneas visibles
        """
        count = 0

        for index in range(len(self.md_lines)):
            state = self.state_manager.get_state(index)
            if state.visible:
                count += 1

        return count

    def _is_valid_index(self, index: int) -> bool:
        """Valida que un índice esté dentro del rango."""
        return 0 <= index < len(self.md_lines)

    # ==========================================================================
    # Representación
    # ==========================================================================

    def __repr__(self) -> str:
        """Representación legible del servicio."""
        visible = self.get_visible_count()
        return f"NavigationService(lines={len(self.md_lines)}, visible={visible})"
