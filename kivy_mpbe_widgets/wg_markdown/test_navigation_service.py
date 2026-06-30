#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_navigation_service.py
#
#  Tests unitarios para NavigationService
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
Tests para NavigationService

Cobertura:
- Navegación secuencial (next/previous line)
- Navegación por títulos (next/previous/parent/sibling)
- Navegación por tipo de línea
- Búsqueda de líneas (por texto, por predicado)
- Navegación por visibilidad
- Consultas y utilidades
"""

import unittest
import sys
from pathlib import Path

# Agregar paths necesarios
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager
from kivy_mpbe_widgets.wg_markdown.services.navigation_service import NavigationService
from helpers_mpbe.markdown_document import MD_LINE_TYPE


class FakeMDLine:
    """MDLine simulada para testing."""

    def __init__(self, text: str, num: int, line_type: MD_LINE_TYPE = MD_LINE_TYPE.TEXT):
        self.md_text = text
        self.num_line = num
        self.type = line_type
        self.prev_line = None
        self.next_line = None

    def get_title_parent(self):
        """Simula obtener título padre."""
        if self.type != MD_LINE_TYPE.TITLE:
            return None

        # Buscar título de nivel superior hacia atrás
        current = self.prev_line
        current_level = self._get_level()

        while current:
            if current.type == MD_LINE_TYPE.TITLE:
                if current._get_level() < current_level:
                    return current
            current = current.prev_line

        return None

    def get_title_next(self):
        """Simula obtener siguiente título del mismo nivel."""
        if self.type != MD_LINE_TYPE.TITLE:
            return None

        current_level = self._get_level()
        current = self.next_line

        while current:
            if current.type == MD_LINE_TYPE.TITLE:
                level = current._get_level()
                if level == current_level:
                    return current
                elif level < current_level:
                    # Encontramos un nivel superior, no hay más hermanos
                    return None
            current = current.next_line

        return None

    def _get_level(self):
        """Obtiene nivel del título contando #."""
        if not self.md_text.startswith('#'):
            return 0
        return len(self.md_text) - len(self.md_text.lstrip('#'))


class TestNavigationServiceSequential(unittest.TestCase):
    """Tests para navegación secuencial."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        # Actualizar referencias prev/next
        for i in range(len(self.md_lines)):
            if i > 0:
                self.md_lines[i].prev_line = self.md_lines[i - 1]
            if i < len(self.md_lines) - 1:
                self.md_lines[i].next_line = self.md_lines[i + 1]

        self.state_manager.initialize_states(len(self.md_lines))
        self.service = NavigationService(self.state_manager, self.md_lines)

    def test_navigate_to_next_line(self):
        """Test navegar a siguiente línea."""
        # Activar línea 5
        self.state_manager.activate_line(5)

        next_index = self.service.navigate_to_next_line()

        self.assertEqual(next_index, 6)

    def test_navigate_to_previous_line(self):
        """Test navegar a línea anterior."""
        # Activar línea 5
        self.state_manager.activate_line(5)

        prev_index = self.service.navigate_to_previous_line()

        self.assertEqual(prev_index, 4)

    def test_navigate_next_from_last_line(self):
        """Test navegar next desde última línea."""
        # Activar última línea
        self.state_manager.activate_line(9)

        next_index = self.service.navigate_to_next_line()

        # No hay siguiente
        self.assertIsNone(next_index)

    def test_navigate_previous_from_first_line(self):
        """Test navegar previous desde primera línea."""
        # Activar primera línea
        self.state_manager.activate_line(0)

        prev_index = self.service.navigate_to_previous_line()

        # No hay anterior
        self.assertIsNone(prev_index)

    def test_navigate_without_active_line(self):
        """Test navegar sin línea activa."""
        # No activar ninguna línea

        next_index = self.service.navigate_to_next_line()
        prev_index = self.service.navigate_to_previous_line()

        # Debe retornar primera/última línea
        self.assertEqual(next_index, 0)
        self.assertEqual(prev_index, 9)

    def test_navigate_to_first_line(self):
        """Test navegar a primera línea."""
        index = self.service.navigate_to_first_line()
        self.assertEqual(index, 0)

    def test_navigate_to_last_line(self):
        """Test navegar a última línea."""
        index = self.service.navigate_to_last_line()
        self.assertEqual(index, 9)


class TestNavigationServiceTitles(unittest.TestCase):
    """Tests para navegación por títulos."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine("# Title 1", 1, MD_LINE_TYPE.TITLE),
            FakeMDLine("Text", 2, MD_LINE_TYPE.TEXT),
            FakeMDLine("## Title 2", 3, MD_LINE_TYPE.TITLE),
            FakeMDLine("Text", 4, MD_LINE_TYPE.TEXT),
            FakeMDLine("## Title 3", 5, MD_LINE_TYPE.TITLE),
            FakeMDLine("Text", 6, MD_LINE_TYPE.TEXT),
            FakeMDLine("# Title 4", 7, MD_LINE_TYPE.TITLE),
            FakeMDLine("Text", 8, MD_LINE_TYPE.TEXT),
        ]
        # Actualizar referencias prev/next
        for i in range(len(self.md_lines)):
            if i > 0:
                self.md_lines[i].prev_line = self.md_lines[i - 1]
            if i < len(self.md_lines) - 1:
                self.md_lines[i].next_line = self.md_lines[i + 1]

        self.state_manager.initialize_states(len(self.md_lines))
        self.service = NavigationService(self.state_manager, self.md_lines)

    def test_navigate_to_next_title(self):
        """Test navegar a siguiente título."""
        # Desde línea 1 (texto)
        next_title = self.service.navigate_to_next_title(from_index=1)

        # Debe encontrar título en índice 2
        self.assertEqual(next_title, 2)

    def test_navigate_to_previous_title(self):
        """Test navegar a título anterior."""
        # Desde línea 5
        prev_title = self.service.navigate_to_previous_title(from_index=5)

        # Debe encontrar título en índice 2
        self.assertEqual(prev_title, 2)

    def test_navigate_to_parent_title(self):
        """Test navegar a título padre."""
        # Desde título nivel 2 (índice 2) al padre nivel 1 (índice 0)
        parent = self.service.navigate_to_parent_title(from_index=2)

        self.assertEqual(parent, 0)

    def test_navigate_to_next_sibling_title(self):
        """Test navegar a siguiente título hermano."""
        # Desde título nivel 2 (índice 2) al siguiente nivel 2 (índice 4)
        sibling = self.service.navigate_to_next_sibling_title(from_index=2)

        self.assertEqual(sibling, 4)

    def test_no_more_titles(self):
        """Test cuando no hay más títulos."""
        # Desde última línea, no debe haber siguiente título
        next_title = self.service.navigate_to_next_title(from_index=7)

        self.assertIsNone(next_title)


