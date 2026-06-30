#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ListBoxLayout - Layout simple sin reciclaje de widgets

Este módulo implementa un layout que crea un widget por cada línea
del documento SIN reciclar. Cada línea mantiene su widget permanentemente.

Diferencias con RecycleBoxLayout:
- NO recicla widgets (cada línea tiene su widget permanente)
- Más simple de implementar y depurar
- Mejor para documentos pequeños/medianos (<500 líneas)
- Widgets hacen bind directo a su LineState

Responsabilidades:
1. Crear widget para cada LineState
2. Gestionar add/remove/move de widgets
3. Sincronizar con StateManager via EventDispatcher
4. Mantener orden correcto de widgets en layout

Fecha: 2026-02-01
Autor: Martin Pablo Bellanca
"""

from typing import Dict, List, Optional, Type
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, NumericProperty
from kivy.logger import Logger

# Importar LineState
from .line_state import LineState
from .state_manager import DocumentStateManager as StateManager


# VER SI TIENE SENTIDO UASR ESTA CLASE. YO CREO QUE NO
# usar BoxLout y incorporar las funciones que sirvan md_document_editor.py, como el populate() que crea los widgets, pero sin reciclar, y con bind directo a LineState. El tema es que no se si conviene tener esta clase aparte o incorporar esa funcionalidad directamente en md_document_editor.py. Quizás lo mejor sea tener esta clase aparte para mantener md_document_editor.py más limpio y enfocado en la lógica de edición, mientras que ListBoxLayout se encarga exclusivamente de la gestión de widgets y su sincronización con el StateManager. De esta forma, si en el futuro quiero implementar otro tipo de layout (como un RecycleBoxLayout), puedo reutilizar la lógica de md_document_editor.py sin cambios significativos.
# NO LA USO PORQUE ES MÁS SIMPLE USAR DIRECTAMENTE UN BOXLAYOUT Y MANEJAR LOS WIDGETS MANUALMENTE DESDE MD_DOCUMENT_EDITOR.PY. ESTA CLASE QUEDA COMO REFERENCIA PARA UNA IMPLEMENTACIÓN FUTURA MÁS COMPLEJA, PERO POR AHORA NO LA USO PARA MANTENER LAS COSAS SIMPLES.

# Guardo como referencia de funciones

# 
class ListBoxLayout(BoxLayout):
    """
    Layout simple que crea un widget por cada línea sin reciclar.

    Cada LineState tiene su widget permanente que hace bind directo
    a las propiedades del LineState. Los cambios de estado se propagan
    automáticamente via el sistema de eventos de Kivy.

    Attributes:
        state_manager: Referencia al StateManager (EventDispatcher)
        line_widgets: Dict[int, Widget] - Widgets por índice
        widget_class: Clase de widget a instanciar para cada línea

    Events:
        on_widget_created: Disparado cuando se crea un widget
        on_widget_removed: Disparado cuando se elimina un widget

    Example:
        >>> layout = ListBoxLayout()
        >>> layout.set_state_manager(state_manager)
        >>> layout.set_widget_class(MDDocumentLineEditor)
        >>> layout.populate()  # Crea widgets para todas las líneas
    """

    # ========================================================================
    # Properties
    # ========================================================================
    state_manager = ObjectProperty(None, allownone=True)
    total_height = NumericProperty(0.0)

    def __init__(self, state_manager: StateManager, **kwargs):
        """
        Inicializa el ListBoxLayout.

        Args:
            **kwargs: Argumentos adicionales para BoxLayout
        """
        # Configurar como BoxLayout vertical
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('spacing', 0)

        super().__init__(**kwargs)

        self.state_manager = state_manager
        # ====================================================================
        # Registrar eventos personalizados
        # ====================================================================
        self.register_event_type('on_widget_created')
        self.register_event_type('on_widget_removed')

        # ====================================================================
        # Almacenamiento de widgets
        # ====================================================================
        self.line_widgets: Dict[int, Widget] = {}

        # ====================================================================
        # Clase de widget a usar (se configura externamente)
        # ====================================================================
        self._widget_class: Optional[Type[Widget]] = None

        # ====================================================================
        # Bind altura a contenido
        # ====================================================================
        self.bind(minimum_height=self.setter('height'))

        Logger.info("ListBoxLayout: Initialized")

    # ========================================================================
    # CONFIGURACIÓN
    # ========================================================================

    def set_widget_class(self, widget_class: Type[Widget]):
        """
        Establecer la clase de widget a usar para las líneas.

        Args:
            widget_class: Clase que hereda de Widget (ej: MDDocumentLineEditor)

        Example:
            >>> layout.set_widget_class(MDDocumentLineEditor)
        """
        self._widget_class = widget_class
        Logger.info(f"ListBoxLayout: Widget class set to {widget_class.__name__}")

    def set_state_manager(self, state_manager:StateManager):
        """
        Establecer el StateManager y hacer bind a sus eventos.

        Args:
            state_manager: Instancia de StateManager (EventDispatcher)
        """
        # Unbind del anterior si existe
        if self.state_manager is not None:
            self._unbind_state_manager()

        self.state_manager = state_manager

        # Bind a eventos estructurales del StateManager
        self._bind_state_manager()

        Logger.info("ListBoxLayout: StateManager connected")

    def _bind_state_manager(self):
        """Hacer bind a los eventos del StateManager."""
        if self.state_manager is None:
            return

        # Bind a eventos estructurales (add/remove/move)
        if hasattr(self.state_manager, 'bind'):
            self.state_manager.bind(on_line_added=self._on_line_added)
            self.state_manager.bind(on_line_removed=self._on_line_removed)
            self.state_manager.bind(on_line_moved=self._on_line_moved)

    def _unbind_state_manager(self):
        """Quitar bindings del StateManager anterior."""
        if self.state_manager is None:
            return

        if hasattr(self.state_manager, 'unbind'):
            self.state_manager.unbind(on_line_added=self._on_line_added)
            self.state_manager.unbind(on_line_removed=self._on_line_removed)
            self.state_manager.unbind(on_line_moved=self._on_line_moved)

    # ========================================================================
    # POBLACIÓN INICIAL
    # ========================================================================

    def populate(self):
        """
        Crear widgets para todas las líneas del StateManager.

        Limpia widgets existentes y crea uno nuevo para cada LineState.
        Cada widget hace bind directo a su LineState.

        Example:
            >>> layout.populate()
            >>> print(len(layout.line_widgets))
            100  # Si hay 100 líneas
        """
        if self.state_manager is None:
            Logger.warning("ListBoxLayout: No state_manager set")
            return

        if self._widget_class is None:
            Logger.warning("ListBoxLayout: No widget_class set")
            return

        Logger.info("ListBoxLayout: Populating widgets...")

        # Limpiar widgets existentes
        self.clear_all()

        # Obtener número de líneas
        total_lines = self.state_manager.get_total_lines()

        # Crear widget para cada línea
        for index in range(total_lines):
            self._create_widget_for_index(index)

        # Actualizar altura total
        self._update_total_height()

        Logger.info(
            f"ListBoxLayout: Populated {len(self.line_widgets)} widgets, "
            f"height={self.total_height:.0f}px"
        )

    def _create_widget_for_index(self, index: int) -> Optional[Widget]:
        """
        Crear widget para un índice específico.

        Args:
            index: Índice de la línea

        Returns:
            Widget creado o None si falla
        """
        # Obtener LineState
        line_state = self.state_manager.get_state(index)
        if line_state is None:
            Logger.warning(f"ListBoxLayout: No state for index {index}")
            return None

        # Crear widget
        widget = self._widget_class()

        # Configurar widget con LineState
        self._configure_widget(widget, line_state)

        # Registrar widget
        self.line_widgets[index] = widget

        # Agregar al layout (al final = bottom, orden invertido en BoxLayout)
        self.add_widget(widget)

        # Disparar evento
        self.dispatch('on_widget_created', index, widget)

        Logger.debug(f"ListBoxLayout: Created widget for line {index}")

        return widget

    def _configure_widget(self, widget: Widget, line_state: LineState):
        """
        Configurar widget con su LineState.

        El widget recibe el LineState y debe hacer bind a sus propiedades.

        Args:
            widget: Widget a configurar
            line_state: LineState de la línea
        """
        # Asignar LineState al widget
        if hasattr(widget, 'line_state'):
            widget.line_state = line_state

        # Asignar index directamente también (conveniencia)
        if hasattr(widget, 'index'):
            widget.index = line_state.index

        # Configurar altura basada en LineState
        if hasattr(widget, 'height'):
            widget.height = line_state.height
            widget.size_hint_y = None

        # El widget debería hacer bind internamente a line_state
        # cuando se le asigna (en su setter de line_state)

    # ========================================================================
    # CALLBACKS DE EVENTOS ESTRUCTURALES
    # ========================================================================

    def _on_line_added(self, instance, event):
        """
        Callback cuando se agrega una línea.

        Args:
            instance: StateManager que emitió el evento
            event: LineStateEvent con información del cambio
        """
        index = event.index
        Logger.debug(f"ListBoxLayout: Line added at index {index}")

        # Reindexar widgets existentes (los que están después del nuevo)
        self._reindex_widgets_after(index)

        # Crear widget para la nueva línea
        self._create_widget_at_position(index)

        # Actualizar altura
        self._update_total_height()

    def _on_line_removed(self, instance, event):
        """
        Callback cuando se elimina una línea.

        Args:
            instance: StateManager que emitió el evento
            event: LineStateEvent con información del cambio
        """
        index = event.index
        Logger.debug(f"ListBoxLayout: Line removed at index {index}")

        # Remover widget
        self._remove_widget_at_index(index)

        # Reindexar widgets después del eliminado
        self._reindex_widgets_after(index, removed=True)

        # Actualizar altura
        self._update_total_height()

    def _on_line_moved(self, instance, event):
        """
        Callback cuando se mueve una línea.

        Args:
            instance: StateManager que emitió el evento
            event: LineStateEvent con información del cambio
        """
        # Para mover, reordenamos el layout completo
        # (más simple que calcular posiciones individuales)
        Logger.debug(f"ListBoxLayout: Line moved, reordering layout")
        self._reorder_layout()

    # ========================================================================
    # GESTIÓN DE WIDGETS
    # ========================================================================

    def _create_widget_at_position(self, index: int):
        """
        Crear widget e insertarlo en la posición correcta.

        Args:
            index: Índice de la línea
        """
        if self._widget_class is None:
            return

        line_state = self.state_manager.get_state(index)
        if line_state is None:
            return

        # Crear widget
        widget = self._widget_class()
        self._configure_widget(widget, line_state)

        # Registrar
        self.line_widgets[index] = widget

        # Calcular posición en children (invertido)
        # children[0] = último widget (bottom)
        # Queremos insertar en la posición correcta
        children_pos = self._index_to_children_position(index)
        self.add_widget(widget, index=children_pos)

        # Disparar evento
        self.dispatch('on_widget_created', index, widget)

    def _remove_widget_at_index(self, index: int):
        """
        Remover widget de un índice.

        Args:
            index: Índice de la línea
        """
        if index not in self.line_widgets:
            return

        widget = self.line_widgets.pop(index)

        # Remover del layout
        self.remove_widget(widget)

        # Disparar evento
        self.dispatch('on_widget_removed', index, widget)

        Logger.debug(f"ListBoxLayout: Removed widget at index {index}")

    def _reindex_widgets_after(self, index: int, removed: bool = False):
        """
        Reindexar widgets después de una inserción o eliminación.

        Args:
            index: Índice donde ocurrió el cambio
            removed: True si se eliminó, False si se insertó
        """
        # Crear nuevo diccionario con índices actualizados
        new_widgets = {}
        delta = -1 if removed else 1

        for old_index, widget in self.line_widgets.items():
            if old_index < index:
                # Widgets antes del cambio: mantener índice
                new_widgets[old_index] = widget
            elif old_index == index and not removed:
                # Widget en el índice de inserción: ya manejado
                continue
            else:
                # Widgets después: ajustar índice
                new_index = old_index + delta
                new_widgets[new_index] = widget

                # Actualizar índice en el widget
                if hasattr(widget, 'index'):
                    widget.index = new_index

                # Actualizar LineState en widget
                new_state = self.state_manager.get_state(new_index)
                if new_state and hasattr(widget, 'line_state'):
                    widget.line_state = new_state

        self.line_widgets = new_widgets

    def _reorder_layout(self):
        """
        Reordenar widgets en el layout según índices actuales.

        Usado después de operaciones de mover líneas.
        """
        # Obtener widgets ordenados por índice
        sorted_indices = sorted(self.line_widgets.keys())

        # Limpiar layout (sin destruir widgets)
        for widget in list(self.children):
            self.remove_widget(widget)

        # Re-agregar en orden correcto
        # BoxLayout agrega al final = top, así que agregamos en orden inverso
        for index in reversed(sorted_indices):
            widget = self.line_widgets[index]
            self.add_widget(widget)

    def _index_to_children_position(self, index: int) -> int:
        """
        Convertir índice de línea a posición en children.

        BoxLayout.children está invertido:
        - children[0] = bottom (última línea visible)
        - children[-1] = top (primera línea visible)

        Args:
            index: Índice de la línea en el documento

        Returns:
            Posición en children donde insertar
        """
        total = len(self.children)
        # Para insertar en la posición correcta
        # index 0 debería estar en children[-1] (top)
        # index N debería estar en children[0] (bottom)
        return total - index

    # ========================================================================
    # ACCESO A WIDGETS
    # ========================================================================

    def get_widget(self, index: int) -> Optional[Widget]:
        """
        Obtener widget de un índice.

        Args:
            index: Índice de la línea

        Returns:
            Widget de la línea o None si no existe
        """
        return self.line_widgets.get(index)

    def get_widget_count(self) -> int:
        """
        Obtener número de widgets.

        Returns:
            Número de widgets en el layout
        """
        return len(self.line_widgets)

    def has_widget(self, index: int) -> bool:
        """
        Verificar si existe widget para un índice.

        Args:
            index: Índice de la línea

        Returns:
            True si existe widget
        """
        return index in self.line_widgets

    # ========================================================================
    # ALTURA Y GEOMETRÍA
    # ========================================================================

    def _update_total_height(self):
        """
        Actualizar altura total del layout.

        La altura es la suma de alturas de todos los widgets visibles.
        """
        total = 0.0
        for widget in self.line_widgets.values():
            if hasattr(widget, 'height'):
                total += widget.height

        # Agregar spacing
        if len(self.line_widgets) > 1:
            total += self.spacing * (len(self.line_widgets) - 1)

        self.total_height = total
        self.height = total

    def update_widget_height(self, index: int, new_height: float):
        """
        Actualizar altura de un widget específico.

        Args:
            index: Índice de la línea
            new_height: Nueva altura en pixels
        """
        if index not in self.line_widgets:
            return

        widget = self.line_widgets[index]
        if hasattr(widget, 'height'):
            widget.height = new_height

        # Actualizar altura total
        self._update_total_height()

    # ========================================================================
    # LIMPIEZA
    # ========================================================================

    def clear_all(self):
        """
        Limpiar todos los widgets.
        """
        Logger.info("ListBoxLayout: Clearing all widgets")

        # Disparar eventos de remoción
        for index, widget in list(self.line_widgets.items()):
            self.dispatch('on_widget_removed', index, widget)

        # Limpiar layout
        self.clear_widgets()

        # Limpiar diccionario
        self.line_widgets.clear()

        # Reset altura
        self.total_height = 0.0

    # ========================================================================
    # EVENTOS (handlers vacíos requeridos por register_event_type)
    # ========================================================================

    def on_widget_created(self, index: int, widget: Widget):
        """Handler por defecto para on_widget_created."""
        pass

    def on_widget_removed(self, index: int, widget: Widget):
        """Handler por defecto para on_widget_removed."""
        pass

    # ========================================================================
    # REPRESENTACIÓN
    # ========================================================================

    def __repr__(self) -> str:
        """Representación string del layout."""
        count = len(self.line_widgets) if hasattr(self, 'line_widgets') else 0
        height = self.total_height if hasattr(self, 'total_height') else 0.0

        return f"ListBoxLayout(widgets={count}, height={height:.0f}px)"
