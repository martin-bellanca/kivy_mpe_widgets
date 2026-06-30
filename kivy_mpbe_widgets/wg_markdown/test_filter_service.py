#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_filter_service.py
#
#  Tests unitarios para FilterService
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
Tests para FilterService

Cobertura:
- Filtrado por texto
- Filtrado con inclusión de padres (filter_up)
- Filtrado por tipo de línea
- Filtrado por predicado personalizado
- Aplicación de filtros al StateManager
- Limpieza de filtros
- Filtros preconfigurados
- Consultas y estadísticas
"""

import unittest
import sys
from pathlib import Path

# Agregar paths necesarios
project_root = Path(__file__).parent.parent.parent
helpers_root = Path.home() / 'Documentos' / 'Programacion' / 'Programacion_lin' / 'Visual_Studio_Code' / 'helpers_mpbe_prj'
widgets_root = Path.home() / 'Documentos' / 'Programacion' / 'Programacion_lin' / 'Visual_Studio_Code' / 'kivy_mpe_widgets_prj'

for path in [project_root, helpers_root, widgets_root]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager
from kivy_mpbe_widgets.wg_markdown.services.filter_service import FilterService
from helpers_mpbe.markdown_document import MD_LINE_TYPE


class FakeMDLine:
    """MDLine simulada para testing."""

    def __init__(self, text: str, num: int, line_type: MD_LINE_TYPE = MD_LINE_TYPE.TEXT):
        self.md_text = text
        self.num_line = num
        self.type = line_type
        self.prev_line = None
        self.next_line = None

    def get_title_level(self) -> int:
        """Obtiene nivel del título contando #."""
        if self.type != MD_LINE_TYPE.TITLE:
            return 0
        count = 0
        for char in self.md_text:
            if char == '#':
                count += 1
            else:
                break
        return count


def create_test_document():
    """Crea un documento de prueba con jerarquía de títulos."""
    lines = [
        FakeMDLine("# Title Level 1", 1, MD_LINE_TYPE.TITLE),          # 0
        FakeMDLine("Some text under title 1", 2, MD_LINE_TYPE.TEXT),   # 1
        FakeMDLine("## Title Level 2 A", 3, MD_LINE_TYPE.TITLE),       # 2
        FakeMDLine("Text under 2A", 4, MD_LINE_TYPE.TEXT),             # 3
        FakeMDLine("### Title Level 3", 5, MD_LINE_TYPE.TITLE),        # 4
        FakeMDLine("Important keyword here", 6, MD_LINE_TYPE.TEXT),    # 5
        FakeMDLine("## Title Level 2 B", 7, MD_LINE_TYPE.TITLE),       # 6
        FakeMDLine("More text", 8, MD_LINE_TYPE.TEXT),                 # 7
        FakeMDLine("- List item 1", 9, MD_LINE_TYPE.LIST),             # 8
        FakeMDLine("- [ ] Task item", 10, MD_LINE_TYPE.TASK),          # 9
        FakeMDLine("- [x] Done item", 11, MD_LINE_TYPE.TODO),          # 10
        FakeMDLine("```python", 12, MD_LINE_TYPE.START_CODE),          # 11
        FakeMDLine("code line", 13, MD_LINE_TYPE.CODE),                # 12
        FakeMDLine("```", 14, MD_LINE_TYPE.END_CODE),                  # 13
    ]

    # Configurar prev/next
    for i in range(len(lines)):
        if i > 0:
            lines[i].prev_line = lines[i - 1]
        if i < len(lines) - 1:
            lines[i].next_line = lines[i + 1]

    return lines


