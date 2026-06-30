#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_state_manager.py
#
#  Tests unitarios para DocumentStateManager y LineState
#
#  Created on 25/12/2024
#  @author: mpbe
#

import unittest
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from kivy_mpbe_widgets.wg_markdown.state_manager import (
    LineState,
    StateChangeEvent,
    DocumentStateManager
)


class TestLineState(unittest.TestCase):
    """Tests para la clase LineState."""

    def test_default_state(self):
        """Test estado por defecto."""
        state = LineState(index=0)

        self.assertEqual(state.index, 0)
        self.assertFalse(state.selected)
        self.assertFalse(state.active)
        self.assertFalse(state.editing)
        self.assertFalse(state.hotlight)
        self.assertTrue(state.visible)
        self.assertEqual(state.cursor_pos, (0, 0))

    def test_custom_state(self):
        """Test estado con valores personalizados."""
        state = LineState(
            index=5,
            selected=True,
            active=True,
            editing=True,
            cursor_pos=(10, 2)
        )

        self.assertEqual(state.index, 5)
        self.assertTrue(state.selected)
        self.assertTrue(state.active)
        self.assertTrue(state.editing)
        self.assertEqual(state.cursor_pos, (10, 2))

    def test_immutability(self):
        """Test que LineState es inmutable."""
        state = LineState(index=0, selected=False)

        # Intentar modificar debería fallar
        with self.assertRaises(AttributeError):
            state.selected = True

    def test_with_changes(self):
        """Test método with_changes crea nuevo estado."""
        old_state = LineState(index=5, selected=False, active=False)
        new_state = old_state.with_changes(selected=True, active=True)

        # Nuevo estado tiene los cambios
        self.assertTrue(new_state.selected)
        self.assertTrue(new_state.active)
        self.assertEqual(new_state.index, 5)

        # Estado original no cambió
        self.assertFalse(old_state.selected)
        self.assertFalse(old_state.active)

    def test_with_changes_partial(self):
        """Test with_changes con cambios parciales."""
        state = LineState(index=3, selected=True, active=False, editing=True)
        new_state = state.with_changes(active=True)

        # Solo active cambió
        self.assertTrue(new_state.active)
        # Los demás se mantienen
        self.assertTrue(new_state.selected)
        self.assertTrue(new_state.editing)
        self.assertEqual(new_state.index, 3)

    def test_repr(self):
        """Test representación en string."""
        state1 = LineState(index=0)
        self.assertIn("LineState[0]", repr(state1))
        self.assertIn("NONE", repr(state1))

        state2 = LineState(index=5, selected=True, active=True, editing=True)
        repr_str = repr(state2)
        self.assertIn("LineState[5]", repr_str)
        self.assertIn("SEL", repr_str)
        self.assertIn("ACT", repr_str)
        self.assertIn("EDIT", repr_str)


class TestStateChangeEvent(unittest.TestCase):
    """Tests para la clase StateChangeEvent."""

    def test_event_creation(self):
        """Test creación de evento."""
        old_state = LineState(index=3, selected=False)
        new_state = LineState(index=3, selected=True)

        event = StateChangeEvent(3, old_state, new_state)

        self.assertEqual(event.index, 3)
        self.assertEqual(event.old_state, old_state)
        self.assertEqual(event.new_state, new_state)

    def test_changed_attributes_single(self):
        """Test detección de un atributo cambiado."""
        old_state = LineState(index=5, selected=False, active=False)
        new_state = old_state.with_changes(selected=True)

        event = StateChangeEvent(5, old_state, new_state)

        self.assertEqual(event.changed_attributes, {'selected'})

    def test_changed_attributes_multiple(self):
        """Test detección de múltiples atributos cambiados."""
        old_state = LineState(index=5, selected=False, active=False, editing=False)
        new_state = old_state.with_changes(selected=True, active=True, editing=True)

        event = StateChangeEvent(5, old_state, new_state)

        self.assertEqual(event.changed_attributes, {'selected', 'active', 'editing'})

    def test_changed_attributes_none(self):
        """Test cuando no hay cambios."""
        state = LineState(index=5, selected=True)
        event = StateChangeEvent(5, state, state)

        self.assertEqual(event.changed_attributes, set())


