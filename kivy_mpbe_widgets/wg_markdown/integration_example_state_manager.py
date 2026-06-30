#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  integration_example_state_manager.py
#
#  Ejemplo de integración del StateManager con MDDocumentEditor
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
EJEMPLO DE INTEGRACIÓN: DocumentStateManager

Este archivo muestra cómo integrar el DocumentStateManager
en MDDocumentEditor y MDDocumentLineEditor.

NO es código de producción, es un ejemplo de referencia.
"""

from typing import Optional, Tuple
from kivy.logger import Logger
from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager, StateChangeEvent, LineState


# ==============================================================================
# PASO 1: Modificar MDDocumentEditor para usar StateManager
# ==============================================================================

class MDDocumentEditorRefactored:
    """
    Versión refactorizada de MDDocumentEditor usando StateManager.

    CAMBIOS PRINCIPALES:
    - Eliminar variables de estado dispersas
    - Usar DocumentStateManager como única fuente de verdad
    - Delegar operaciones de estado al manager
    """

    def __init__(self, **kwargs):
        """Inicializa el editor con StateManager."""
        # ... código existente ...

        # ✅ NUEVO: StateManager como única fuente de verdad
        self.state_manager = DocumentStateManager(enable_history=False)

        # ✅ NUEVO: Suscribirse a cambios de estado
        self.state_manager.subscribe(self._on_line_state_changed)

        # ❌ ELIMINAR: Variables de estado duplicadas
        # self._selected_indexs = []
        # self._active_index = -1
        # self._mode_editor = False

        Logger.info("MDDocumentEditor: Initialized with StateManager")

    def populate_from_md_lines(self, md_lines):
        """
        Carga documento desde MDLines.

        CAMBIOS:
        - Inicializar estados en StateManager
        """
        Logger.info("MDDocumentEditor: Populating from md_lines")

        # ... código existente de carga ...
        self._md_lines = md_lines

        # ✅ NUEVO: Inicializar estados
        self.state_manager.initialize_states(len(md_lines))

        # ... código existente de actualización de data ...
        self._refresh_recycleview_data()

    def _refresh_recycleview_data(self):
        """
        Actualiza RecycleView.data desde data_source.

        CAMBIOS:
        - Incluir estado desde StateManager en cada item
        """
        self.data = []

        for index, md_line in enumerate(self._md_lines):
            # ✅ NUEVO: Obtener estado del manager
            state = self.state_manager.get_state(index)

            self.data.append({
                'md_line': md_line,
                'index': index,
                'line_number': md_line.num_line,

                # ✅ NUEVO: Estado desde StateManager
                'state': state,

                # UI config
                'show': {'number_line': True, 'tree': False, 'infobar': False},
                'themed': {'alpha_background': 0.0}
            })

    def _on_line_state_changed(self, event: StateChangeEvent):
        """
        Callback cuando cambia el estado de una línea.

        Este método se llama automáticamente cada vez que
        el StateManager actualiza el estado de una línea.

        Args:
            event: Evento con información del cambio
        """
        Logger.debug(f"MDDocumentEditor: State changed - {event}")

        # Actualizar solo si el widget es visible
        widget = self._get_widget_at_index(event.index)

        if widget:
            # ✅ NUEVO: Aplicar nuevo estado al widget
            widget.apply_state(event.new_state)
        else:
            # Widget no visible, se actualizará cuando sea reciclado
            Logger.debug(f"Widget at index {event.index} not visible, will update on recycle")

    def _get_widget_at_index(self, index: int):
        """
        Obtiene el widget visible en el índice dado.

        Returns:
            MDDocumentLineEditor o None si no es visible
        """
        # Buscar en los widgets visibles del layout
        if hasattr(self, 'layout') and hasattr(self.layout, 'children'):
            for widget in self.layout.children:
                if hasattr(widget, 'index') and widget.index == index:
                    return widget

        return None

    # ==========================================================================
    # Métodos de Manejo de Eventos (REFACTORIZADOS)
    # ==========================================================================

    def handle_touch_left_up_event(self, index: int, view, touch):
        """
        Maneja click izquierdo en una línea.

        CAMBIOS:
        - Usar StateManager en lugar de variables locales
        """
        Logger.debug(f"MDDocumentEditor: Touch left up on index {index}")

        # Obtener posición del cursor
        cursor_pos = view.wg_line_editor.md_editor.get_cursor_from_xy(
            *view.to_local(*touch.pos)
        )

        # ✅ NUEVO: Activar usando StateManager
        # Automáticamente desactiva línea anterior y actualiza selección
        self.state_manager.activate_line(
            index,
            enter_edit_mode=True,
            cursor_pos=cursor_pos
        )

        # ❌ ELIMINAR: Código viejo
        # self._active_index = index
        # self._selected_indexs.append(index)
        # self._mode_editor = True
        # ... etc

        # Refrescar vista si es necesario
        # (En realidad, el observer ya actualizó el widget)
        # self._refresh_recycleview_data()

    def handle_hotlight_event(self, index: int, view, active: bool):
        """
        Maneja evento de hotlight (hover del mouse).

        CAMBIOS:
        - Usar StateManager
        """
        # ✅ NUEVO: Actualizar hotlight en StateManager
        self.state_manager.set_hotlight(index, active)

        # ❌ ELIMINAR: Código viejo de actualización manual
        # if hasattr(view, 'graphic_hotlight'):
        #     view.graphic_hotlight.animate(active)

    def on_filter_state_change(self, instance, value):
        """
        Maneja cambio de estado de filtro.

        CAMBIOS:
        - Actualizar visibilidad en StateManager
        """
        filter_text = self.widgets['search_filter_bar'].text

        if value and filter_text:
            # Aplicar filtro y actualizar visibilidad
            for index, md_line in enumerate(self._md_lines):
                visible = filter_text.lower() in md_line.md_text.lower()

                # ✅ NUEVO: Actualizar visibilidad en StateManager
                self.state_manager.set_visibility(index, visible)
        else:
            # Limpiar filtro
            for index in range(len(self._md_lines)):
                # ✅ NUEVO: Restaurar visibilidad
                self.state_manager.set_visibility(index, True)

        # Refrescar vista
        self._refresh_recycleview_data()

    # ==========================================================================
    # Métodos de Navegación (REFACTORIZADOS)
    # ==========================================================================

    def active_to_next_item(self, cursor_pos: Optional[Tuple[int, int]] = None):
        """
        Activa la siguiente línea.

        CAMBIOS:
        - Usar StateManager
        """
        # ✅ NUEVO: Obtener índice activo del StateManager
        current_index = self.state_manager.get_active_index()

        if current_index is None:
            next_index = 0
        else:
            next_index = min(current_index + 1, len(self._md_lines) - 1)

        # ✅ NUEVO: Activar usando StateManager
        self.state_manager.activate_line(next_index, enter_edit_mode=True, cursor_pos=cursor_pos)

        # Ajustar scroll para que sea visible
        self._ensure_line_visible(next_index)

    def active_to_previus_item(self, cursor_pos: Optional[Tuple[int, int]] = None):
        """
        Activa la línea anterior.

        CAMBIOS:
        - Usar StateManager
        """
        # ✅ NUEVO: Obtener índice activo del StateManager
        current_index = self.state_manager.get_active_index()

        if current_index is None:
            prev_index = len(self._md_lines) - 1
        else:
            prev_index = max(current_index - 1, 0)

        # ✅ NUEVO: Activar usando StateManager
        self.state_manager.activate_line(prev_index, enter_edit_mode=True, cursor_pos=cursor_pos)

        # Ajustar scroll
        self._ensure_line_visible(prev_index)

    def _ensure_line_visible(self, index: int):
        """
        Asegura que la línea en el índice dado sea visible.

        (Código de scroll no cambia)
        """
        # ... código existente de scroll ...
        pass

    # ==========================================================================
    # Métodos de Acceso Públicos (SIMPLIFICADOS)
    # ==========================================================================

    def get_active_index(self) -> Optional[int]:
        """
        Retorna el índice de la línea activa.

        SIMPLIFICADO: Delega al StateManager
        """
        # ✅ NUEVO: Delegar al StateManager
        return self.state_manager.get_active_index()

        # ❌ ELIMINAR: Variable local
        # return self._active_index

    def get_selected_indices(self):
        """
        Retorna los índices seleccionados.

        SIMPLIFICADO: Delega al StateManager
        """
        # ✅ NUEVO: Delegar al StateManager
        return self.state_manager.get_selected_indices()

        # ❌ ELIMINAR: Variable local
        # return self._selected_indexs

    def is_in_edit_mode(self) -> bool:
        """
        Verifica si hay alguna línea en modo edición.

        SIMPLIFICADO: Consulta al StateManager
        """
        # ✅ NUEVO: Consultar al StateManager
        active_index = self.state_manager.get_active_index()

        if active_index is not None:
            state = self.state_manager.get_state(active_index)
            return state.editing

        return False

        # ❌ ELIMINAR: Variable local
        # return self._mode_editor


# ==============================================================================
# PASO 2: Modificar MDDocumentLineEditor para usar estados
# ==============================================================================

class MDDocumentLineEditorRefactored:
    """
    Versión refactorizada de MDDocumentLineEditor usando estados.

    CAMBIOS PRINCIPALES:
    - Eliminar propiedades de estado locales
    - Recibir estado completo desde StateManager
    - Aplicar estado con método unificado
    """

    def __init__(self):
        """Inicializa el editor de línea."""
        # ... código existente ...

        # ❌ ELIMINAR: Variables de estado locales
        # self.hotlight = BooleanProperty(defaultvalue=False)
        # self.di_state = DataState()

        # ✅ NUEVO: Solo referencia al índice
        self.index = -1

        # Gráficos (sin cambios)
        self.graphic_select = None  # GSelectItem
        self.graphic_active = None  # GActiveItem
        self.graphic_hotlight = None  # GHotlightItem

        # ... resto del código ...

    def apply_state(self, state: LineState):
        """
        Aplica un estado completo al widget.

        Este es el método principal que actualiza la visualización
        del widget basado en el estado proporcionado.

        Args:
            state: Estado a aplicar

        NUEVO MÉTODO - reemplaza múltiples métodos de actualización
        """
        Logger.debug(f"MDDocumentLineEditor[{self.index}]: Applying state - {state}")

        # Actualizar selección
        if hasattr(self, 'graphic_select') and self.graphic_select:
            if state.selected != self.graphic_select.is_visible():
                self.graphic_select.show(state.selected)

        # Actualizar activación
        if hasattr(self, 'graphic_active') and self.graphic_active:
            if state.active != self.graphic_active.is_visible():
                self.graphic_active.show(state.active)

        # Actualizar hotlight
        if hasattr(self, 'graphic_hotlight') and self.graphic_hotlight:
            if state.hotlight != self.graphic_hotlight.is_visible():
                self.graphic_hotlight.show(state.hotlight)

        # Actualizar modo edición
        if hasattr(self, 'wg_line_editor'):
            current_editing = self.wg_line_editor.mode_editor

            if state.editing != current_editing:
                if state.editing:
                    self.wg_line_editor.show_editor(
                        show=True,
                        cursor=state.cursor_pos
                    )
                else:
                    self.wg_line_editor.show_editor(show=False)

        # Actualizar visibilidad (para filtros)
        # Esto normalmente se maneja a nivel de RecycleView
        # pero podría usarse para efectos visuales
        if not state.visible:
            self.opacity = 0.3  # Ejemplo: atenuar líneas filtradas
        else:
            self.opacity = 1.0

    def refresh_view_attrs(self, rv, index, data):
        """
        Actualiza el widget cuando RecycleView recicla.

        CAMBIOS:
        - Usar estado del data en lugar de múltiples atributos
        """
        Logger.debug(f"MDDocumentLineEditor: Refreshing view attrs for index {index}")

        self.index = index

        # ✅ NUEVO: Obtener estado completo del data
        state = data.get('state')

        if state:
            # Aplicar estado completo de una vez
            self.apply_state(state)

        # ❌ ELIMINAR: Actualización manual de múltiples atributos
        # self.di_state = data.get('state')
        # self.show_number_line(data.get('show').number_line, ...)
        # self.graphic_select.show(self.di_state.selected)
        # ... etc

        # ... resto del código de actualización (md_line, etc) ...

        return super().refresh_view_attrs(rv, index, data)

    def on_mouse_move(self, instance, mp):
        """
        Maneja movimiento del mouse.

        CAMBIOS:
        - Notificar al parent (MDDocumentEditor) del cambio de hotlight
        - El parent usa StateManager
        """
        is_over = self.collide_point_to_window(*mp)

        # ✅ NUEVO: Notificar al parent en lugar de actualizar directamente
        if hasattr(self, 'parent') and hasattr(self.parent, 'parent'):
            editor = self.parent.parent  # MDDocumentEditor

            if hasattr(editor, 'handle_hotlight_event'):
                editor.handle_hotlight_event(self.index, self, is_over)

        # ❌ ELIMINAR: Actualización directa
        # self.graphic_hotlight.animate(is_over)
        # self.di_state.hotlight = is_over

    def on_touch_up(self, touch):
        """
        Maneja evento de touch up.

        CAMBIOS:
        - Delegar al parent para usar StateManager
        """
        if touch.grab_current is self and touch.button == 'left':
            # ✅ NUEVO: Delegar al parent
            if hasattr(self, 'parent') and hasattr(self.parent, 'parent'):
                editor = self.parent.parent

                if hasattr(editor, 'handle_touch_left_up_event'):
                    editor.handle_touch_left_up_event(self.index, self, touch)
                    return True

            # ❌ ELIMINAR: Actualización directa de estado
            # self.di_state.active = True
            # self.activate(value=True, show_editor=True, ...)

        return super().on_touch_up(touch)


# ==============================================================================
# PASO 3: Ejemplo de Uso Completo
# ==============================================================================

def example_usage():
    """
    Ejemplo de uso del StateManager en el flujo completo.
    """
    print("\n" + "="*80)
    print("EJEMPLO DE USO: DocumentStateManager")
    print("="*80 + "\n")

    # 1. Crear editor (simulado)
    print("1. Crear MDDocumentEditor con StateManager")
    editor = MDDocumentEditorRefactored()

    # 2. Cargar documento
    print("\n2. Cargar documento con 10 líneas")
    # (Simulado - en realidad serían objetos MDLine)
    # Crear objetos simulados con atributo num_line
    class FakeMDLine:
        def __init__(self, text, num):
            self.md_text = text
            self.num_line = num

    md_lines = [FakeMDLine(f"Line {i}", i+1) for i in range(10)]
    editor.populate_from_md_lines(md_lines)

    # 3. Usuario hace click en línea 5
    print("\n3. Usuario hace click en línea 5")
    print("   → Línea 5 se activa y entra en modo edición")

    # Simular click
    class FakeView:
        class FakeEditor:
            class FakeMdEditor:
                @staticmethod
                def get_cursor_from_xy(x, y):
                    return (x, y)

            md_editor = FakeMdEditor()

        wg_line_editor = FakeEditor()

        @staticmethod
        def to_local(x, y):
            return (x, y)

    class FakeTouch:
        pos = (10, 5)

    editor.handle_touch_left_up_event(5, FakeView(), FakeTouch())

    # Verificar estado
    state = editor.state_manager.get_state(5)
    print(f"   Estado de línea 5: {state}")

    assert state.active
    assert state.selected
    assert state.editing
    assert state.cursor_pos == (10, 5)

    # 4. Usuario mueve mouse sobre línea 8
    print("\n4. Usuario mueve mouse sobre línea 8")
    print("   → Línea 8 muestra hotlight")

    editor.handle_hotlight_event(8, FakeView(), True)

    state = editor.state_manager.get_state(8)
    print(f"   Estado de línea 8: {state}")

    assert state.hotlight

    # 5. Usuario presiona flecha abajo (navega a línea 6)
    print("\n5. Usuario presiona flecha abajo")
    print("   → Línea 5 se desactiva, línea 6 se activa")

    editor.active_to_next_item(cursor_pos=(0, 0))

    state5 = editor.state_manager.get_state(5)
    state6 = editor.state_manager.get_state(6)

    print(f"   Estado de línea 5: {state5}")
    print(f"   Estado de línea 6: {state6}")

    assert not state5.active
    assert state6.active

    # 6. Aplicar filtro que oculta líneas impares
    print("\n6. Aplicar filtro que oculta líneas impares")

    class FakeFilterBar:
        text = "Line 2"

    class FakeWidgets:
        def __getitem__(self, key):
            return FakeFilterBar()

    editor.widgets = FakeWidgets()
    editor.on_filter_state_change(None, True)

    print("   Líneas visibles:")
    for i in range(10):
        state = editor.state_manager.get_state(i)
        if state.visible:
            print(f"   - Línea {i}: {md_lines[i]}")

    # 7. Resumen final
    print("\n7. Resumen del estado del documento:")
    editor.state_manager.print_state_summary()

    # 8. Validar invariantes
    print("8. Validar invariantes del estado:")
    if editor.state_manager.validate_invariants():
        print("   ✅ Todos los invariantes son válidos")
    else:
        print("   ❌ Hay invariantes inválidos")

    print("\n" + "="*80)
    print("FIN DEL EJEMPLO")
    print("="*80 + "\n")


if __name__ == '__main__':
    example_usage()