class TestFilterByText(unittest.TestCase):
    """Tests para filtrado por texto."""

    def setUp(self):
        self.md_lines = create_test_document()
        self.state_manager = DocumentStateManager()
        self.state_manager.initialize_states(len(self.md_lines))
        self.filter_service = FilterService(self.state_manager, self.md_lines)

    def test_filter_by_text_basic(self):
        """Test filtrado básico por texto."""
        matches = self.filter_service.filter_by_text("keyword")
        self.assertIn(5, matches)  # "Important keyword here"
        self.assertEqual(len(matches), 1)

    def test_filter_by_text_case_insensitive(self):
        """Test filtrado sin distinguir mayúsculas."""
        matches = self.filter_service.filter_by_text("KEYWORD", case_sensitive=False)
        self.assertIn(5, matches)

    def test_filter_by_text_case_sensitive(self):
        """Test filtrado distinguiendo mayúsculas."""
        matches = self.filter_service.filter_by_text("keyword", case_sensitive=True)
        self.assertIn(5, matches)

        matches = self.filter_service.filter_by_text("KEYWORD", case_sensitive=True)
        self.assertNotIn(5, matches)

    def test_filter_empty_text(self):
        """Test con texto vacío devuelve todas las líneas."""
        matches = self.filter_service.filter_by_text("")
        self.assertEqual(len(matches), len(self.md_lines))

    def test_filter_multiple_matches(self):
        """Test con múltiples coincidencias."""
        matches = self.filter_service.filter_by_text("text")
        self.assertGreater(len(matches), 1)


class TestFilterWithParents(unittest.TestCase):
    """Tests para filtrado con inclusión de padres."""

    def setUp(self):
        self.md_lines = create_test_document()
        self.state_manager = DocumentStateManager()
        self.state_manager.initialize_states(len(self.md_lines))
        self.filter_service = FilterService(self.state_manager, self.md_lines)

    def test_filter_with_parents_basic(self):
        """Test inclusión de títulos padre."""
        # Buscar "keyword" que está bajo "### Title Level 3"
        matches = self.filter_service.filter_by_text("keyword", include_parents=True)

        # Debe incluir:
        # - Línea 5: "Important keyword here"
        # - Línea 4: "### Title Level 3" (padre directo)
        # - Línea 2: "## Title Level 2 A" (abuelo)
        # - Línea 0: "# Title Level 1" (bisabuelo)
        self.assertIn(5, matches)  # La línea que coincide
        self.assertIn(4, matches)  # ### Title Level 3
        self.assertIn(2, matches)  # ## Title Level 2 A
        self.assertIn(0, matches)  # # Title Level 1

    def test_filter_without_parents(self):
        """Test sin inclusión de padres."""
        matches = self.filter_service.filter_by_text("keyword", include_parents=False)
        self.assertEqual(len(matches), 1)
        self.assertIn(5, matches)

    def test_get_parent_title_indices(self):
        """Test obtención de índices de títulos padre."""
        # Índice 5 ("Important keyword here") está bajo:
        # - Índice 4: ### Title Level 3
        # - Índice 2: ## Title Level 2 A
        # - Índice 0: # Title Level 1
        parents = self.filter_service._get_parent_title_indices(5)
        self.assertEqual(parents, [0, 2, 4])