class TestDocumentStateManager(unittest.TestCase):
    """Tests para la clase DocumentStateManager."""

    def setUp(self):
        """Configuración antes de cada test."""
        self.manager = DocumentStateManager()

    def tearDown(self):
        """Limpieza después de cada test."""
        self.manager.clear_all()

    # ========================================================================
    # Tests de Acceso a Estados
    # ========================================================================

    def test_get_default_state(self):
        """Test obtener estado por defecto."""
        state = self.manager.get_state(0)

        self.assertEqual(state.index, 0)
        self.assertFalse(state.selected)
        self.assertFalse(state.active)

    def test_get_active_index_none(self):
        """Test índice activo cuando no hay."""
        self.assertIsNone(self.manager.get_active_index())

    def test_get_selected_indices_empty(self):
        """Test índices seleccionados cuando no hay."""
        self.assertEqual(self.manager.get_selected_indices(), set())

    def test_has_selection_false(self):
        """Test has_selection sin selección."""
        self.assertFalse(self.manager.has_selection())

    def test_has_active_line_false(self):
        """Test has_active_line sin línea activa."""
        self.assertFalse(self.manager.has_active_line())

    # ========================================================================
    # Tests de Modificación de Estados
    # ========================================================================

    def test_update_state(self):
        """Test actualización básica de estado."""
        self.manager.update_state(0, selected=True, active=True)

        state = self.manager.get_state(0)
        self.assertTrue(state.selected)
        self.assertTrue(state.active)

    def test_update_state_multiple_times(self):
        """Test actualización múltiple."""
        self.manager.update_state(0, selected=True)
        self.manager.update_state(0, active=True)
        self.manager.update_state(0, editing=True)

        state = self.manager.get_state(0)
        self.assertTrue(state.selected)
        self.assertTrue(state.active)
        self.assertTrue(state.editing)

    def test_activate_line_single(self):
        """Test activar una línea."""
        self.manager.activate_line(5)

        state = self.manager.get_state(5)
        self.assertTrue(state.active)
        self.assertTrue(state.selected)
        self.assertFalse(state.editing)

        self.assertEqual(self.manager.get_active_index(), 5)
        self.assertIn(5, self.manager.get_selected_indices())

    def test_activate_line_with_edit_mode(self):
        """Test activar línea en modo edición."""
        self.manager.activate_line(3, enter_edit_mode=True)

        state = self.manager.get_state(3)
        self.assertTrue(state.active)
        self.assertTrue(state.selected)
        self.assertTrue(state.editing)

    def test_activate_line_with_cursor(self):
        """Test activar línea con posición de cursor."""
        self.manager.activate_line(2, cursor_pos=(10, 5))

        state = self.manager.get_state(2)
        self.assertEqual(state.cursor_pos, (10, 5))

    def test_activate_line_deactivates_previous(self):
        """Test que activar desactiva la línea anterior."""
        # Activar línea 5
        self.manager.activate_line(5)
        self.assertTrue(self.manager.get_state(5).active)

        # Activar línea 10 (debe desactivar 5)
        self.manager.activate_line(10)

        self.assertFalse(self.manager.get_state(5).active)
        self.assertTrue(self.manager.get_state(10).active)
        self.assertEqual(self.manager.get_active_index(), 10)

    def test_deactivate_line(self):
        """Test desactivar línea."""
        self.manager.activate_line(5, enter_edit_mode=True)
        self.manager.deactivate_line(5)

        state = self.manager.get_state(5)
        self.assertFalse(state.active)
        self.assertFalse(state.editing)
        self.assertIsNone(self.manager.get_active_index())

    def test_deactivate_all(self):
        """Test desactivar todas las líneas."""
        self.manager.activate_line(3)
        self.manager.deactivate_all()

        self.assertFalse(self.manager.get_state(3).active)
        self.assertIsNone(self.manager.get_active_index())

    # ========================================================================
    # Tests de Selección
    # ========================================================================

    def test_select_line_single(self):
        """Test seleccionar una línea."""
        self.manager.select_line(5)

        self.assertTrue(self.manager.get_state(5).selected)
        self.assertIn(5, self.manager.get_selected_indices())

    def test_select_line_multi_false_clears(self):
        """Test selección con multi=False limpia anteriores."""
        self.manager.select_line(3, multi=True)
        self.manager.select_line(5, multi=False)

        self.assertFalse(self.manager.get_state(3).selected)
        self.assertTrue(self.manager.get_state(5).selected)
        self.assertEqual(self.manager.get_selected_indices(), {5})

    def test_select_line_multi_true_adds(self):
        """Test selección con multi=True agrega."""
        self.manager.select_line(3, multi=True)
        self.manager.select_line(5, multi=True)
        self.manager.select_line(7, multi=True)

        self.assertEqual(self.manager.get_selected_indices(), {3, 5, 7})

    def test_unselect_line(self):
        """Test des-seleccionar línea."""
        self.manager.select_line(5)
        self.manager.unselect_line(5)

        self.assertFalse(self.manager.get_state(5).selected)
        self.assertNotIn(5, self.manager.get_selected_indices())

    def test_toggle_selection_on(self):
        """Test toggle activa selección."""
        self.manager.toggle_selection(5)

        self.assertTrue(self.manager.get_state(5).selected)

    def test_toggle_selection_off(self):
        """Test toggle desactiva selección."""
        self.manager.select_line(5)
        self.manager.toggle_selection(5)

        self.assertFalse(self.manager.get_state(5).selected)

    def test_select_range(self):
        """Test seleccionar rango."""
        self.manager.select_range(3, 7)

        for i in range(3, 8):
            self.assertTrue(self.manager.get_state(i).selected, f"Line {i} should be selected")

        self.assertEqual(self.manager.get_selected_indices(), {3, 4, 5, 6, 7})

    def test_select_range_reverse(self):
        """Test seleccionar rango invertido."""
        self.manager.select_range(7, 3)

        self.assertEqual(self.manager.get_selected_indices(), {3, 4, 5, 6, 7})

    def test_clear_selection(self):
        """Test limpiar selección."""
        self.manager.select_line(3, multi=True)
        self.manager.select_line(5, multi=True)
        self.manager.select_line(7, multi=True)

        self.manager.clear_selection()

        self.assertEqual(self.manager.get_selected_indices(), set())
        self.assertFalse(self.manager.get_state(3).selected)
        self.assertFalse(self.manager.get_state(5).selected)
        self.assertFalse(self.manager.get_state(7).selected)

    # ========================================================================
    # Tests de Edición
    # ========================================================================

    def test_toggle_edit_mode_on(self):
        """Test toggle edit mode activa."""
        self.manager.activate_line(5, enter_edit_mode=False)
        self.manager.toggle_edit_mode(5)

        self.assertTrue(self.manager.get_state(5).editing)

    def test_toggle_edit_mode_off(self):
        """Test toggle edit mode desactiva."""
        self.manager.activate_line(5, enter_edit_mode=True)
        self.manager.toggle_edit_mode(5)

        self.assertFalse(self.manager.get_state(5).editing)

    def test_toggle_edit_mode_only_if_active(self):
        """Test toggle edit solo funciona si está activa."""
        self.manager.select_line(5)  # Seleccionada pero no activa
        self.manager.toggle_edit_mode(5)

        # No debería cambiar porque no está activa
        self.assertFalse(self.manager.get_state(5).editing)

    # ========================================================================
    # Tests de Hotlight
    # ========================================================================

    def test_set_hotlight_on(self):
        """Test activar hotlight."""
        self.manager.set_hotlight(5, True)

        self.assertTrue(self.manager.get_state(5).hotlight)

    def test_set_hotlight_off(self):
        """Test desactivar hotlight."""
        self.manager.set_hotlight(5, True)
        self.manager.set_hotlight(5, False)

        self.assertFalse(self.manager.get_state(5).hotlight)

    # ========================================================================
    # Tests de Visibilidad
    # ========================================================================

    def test_set_visibility_hidden(self):
        """Test ocultar línea."""
        self.manager.set_visibility(5, False)

        self.assertFalse(self.manager.get_state(5).visible)

    def test_set_visibility_visible(self):
        """Test mostrar línea."""
        self.manager.set_visibility(5, False)
        self.manager.set_visibility(5, True)

        self.assertTrue(self.manager.get_state(5).visible)

    # ========================================================================
    # Tests de Operaciones de Documento
    # ========================================================================

    def test_initialize_states(self):
        """Test inicialización de estados."""
        self.manager.initialize_states(10)

        self.assertEqual(len(self.manager.get_all_states()), 10)

        for i in range(10):
            state = self.manager.get_state(i)
            self.assertEqual(state.index, i)
            self.assertFalse(state.selected)
            self.assertFalse(state.active)

    def test_shift_indices_insert(self):
        """Test shift indices al insertar."""
        # Crear estados
        self.manager.initialize_states(5)
        self.manager.activate_line(3)

        # Insertar línea en índice 2 (shift +1 desde índice 2)
        self.manager.shift_indices(start_index=2, delta=1)

        # Índice activo debe ser 4 ahora (3 + 1)
        self.assertEqual(self.manager.get_active_index(), 4)

    def test_shift_indices_delete(self):
        """Test shift indices al eliminar."""
        self.manager.initialize_states(10)
        self.manager.activate_line(7)
        self.manager.select_line(5, multi=True)

        # Eliminar línea en índice 3 (shift -1 desde índice 4)
        self.manager.shift_indices(start_index=4, delta=-1)

        # Índice activo debe ser 6 ahora (7 - 1)
        self.assertEqual(self.manager.get_active_index(), 6)

        # Índice seleccionado 5 debe ser 4 ahora
        self.assertIn(4, self.manager.get_selected_indices())

    def test_remove_state(self):
        """Test eliminar estado."""
        self.manager.update_state(5, selected=True)
        self.manager.remove_state(5)

        # Estado por defecto ahora
        state = self.manager.get_state(5)
        self.assertFalse(state.selected)

    def test_clear_all(self):
        """Test limpiar todos los estados."""
        self.manager.initialize_states(10)
        self.manager.activate_line(5)
        self.manager.select_line(3, multi=True)

        self.manager.clear_all()

        self.assertEqual(len(self.manager.get_all_states()), 0)
        self.assertIsNone(self.manager.get_active_index())
        self.assertEqual(len(self.manager.get_selected_indices()), 0)

    # ========================================================================
    # Tests de Sistema de Observadores
    # ========================================================================

    def test_subscribe_observer(self):
        """Test suscribir observador."""
        events_received = []

        def observer(event):
            events_received.append(event)

        self.manager.subscribe(observer)
        self.manager.update_state(5, selected=True)

        self.assertEqual(len(events_received), 1)
        event = events_received[0]
        self.assertEqual(event.index, 5)
        self.assertIn('selected', event.changed_attributes)

    def test_multiple_observers(self):
        """Test múltiples observadores."""
        events1 = []
        events2 = []

        self.manager.subscribe(lambda e: events1.append(e))
        self.manager.subscribe(lambda e: events2.append(e))

        self.manager.update_state(3, active=True)

        self.assertEqual(len(events1), 1)
        self.assertEqual(len(events2), 1)

    def test_unsubscribe_observer(self):
        """Test des-suscribir observador."""
        events_received = []

        def observer(event):
            events_received.append(event)

        self.manager.subscribe(observer)
        self.manager.update_state(5, selected=True)

        self.manager.unsubscribe(observer)
        self.manager.update_state(5, active=True)

        # Solo debe haber recibido el primer evento
        self.assertEqual(len(events_received), 1)

    def test_observer_not_called_if_no_change(self):
        """Test observador no se llama si no hay cambio."""
        events_received = []

        self.manager.subscribe(lambda e: events_received.append(e))

        # Actualizar con el mismo valor
        self.manager.update_state(5, selected=False)
        self.manager.update_state(5, selected=False)

        # Solo se llamó la primera vez (cambió de None a estado por defecto)
        # Pero como el estado por defecto ya es selected=False, no debería cambiar
        # En realidad, get_state crea uno nuevo, así que sí cambia
        # Mejor test: actualizar dos veces con mismo valor
        events_received.clear()
        state = self.manager.get_state(5)
        self.manager.update_state(5, selected=state.selected)

        self.assertEqual(len(events_received), 0)

    # ========================================================================
    # Tests de Validación
    # ========================================================================

    def test_validate_invariants_valid(self):
        """Test validación de invariantes con estado válido."""
        self.manager.initialize_states(10)
        self.manager.activate_line(5)
        self.manager.select_line(3, multi=True)

        self.assertTrue(self.manager.validate_invariants())

    def test_validate_invariants_active_not_selected(self):
        """Test validación falla si línea activa no está seleccionada."""
        # Forzar estado inválido manipulando directamente
        self.manager._states[5] = LineState(index=5, active=True, selected=False)
        self.manager._active_index = 5

        self.assertFalse(self.manager.validate_invariants())

    def test_validate_invariants_multiple_active(self):
        """Test validación falla si hay múltiples líneas activas."""
        # Forzar estado inválido
        self.manager._states[3] = LineState(index=3, active=True, selected=True)
        self.manager._states[5] = LineState(index=5, active=True, selected=True)

        self.assertFalse(self.manager.validate_invariants())

    # ========================================================================
    # Tests de Historial (Debug)
    # ========================================================================

    def test_history_disabled_by_default(self):
        """Test historial deshabilitado por defecto."""
        manager = DocumentStateManager(enable_history=False)
        manager.update_state(5, selected=True)

        history = manager.get_history()
        self.assertEqual(history, [])

    def test_history_enabled(self):
        """Test historial habilitado."""
        manager = DocumentStateManager(enable_history=True)
        manager.update_state(5, selected=True)
        manager.update_state(3, active=True)

        history = manager.get_history()
        self.assertEqual(len(history), 2)

        # Verificar eventos en historial
        self.assertEqual(history[0].index, 5)
        self.assertEqual(history[1].index, 3)


