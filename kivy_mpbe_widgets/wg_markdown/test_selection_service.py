#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_selection_service.py
#
#  Tests unitarios para SelectionService
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
Tests para SelectionService

Cobertura:
- Selección simple
- Selección múltiple
- Selección de rangos
- Toggle de selección
- Deselección
- Selección inteligente (all, visible, invert)
- Extensión de selección
- Consultas de selección
"""

import unittest
import sys
from pathlib import Path

# Agregar paths necesarios
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager
from kivy_mpbe_widgets.wg_markdown.services.selection_service import SelectionService
from helpers_mpbe.markdown_document import MD_LINE_TYPE


class FakeMDLine:
    """MDLine simulada para testing."""

    def __init__(self, text: str, num: int):
        self.md_text = text
        self.num_line = num
        self.type = MD_LINE_TYPE.TEXT


class TestSelectionServiceSingle(unittest.TestCase):
    """Tests para selección simple."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = SelectionService(self.state_manager, self.md_lines)

    def test_select_single_line(self):
        """Test selección simple de una línea."""
        success = self.service.select_single(3)

        self.assertTrue(success)
        self.assertTrue(self.service.is_selected(3))
        self.assertEqual(self.service.get_selected_count(), 1)

    def test_select_single_clears_previous(self):
        """Test que selección simple limpia selección anterior."""
        # Seleccionar múltiples líneas
        self.service.select_multi(2)
        self.service.select_multi(5)
        self.service.select_multi(7)
        self.assertEqual(self.service.get_selected_count(), 3)

        # Selección simple debe limpiar anteriores
        self.service.select_single(9)

        self.assertEqual(self.service.get_selected_count(), 1)
        self.assertTrue(self.service.is_selected(9))
        self.assertFalse(self.service.is_selected(2))
        self.assertFalse(self.service.is_selected(5))
        self.assertFalse(self.service.is_selected(7))

    def test_select_invalid_index(self):
        """Test selección con índice inválido."""
        success = self.service.select_single(100)
        self.assertFalse(success)

        success = self.service.select_single(-1)
        self.assertFalse(success)


class TestSelectionServiceMulti(unittest.TestCase):
    """Tests para selección múltiple."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = SelectionService(self.state_manager, self.md_lines)

    def test_select_multi(self):
        """Test selección múltiple."""
        self.service.select_multi(2)
        self.service.select_multi(5)
        self.service.select_multi(8)

        self.assertEqual(self.service.get_selected_count(), 3)
        self.assertTrue(self.service.is_selected(2))
        self.assertTrue(self.service.is_selected(5))
        self.assertTrue(self.service.is_selected(8))

    def test_select_multi_preserves_previous(self):
        """Test que multi preserva selecciones anteriores."""
        self.service.select_multi(3)
        self.assertEqual(self.service.get_selected_count(), 1)

        self.service.select_multi(7)
        self.assertEqual(self.service.get_selected_count(), 2)

        # Ambas deben estar seleccionadas
        self.assertTrue(self.service.is_selected(3))
        self.assertTrue(self.service.is_selected(7))


class TestSelectionServiceRange(unittest.TestCase):
    """Tests para selección de rangos."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = SelectionService(self.state_manager, self.md_lines)

    def test_select_range(self):
        """Test selección de rango."""
        count = self.service.select_range(3, 7)

        self.assertEqual(count, 5)  # 3, 4, 5, 6, 7
        self.assertEqual(self.service.get_selected_count(), 5)

        for i in range(3, 8):
            self.assertTrue(self.service.is_selected(i))

    def test_select_range_reversed(self):
        """Test que rango funciona aunque start > end."""
        count = self.service.select_range(7, 3)

        self.assertEqual(count, 5)
        self.assertEqual(self.service.get_selected_count(), 5)

    def test_select_range_single(self):
        """Test rango de una sola línea."""
        count = self.service.select_range(5, 5)

        self.assertEqual(count, 1)
        self.assertTrue(self.service.is_selected(5))