class TestFilterByType(unittest.TestCase):
    """Tests para filtrado por tipo de línea."""

    def setUp(self):
        self.md_lines = create_test_document()
        self.state_manager = DocumentStateManager()
        self.state_manager.initialize_states(len(self.md_lines))
        self.filter_service = FilterService(self.state_manager, self.md_lines)

    def test_filter_only_titles(self):
        """Test filtrar solo títulos."""
        matches = self.filter_service.filter_by_type([MD_LINE_TYPE.TITLE])
        # Títulos en índices: 0, 2, 4, 6
        self.assertEqual(len(matches), 4)
        self.assertIn(0, matches)
        self.assertIn(2, matches)
        self.assertIn(4, matches)
        self.assertIn(6, matches)

    def test_filter_only_lists(self):
        """Test filtrar solo listas."""
        matches = self.filter_service.filter_by_type([MD_LINE_TYPE.LIST])
        self.assertEqual(len(matches), 1)
        self.assertIn(8, matches)

    def test_filter_tasks_and_todos(self):
        """Test filtrar tareas y TODOs."""
        matches = self.filter_service.filter_by_type([MD_LINE_TYPE.TASK, MD_LINE_TYPE.TODO])
        self.assertEqual(len(matches), 2)
        self.assertIn(9, matches)   # TASK
        self.assertIn(10, matches)  # TODO

    def test_filter_code_blocks(self):
        """Test filtrar bloques de código."""
        matches = self.filter_service.filter_by_type([
            MD_LINE_TYPE.CODE,
            MD_LINE_TYPE.START_CODE,
            MD_LINE_TYPE.END_CODE
        ])
        self.assertEqual(len(matches), 3)
        self.assertIn(11, matches)  # START_CODE
        self.assertIn(12, matches)  # CODE
        self.assertIn(13, matches)  # END_CODE


class TestFilterByPredicate(unittest.TestCase):
    """Tests para filtrado con predicado personalizado."""

    def setUp(self):
        self.md_lines = create_test_document()
        self.state_manager = DocumentStateManager()
        self.state_manager.initialize_states(len(self.md_lines))
        self.filter_service = FilterService(self.state_manager, self.md_lines)

    def test_filter_by_predicate_simple(self):
        """Test con predicado simple."""
        # Filtrar líneas que contienen "Title"
        matches = self.filter_service.filter_by_predicate(
            lambda line: "Title" in line.md_text
        )
        self.assertEqual(len(matches), 4)  # 4 títulos tienen "Title"

    def test_filter_by_predicate_complex(self):
        """Test con predicado complejo."""
        # Filtrar líneas de tipo TITLE con nivel 2
        matches = self.filter_service.filter_by_predicate(
            lambda line: line.type == MD_LINE_TYPE.TITLE and line.get_title_level() == 2
        )
        self.assertEqual(len(matches), 2)  # 2 títulos nivel 2

    def test_filter_by_predicate_with_parents(self):
        """Test predicado con inclusión de padres."""
        # Filtrar tareas e incluir padres
        matches = self.filter_service.filter_by_predicate(
            lambda line: line.type == MD_LINE_TYPE.TASK,
            include_parents=True
        )
        self.assertIn(9, matches)  # La tarea
        # Los títulos padre también deberían estar incluidos


class TestApplyFilter(unittest.TestCase):
    """Tests para aplicación de filtros al StateManager."""

    def setUp(self):
        self.md_lines = create_test_document()
        self.state_manager = DocumentStateManager()
        self.state_manager.initialize_states(len(self.md_lines))
        self.filter_service = FilterService(self.state_manager, self.md_lines)

    def test_apply_filter_hides_non_matching(self):
        """Test que apply_filter oculta líneas que no coinciden."""
        matches = {0, 2, 5}  # Solo 3 líneas
        visible_count = self.filter_service.apply_filter(matches, hide_non_matching=True)

        self.assertEqual(visible_count, 3)

        # Verificar visibilidad
        self.assertTrue(self.state_manager.get_state(0).visible)
        self.assertFalse(self.state_manager.get_state(1).visible)
        self.assertTrue(self.state_manager.get_state(2).visible)
        self.assertFalse(self.state_manager.get_state(3).visible)
        self.assertFalse(self.state_manager.get_state(4).visible)
        self.assertTrue(self.state_manager.get_state(5).visible)

    def test_clear_filter_shows_all(self):
        """Test que clear_filter muestra todas las líneas."""
        # Primero aplicar un filtro
        matches = {0, 2}
        self.filter_service.apply_filter(matches, hide_non_matching=True)

        # Verificar que algunas líneas están ocultas
        self.assertFalse(self.state_manager.get_state(1).visible)

        # Limpiar filtro
        visible_count = self.filter_service.clear_filter()

        # Todas las líneas deben estar visibles
        self.assertEqual(visible_count, len(self.md_lines))
        for i in range(len(self.md_lines)):
            self.assertTrue(self.state_manager.get_state(i).visible)


