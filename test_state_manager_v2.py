#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar los cambios en DocumentStateManager V2.

Prueba:
1. El nuevo atributo old_values en LineStateEvent
2. La emisión del evento on_line_state_changed desde update_state
3. Que solo se emite cuando hay cambios reales
"""

import sys
from pathlib import Path

# Agregar rutas al path
kivy_widgets_path = Path(__file__).parent
helpers_path = Path.home() / "Documentos/Programacion/Programacion_lin/Visual_Studio_Code/helpers_mpbe_prj"
sys.path.insert(0, str(kivy_widgets_path))
sys.path.insert(0, str(helpers_path))

# Configurar Kivy para modo headless (sin ventana)
import os
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy_mpbe_widgets.wg_markdown2.core.state_manager import (
    DocumentStateManager,
    LineStateEvent,
    EventType
)
from helpers_mpbe.markdown_document.md_document import MDDocument, MDLine
from helpers_mpbe.markdown_document import MD_LINE_TYPE


def test_update_state_event():
    """Probar que update_state emite eventos CHANGED correctamente."""

    print("\n" + "="*70)
    print("TEST: update_state debe emitir evento on_line_state_changed")
    print("="*70)

    # Crear manager
    manager = DocumentStateManager()

    # Crear documento simple
    md_doc = MDDocument()
    md_lines = [
        MDLine(index=0, line_type=MD_LINE_TYPE.TEXT, text="Línea 1"),
        MDLine(index=1, line_type=MD_LINE_TYPE.TEXT, text="Línea 2"),
        MDLine(index=2, line_type=MD_LINE_TYPE.TEXT, text="Línea 3"),
    ]
    md_doc.load_lines(md_lines)
    manager.md_document = md_doc
    manager.load_document(md_lines)

    # Variable para capturar eventos
    events_captured = []

    def on_state_changed(instance, event: LineStateEvent):
        """Callback para capturar eventos."""
        events_captured.append({
            'index': event.index,
            'event_type': event.event_type,
            'changed_attrs': event.changed_attributes,
            'old_values': event.old_values,
            'line_state': event.line_state
        })
        print(f"\n✓ Evento capturado:")
        print(f"  - Index: {event.index}")
        print(f"  - Event Type: {event.event_type.name}")
        print(f"  - Changed Attributes: {event.changed_attributes}")
        print(f"  - Old Values: {event.old_values}")
        print(f"  - New State:")
        for attr in event.changed_attributes:
            new_val = getattr(event.line_state, attr)
            print(f"    - {attr}: {event.old_values[attr]} → {new_val}")

    # Bindear al evento
    manager.bind(on_line_state_changed=on_state_changed)

    # TEST 1: Cambiar una propiedad
    print("\n--- Test 1: Cambiar una propiedad (active=True) ---")
    manager.update_state(1, active=True)
    assert len(events_captured) == 1, "Debería emitirse 1 evento"
    assert events_captured[0]['changed_attrs'] == {'active'}, "Debería cambiar 'active'"
    assert events_captured[0]['old_values']['active'] == False, "Valor anterior debería ser False"
    print("✓ Test 1 PASADO")

    # TEST 2: Cambiar múltiples propiedades
    print("\n--- Test 2: Cambiar múltiples propiedades ---")
    events_captured.clear()
    manager.update_state(1, selected=True, editing=True, hotlight=True)
    assert len(events_captured) == 1, "Debería emitirse 1 evento"
    assert events_captured[0]['changed_attrs'] == {'selected', 'editing', 'hotlight'}, \
        "Deberían cambiar 3 atributos"
    print("✓ Test 2 PASADO")

    # TEST 3: No cambiar nada (mismo valor)
    print("\n--- Test 3: Asignar el mismo valor (no debería emitir evento) ---")
    events_captured.clear()
    manager.update_state(1, active=True)  # Ya está en True
    assert len(events_captured) == 0, "NO debería emitirse evento si no hay cambios"
    print("✓ Test 3 PASADO - No se emitió evento innecesario")

    # TEST 4: Verificar que old_values está presente
    print("\n--- Test 4: Verificar estructura del evento ---")
    events_captured.clear()
    manager.update_state(2, active=True)
    event_data = events_captured[0]
    assert 'old_values' in event_data, "Evento debe tener 'old_values'"
    assert 'active' in event_data['old_values'], "old_values debe contener 'active'"
    assert event_data['event_type'] == EventType.CHANGED, "event_type debe ser CHANGED"
    print("✓ Test 4 PASADO")

    print("\n" + "="*70)
    print("TODOS LOS TESTS PASARON ✓")
    print("="*70)


if __name__ == "__main__":
    test_update_state_event()
    print("\n✓ Script completado exitosamente\n")