class TestSelectionServiceToggle(unittest.TestCase):
    """Tests para toggle de selección."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = SelectionService(self.state_manager, self.md_lines)

    def test_toggle_selection_selects(self):
        """Test toggle selecciona línea no seleccionada."""
        is_selected = self.service.toggle_selection(5)

        self.assertTrue(is_selected)
        self.assertTrue(self.service.is_selected(5))

    def test_toggle_selection_deselects(self):
        """Test toggle deselecciona línea seleccionada."""
        # Seleccionar primero
        self.service.select_single(5)
        self.assertTrue(self.service.is_selected(5))

        # Toggle debe deseleccionar
        is_selected = self.service.toggle_selection(5)

        self.assertFalse(is_selected)
        self.assertFalse(self.service.is_selected(5))

    def test_toggle_multiple_times(self):
        """Test toggle múltiples veces."""
        # Toggle 1: Selecciona
        self.assertTrue(self.service.toggle_selection(3))
        self.assertTrue(self.service.is_selected(3))

        # Toggle 2: Deselecciona
        self.assertFalse(self.service.toggle_selection(3))
        self.assertFalse(self.service.is_selected(3))

        # Toggle 3: Selecciona de nuevo
        self.assertTrue(self.service.toggle_selection(3))
        self.assertTrue(self.service.is_selected(3))


class TestSelectionServiceDeselection(unittest.TestCase):
    """Tests para deselección."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = SelectionService(self.state_manager, self.md_lines)

    def test_unselect_line(self):
        """Test deseleccionar línea específica."""
        # Seleccionar líneas
        self.service.select_multi(3)
        self.service.select_multi(5)
        self.service.select_multi(7)

        # Deseleccionar una
        success = self.service.unselect(5)

        self.assertTrue(success)
        self.assertFalse(self.service.is_selected(5))
        self.assertEqual(self.service.get_selected_count(), 2)

        # Otras deben seguir seleccionadas
        self.assertTrue(self.service.is_selected(3))
        self.assertTrue(self.service.is_selected(7))

    def test_clear_selection(self):
        """Test limpiar toda la selección."""
        # Seleccionar múltiples líneas
        self.service.select_range(2, 7)
        self.assertEqual(self.service.get_selected_count(), 6)

        # Limpiar
        count = self.service.clear_selection()

        self.assertEqual(count, 6)  # Retorna cantidad deseleccionada
        self.assertEqual(self.service.get_selected_count(), 0)
        self.assertFalse(self.service.has_selection())

    def test_clear_empty_selection(self):
        """Test limpiar cuando no hay selección."""
        count = self.service.clear_selection()
        self.assertEqual(count, 0)


class TestSelectionServiceSmart(unittest.TestCase):
    """Tests para selección inteligente."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = SelectionService(self.state_manager, self.md_lines)

    def test_select_all(self):
        """Test seleccionar todas las líneas."""
        count = self.service.select_all()

        self.assertEqual(count, 10)
        self.assertEqual(self.service.get_selected_count(), 10)

        for i in range(10):
            self.assertTrue(self.service.is_selected(i))

    def test_select_visible(self):
        """Test seleccionar solo líneas visibles."""
        # Ocultar algunas líneas
        self.state_manager.set_visibility(2, False)
        self.state_manager.set_visibility(5, False)
        self.state_manager.set_visibility(8, False)

        count = self.service.select_visible()

        # Deben seleccionarse solo las visibles (7 de 10)
        self.assertEqual(count, 7)
        self.assertEqual(self.service.get_selected_count(), 7)

        # Verificar que ocultas NO están seleccionadas
        self.assertFalse(self.service.is_selected(2))
        self.assertFalse(self.service.is_selected(5))
        self.assertFalse(self.service.is_selected(8))

    def test_invert_selection(self):
        """Test invertir selección."""
        # Seleccionar algunas líneas
        self.service.select_range(2, 5)
        self.assertEqual(self.service.get_selected_count(), 4)

        # Invertir
        count = self.service.invert_selection()

        # Ahora deben estar seleccionadas las otras 6
        self.assertEqual(count, 6)
        self.assertEqual(self.service.get_selected_count(), 6)

        # Verificar que 2-5 NO están seleccionadas
        for i in range(2, 6):
            self.assertFalse(self.service.is_selected(i))

        # Verificar que 0-1 y 6-9 SÍ están seleccionadas
        self.assertTrue(self.service.is_selected(0))
        self.assertTrue(self.service.is_selected(1))
        self.assertTrue(self.service.is_selected(6))
        self.assertTrue(self.service.is_selected(9))


class TestSelectionServiceExtension(unittest.TestCase):
    """Tests para extensión de selección."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = SelectionService(self.state_manager, self.md_lines)

    def test_extend_selection_to(self):
        """Test extender selección desde línea activa."""
        # Activar línea 3
        self.state_manager.activate_line(3)

        # Extender hasta línea 7
        count = self.service.extend_selection_to(7)

        self.assertEqual(count, 5)  # 3, 4, 5, 6, 7

        for i in range(3, 8):
            self.assertTrue(self.service.is_selected(i))

    def test_extend_selection_backwards(self):
        """Test extender selección hacia atrás."""
        # Activar línea 7
        self.state_manager.activate_line(7)

        # Extender hasta línea 3
        count = self.service.extend_selection_to(3)

        self.assertEqual(count, 5)

        for i in range(3, 8):
            self.assertTrue(self.service.is_selected(i))

    def test_extend_without_active_line(self):
        """Test extender sin línea activa."""
        # No hay línea activa
        count = self.service.extend_selection_to(5)

        # Debe seleccionar solo la línea objetivo
        self.assertEqual(count, 1)
        self.assertTrue(self.service.is_selected(5))


