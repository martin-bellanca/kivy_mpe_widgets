#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_md_editor_v2.py
#
#  Script de prueba para MDDocumentEditorV2
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
Script de Prueba para MDDocumentEditorV2

Prueba las siguientes funcionalidades:
1. Inicialización del editor
2. Carga de documento
3. Integración con StateManager
4. Integración con Services
5. Eventos básicos
6. Validación de estado
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
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy_mpbe_widgets.wg_markdown.md_document_editor_v2 import MDDocumentEditorV2
from helpers_mpbe.markdown_document.md_document import MDLine
from helpers_mpbe.markdown_document import MD_LINE_TYPE


class TestApp(App):
    """Aplicación de prueba para MDDocumentEditorV2."""

    def build(self):
        """Construye la interfaz de prueba."""
        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Label de título
        title = Label(
            text='Test MDDocumentEditorV2',
            size_hint_y=None,
            height=40,
            font_size=20
        )
        layout.add_widget(title)

        # Editor
        self.editor = MDDocumentEditorV2()
        layout.add_widget(self.editor)

        # Panel de botones
        button_panel = BoxLayout(size_hint_y=None, height=50, spacing=5)

        # Botón cargar documento
        btn_load = Button(text='Cargar Documento')
        btn_load.bind(on_press=self.load_test_document)
        button_panel.add_widget(btn_load)

        # Botón validar estado
        btn_validate = Button(text='Validar Estado')
        btn_validate.bind(on_press=self.validate_state)
        button_panel.add_widget(btn_validate)

        # Botón print estado
        btn_print = Button(text='Print Estado')
        btn_print.bind(on_press=self.print_state)
        button_panel.add_widget(btn_print)

        # Botón activar línea 5
        btn_activate = Button(text='Activar Línea 5')
        btn_activate.bind(on_press=self.activate_line_5)
        button_panel.add_widget(btn_activate)

        layout.add_widget(button_panel)

        # Label de status
        self.status_label = Label(
            text='Listo. Presiona "Cargar Documento"',
            size_hint_y=None,
            height=30
        )
        layout.add_widget(self.status_label)

        return layout

    def load_test_document(self, instance):
        """Carga un documento de prueba."""
        # Crear documento de prueba
        md_lines = [
            self._create_md_line("# Título Principal", 1, MD_LINE_TYPE.TITLE),
            self._create_md_line("Este es un texto normal", 2, MD_LINE_TYPE.TEXT),
            self._create_md_line("## Subtítulo 1", 3, MD_LINE_TYPE.TITLE),
            self._create_md_line("- Item de lista 1", 4, MD_LINE_TYPE.LIST),
            self._create_md_line("- Item de lista 2", 5, MD_LINE_TYPE.LIST),
            self._create_md_line("## Subtítulo 2", 6, MD_LINE_TYPE.TITLE),
            self._create_md_line("Más texto normal", 7, MD_LINE_TYPE.TEXT),
            self._create_md_line("- [ ] Tarea pendiente", 8, MD_LINE_TYPE.TASK),
            self._create_md_line("- [x] Tarea completada", 9, MD_LINE_TYPE.TODO),
            self._create_md_line("### Subtítulo 3", 10, MD_LINE_TYPE.TITLE),
        ]

        # Actualizar referencias prev/next
        for i in range(len(md_lines)):
            if i > 0:
                md_lines[i].prev_line = md_lines[i - 1]
            if i < len(md_lines) - 1:
                md_lines[i].next_line = md_lines[i + 1]

        # Cargar en el editor
        self.editor.populate_from_md_lines(md_lines)

        # Actualizar status
        self.status_label.text = f'Documento cargado: {len(md_lines)} líneas'

        print("\n" + "=" * 80)
        print("DOCUMENTO CARGADO")
        print("=" * 80)
        print(f"Líneas: {len(md_lines)}")
        print(f"StateManager: {self.editor.state_manager}")
        print(f"LineService: {self.editor.line_service}")
        print(f"SelectionService: {self.editor.selection_service}")
        print(f"NavigationService: {self.editor.navigation_service}")
        print("=" * 80 + "\n")

    def _create_md_line(self, text: str, num: int, line_type: MD_LINE_TYPE) -> MDLine:
        """Crea una MDLine para pruebas."""
        line = MDLine(md_text=text, num_line=num)
        line.type = line_type
        return line

    def validate_state(self, instance):
        """Valida el estado del editor."""
        is_valid = self.editor.validate_state()

        if is_valid:
            self.status_label.text = '✅ Estado válido'
            print("\n✅ ESTADO VÁLIDO - Todos los invariantes OK\n")
        else:
            self.status_label.text = '❌ Estado inválido'
            print("\n❌ ESTADO INVÁLIDO - Ver logs\n")

    def print_state(self, instance):
        """Imprime resumen del estado."""
        print("\n" + "=" * 80)
        self.editor.print_state_summary()
        print("=" * 80 + "\n")

        self.status_label.text = 'Estado impreso en consola'

    def activate_line_5(self, instance):
        """Activa la línea 5 (índice 4)."""
        if not self.editor.line_service:
            self.status_label.text = 'Error: Cargar documento primero'
            return

        success = self.editor.line_service.activate_line(4, enter_edit=True)

        if success:
            self.status_label.text = '✅ Línea 5 activada'
            print("\n✅ Línea 5 (índice 4) activada\n")
        else:
            self.status_label.text = '❌ No se pudo activar línea 5'
            print("\n❌ No se pudo activar línea 5\n")


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                   TEST MDDocumentEditorV2                              ║
    ║                                                                        ║
    ║  Prueba la integración de StateManager y Service Layer                ║
    ║                                                                        ║
    ║  Funcionalidades a probar:                                            ║
    ║  1. Cargar documento                                                  ║
    ║  2. Validar estado                                                    ║
    ║  3. Activar líneas                                                    ║
    ║  4. Navegar con teclado (flechas arriba/abajo)                       ║
    ║  5. Insertar líneas (Enter)                                          ║
    ║  6. Eliminar líneas (Delete)                                         ║
    ║                                                                        ║
    ║  Usa los botones en la interfaz o las teclas:                        ║
    ║  - Flecha Arriba/Abajo: Navegar                                      ║
    ║  - Ctrl+Flecha: Navegar por títulos                                  ║
    ║  - Enter: Insertar línea                                             ║
    ║  - Delete: Eliminar línea                                            ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """)

    TestApp().run()
