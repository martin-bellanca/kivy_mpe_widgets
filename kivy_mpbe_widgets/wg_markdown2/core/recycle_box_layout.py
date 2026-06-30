#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RecycleBoxLayout - Layout con reciclaje inteligente de widgets

Este módulo implementa un layout personalizado que recicla widgets
de líneas basándose en el viewport visible.

Diferencias con RecycleView estándar de Kivy:
- Control total sobre cuándo reciclar
- Widgets visibles NUNCA se reciclan
- Widget activo NUNCA se recicla (preserva estado de edición)
- Acceso directo a widgets por índice

Responsabilidades:
1. Crear/reciclar widgets según visible_in_viewport
2. Mantener pool de widgets reciclables
3. Usar placeholders para líneas no renderizadas
4. Sincronizar con StateManager

Fecha: 2026-01-12
Autor: Martin Pablo Bellanca
"""

from typing import Dict, List, Optional
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.logger import Logger

# Importar StateManager
from .state_manager import DocumentStateManager as StateManager

# Importar widget de línea (reutilizamos el existente)
from kivy_mpbe_widgets.wg_markdown.md_line_editors_v2 import MDDocumentLineEditor



# TODO: Usar en segunda etapa en MDDocumentEditor



class RecycleBoxLayout(BoxLayout):
    """
    Layout personalizado que recicla widgets de líneas inteligentemente.

    Características:
    - Recicla SOLO widgets fuera del viewport
    - Widgets visibles mantienen estado completo
    - Widget activo NUNCA se recicla
    - Placeholders mantienen layout correcto

    Attributes:
        state_manager (StateManager): Referencia al StateManager
        active_widgets (Dict[int, MDDocumentLineEditor]): Widgets renderizados
        recycled_pool (List[MDDocumentLineEditor]): Widgets reciclables
        placeholders (Dict[int, Widget]): Placeholders para líneas no renderizadas
        last_visible_indices (List[int]): Último rango visible (para detectar cambios)

    Example:
        >>> layout = RecycleBoxLayout(state_manager=manager)
        >>> layout.update_visible_range([10, 11, 12, ..., 40])
        >>> widget = layout.get_widget(15)
        >>> print(widget.index)
        15
    """

    def __init__(self, state_manager: StateManager, **kwargs):
        """
        Inicializa el RecycleBoxLayout.

        Args:
            state_manager: Instancia de StateManager
            **kwargs: Argumentos adicionales para BoxLayout
        """
        # Configurar como BoxLayout vertical
        kwargs['orientation'] = 'vertical'
        kwargs['size_hint_y'] = None
        kwargs['spacing'] = 0

        super().__init__(**kwargs)

        # ====================================================================
        # Referencia al StateManager
        # ====================================================================
        self.state_manager = state_manager

        # ====================================================================
        # Bind altura a contenido
        # ====================================================================
        self.bind(minimum_height=self.setter('height'))

        # ====================================================================
        # Pools de widgets
        # ====================================================================
        self.active_widgets: Dict[int, MDDocumentLineEditor] = {}
        self.recycled_pool: List[MDDocumentLineEditor] = []

        # ====================================================================
        # Placeholders
        # ====================================================================
        self.placeholders: Dict[int, Widget] = {}

        # ====================================================================
        # Último rango visible (para detectar cambios)
        # ====================================================================
        self.last_visible_indices: List[int] = []

        Logger.info("RecycleBoxLayout: Initialized")

    # ========================================================================
    # FUNCIÓN CENTRAL: ACTUALIZAR RANGO VISIBLE
    # ========================================================================

    def update_visible_range(self, visible_indices: List[int]):
        """
        FUNCIÓN CENTRAL: Actualizar widgets visibles.

        Esta es la ÚNICA función que crea/recicla widgets.
        Llamada desde MDDocumentEditor en:
        - Scroll
        - Insert/Delete línea
        - Aplicar filtro
        - Resize de ventana

        Args:
            visible_indices: Lista de índices a renderizar

        Algorithm:
            1. Comparar con last_visible_indices
            2. Calcular: to_add (nuevos), to_remove (viejos)
            3. Reciclar widgets en to_remove
            4. Crear/reutilizar widgets en to_add
            5. Actualizar last_visible_indices

        Example:
            >>> # Scroll hacia abajo
            >>> layout.update_visible_range([20, 21, ..., 50])
            >>> # Recicla widgets [0-9], crea widgets [41-50]
        """
        # Detectar si cambió algo
        if visible_indices == self.last_visible_indices:
            return

        # Convertir a sets para operaciones eficientes
        indices_set = set(visible_indices)
        last_set = set(self.last_visible_indices)

        # Calcular diferencias
        to_add = indices_set - last_set      # Nuevas líneas a renderizar
        to_remove = last_set - indices_set   # Líneas a reciclar

        Logger.debug(
            f"RecycleBoxLayout: update_visible_range - "
            f"to_add={len(to_add)}, to_remove={len(to_remove)}"
        )

        # 1. Reciclar widgets que ya no son visibles
        for index in to_remove:
            self._recycle_widget_at_index(index)

        # 2. Crear/reutilizar widgets para nuevas líneas visibles
        for index in to_add:
            self._create_or_reuse_widget_at_index(index)

        # 3. Actualizar registro
        self.last_visible_indices = visible_indices

        Logger.debug(
            f"RecycleBoxLayout: Active widgets: {len(self.active_widgets)}, "
            f"Recycled pool: {len(self.recycled_pool)}"
        )

    # ========================================================================
    # CREAR/REUTILIZAR WIDGET
    # ========================================================================

    def _create_or_reuse_widget_at_index(self, index: int):
        """
        Crear o reutilizar widget para un índice.

        Pasos:
        1. Obtener estado del StateManager
        2. Obtener widget del pool o crear nuevo
        3. Asignar datos al widget
        4. Sincronizar estado visual (SIN animación)
        5. Insertar en layout

        Args:
            index: Índice de la línea
        """
        # Obtener estado
        state = self.state_manager.get_state(index)
        if not state:
            Logger.warning(f"RecycleBoxLayout: No state for index {index}")
            return

        # Obtener widget del pool o crear nuevo
        if self.recycled_pool:
            widget = self.recycled_pool.pop()
            Logger.debug(f"RecycleBoxLayout: Reusing widget for line {index}")
        else:
            widget = MDDocumentLineEditor()
            Logger.debug(f"RecycleBoxLayout: Creating new widget for line {index}")

        # Asignar datos del StateManager
        self._bind_widget_data(widget, index, state)

        # Registrar en active_widgets
        self.active_widgets[index] = widget

        # Insertar en layout
        self._insert_widget_in_layout(index, widget)

    def _bind_widget_data(self, widget: MDDocumentLineEditor, index: int, state):
        """
        Asignar datos de LineState al widget.

        Similar a refresh_view_attrs de RecycleView pero MÁS SIMPLE.
        NO ejecuta animaciones (es solo sincronización de datos).

        Args:
            widget: Widget a actualizar
            index: Índice de la línea
            state: LineState con los datos
        """
        # Asignar datos básicos
        widget.index = index
        widget.md_line = state.md_line

        # Sincronizar estado visual (SIN animación, es reciclaje)
        widget.active = state.active
        widget.selected = state.selected
        widget.hotlight = state.hotlight

        # Actualizar gráficos de selección
        if hasattr(widget, 'graphic_select'):
            widget.graphic_select.show(state.selected)

        # Si está en modo edición, mostrar editor
        if state.active and state.editing:
            if hasattr(widget.wg_line_editor, 'show_editor'):
                widget.wg_line_editor.show_editor(True)
                # Restaurar cursor si es posible
                if hasattr(widget.wg_line_editor, 'md_editor'):
                    widget.wg_line_editor.md_editor.cursor = state.cursor_pos
        else:
            if hasattr(widget.wg_line_editor, 'show_editor'):
                widget.wg_line_editor.show_editor(False)

        Logger.debug(f"RecycleBoxLayout: Bound data to widget for line {index}")

    # ========================================================================
    # RECICLAR WIDGET
    # ========================================================================

    def _recycle_widget_at_index(self, index: int):
        """
        Reciclar widget de un índice.

        IMPORTANTE: NO recicla el widget activo (preserva estado de edición).

        Pasos:
        1. Verificar si existe el widget
        2. Verificar si es el widget activo (NO reciclar)
        3. Agregar a pool de reciclaje
        4. Reemplazar con placeholder

        Args:
            index: Índice de la línea
        """
        if index not in self.active_widgets:
            return

        widget = self.active_widgets[index]

        # ⚠️ PROTECCIÓN: NO reciclar widget activo
        # Esto preserva el estado de edición cuando el usuario
        # está editando una línea que sale del viewport
        if hasattr(self.parent, 'active_line_widget'):
            if widget == self.parent.active_line_widget:
                Logger.debug(
                    f"RecycleBoxLayout: NOT recycling active widget at index {index}"
                )
                return

        # Remover de active_widgets
        self.active_widgets.pop(index)

        # Agregar a pool de reciclaje
        self.recycled_pool.append(widget)

        # Reemplazar con placeholder
        self._replace_widget_with_placeholder(index, widget)

        Logger.debug(f"RecycleBoxLayout: Recycled widget at index {index}")

    # ========================================================================
    # MANEJO DE PLACEHOLDERS
    # ========================================================================

    def _replace_widget_with_placeholder(self, index: int, old_widget: Widget):
        """
        Reemplazar widget con placeholder.

        Los placeholders son widgets dummy que mantienen el espacio
        en el layout cuando el widget real se recicla.

        Args:
            index: Índice de la línea
            old_widget: Widget a reemplazar
        """
        state = self.state_manager.get_state(index)
        if not state:
            return

        # Crear placeholder con misma altura
        placeholder = Widget(
            size_hint_y=None,
            height=state.height
        )

        # Obtener posición del widget en children
        try:
            widget_pos = self.children.index(old_widget)
        except ValueError:
            # Widget no está en children (no debería pasar)
            Logger.warning(
                f"RecycleBoxLayout: Widget at index {index} not in children"
            )
            return

        # Reemplazar en layout
        self.remove_widget(old_widget)
        self.add_widget(placeholder, index=widget_pos)

        # Guardar referencia
        self.placeholders[index] = placeholder

        Logger.debug(
            f"RecycleBoxLayout: Replaced widget {index} with placeholder "
            f"(height={state.height:.0f}px)"
        )

    def _insert_widget_in_layout(self, index: int, widget: Widget):
        """
        Insertar widget en la posición correcta del layout.

        Si existe un placeholder, lo reemplaza.
        Si no, calcula la posición de inserción correcta.

        Args:
            index: Índice de la línea
            widget: Widget a insertar

        Note:
            BoxLayout.children está invertido: children[0] = bottom, children[-1] = top
        """
        # Si hay placeholder, reemplazarlo
        if index in self.placeholders:
            placeholder = self.placeholders.pop(index)
            try:
                placeholder_pos = self.children.index(placeholder)
                self.remove_widget(placeholder)
                self.add_widget(widget, index=placeholder_pos)
                Logger.debug(f"RecycleBoxLayout: Replaced placeholder at index {index}")
                return
            except ValueError:
                # Placeholder no está en children (no debería pasar)
                Logger.warning(
                    f"RecycleBoxLayout: Placeholder {index} not in children"
                )

        # No hay placeholder, calcular posición de inserción
        insert_pos = self._calculate_insert_position(index)
        self.add_widget(widget, index=insert_pos)

        Logger.debug(
            f"RecycleBoxLayout: Inserted widget at index {index}, "
            f"layout position {insert_pos}"
        )

    def _calculate_insert_position(self, index: int) -> int:
        """
        Calcular posición de inserción en children para un índice.

        BoxLayout.children está invertido:
        - children[0] = bottom (última línea del documento)
        - children[-1] = top (primera línea del documento)

        Args:
            index: Índice de la línea en el documento

        Returns:
            int: Posición en children donde insertar
        """
        # Obtener líneas visibles ordenadas
        visible_sorted = sorted(self.state_manager.visible_indices)

        if not visible_sorted or index not in visible_sorted:
            return 0

        # Posición en lista visible
        position_in_visible = visible_sorted.index(index)

        # Invertir para children (children[0] = bottom)
        children_position = len(visible_sorted) - position_in_visible - 1

        return children_position

    # ========================================================================
    # ACCESO A WIDGETS
    # ========================================================================

    def get_widget(self, index: int) -> Optional[MDDocumentLineEditor]:
        """
        Obtener widget de un índice (si está renderizado).

        Args:
            index: Índice de la línea

        Returns:
            MDDocumentLineEditor | None: Widget si está activo, None si no
        """
        return self.active_widgets.get(index)

    def has_widget(self, index: int) -> bool:
        """
        Verificar si un índice tiene widget renderizado.

        Args:
            index: Índice de la línea

        Returns:
            bool: True si tiene widget activo
        """
        return index in self.active_widgets

    # ========================================================================
    # UTILIDADES
    # ========================================================================

    def clear_all(self):
        """
        Limpiar todos los widgets y pools.

        Útil para resetear el layout completamente.
        """
        Logger.info("RecycleBoxLayout: Clearing all widgets")

        # Limpiar layout
        self.clear_widgets()

        # Limpiar pools
        self.active_widgets.clear()
        self.recycled_pool.clear()
        self.placeholders.clear()
        self.last_visible_indices.clear()

    def __repr__(self) -> str:
        """Representación string del layout."""
        # Protección: __repr__ puede ser llamado antes de __init__ completo
        active = len(self.active_widgets) if hasattr(self, 'active_widgets') else 0
        recycled = len(self.recycled_pool) if hasattr(self, 'recycled_pool') else 0
        placeholders = len(self.placeholders) if hasattr(self, 'placeholders') else 0

        return (
            f"RecycleBoxLayout("
            f"active={active}, "
            f"recycled={recycled}, "
            f"placeholders={placeholders}"
            f")"
        )
