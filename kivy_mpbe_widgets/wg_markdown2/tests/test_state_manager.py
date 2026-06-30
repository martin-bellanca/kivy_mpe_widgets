#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test unitario para StateManager - NO requiere display gráfico

Este test verifica la lógica del StateManager sin necesidad de
crear ventana de Kivy.

Para ejecutar:
    python test_state_manager.py

Fecha: 2026-01-15
Autor: Martin Pablo Bellanca
"""

import sys
import os

# Agregar paths al PYTHONPATH
sys.path.insert(0, '/home/mpbe/Documentos/Programacion/Programacion_lin/Visual_Studio_Code/kivy_mpe_widgets_prj')
sys.path.insert(0, '/home/mpbe/Documentos/Programacion/Programacion_lin/Visual_Studio_Code/helpers_mpbe_prj')

# Importar sin necesidad de display
os.environ['KIVY_NO_ARGS'] = '1'

from helpers_mpbe.markdown_document.md_document import MDDocument, MDLine
from helpers_mpbe.markdown_document import MD_LINE_TYPE

# Importar StateManager y LineState
from kivy_mpbe_widgets.wg_markdown2.core.state_manager import StateManager
from kivy_mpbe_widgets.wg_markdown2.core.line_state import LineState


def create_test_md_lines(count: int) -> list:
    """
    Crear lista de MDLines de prueba.

    Args:
        count: Número de líneas a crear

    Returns:
        List[MDLine]: Lista de líneas de prueba
    """
    lines = []
    prev_line = None

    for i in range(count):
        # Variar tipos para alturas no uniformes
        if i % 10 == 0:
            md_text = f"# Título {i}"
            line_type = MD_LINE_TYPE.TITLE
        elif i % 5 == 0:
            md_text = f"- Item de lista {i}"
            line_type = MD_LINE_TYPE.LIST
        else:
            md_text = f"Texto normal de la línea {i}"
            line_type = MD_LINE_TYPE.TEXT

        # Crear MDLine con argumentos requeridos
        md_line = MDLine(
            md_text=md_text,
            prev_line=prev_line,
            next_line=None,
            type=line_type,
            num_line=i
        )

        # Enlazar con línea anterior
        if prev_line is not None:
            prev_line.next_line = md_line

        lines.append(md_line)
        prev_line = md_line

    return lines


def test_load_document():
    """Test: Cargar documento en StateManager."""
    print("\n" + "=" * 60)
    print("TEST: load_document")
    print("=" * 60)

    manager = StateManager()
    lines = create_test_md_lines(100)

    manager.load_document(lines)

    # Verificaciones
    assert manager.get_total_lines() == 100, "Debería tener 100 líneas"
    assert manager.get_visible_lines_count() == 100, "Todas deberían ser visibles"
    assert manager.total_height > 0, "Altura total debería ser > 0"

    print(f"✓ Total líneas: {manager.get_total_lines()}")
    print(f"✓ Líneas visibles: {manager.get_visible_lines_count()}")
    print(f"✓ Altura total: {manager.total_height:.0f}px")
    print(f"✓ StateManager: {manager}")

    return manager


def test_get_state():
    """Test: Obtener estado de línea."""
    print("\n" + "=" * 60)
    print("TEST: get_state")
    print("=" * 60)

    manager = StateManager()
    lines = create_test_md_lines(50)
    manager.load_document(lines)

    # Obtener estado de línea 10
    state = manager.get_state(10)

    assert state is not None, "Estado no debería ser None"
    assert state.index == 10, "Índice debería ser 10"
    assert state.visible == True, "Debería ser visible"
    assert state.active == False, "No debería estar activo"

    print(f"✓ Estado línea 10: {state}")
    print(f"✓ Tipo: {state.md_line.type}")
    print(f"✓ Texto: {state.md_line.md_text[:30]}...")
    print(f"✓ Altura: {state.height:.0f}px")
    print(f"✓ Posición Y: {state.y_position:.0f}px")


def test_update_state():
    """Test: Actualizar estado de línea."""
    print("\n" + "=" * 60)
    print("TEST: update_state")
    print("=" * 60)

    manager = StateManager()
    lines = create_test_md_lines(30)
    manager.load_document(lines)

    # Estado inicial
    state_before = manager.get_state(5)
    print(f"Estado antes: {state_before}")

    # Activar línea 5
    manager.update_state(5, active=True, editing=True)

    # Verificar cambio
    state_after = manager.get_state(5)

    assert state_after.active == True, "Debería estar activo"
    assert state_after.editing == True, "Debería estar en edición"

    print(f"Estado después: {state_after}")
    print(f"✓ active: {state_after.active}")
    print(f"✓ editing: {state_after.editing}")


def test_viewport_calculation():
    """Test: Cálculo de líneas en viewport."""
    print("\n" + "=" * 60)
    print("TEST: get_visible_in_viewport")
    print("=" * 60)

    manager = StateManager()
    lines = create_test_md_lines(100)
    manager.load_document(lines)

    # Simular viewport de 600px de altura
    viewport_height = 600.0

    # Test 1: scroll_y = 1.0 (top)
    visible_top = manager.get_visible_in_viewport(
        scroll_y=1.0,
        viewport_height=viewport_height
    )

    print(f"\nscroll_y=1.0 (top):")
    print(f"  Líneas visibles: {len(visible_top)}")
    print(f"  Rango: [{min(visible_top) if visible_top else 'N/A'}, {max(visible_top) if visible_top else 'N/A'}]")

    assert len(visible_top) > 0, "Debería haber líneas visibles"
    assert min(visible_top) == 0, "Primera línea visible debería ser 0 (top)"

    # Test 2: scroll_y = 0.5 (medio)
    visible_mid = manager.get_visible_in_viewport(
        scroll_y=0.5,
        viewport_height=viewport_height
    )

    print(f"\nscroll_y=0.5 (medio):")
    print(f"  Líneas visibles: {len(visible_mid)}")
    print(f"  Rango: [{min(visible_mid) if visible_mid else 'N/A'}, {max(visible_mid) if visible_mid else 'N/A'}]")

    assert len(visible_mid) > 0, "Debería haber líneas visibles"

    # Test 3: scroll_y = 0.0 (bottom)
    visible_bottom = manager.get_visible_in_viewport(
        scroll_y=0.0,
        viewport_height=viewport_height
    )

    print(f"\nscroll_y=0.0 (bottom):")
    print(f"  Líneas visibles: {len(visible_bottom)}")
    print(f"  Rango: [{min(visible_bottom) if visible_bottom else 'N/A'}, {max(visible_bottom) if visible_bottom else 'N/A'}]")

    assert len(visible_bottom) > 0, "Debería haber líneas visibles"
    assert max(visible_bottom) == 99, "Última línea visible debería ser 99 (bottom)"

    print("\n✓ Viewport calculation funciona correctamente")


def test_line_heights():
    """Test: Alturas no uniformes de líneas."""
    print("\n" + "=" * 60)
    print("TEST: Alturas no uniformes")
    print("=" * 60)

    manager = StateManager()
    lines = create_test_md_lines(20)
    manager.load_document(lines)

    heights = {}
    for i in range(20):
        state = manager.get_state(i)
        line_type = state.md_line.type.name
        if line_type not in heights:
            heights[line_type] = []
        heights[line_type].append(state.height)

    print("Alturas por tipo:")
    for line_type, height_list in heights.items():
        avg_height = sum(height_list) / len(height_list)
        print(f"  {line_type}: {avg_height:.0f}px (n={len(height_list)})")

    # Verificar que hay diferentes alturas
    unique_heights = set()
    for i in range(20):
        state = manager.get_state(i)
        unique_heights.add(state.height)

    assert len(unique_heights) > 1, "Debería haber alturas variadas"
    print(f"\n✓ Alturas únicas encontradas: {len(unique_heights)}")


def test_geometry_positions():
    """Test: Posiciones Y calculadas correctamente."""
    print("\n" + "=" * 60)
    print("TEST: Geometría (posiciones Y)")
    print("=" * 60)

    manager = StateManager()
    lines = create_test_md_lines(10)
    manager.load_document(lines)

    print("Posiciones Y de líneas:")
    last_y = 0.0
    for i in range(10):
        state = manager.get_state(i)
        print(f"  Línea {i}: y={state.y_position:.0f}px, h={state.height:.0f}px")

        # Verificar que posiciones son consecutivas
        if i > 0:
            prev_state = manager.get_state(i - 1)
            expected_y = prev_state.y_position + prev_state.height
            assert abs(state.y_position - expected_y) < 0.1, \
                f"Posición Y incorrecta para línea {i}"

        last_y = state.y_position + state.height

    # Verificar altura total
    assert abs(manager.total_height - last_y) < 0.1, \
        "Altura total debería coincidir con última posición + altura"

    print(f"\n✓ Altura total: {manager.total_height:.0f}px")
    print(f"✓ Última posición + altura: {last_y:.0f}px")


def test_line_state_mutability_and_events():
    """Test: LineState es mutable y dispara eventos correctamente."""
    print("\n" + "=" * 60)
    print("TEST: LineState mutabilidad y eventos")
    print("=" * 60)

    md_line = MDLine(
        md_text="Test",
        prev_line=None,
        next_line=None,
        type=MD_LINE_TYPE.TEXT,
        num_line=0
    )

    state = LineState(
        index=0,
        md_line=md_line,
        active=False
    )

    print(f"Estado inicial: {state}")

    # Verificar valores iniciales
    assert state.active == False, "Debería iniciar como active=False"
    assert state.editing == False, "Debería iniciar como editing=False"
    assert state.hotlight == False, "Debería iniciar como hotlight=False"

    # Tracking de eventos disparados
    events_fired = []

    def on_active_change(instance, value):
        events_fired.append(('active', value))

    def on_editing_change(instance, value):
        events_fired.append(('editing', value))

    # Bind a eventos
    state.bind(active=on_active_change)
    state.bind(editing=on_editing_change)

    # Modificar directamente (mutable)
    state.active = True
    print(f"✓ Modificación directa funciona: active={state.active}")

    state.editing = True
    print(f"✓ Modificación directa funciona: editing={state.editing}")

    # Verificar que los eventos se dispararon
    assert ('active', True) in events_fired, "Evento on_active debería dispararse"
    assert ('editing', True) in events_fired, "Evento on_editing debería dispararse"

    print(f"✓ Eventos disparados: {events_fired}")

    # Verificar estado final
    print(f"Estado final: {state}")
    assert state.active == True, "active debería ser True"
    assert state.editing == True, "editing debería ser True"

    # Test de propiedades adicionales
    state.hotlight = True
    state.selected = True
    state.cursor_col = 10
    state.cursor_row = 5

    assert state.cursor_pos == (10, 5), "cursor_pos debería retornar (10, 5)"

    print(f"✓ hotlight: {state.hotlight}")
    print(f"✓ selected: {state.selected}")
    print(f"✓ cursor_pos: {state.cursor_pos}")


def run_all_tests():
    """Ejecutar todos los tests."""
    print("\n" + "=" * 60)
    print(" TESTS UNITARIOS - StateManager")
    print(" wg_markdown2 - Etapa I")
    print("=" * 60)

    tests = [
        test_load_document,
        test_get_state,
        test_update_state,
        test_viewport_calculation,
        test_line_heights,
        test_geometry_positions,
        test_line_state_mutability_and_events,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ FALLÓ: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f" RESULTADOS: {passed} pasaron, {failed} fallaron")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
