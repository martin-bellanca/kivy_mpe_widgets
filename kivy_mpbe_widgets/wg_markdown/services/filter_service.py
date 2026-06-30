#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  filter_service.py
#
#  Servicio para filtrado de documentos markdown
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
FilterService - Servicio para Filtrado de Documentos

Encapsula toda la lógica de negocio relacionada con:
- Filtrado por texto
- Filtrado con inclusión de padres (filter_up)
- Filtrado por tipo de línea
- Filtrado por criterios personalizados

Desacopla la lógica de negocio de la UI (widgets).
"""

from typing import Optional, List, Set, Callable
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


class FilterService:
    """
    Servicio para filtrado de documentos markdown.

    Este servicio encapsula toda la lógica de negocio relacionada
    con el filtrado de líneas de documento.

    Responsibilities:
        - Filtrar líneas por texto
        - Incluir títulos padre (filter_up)
        - Filtrar por tipo de línea
        - Aplicar filtros personalizados
        - Gestionar visibilidad de líneas

    Attributes:
        state_manager: Referencia al DocumentStateManager
        md_lines: Lista de líneas del documento
    """

    def __init__(
        self,
        state_manager: DocumentStateManager,
        md_lines: List[MDLine]
    ):
        """
        Inicializa el servicio de filtrado.

        Args:
            state_manager: Instancia del DocumentStateManager
            md_lines: Lista de líneas del documento
        """
        self.state_manager = state_manager
        self.md_lines = md_lines

    # ===========================================================================
    # FILTRADO BÁSICO POR TEXTO
    # ===========================================================================

    def filter_by_text(
        self,
        filter_text: str,
        case_sensitive: bool = False,
        include_parents: bool = False
    ) -> Set[int]:
        """
        Filtra líneas por texto.

        Args:
            filter_text: Texto a buscar
            case_sensitive: Si distingue mayúsculas/minúsculas
            include_parents: Si incluye títulos padre

        Returns:
            Set de índices que coinciden con el filtro
        """
        if not filter_text.strip():
            # Sin filtro, todas las líneas visibles
            return set(range(len(self.md_lines)))

        # Preparar texto de búsqueda
        search_text = filter_text if case_sensitive else filter_text.lower()

        # Encontrar líneas que coinciden
        matching_indices = set()

        for index, md_line in enumerate(self.md_lines):
            line_text = md_line.md_text if case_sensitive else md_line.md_text.lower()

            if search_text in line_text:
                matching_indices.add(index)

        # Incluir padres si se solicita
        if include_parents and matching_indices:
            matching_indices = self._include_parent_titles(matching_indices)

        Logger.info(
            f"FilterService: filter_by_text '{filter_text}' -> "
            f"{len(matching_indices)} matches (include_parents={include_parents})"
        )

        return matching_indices

    def _include_parent_titles(self, matching_indices: Set[int]) -> Set[int]:
        """
        Incluye títulos padre de las líneas que coinciden.

        Para cada línea que coincide, incluye todos los títulos padre
        en la jerarquía hasta el nivel superior.

        Args:
            matching_indices: Índices que ya coinciden

        Returns:
            Set expandido con índices de títulos padre
        """
        expanded_indices = matching_indices.copy()

        for index in matching_indices:
            # Obtener títulos padre de esta línea
            parent_indices = self._get_parent_title_indices(index)
            expanded_indices.update(parent_indices)

        Logger.info(
            f"FilterService: include_parents expanded "
            f"{len(matching_indices)} -> {len(expanded_indices)} lines"
        )

        return expanded_indices

    def _get_parent_title_indices(self, index: int) -> List[int]:
        """
        Obtiene los índices de todos los títulos padre de una línea.

        Recorre hacia arriba desde la línea actual buscando títulos
        de nivel superior jerárquicamente.

        Args:
            index: Índice de la línea

        Returns:
            Lista de índices de títulos padre (ordenados del más lejano al más cercano)
        """
        if index < 0 or index >= len(self.md_lines):
            return []

        parent_indices = []
        current_line = self.md_lines[index]

        # Si la línea actual es un título, obtener su nivel
        current_level = None
        if current_line.type == MD_LINE_TYPE.TITLE:
            current_level = current_line.get_title_level()

        # Recorrer hacia arriba buscando títulos padre
        for i in range(index - 1, -1, -1):
            line = self.md_lines[i]

            if line.type == MD_LINE_TYPE.TITLE:
                line_level = line.get_title_level()

                # Si es el primer título o es de nivel superior
                if current_level is None or line_level < current_level:
                    parent_indices.insert(0, i)  # Insertar al inicio para mantener orden
                    current_level = line_level

                    # Si llegamos al nivel más alto (nivel 1), terminar
                    if line_level == 1:
                        break

        return parent_indices

    # ===========================================================================
    # FILTRADO POR TIPO
    # ===========================================================================

    def filter_by_type(
        self,
        line_types: List[MD_LINE_TYPE],
        include_parents: bool = False
    ) -> Set[int]:
        """
        Filtra líneas por tipo.

        Args:
            line_types: Lista de tipos de línea a incluir
            include_parents: Si incluye títulos padre

        Returns:
            Set de índices que coinciden
        """
        matching_indices = set()

        for index, md_line in enumerate(self.md_lines):
            if md_line.type in line_types:
                matching_indices.add(index)

        # Incluir padres si se solicita
        if include_parents and matching_indices:
            matching_indices = self._include_parent_titles(matching_indices)

        Logger.info(
            f"FilterService: filter_by_type {line_types} -> "
            f"{len(matching_indices)} matches"
        )

        return matching_indices

    # ===========================================================================
    # FILTRADO PERSONALIZADO
    # ===========================================================================

    def filter_by_predicate(
        self,
        predicate: Callable[[MDLine], bool],
        include_parents: bool = False
    ) -> Set[int]:
        """
        Filtra líneas usando un predicado personalizado.

        Args:
            predicate: Función que toma MDLine y retorna bool
            include_parents: Si incluye títulos padre

        Returns:
            Set de índices que coinciden
        """
        matching_indices = set()

        for index, md_line in enumerate(self.md_lines):
            try:
                if predicate(md_line):
                    matching_indices.add(index)
            except Exception as e:
                Logger.warning(
                    f"FilterService: Error in predicate for line {index}: {e}"
                )

        # Incluir padres si se solicita
        if include_parents and matching_indices:
            matching_indices = self._include_parent_titles(matching_indices)

        Logger.info(
            f"FilterService: filter_by_predicate -> "
            f"{len(matching_indices)} matches"
        )

        return matching_indices

    # ===========================================================================
    # APLICAR FILTROS AL STATE MANAGER
    # ===========================================================================

    def apply_filter(
        self,
        matching_indices: Set[int],
        hide_non_matching: bool = True
    ) -> int:
        """
        Aplica el filtro al StateManager actualizando visibilidad.

        Args:
            matching_indices: Set de índices que coinciden con el filtro
            hide_non_matching: Si oculta las líneas que no coinciden

        Returns:
            Cantidad de líneas visibles después del filtro
        """
        visible_count = 0

        for index in range(len(self.md_lines)):
            should_be_visible = index in matching_indices

            if hide_non_matching:
                # Modo filtro: solo visibles las que coinciden
                self.state_manager.set_visibility(index, should_be_visible)
                if should_be_visible:
                    visible_count += 1
            else:
                # Modo resaltado: todas visibles, pero marcar las que coinciden
                self.state_manager.set_visibility(index, True)
                visible_count += 1

        Logger.info(
            f"FilterService: apply_filter -> "
            f"{visible_count}/{len(self.md_lines)} lines visible"
        )

        return visible_count

    def clear_filter(self) -> int:
        """
        Limpia el filtro mostrando todas las líneas.

        Returns:
            Cantidad de líneas visibles (todas)
        """
        for index in range(len(self.md_lines)):
            self.state_manager.set_visibility(index, True)

        Logger.info(
            f"FilterService: clear_filter -> "
            f"all {len(self.md_lines)} lines visible"
        )

        return len(self.md_lines)

    # ===========================================================================
    # FILTROS PRECONFIGURADOS
    # ===========================================================================

    def filter_only_titles(self, include_parents: bool = False) -> Set[int]:
        """Filtra solo títulos."""
        return self.filter_by_type([MD_LINE_TYPE.TITLE], include_parents)

    def filter_only_tasks(self, include_parents: bool = False) -> Set[int]:
        """Filtra solo tareas y TODOs."""
        return self.filter_by_type(
            [MD_LINE_TYPE.TASK, MD_LINE_TYPE.TODO],
            include_parents
        )

    def filter_only_lists(self, include_parents: bool = False) -> Set[int]:
        """Filtra solo listas."""
        return self.filter_by_type(
            [MD_LINE_TYPE.LIST, MD_LINE_TYPE.ORDER_LIST],
            include_parents
        )

    def filter_only_code(self, include_parents: bool = False) -> Set[int]:
        """Filtra solo bloques de código."""
        return self.filter_by_type(
            [MD_LINE_TYPE.CODE, MD_LINE_TYPE.START_CODE, MD_LINE_TYPE.END_CODE],
            include_parents
        )

    # ===========================================================================
    # CONSULTAS DE FILTRADO
    # ===========================================================================

    def get_visible_indices(self) -> List[int]:
        """
        Obtiene los índices de las líneas visibles actualmente.

        Returns:
            Lista de índices visibles
        """
        visible = []
        for index in range(len(self.md_lines)):
            state = self.state_manager.get_state(index)
            if state and state.visible:
                visible.append(index)

        return visible

    def get_hidden_indices(self) -> List[int]:
        """
        Obtiene los índices de las líneas ocultas actualmente.

        Returns:
            Lista de índices ocultos
        """
        hidden = []
        for index in range(len(self.md_lines)):
            state = self.state_manager.get_state(index)
            if state and not state.visible:
                hidden.append(index)

        return hidden

    def is_filter_active(self) -> bool:
        """
        Verifica si hay un filtro activo (algunas líneas ocultas).

        Returns:
            True si hay líneas ocultas
        """
        return len(self.get_hidden_indices()) > 0

    def get_filter_stats(self) -> dict:
        """
        Obtiene estadísticas del filtro actual.

        Returns:
            Dict con estadísticas
        """
        visible = self.get_visible_indices()
        hidden = self.get_hidden_indices()

        return {
            'total_lines': len(self.md_lines),
            'visible_lines': len(visible),
            'hidden_lines': len(hidden),
            'filter_active': self.is_filter_active(),
            'visibility_percentage': (len(visible) / len(self.md_lines) * 100) if self.md_lines else 0
        }
