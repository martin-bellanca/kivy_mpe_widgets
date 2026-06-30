#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_line_service.py
#
#  Tests unitarios para LineService
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
Tests para LineService

Cobertura:
- Activación y desactivación de líneas
- Edición de líneas
- Movimiento de líneas (arriba/abajo)
- Inserción de líneas (arriba/abajo)
- Eliminación de líneas
- Validaciones de editabilidad
- Actualización de texto
- Consultas de línea
"""

import unittest
import sys
from pathlib import Path

# Agregar paths necesarios
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager
from kivy_mpbe_widgets.wg_markdown.services.line_service import LineService
from helpers_mpbe.markdown_document import MD_LINE_TYPE
from helpers_mpbe.markdown_document.md_document import MDLine


class FakeMDLine:
    """MDLine simulada para testing."""

    def __init__(self, text: str, num: int, line_type: MD_LINE_TYPE = MD_LINE_TYPE.TEXT):
        self.md_text = text
        self.num_line = num
        self.type = line_type
        self.prev_line = None
        self.next_line = None

    def update_type(self):
        """Simula actualización de tipo."""
        # Detectar tipo básico basado en texto
        if self.md_text.startswith('#'):
            self.type = MD_LINE_TYPE.TITLE
        elif self.md_text.startswith('- '):
            self.type = MD_LINE_TYPE.LIST
        elif self.md_text.startswith('---'):
            self.type = MD_LINE_TYPE.SEPARATOR
        else:
            self.type = MD_LINE_TYPE.TEXT


class TestLineServiceActivation(unittest.TestCase):
    """Tests para activación/desactivación de líneas."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = LineService(self.state_manager, self.md_lines)

    def test_activate_line_simple(self):
        """Test activación simple de línea."""
        success = self.service.activate_line(3)

        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_active_index(), 3)

        state = self.state_manager.get_state(3)
        self.assertTrue(state.active)
        self.assertTrue(state.selected)
        self.assertFalse(state.editing)

    def test_activate_line_with_edit_mode(self):
        """Test activación con modo edición."""
        success = self.service.activate_line(5, enter_edit=True, cursor_pos=(10, 0))

        self.assertTrue(success)

        state = self.state_manager.get_state(5)
        self.assertTrue(state.active)
        self.assertTrue(state.selected)
        self.assertTrue(state.editing)
        self.assertEqual(state.cursor_pos, (10, 0))

    def test_activate_line_deactivates_previous(self):
        """Test que activar una línea desactiva la anterior."""
        # Activar línea 2
        self.service.activate_line(2)
        self.assertEqual(self.state_manager.get_active_index(), 2)

        # Activar línea 7
        self.service.activate_line(7)
        self.assertEqual(self.state_manager.get_active_index(), 7)

        # Verificar que línea 2 ya no está activa
        state_2 = self.state_manager.get_state(2)
        self.assertFalse(state_2.active)
        self.assertFalse(state_2.editing)

    def test_activate_invalid_index(self):
        """Test activación con índice inválido."""
        success = self.service.activate_line(100)
        self.assertFalse(success)

        success = self.service.activate_line(-1)
        self.assertFalse(success)

    def test_activate_non_editable_in_edit_mode(self):
        """Test que no se puede editar línea no editable."""
        # Cambiar tipo a SEPARATOR (no editable)
        self.md_lines[3].type = MD_LINE_TYPE.SEPARATOR

        success = self.service.activate_line(3, enter_edit=True)

        # No debe permitir activar en modo edición
        self.assertFalse(success)

    def test_deactivate_current_line(self):
        """Test desactivación de línea actual."""
        # Activar línea
        self.service.activate_line(5, enter_edit=True)
        self.assertTrue(self.state_manager.get_state(5).active)

        # Desactivar
        success = self.service.deactivate_current_line()
        self.assertTrue(success)

        state = self.state_manager.get_state(5)
        self.assertFalse(state.active)
        self.assertFalse(state.editing)

    def test_deactivate_when_no_active_line(self):
        """Test desactivación cuando no hay línea activa."""
        success = self.service.deactivate_current_line()
        self.assertFalse(success)

    def test_toggle_edit_mode(self):
        """Test alternar modo edición."""
        # Activar línea sin edición
        self.service.activate_line(4)
        self.assertFalse(self.state_manager.get_state(4).editing)

        # Entrar en modo edición
        success = self.service.toggle_edit_mode()
        self.assertTrue(success)
        self.assertTrue(self.state_manager.get_state(4).editing)

        # Salir de modo edición
        success = self.service.toggle_edit_mode()
        self.assertTrue(success)
        self.assertFalse(self.state_manager.get_state(4).editing)

    def test_toggle_edit_mode_non_editable(self):
        """Test toggle en línea no editable."""
        # Cambiar tipo a no editable
        self.md_lines[3].type = MD_LINE_TYPE.CODE

        # Activar línea
        self.service.activate_line(3)

        # Intentar toggle
        success = self.service.toggle_edit_mode()
        self.assertFalse(success)