class TestNavigationServiceByType(unittest.TestCase):
    """Tests para navegación por tipo de línea."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine("Text", 1, MD_LINE_TYPE.TEXT),
            FakeMDLine("- List 1", 2, MD_LINE_TYPE.LIST),
            FakeMDLine("Text", 3, MD_LINE_TYPE.TEXT),
            FakeMDLine("- List 2", 4, MD_LINE_TYPE.LIST),
            FakeMDLine("Text", 5, MD_LINE_TYPE.TEXT),
            FakeMDLine("- List 3", 6, MD_LINE_TYPE.LIST),
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = NavigationService(self.state_manager, self.md_lines)

    def test_navigate_to_next_of_type(self):
        """Test navegar a siguiente línea de tipo específico."""
        # Buscar siguiente LIST desde índice 0
        next_list = self.service.navigate_to_next_of_type(
            MD_LINE_TYPE.LIST,
            from_index=0
        )

        self.assertEqual(next_list, 1)

    def test_navigate_to_previous_of_type(self):
        """Test navegar a línea anterior de tipo específico."""
        # Buscar LIST anterior desde índice 5
        prev_list = self.service.navigate_to_previous_of_type(
            MD_LINE_TYPE.LIST,
            from_index=5
        )

        self.assertEqual(prev_list, 3)

    def test_no_more_of_type(self):
        """Test cuando no hay más líneas del tipo."""
        # Buscar LIST después del último
        next_list = self.service.navigate_to_next_of_type(
            MD_LINE_TYPE.LIST,
            from_index=5
        )

        self.assertIsNone(next_list)


class TestNavigationServiceSearch(unittest.TestCase):
    """Tests para búsqueda de líneas."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine("Hello World", 1),
            FakeMDLine("TODO: Fix bug", 2),
            FakeMDLine("Normal text", 3),
            FakeMDLine("Another TODO item", 4),
            FakeMDLine("Final line", 5),
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = NavigationService(self.state_manager, self.md_lines)

    def test_find_line_by_text(self):
        """Test buscar línea por texto."""
        found = self.service.find_line_by_text("TODO", from_index=0)

        # Debe encontrar primera línea con TODO (índice 1)
        self.assertEqual(found, 1)

    def test_find_line_by_text_case_sensitive(self):
        """Test búsqueda sensible a mayúsculas."""
        found = self.service.find_line_by_text(
            "todo",
            case_sensitive=True,
            from_index=0
        )

        # No debe encontrar (TODO != todo)
        self.assertIsNone(found)

    def test_find_line_by_text_case_insensitive(self):
        """Test búsqueda insensible a mayúsculas."""
        found = self.service.find_line_by_text(
            "todo",
            case_sensitive=False,
            from_index=0
        )

        # Debe encontrar (TODO == todo con case_sensitive=False)
        self.assertEqual(found, 1)

    def test_find_next_occurrence(self):
        """Test buscar siguiente ocurrencia."""
        # Encontrar primera ocurrencia
        first = self.service.find_line_by_text("TODO", from_index=0)
        self.assertEqual(first, 1)

        # Encontrar siguiente ocurrencia
        second = self.service.find_line_by_text("TODO", from_index=first)
        self.assertEqual(second, 3)

    def test_find_line_by_predicate(self):
        """Test buscar línea por predicado."""
        # Buscar línea con más de 15 caracteres
        found = self.service.find_line_by_predicate(
            lambda line: len(line.md_text) > 15,
            from_index=0
        )

        # Debe encontrar "Another TODO item" (índice 3)
        self.assertEqual(found, 3)

    def test_find_all_of_type(self):
        """Test encontrar todas las líneas de un tipo."""
        # Agregar algunas listas
        self.md_lines[1].type = MD_LINE_TYPE.LIST
        self.md_lines[3].type = MD_LINE_TYPE.LIST

        all_lists = self.service.find_all_of_type(MD_LINE_TYPE.LIST)

        self.assertEqual(len(all_lists), 2)
        self.assertIn(1, all_lists)
        self.assertIn(3, all_lists)


