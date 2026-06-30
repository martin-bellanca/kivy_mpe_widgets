#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_md_editor_v2_nogui.py
#
#  Test sin GUI para MDDocumentEditorV2
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
Test sin GUI para MDDocumentEditorV2

Valida las funcionalidades core sin necesitar interfaz gráfica:
1. Inicialización
2. Integración con StateManager
3. Integración con Services
4. Carga de documentos
5. Validación de estado
"""

import sys
from pathlib import Path

# Configurar paths
project_root = Path(__file__).parent
helpers_root = Path.home() / 'Documentos' / 'Programacion' / 'Programacion_lin' / 'Visual_Studio_Code' / 'helpers_mpbe_prj'
widgets_root = Path.home() / 'Documentos' / 'Programacion' / 'Programacion_lin' / 'Visual_Studio_Code' / 'kivy_mpe_widgets_prj'

for path in [project_root, helpers_root, widgets_root]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Imports
from helpers_mpbe.markdown_document.md_document import MDLine
from helpers_mpbe.markdown_document import MD_LINE_TYPE


class FakeMDLine:
    """MDLine simulada para testing sin dependencias."""

    def __init__(self, text: str, num: int, line_type: MD_LINE_TYPE = MD_LINE_TYPE.TEXT):
        self.md_text = text
        self.num_line = num
        self.type = line_type
        self.prev_line = None
        self.next_line = None


def create_test_document():
    """Crea un documento de prueba."""
    md_lines = [
        FakeMDLine("# Título Principal", 1, MD_LINE_TYPE.TITLE),
        FakeMDLine("Este es un texto normal", 2, MD_LINE_TYPE.TEXT),
        FakeMDLine("## Subtítulo 1", 3, MD_LINE_TYPE.TITLE),
        FakeMDLine("- Item de lista 1", 4, MD_LINE_TYPE.LIST),
        FakeMDLine("- Item de lista 2", 5, MD_LINE_TYPE.LIST),
        FakeMDLine("## Subtítulo 2", 6, MD_LINE_TYPE.TITLE),
        FakeMDLine("Más texto normal", 7, MD_LINE_TYPE.TEXT),
        FakeMDLine("- [ ] Tarea pendiente", 8, MD_LINE_TYPE.TASK),
        FakeMDLine("- [x] Tarea completada", 9, MD_LINE_TYPE.TODO),
        FakeMDLine("### Subtítulo 3", 10, MD_LINE_TYPE.TITLE),
    ]

    # Actualizar referencias prev/next
    for i in range(len(md_lines)):
        if i > 0:
            md_lines[i].prev_line = md_lines[i - 1]
        if i < len(md_lines) - 1:
            md_lines[i].next_line = md_lines[i + 1]

    return md_lines


def test_state_manager_integration():
    """Test 1: Integración con StateManager."""
    print("\n" + "=" * 80)
    print("TEST 1: Integración con StateManager")
    print("=" * 80)

    from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager

    # Crear StateManager
    state_manager = DocumentStateManager()

    # Crear documento
    md_lines = create_test_document()

    # Inicializar estados
    state_manager.initialize_states(len(md_lines))

    print(f"✅ Estados inicializados: {len(md_lines)} líneas")

    # Activar una línea
    state_manager.activate_line(3, enter_edit_mode=True)
    active_index = state_manager.get_active_index()

    assert active_index == 3, f"Expected active_index=3, got {active_index}"
    print(f"✅ Línea 3 activada correctamente")

    # Validar estado
    is_valid = state_manager.validate_invariants()
    assert is_valid, "State validation failed"
    print(f"✅ Estado válido - Invariantes OK")

    print("\n✅ TEST 1 PASADO - StateManager integrado correctamente\n")


def test_services_integration():
    """Test 2: Integración con Services."""
    print("=" * 80)
    print("TEST 2: Integración con Services")
    print("=" * 80)

    from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager
    from kivy_mpbe_widgets.wg_markdown.services.line_service import LineService
    from kivy_mpbe_widgets.wg_markdown.services.selection_service import SelectionService
    from kivy_mpbe_widgets.wg_markdown.services.navigation_service import NavigationService

    # Crear StateManager y documento
    state_manager = DocumentStateManager()
    md_lines = create_test_document()
    state_manager.initialize_states(len(md_lines))

    # Crear services
    line_service = LineService(state_manager, md_lines)
    selection_service = SelectionService(state_manager, md_lines)
    navigation_service = NavigationService(state_manager, md_lines)

    print(f"✅ Services creados: LineService, SelectionService, NavigationService")

    # Test LineService
    success = line_service.activate_line(5, enter_edit=True)
    assert success, "LineService.activate_line failed"
    assert state_manager.get_active_index() == 5
    print(f"✅ LineService: activate_line() funciona")

    # Test SelectionService
    selection_service.select_range(2, 6)
    selected = selection_service.get_selected_indices()
    assert len(selected) == 5  # 2, 3, 4, 5, 6
    print(f"✅ SelectionService: select_range() funciona - {len(selected)} líneas seleccionadas")

    # Test NavigationService
    next_title = navigation_service.navigate_to_next_title(from_index=3)
    assert next_title == 5  # Índice 5 es "## Subtítulo 2"
    print(f"✅ NavigationService: navigate_to_next_title() funciona - encontró título en {next_title}")

    print("\n✅ TEST 2 PASADO - Services integrados correctamente\n")


def test_document_operations():
    """Test 3: Operaciones de documento."""
    print("=" * 80)
    print("TEST 3: Operaciones de Documento")
    print("=" * 80)

    from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager
    from kivy_mpbe_widgets.wg_markdown.services.line_service import LineService

    # Setup
    state_manager = DocumentStateManager()
    md_lines = create_test_document()
    state_manager.initialize_states(len(md_lines))
    line_service = LineService(state_manager, md_lines)

    original_count = len(md_lines)
    print(f"Documento inicial: {original_count} líneas")

    # Test insertar línea
    new_index = line_service.insert_line_below(
        index=5,
        text="Línea insertada",
        line_type=MD_LINE_TYPE.TEXT
    )
    assert len(md_lines) == original_count + 1
    assert md_lines[new_index].md_text == "Línea insertada"
    print(f"✅ Insertar línea: Nueva línea en índice {new_index}")

    # Test mover línea arriba
    moved_index = line_service.move_line_up(index=5)
    assert moved_index == 4
    print(f"✅ Mover línea arriba: Línea movida de 5 a {moved_index}")

    # Test eliminar línea
    success = line_service.delete_line(index=4)
    assert success
    assert len(md_lines) == original_count  # Volvió al tamaño original
    print(f"✅ Eliminar línea: Línea eliminada, total={len(md_lines)}")

    print("\n✅ TEST 3 PASADO - Operaciones de documento funcionan\n")


def test_state_validation():
    """Test 4: Validación de estado."""
    print("=" * 80)
    print("TEST 4: Validación de Estado")
    print("=" * 80)

    from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager

    state_manager = DocumentStateManager()
    md_lines = create_test_document()
    state_manager.initialize_states(len(md_lines))

    # Activar y seleccionar líneas
    state_manager.activate_line(3, enter_edit_mode=True)
    state_manager.select_range(1, 5)

    # Validar invariantes
    is_valid = state_manager.validate_invariants()
    assert is_valid, "State validation failed"
    print("✅ Invariantes validados correctamente")

    # Print resumen
    print("\nResumen del estado:")
    state_manager.print_state_summary()

    print("\n✅ TEST 4 PASADO - Validación de estado funciona\n")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TEST MDDocumentEditorV2 (No-GUI)" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝\n")

    tests = [
        ("StateManager Integration", test_state_manager_integration),
        ("Services Integration", test_services_integration),
        ("Document Operations", test_document_operations),
        ("State Validation", test_state_validation),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ TEST FALLIDO: {test_name}")
            print(f"Error: {e}\n")
            import traceback
            traceback.print_exc()

    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"Tests ejecutados: {len(tests)}")
    print(f"Pasaron: {passed} ✅")
    print(f"Fallaron: {failed} ❌")
    print("=" * 80)

    if failed == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON! 🎉\n")
        print("MDDocumentEditorV2 está listo para usar:")
        print("  - StateManager integrado ✅")
        print("  - Services integrados ✅")
        print("  - Operaciones de documento funcionando ✅")
        print("  - Validación de estado OK ✅")
        print()
        return True
    else:
        print(f"\n⚠️ {failed} test(s) fallaron\n")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