class TestLineServiceMovement(unittest.TestCase):
    """Tests para movimiento de líneas."""

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
        self.service = LineService(self.state_manager, self.md_lines)

    def test_move_line_up(self):
        """Test mover línea hacia arriba."""
        original_line = self.md_lines[5]

        new_index = self.service.move_line_up(5)

        self.assertEqual(new_index, 4)
        self.assertIs(self.md_lines[4], original_line)
        self.assertEqual(self.md_lines[4].num_line, 5)

    def test_move_line_down(self):
        """Test mover línea hacia abajo."""
        original_line = self.md_lines[3]

        new_index = self.service.move_line_down(3)

        self.assertEqual(new_index, 4)
        self.assertIs(self.md_lines[4], original_line)
        self.assertEqual(self.md_lines[4].num_line, 5)

    def test_move_first_line_up_fails(self):
        """Test que no se puede mover primera línea arriba."""
        new_index = self.service.move_line_up(0)
        self.assertIsNone(new_index)

    def test_move_last_line_down_fails(self):
        """Test que no se puede mover última línea abajo."""
        new_index = self.service.move_line_down(9)
        self.assertIsNone(new_index)

    def test_move_active_line_up(self):
        """Test mover línea activa hacia arriba (sin especificar índice)."""
        # Activar línea 6
        self.service.activate_line(6)

        # Mover sin especificar índice
        new_index = self.service.move_line_up()

        self.assertEqual(new_index, 5)

    def test_move_with_no_active_line_fails(self):
        """Test que falla si no hay línea activa y no se especifica índice."""
        new_index = self.service.move_line_up()
        self.assertIsNone(new_index)


class TestLineServiceInsertion(unittest.TestCase):
    """Tests para inserción de líneas."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(5)
        ]
        # Actualizar referencias
        for i in range(len(self.md_lines)):
            if i > 0:
                self.md_lines[i].prev_line = self.md_lines[i - 1]
            if i < len(self.md_lines) - 1:
                self.md_lines[i].next_line = self.md_lines[i + 1]

        self.state_manager.initialize_states(len(self.md_lines))
        self.service = LineService(self.state_manager, self.md_lines)

    def test_insert_line_below(self):
        """Test insertar línea debajo de índice especificado."""
        original_count = len(self.md_lines)

        new_index = self.service.insert_line_below(
            index=2,
            text="New line",
            line_type=MD_LINE_TYPE.TEXT
        )

        self.assertEqual(new_index, 3)
        self.assertEqual(len(self.md_lines), original_count + 1)
        self.assertEqual(self.md_lines[3].md_text, "New line")
        self.assertEqual(self.md_lines[3].num_line, 4)

    def test_insert_line_above(self):
        """Test insertar línea encima de índice especificado."""
        original_count = len(self.md_lines)

        new_index = self.service.insert_line_above(
            index=3,
            text="New line above",
            line_type=MD_LINE_TYPE.TEXT
        )

        self.assertEqual(new_index, 3)
        self.assertEqual(len(self.md_lines), original_count + 1)
        self.assertEqual(self.md_lines[3].md_text, "New line above")

    def test_insert_at_beginning(self):
        """Test insertar al principio del documento."""
        new_index = self.service.insert_line_above(
            index=0,
            text="First line",
            line_type=MD_LINE_TYPE.TEXT
        )

        self.assertEqual(new_index, 0)
        self.assertEqual(self.md_lines[0].md_text, "First line")
        self.assertEqual(self.md_lines[0].num_line, 1)

    def test_insert_updates_references(self):
        """Test que insertar actualiza referencias prev/next."""
        self.service.insert_line_below(2, "Inserted", MD_LINE_TYPE.TEXT)

        # Verificar que referencias están actualizadas
        inserted = self.md_lines[3]
        self.assertIsNotNone(inserted.prev_line)
        self.assertIsNotNone(inserted.next_line)
        self.assertEqual(inserted.prev_line, self.md_lines[2])
        self.assertEqual(inserted.next_line, self.md_lines[4])


class TestLineServiceDeletion(unittest.TestCase):
    """Tests para eliminación de líneas."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine(f"Line {i}", i + 1) for i in range(10)
        ]
        # Actualizar referencias
        for i in range(len(self.md_lines)):
            if i > 0:
                self.md_lines[i].prev_line = self.md_lines[i - 1]
            if i < len(self.md_lines) - 1:
                self.md_lines[i].next_line = self.md_lines[i + 1]

        self.state_manager.initialize_states(len(self.md_lines))
        self.service = LineService(self.state_manager, self.md_lines)

    def test_delete_line(self):
        """Test eliminar línea."""
        original_count = len(self.md_lines)

        success = self.service.delete_line(5)

        self.assertTrue(success)
        self.assertEqual(len(self.md_lines), original_count - 1)

    def test_delete_updates_num_lines(self):
        """Test que eliminar actualiza números de línea."""
        self.service.delete_line(3)

        # Verificar que números de línea están actualizados
        for i, line in enumerate(self.md_lines):
            self.assertEqual(line.num_line, i + 1)

    def test_delete_updates_references(self):
        """Test que eliminar actualiza referencias prev/next."""
        # Eliminar línea 5
        self.service.delete_line(5)

        # Verificar que línea 4 ahora apunta a línea 6 (antigua 7)
        line_4 = self.md_lines[4]
        line_5_new = self.md_lines[5]

        self.assertEqual(line_4.next_line, line_5_new)
        self.assertEqual(line_5_new.prev_line, line_4)

    def test_cannot_delete_last_line(self):
        """Test que no se puede eliminar la última línea."""
        # Crear lista con solo 1 línea
        self.md_lines = [FakeMDLine("Only line", 1)]
        self.state_manager.initialize_states(1)
        self.service = LineService(self.state_manager, self.md_lines)

        success = self.service.delete_line(0)
        self.assertFalse(success)

    def test_delete_active_line(self):
        """Test eliminar línea activa (sin especificar índice)."""
        # Activar línea 6
        self.service.activate_line(6)

        # Eliminar sin especificar índice
        success = self.service.delete_line()

        self.assertTrue(success)
        self.assertEqual(len(self.md_lines), 9)


