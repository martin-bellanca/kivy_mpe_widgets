#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar las nuevas variables de estado en StateManager.

Tests:
1. Creación de LineState con valores por defecto
2. Modificación de variables de visibilidad (show_number_line, show_tree, show_infobar)
3. Modificación de variables de tema (alpha_background)
4. Métodos globales de actualización (*_all)
5. Método zebra para alpha_background
6. Validación de invariantes
7. Sistema de observadores con nuevas variables

@author: mpbe
"""

from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager, LineState


def test_line_state_defaults():
    """Test 1: Verificar valores por defecto de LineState."""
    print("\n" + "="*80)
    print("TEST 1: LineState - Valores por defecto")
    print("="*80)

    state = LineState(index=0)

    print(f"index: {state.index}")
    print(f"selected: {state.selected}")
    print(f"active: {state.active}")
    print(f"editing: {state.editing}")
    print(f"hotlight: {state.hotlight}")
    print(f"visible: {state.visible}")
    print(f"cursor_pos: {state.cursor_pos}")
    print(f"\nshow_number_line: {state.show_number_line} (esperado: True)")
    print(f"show_tree: {state.show_tree} (esperado: False)")
    print(f"show_infobar: {state.show_infobar} (esperado: False)")
    print(f"alpha_background: {state.alpha_background} (esperado: 0.0)")

    assert state.show_number_line == True, "show_number_line debe ser True por defecto"
    assert state.show_tree == False, "show_tree debe ser False por defecto"
    assert state.show_infobar == False, "show_infobar debe ser False por defecto"
    assert state.alpha_background == 0.0, "alpha_background debe ser 0.0 por defecto"

    print("\n✓ TEST 1 PASÓ")


def test_line_state_with_changes():
    """Test 2: Modificar variables con with_changes()."""
    print("\n" + "="*80)
    print("TEST 2: LineState.with_changes() - Modificación de variables")
    print("="*80)

    old_state = LineState(index=5)
    new_state = old_state.with_changes(
        show_number_line=False,
        show_tree=True,
        show_infobar=True,
        alpha_background=0.5
    )

    print(f"Estado original: {old_state}")
    print(f"Estado nuevo: {new_state}")

    assert new_state.show_number_line == False, "show_number_line debe cambiar"
    assert new_state.show_tree == True, "show_tree debe cambiar"
    assert new_state.show_infobar == True, "show_infobar debe cambiar"
    assert new_state.alpha_background == 0.5, "alpha_background debe cambiar"

    # Verificar inmutabilidad
    assert old_state.show_number_line == True, "Estado original no debe cambiar (inmutabilidad)"

    print("\n✓ TEST 2 PASÓ")


def test_state_manager_individual():
    """Test 3: Métodos individuales del StateManager."""
    print("\n" + "="*80)
    print("TEST 3: DocumentStateManager - Métodos individuales")
    print("="*80)

    manager = DocumentStateManager()
    manager.initialize_states(10)

    # Test set_show_number_line
    manager.set_show_number_line(3, False)
    state = manager.get_state(3)
    assert state.show_number_line == False, "set_show_number_line debe funcionar"
    print(f"✓ set_show_number_line(3, False): {state}")

    # Test set_show_tree
    manager.set_show_tree(5, True)
    state = manager.get_state(5)
    assert state.show_tree == True, "set_show_tree debe funcionar"
    print(f"✓ set_show_tree(5, True): {state}")

    # Test set_show_infobar
    manager.set_show_infobar(7, True)
    state = manager.get_state(7)
    assert state.show_infobar == True, "set_show_infobar debe funcionar"
    print(f"✓ set_show_infobar(7, True): {state}")

    # Test set_alpha_background
    manager.set_alpha_background(2, 0.8)
    state = manager.get_state(2)
    assert state.alpha_background == 0.8, "set_alpha_background debe funcionar"
    print(f"✓ set_alpha_background(2, 0.8): {state}")

    # Test validación de rango (alpha > 1.0)
    manager.set_alpha_background(4, 1.5)
    state = manager.get_state(4)
    assert state.alpha_background == 1.0, "alpha debe limitarse a 1.0"
    print(f"✓ set_alpha_background(4, 1.5) -> limitado a {state.alpha_background}")

    print("\n✓ TEST 3 PASÓ")


def test_state_manager_global():
    """Test 4: Métodos globales (*_all)."""
    print("\n" + "="*80)
    print("TEST 4: DocumentStateManager - Métodos globales")
    print("="*80)

    manager = DocumentStateManager()
    manager.initialize_states(20)

    # Test set_show_number_line_all
    manager.set_show_number_line_all(False)
    for i in range(20):
        state = manager.get_state(i)
        assert state.show_number_line == False, f"Línea {i} debe tener show_number_line=False"
    print(f"✓ set_show_number_line_all(False) aplicado a 20 líneas")

    # Test set_show_tree_all
    manager.set_show_tree_all(True)
    for i in range(20):
        state = manager.get_state(i)
        assert state.show_tree == True, f"Línea {i} debe tener show_tree=True"
    print(f"✓ set_show_tree_all(True) aplicado a 20 líneas")

    # Test set_show_infobar_all
    manager.set_show_infobar_all(True)
    for i in range(20):
        state = manager.get_state(i)
        assert state.show_infobar == True, f"Línea {i} debe tener show_infobar=True"
    print(f"✓ set_show_infobar_all(True) aplicado a 20 líneas")

    # Test set_alpha_background_all
    manager.set_alpha_background_all(0.3)
    for i in range(20):
        state = manager.get_state(i)
        assert state.alpha_background == 0.3, f"Línea {i} debe tener alpha_background=0.3"
    print(f"✓ set_alpha_background_all(0.3) aplicado a 20 líneas")

    print("\n✓ TEST 4 PASÓ")


def test_zebra_pattern():
    """Test 5: Patrón zebra para alpha_background."""
    print("\n" + "="*80)
    print("TEST 5: DocumentStateManager - Patrón Zebra")
    print("="*80)

    manager = DocumentStateManager()
    manager.initialize_states(10)

    # Aplicar patrón zebra
    manager.set_alpha_background_zebra(alpha_even=0.0, alpha_odd=0.2)

    for i in range(10):
        state = manager.get_state(i)
        expected = 0.0 if i % 2 == 0 else 0.2
        assert state.alpha_background == expected, f"Línea {i} debe tener alpha={expected}"
        print(f"  Línea {i}: alpha_background={state.alpha_background} {'(par)' if i % 2 == 0 else '(impar)'}")

    print("\n✓ TEST 5 PASÓ")


def test_observer_notifications():
    """Test 6: Verificar que los observadores reciben notificaciones de cambios."""
    print("\n" + "="*80)
    print("TEST 6: Sistema de Observadores - Nuevas variables")
    print("="*80)

    manager = DocumentStateManager()
    manager.initialize_states(5)

    # Lista para capturar eventos
    events = []

    def observer(event):
        events.append(event)

    manager.subscribe(observer)

    # Cambiar show_number_line
    manager.set_show_number_line(2, False)
    assert len(events) == 1, "Debe haber 1 evento"
    assert 'show_number_line' in events[-1].changed_attributes, "Debe notificar cambio de show_number_line"
    print(f"✓ Evento capturado: {events[-1]}")

    # Cambiar show_tree
    manager.set_show_tree(2, True)
    assert len(events) == 2, "Debe haber 2 eventos"
    assert 'show_tree' in events[-1].changed_attributes, "Debe notificar cambio de show_tree"
    print(f"✓ Evento capturado: {events[-1]}")

    # Cambiar show_infobar
    manager.set_show_infobar(2, True)
    assert len(events) == 3, "Debe haber 3 eventos"
    assert 'show_infobar' in events[-1].changed_attributes, "Debe notificar cambio de show_infobar"
    print(f"✓ Evento capturado: {events[-1]}")

    # Cambiar alpha_background
    manager.set_alpha_background(2, 0.5)
    assert len(events) == 4, "Debe haber 4 eventos"
    assert 'alpha_background' in events[-1].changed_attributes, "Debe notificar cambio de alpha_background"
    print(f"✓ Evento capturado: {events[-1]}")

    print(f"\nTotal de eventos capturados: {len(events)}")
    print("\n✓ TEST 6 PASÓ")


def test_print_summary():
    """Test 7: Verificar que print_state_summary incluye nuevas variables."""
    print("\n" + "="*80)
    print("TEST 7: print_state_summary() - Nuevas secciones")
    print("="*80)

    manager = DocumentStateManager()
    manager.initialize_states(10)

    # Configurar algunos estados
    manager.set_show_number_line_all(False)
    manager.set_show_tree(3, True)
    manager.set_show_tree(5, True)
    manager.set_show_infobar(7, True)
    manager.set_alpha_background_zebra(0.0, 0.15)

    # Imprimir resumen
    manager.print_state_summary()

    print("✓ TEST 7 PASÓ (verificar visualmente el resumen arriba)")


def test_validate_invariants():
    """Test 8: Verificar que validate_invariants sigue funcionando."""
    print("\n" + "="*80)
    print("TEST 8: validate_invariants() - Con nuevas variables")
    print("="*80)

    manager = DocumentStateManager()
    manager.initialize_states(10)

    # Modificar algunas variables
    manager.set_show_number_line(3, False)
    manager.set_show_tree(5, True)
    manager.set_alpha_background(7, 0.5)

    # Activar una línea
    manager.activate_line(5, enter_edit_mode=True)

    # Validar invariantes
    result = manager.validate_invariants()
    assert result == True, "Los invariantes deben ser válidos"

    print("✓ Invariantes validados correctamente")
    print("\n✓ TEST 8 PASÓ")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "="*80)
    print("EJECUTANDO TESTS DEL STATE_MANAGER CON NUEVAS VARIABLES")
    print("="*80)

    try:
        test_line_state_defaults()
        test_line_state_with_changes()
        test_state_manager_individual()
        test_state_manager_global()
        test_zebra_pattern()
        test_observer_notifications()
        test_print_summary()
        test_validate_invariants()

        print("\n" + "="*80)
        print("✓✓✓ TODOS LOS TESTS PASARON EXITOSAMENTE ✓✓✓")
        print("="*80 + "\n")

    except AssertionError as e:
        print(f"\n✗ TEST FALLÓ: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR INESPERADO: {e}")
        raise


if __name__ == '__main__':
    run_all_tests()