class TestIntegrationScenarios(unittest.TestCase):
    """Tests de escenarios de integración complejos."""

    def setUp(self):
        """Configuración antes de cada test."""
        self.manager = DocumentStateManager()
        self.manager.initialize_states(20)

    def test_scenario_edit_workflow(self):
        """Test flujo completo de edición."""
        # 1. Usuario hace click en línea 10
        self.manager.activate_line(10, enter_edit_mode=True, cursor_pos=(5, 0))

        # Verificar estado
        self.assertEqual(self.manager.get_active_index(), 10)
        state = self.manager.get_state(10)
        self.assertTrue(state.active)
        self.assertTrue(state.selected)
        self.assertTrue(state.editing)
        self.assertEqual(state.cursor_pos, (5, 0))

        # 2. Usuario presiona Escape (sale de edición pero mantiene activa)
        self.manager.toggle_edit_mode(10)

        state = self.manager.get_state(10)
        self.assertTrue(state.active)
        self.assertFalse(state.editing)

        # 3. Usuario hace click en otra línea
        self.manager.activate_line(15, enter_edit_mode=True)

        # Línea 10 ya no está activa
        self.assertFalse(self.manager.get_state(10).active)
        # Línea 15 está activa y editando
        self.assertTrue(self.manager.get_state(15).active)
        self.assertTrue(self.manager.get_state(15).editing)

    def test_scenario_multi_selection(self):
        """Test selección múltiple."""
        # 1. Seleccionar línea 5
        self.manager.select_line(5, multi=False)

        # 2. Ctrl+Click en línea 7 (multi-select)
        self.manager.select_line(7, multi=True)

        # 3. Ctrl+Click en línea 10 (multi-select)
        self.manager.select_line(10, multi=True)

        # Verificar
        self.assertEqual(self.manager.get_selected_indices(), {5, 7, 10})

        # 4. Shift+Click en línea 15 (seleccionar rango desde última)
        # Primero activar línea 10 (última seleccionada)
        self.manager.activate_line(10)
        # Luego seleccionar rango hasta 15
        self.manager.select_range(10, 15)

        # Verificar rango
        expected = {10, 11, 12, 13, 14, 15}
        self.assertEqual(self.manager.get_selected_indices(), expected)

    def test_scenario_filter_changes_visibility(self):
        """Test filtrado cambia visibilidad."""
        # Todas las líneas visibles inicialmente
        for i in range(20):
            self.assertTrue(self.manager.get_state(i).visible)

        # Aplicar filtro que oculta líneas impares
        for i in range(20):
            self.manager.set_visibility(i, i % 2 == 0)

        # Verificar
        for i in range(20):
            expected_visible = (i % 2 == 0)
            self.assertEqual(self.manager.get_state(i).visible, expected_visible)

    def test_scenario_insert_line_adjusts_indices(self):
        """Test insertar línea ajusta índices correctamente."""
        # Activar línea 10, seleccionar 5, 10, 15
        self.manager.activate_line(10)
        self.manager.select_line(5, multi=True)
        self.manager.select_line(15, multi=True)

        # Insertar línea en índice 7 (entre 5 y 10)
        self.manager.shift_indices(start_index=7, delta=1)

        # Índices ajustados:
        # - 5 no cambia (antes del punto de inserción)
        # - 10 → 11 (después)
        # - 15 → 16 (después)
        self.assertEqual(self.manager.get_active_index(), 11)
        self.assertIn(5, self.manager.get_selected_indices())
        self.assertIn(11, self.manager.get_selected_indices())
        self.assertIn(16, self.manager.get_selected_indices())


if __name__ == '__main__':
    unittest.main(verbosity=2)
