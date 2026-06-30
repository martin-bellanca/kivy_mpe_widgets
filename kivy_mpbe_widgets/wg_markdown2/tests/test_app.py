#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test App - Aplicación de prueba para wg_markdown2

Esta aplicación prueba la funcionalidad básica de MDDocumentEditor
con RecycleBoxLayout personalizado.

Funcionalidad probada (Etapa I):
- Cargar documento
- Scroll fluido
- Reciclaje de widgets
- Click para activar línea (visual)
- Alturas no uniformes

Para ejecutar:
    python test_app.py

Fecha: 2026-01-12
Autor: Martin Pablo Bellanca
"""

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.config import Config

# Configurar ventana
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', True)

# Importar componentes
from kivy_mpbe_widgets.wg_markdown2 import MDDocumentEditor
from helpers_mpbe.markdown_document.md_document import MDDocument
from kivy_mpbe_widgets.theming import Theme


class TestApp(App):
    """
    Aplicación de prueba para MDDocumentEditor.

    Layout:
    - Header con información y controles
    - MDDocumentEditor (ocupa la mayor parte)
    - Footer con estadísticas
    """
    def __init__(self, **kwargs):
        """Inicializa la aplicación V2 y sus componentes."""
        super(TestApp, self).__init__(**kwargs)

        Logger.info("TestApp: Inicializando aplicación")

        # Configuración de tema
        self.theme = Theme(name='flat_light', style='light')

    def build(self):
        """Construir la UI de la aplicación."""
        # Layout principal
        root = BoxLayout(orientation='vertical', spacing=5, padding=5)

        # ====================================================================
        # HEADER
        # ====================================================================
        header = BoxLayout(size_hint_y=None, height=60, spacing=10)

        # Título
        title = Label(
            text='[b]wg_markdown2 - Test App (Etapa I)[/b]',
            markup=True,
            size_hint_x=0.5,
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        # Botones de control
        btn_layout = BoxLayout(size_hint_x=0.5, spacing=5)

        btn_top = Button(
            text='Top',
            size_hint_x=0.25,
            on_press=self.scroll_to_top
        )
        btn_layout.add_widget(btn_top)

        btn_bottom = Button(
            text='Bottom',
            size_hint_x=0.25,
            on_press=self.scroll_to_bottom
        )
        btn_layout.add_widget(btn_bottom)

        btn_info = Button(
            text='Info',
            size_hint_x=0.25,
            on_press=self.show_info
        )
        btn_layout.add_widget(btn_info)

        btn_reload = Button(
            text='Reload',
            size_hint_x=0.25,
            on_press=self.reload_document
        )
        btn_layout.add_widget(btn_reload)

        header.add_widget(btn_layout)
        root.add_widget(header)

        # ====================================================================
        # EDITOR
        # ====================================================================
        self.editor = MDDocumentEditor()

        # Aplicar tema
        self.editor.theme = Theme(name='flat_light', style='light')

        root.add_widget(self.editor)

        # ====================================================================
        # FOOTER
        # ====================================================================
        footer = BoxLayout(size_hint_y=None, height=40)

        self.status_label = Label(
            text='Cargando documento...',
            size_hint_x=1.0,
            halign='left',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        footer.add_widget(self.status_label)

        root.add_widget(footer)

        # ====================================================================
        # CARGAR DOCUMENTO DE PRUEBA
        # ====================================================================
        self.load_test_document()

        return root

    def load_test_document(self):
        """Cargar documento de prueba."""
        try:
            # Ruta al documento de prueba
            current_dir = os.path.dirname(os.path.abspath(__file__))
            doc_path = current_dir
            doc_name = 'test_document.md'

            Logger.info(f"TestApp: Loading document from {doc_path}/{doc_name}")

            # Cargar con MDDocument
            md_doc = MDDocument()
            md_doc.load_doc(doc_path, doc_name)

            Logger.info(
                f"TestApp: Document loaded - {md_doc.can_lines} lines, "
                f"{len(md_doc.document)} characters"
            )

            # Cargar en editor
            self.editor.load_document(md_doc)

            # Actualizar status
            self.update_status()

            Logger.info("TestApp: Document successfully loaded in editor")

        except Exception as e:
            Logger.error(f"TestApp: Error loading document: {e}")
            import traceback
            traceback.print_exc()

            self.status_label.text = f'[color=ff0000]Error: {e}[/color]'

    def update_status(self):
        """Actualizar barra de estado con información."""
        if not self.editor.md_document:
            self.status_label.text = 'No document loaded'
            return

        doc = self.editor.md_document
        state_mgr = self.editor.state_manager

        total_lines = state_mgr.get_total_lines()
        visible_lines = state_mgr.get_visible_lines_count()
        total_height = state_mgr.total_height

        active_widgets = len(self.editor.doc_lines_layout.active_widgets)
        recycled_widgets = len(self.editor.doc_lines_layout.recycled_pool)

        self.status_label.text = (
            f'[b]{doc.doc_name}[/b] | '
            f'Lines: {total_lines} (visible: {visible_lines}) | '
            f'Height: {total_height:.0f}px | '
            f'Widgets: {active_widgets} active, {recycled_widgets} recycled | '
            f'Scroll: {self.editor.scroll_y:.3f}'
        )

    def scroll_to_top(self, instance):
        """Scrollear al top del documento."""
        self.editor.scroll_to_top()
        self.update_status()
        Logger.info("TestApp: Scrolled to top")

    def scroll_to_bottom(self, instance):
        """Scrollear al bottom del documento."""
        self.editor.scroll_to_bottom()
        self.update_status()
        Logger.info("TestApp: Scrolled to bottom")

    def show_info(self, instance):
        """Mostrar información detallada en logs."""
        Logger.info("=" * 60)
        Logger.info("INFORMACIÓN DEL EDITOR")
        Logger.info("=" * 60)

        # Documento
        if self.editor.md_document:
            doc = self.editor.md_document
            Logger.info(f"Documento: {doc.doc_name}")
            Logger.info(f"  - Líneas: {doc.can_lines}")
            Logger.info(f"  - Caracteres: {len(doc.document)}")

        # StateManager
        state_mgr = self.editor.state_manager
        Logger.info(f"\nStateManager: {state_mgr}")
        Logger.info(f"  - Total lines: {state_mgr.get_total_lines()}")
        Logger.info(f"  - Visible lines: {state_mgr.get_visible_lines_count()}")
        Logger.info(f"  - Total height: {state_mgr.total_height:.0f}px")
        Logger.info(f"  - Viewport buffer: {state_mgr.viewport_buffer} lines")

        # RecycleBoxLayout
        layout = self.editor.doc_lines_layout
        Logger.info(f"\nRecycleBoxLayout: {layout}")
        Logger.info(f"  - Active widgets: {len(layout.active_widgets)}")
        Logger.info(f"  - Recycled pool: {len(layout.recycled_pool)}")
        Logger.info(f"  - Placeholders: {len(layout.placeholders)}")
        Logger.info(f"  - Last visible: {len(layout.last_visible_indices)} indices")

        # Editor
        Logger.info(f"\nMDDocumentEditor:")
        Logger.info(f"  - Scroll Y: {self.editor.scroll_y:.3f}")
        Logger.info(f"  - Viewport height: {self.editor.height:.0f}px")
        Logger.info(f"  - Active line: {self.editor.get_active_line_index()}")

        Logger.info("=" * 60)

        self.update_status()

    def reload_document(self, instance):
        """Recargar documento."""
        Logger.info("TestApp: Reloading document")
        self.load_test_document()

    def on_start(self):
        """Callback cuando la app inicia."""
        Logger.info("TestApp: Application started")

        # Actualizar status periódicamente
        from kivy.clock import Clock
        Clock.schedule_interval(lambda dt: self.update_status(), 0.5)

    def on_stop(self):
        """Callback cuando la app se cierra."""
        Logger.info("TestApp: Application stopped")


if __name__ == '__main__':
    Logger.info("=" * 60)
    Logger.info("wg_markdown2 - Test Application")
    Logger.info("Etapa I: Funcionalidad básica")
    Logger.info("=" * 60)

    app = TestApp()
    app.run()