class TestSelectionServiceQueries(unittest.TestCase):
    """Tests para consultas de selección."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = SelectionService(self.state_manager, self.md_lines)

    def test_is_selected(self):
        """Test verificar si línea está seleccionada."""
        self.service.select_multi(3)
        self.service.select_multi(7)

        self.assertTrue(self.service.is_selected(3))
        self.assertTrue(self.service.is_selected(7))
        self.assertFalse(self.service.is_selected(5))

    def test_get_selected_indices(self):
        """Test obtener índices seleccionados."""
        self.service.select_multi(2)
        self.service.select_multi(5)
        self.service.select_multi(8)

        indices = self.service.get_selected_indices()

        self.assertEqual(len(indices), 3)
        self.assertIn(2, indices)
        self.assertIn(5, indices)
        self.assertIn(8, indices)

    def test_get_selected_count(self):
        """Test obtener cantidad de seleccionadas."""
        self.assertEqual(self.service.get_selected_count(), 0)

        self.service.select_range(3, 7)
        self.assertEqual(self.service.get_selected_count(), 5)

    def test_has_selection(self):
        """Test verificar si hay selección."""
        self.assertFalse(self.service.has_selection())

        self.service.select_single(5)
        self.assertTrue(self.service.has_selection())

        self.service.clear_selection()
        self.assertFalse(self.service.has_selection())

    def test_get_selected_lines(self):
        """Test obtener líneas seleccionadas."""
        self.service.select_multi(2)
        self.service.select_multi(5)
        self.service.select_multi(8)

        lines = self.service.get_selected_lines()

        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], self.md_lines[2])
        self.assertEqual(lines[1], self.md_lines[5])
        self.assertEqual(lines[2], self.md_lines[8])

    def test_get_selection_range(self):
        """Test obtener rango de selección."""
        self.service.select_multi(2)
        self.service.select_multi(5)
        self.service.select_multi(8)

        range_tuple = self.service.get_selection_range()

        self.assertEqual(range_tuple, (2, 8))

    def test_get_selection_range_empty(self):
        """Test rango cuando no hay selección."""
        range_tuple = self.service.get_selection_range()
        self.assertIsNone(range_tuple)


class TestSelectionServiceEdgeCases(unittest.TestCase):
    """Tests para casos límite."""

    def test_empty_document(self):
        """Test con documento vacío."""
        state_manager = DocumentStateManager()
        md_lines = []
        state_manager.initialize_states(0)
        service = SelectionService(state_manager, md_lines)

        # Operaciones deben fallar gracefully
        self.assertFalse(service.select_single(0))
        self.assertEqual(service.select_all(), 0)
        self.assertEqual(service.get_selected_count(), 0)

    def test_service_repr(self):
        """Test representación del servicio."""
        state_manager = DocumentStateManager()
        md_lines = [FakeMDLine(f"Line {i}", i + 1) for i in range(5)]
        state_manager.initialize_states(5)
        service = SelectionService(state_manager, md_lines)

        service.select_multi(1)
        service.select_multi(3)

        repr_str = repr(service)
        self.assertIn("SelectionService", repr_str)
        self.assertIn("5", repr_str)  # Total lines
        self.assertIn("2", repr_str)  # Selected lines


def run_tests():
    """Ejecuta todos los tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceSingle))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceMulti))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceRange))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceToggle))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceDeselection))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceSmart))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceExtension))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceQueries))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