class TestLineServiceQueries(unittest.TestCase):
    """Tests para consultas de línea."""

    def setUp(self):
        """Configuración para cada test."""
        self.state_manager = DocumentStateManager()
        self.md_lines = [
            FakeMDLine("# Title", 1, MD_LINE_TYPE.TITLE),
            FakeMDLine("Text line", 2, MD_LINE_TYPE.TEXT),
            FakeMDLine("---", 3, MD_LINE_TYPE.SEPARATOR),
            FakeMDLine("- List item", 4, MD_LINE_TYPE.LIST),
        ]
        self.state_manager.initialize_states(len(self.md_lines))
        self.service = LineService(self.state_manager, self.md_lines)

    def test_is_line_editable(self):
        """Test verificar si línea es editable."""
        self.assertTrue(self.service.is_line_editable(0))  # TITLE
        self.assertTrue(self.service.is_line_editable(1))  # TEXT
        self.assertFalse(self.service.is_line_editable(2))  # SEPARATOR
        self.assertTrue(self.service.is_line_editable(3))  # LIST

    def test_get_line_type(self):
        """Test obtener tipo de línea."""
        self.assertEqual(self.service.get_line_type(0), MD_LINE_TYPE.TITLE)
        self.assertEqual(self.service.get_line_type(1), MD_LINE_TYPE.TEXT)
        self.assertEqual(self.service.get_line_type(2), MD_LINE_TYPE.SEPARATOR)

    def test_get_line_text(self):
        """Test obtener texto de línea."""
        self.assertEqual(self.service.get_line_text(0), "# Title")
        self.assertEqual(self.service.get_line_text(1), "Text line")
        self.assertEqual(self.service.get_line_text(2), "---")

    def test_update_line_text(self):
        """Test actualizar texto de línea."""
        success = self.service.update_line_text(1, "Updated text")

        self.assertTrue(success)
        self.assertEqual(self.md_lines[1].md_text, "Updated text")

    def test_update_line_text_changes_type(self):
        """Test que actualizar texto actualiza tipo automáticamente."""
        # Cambiar texto normal a título
        self.service.update_line_text(1, "# New title")

        # Verificar que tipo se actualizó
        self.md_lines[1].update_type()
        self.assertEqual(self.md_lines[1].type, MD_LINE_TYPE.TITLE)


class TestLineServiceEdgeCase(unittest.TestCase):
    """Tests para casos límite."""

    def test_empty_document(self):
        """Test con documento vacío."""
        state_manager = DocumentStateManager()
        md_lines = []
        state_manager.initialize_states(0)
        service = LineService(state_manager, md_lines)

        # Todas las operaciones deben fallar gracefully
        self.assertFalse(service.activate_line(0))
        self.assertIsNone(service.move_line_up(0))
        self.assertFalse(service.delete_line(0))

    def test_service_repr(self):
        """Test representación del servicio."""
        state_manager = DocumentStateManager()
        md_lines = [FakeMDLine(f"Line {i}", i + 1) for i in range(5)]
        state_manager.initialize_states(5)
        service = LineService(state_manager, md_lines)

        repr_str = repr(service)
        self.assertIn("LineService", repr_str)
        self.assertIn("5", repr_str)


def run_tests():
    """Ejecuta todos los tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceActivation))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceMovement))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceInsertion))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceDeletion))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceQueries))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceEdgeCase))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