class TestPresetFilters(unittest.TestCase):
    """Tests para filtros preconfigurados."""

    def setUp(self):
        self.md_lines = create_test_document()
        self.state_manager = DocumentStateManager()
        self.state_manager.initialize_states(len(self.md_lines))
        self.filter_service = FilterService(self.state_manager, self.md_lines)

    def test_filter_only_titles_preset(self):
        """Test filtro preconfigurado de títulos."""
        matches = self.filter_service.filter_only_titles()
        self.assertEqual(len(matches), 4)

    def test_filter_only_tasks_preset(self):
        """Test filtro preconfigurado de tareas."""
        matches = self.filter_service.filter_only_tasks()
        self.assertEqual(len(matches), 2)

    def test_filter_only_lists_preset(self):
        """Test filtro preconfigurado de listas."""
        matches = self.filter_service.filter_only_lists()
        self.assertEqual(len(matches), 1)

    def test_filter_only_code_preset(self):
        """Test filtro preconfigurado de código."""
        matches = self.filter_service.filter_only_code()
        self.assertEqual(len(matches), 3)


class TestFilterQueries(unittest.TestCase):
    """Tests para consultas de filtrado."""

    def setUp(self):
        self.md_lines = create_test_document()
        self.state_manager = DocumentStateManager()
        self.state_manager.initialize_states(len(self.md_lines))
        self.filter_service = FilterService(self.state_manager, self.md_lines)

    def test_get_visible_indices(self):
        """Test obtener índices visibles."""
        # Al inicio todas visibles
        visible = self.filter_service.get_visible_indices()
        self.assertEqual(len(visible), len(self.md_lines))

        # Aplicar filtro
        matches = {0, 2, 5}
        self.filter_service.apply_filter(matches, hide_non_matching=True)

        visible = self.filter_service.get_visible_indices()
        self.assertEqual(set(visible), matches)

    def test_get_hidden_indices(self):
        """Test obtener índices ocultos."""
        # Al inicio ninguna oculta
        hidden = self.filter_service.get_hidden_indices()
        self.assertEqual(len(hidden), 0)

        # Aplicar filtro
        matches = {0, 2}
        self.filter_service.apply_filter(matches, hide_non_matching=True)

        hidden = self.filter_service.get_hidden_indices()
        self.assertEqual(len(hidden), len(self.md_lines) - 2)

    def test_is_filter_active(self):
        """Test verificar si filtro está activo."""
        # Sin filtro
        self.assertFalse(self.filter_service.is_filter_active())

        # Con filtro
        matches = {0, 2}
        self.filter_service.apply_filter(matches, hide_non_matching=True)
        self.assertTrue(self.filter_service.is_filter_active())

        # Limpiar filtro
        self.filter_service.clear_filter()
        self.assertFalse(self.filter_service.is_filter_active())

    def test_get_filter_stats(self):
        """Test obtener estadísticas de filtro."""
        # Sin filtro
        stats = self.filter_service.get_filter_stats()
        self.assertEqual(stats['total_lines'], len(self.md_lines))
        self.assertEqual(stats['visible_lines'], len(self.md_lines))
        self.assertEqual(stats['hidden_lines'], 0)
        self.assertFalse(stats['filter_active'])
        self.assertEqual(stats['visibility_percentage'], 100.0)

        # Con filtro (50% visible)
        matches = set(range(0, len(self.md_lines), 2))  # Índices pares
        self.filter_service.apply_filter(matches, hide_non_matching=True)

        stats = self.filter_service.get_filter_stats()
        self.assertEqual(stats['visible_lines'], len(matches))
        self.assertTrue(stats['filter_active'])


if __name__ == '__main__':
    unittest.main()