class TestNavigationServiceVisibility(unittest.TestCase):
    """Tests para navegación por visibilidad."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = NavigationService(self.state_manager, self.md_lines)

        # Ocultar algunas líneas
        self.state_manager.set_visibility(2, False)
        self.state_manager.set_visibility(3, False)
        self.state_manager.set_visibility(7, False)

    def test_navigate_to_next_visible(self):
        """Test navegar a siguiente línea visible."""
        # Desde línea 1, la siguiente visible es 4 (saltando 2 y 3 ocultas)
        next_visible = self.service.navigate_to_next_visible(from_index=1)

        self.assertEqual(next_visible, 4)

    def test_navigate_to_previous_visible(self):
        """Test navegar a línea visible anterior."""
        # Desde línea 4, la anterior visible es 1 (saltando 2 y 3 ocultas)
        prev_visible = self.service.navigate_to_previous_visible(from_index=4)

        self.assertEqual(prev_visible, 1)

    def test_get_visible_count(self):
        """Test contar líneas visibles."""
        count = self.service.get_visible_count()

        # 10 líneas - 3 ocultas = 7 visibles
        self.assertEqual(count, 7)


class TestNavigationServiceUtilities(unittest.TestCase):
    """Tests para utilidades del servicio."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(5)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = NavigationService(self.state_manager, self.md_lines)

    def test_get_line_at_index(self):
        """Test obtener línea en índice."""
        line = self.service.get_line_at_index(2)

        self.assertIsNotNone(line)
        self.assertEqual(line, self.md_lines[2])

    def test_get_line_at_invalid_index(self):
        """Test obtener línea con índice inválido."""
        line = self.service.get_line_at_index(100)
        self.assertIsNone(line)

    def test_service_repr(self):
        """Test representación del servicio."""
        repr_str = repr(self.service)

        self.assertIn("NavigationService", repr_str)
        self.assertIn("5", repr_str)  # Total lines
        self.assertIn("visible=5", repr_str)  # Visible lines


class TestNavigationServiceEdgeCases(unittest.TestCase):
    """Tests para casos límite."""

    def test_empty_document(self):
        """Test con documento vacío."""
        state_manager = DocumentStateManager()
        md_lines = []
        state_manager.initialize_states(0)
        service = NavigationService(state_manager, md_lines)

        # Operaciones deben fallar gracefully
        self.assertIsNone(service.navigate_to_next_line())
        self.assertIsNone(service.navigate_to_first_line())
        self.assertIsNone(service.navigate_to_last_line())
        self.assertEqual(service.get_visible_count(), 0)

    def test_single_line_document(self):
        """Test con documento de una sola línea."""
        state_manager = DocumentStateManager()
        md_lines = [FakeMDLine("Only line", 1)]
        state_manager.initialize_states(1)
        service = NavigationService(state_manager, md_lines)

        # Activar la única línea
        state_manager.activate_line(0)

        # No hay siguiente ni anterior
        self.assertIsNone(service.navigate_to_next_line())
        self.assertIsNone(service.navigate_to_previous_line())

        # Pero sí hay primera y última
        self.assertEqual(service.navigate_to_first_line(), 0)
        self.assertEqual(service.navigate_to_last_line(), 0)


def run_tests():
    """Ejecuta todos los tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceSequential))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceTitles))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceByType))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceSearch))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceVisibility))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
