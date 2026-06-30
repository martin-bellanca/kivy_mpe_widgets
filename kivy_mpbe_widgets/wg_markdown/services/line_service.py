#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  line_service.py
#
#  Servicio para operaciones de líneas del documento
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
LineService - Servicio para Operaciones de Líneas

Encapsula toda la lógica de negocio relacionada con:
- Activación/desactivación de líneas
- Edición de líneas
- Movimiento de líneas
- Inserción/eliminación de líneas

Desacopla la lógica de negocio de la UI (widgets).
"""

from typing import Optional, Tuple, Set, List
from dataclasses import asdict
from kivy.logger import Logger

# Imports relativos dentro del proyecto
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager
from helpers_mpbe.markdown_document import MD_LINE_TYPE
from helpers_mpbe.markdown_document.md_document import MDLine


class LineService:
    """
    Servicio para operaciones de líneas del documento.

    Este servicio encapsula toda la lógica de negocio relacionada
    con operaciones sobre líneas individuales o grupos de líneas.

    Responsibilities:
        - Activar/desactivar líneas
        - Entrar/salir de modo edición
        - Validar operaciones según tipo de línea
        - Mover líneas (arriba/abajo)
        - Insertar/eliminar líneas
        - Actualizar referencias prev/next

    Dependencies:
        - DocumentStateManager: Para gestión de estado
        - md_lines: Lista de MDLine del documento
    """

    # Tipos de línea que se pueden editar
    EDITABLE_TYPES: Set[MD_LINE_TYPE] = {
        MD_LINE_TYPE.TEXT,
        MD_LINE_TYPE.TITLE,
        MD_LINE_TYPE.HEAD_TITLE,
        MD_LINE_TYPE.LIST,
        MD_LINE_TYPE.ORDER_LIST,
        MD_LINE_TYPE.TASK,
        MD_LINE_TYPE.TODO,
        MD_LINE_TYPE.BLOCKQUOTE,
    }

    # Tipos de línea que NO se pueden editar
    NON_EDITABLE_TYPES: Set[MD_LINE_TYPE] = {
        MD_LINE_TYPE.SEPARATOR,
        MD_LINE_TYPE.UNDERLINE_TITLE,
        MD_LINE_TYPE.TABLE,
        MD_LINE_TYPE.IMAGEN,
        MD_LINE_TYPE.CODE,
        MD_LINE_TYPE.START_CODE,
        MD_LINE_TYPE.END_CODE,
    }

    def __init__(self,
                 state_manager: DocumentStateManager,
                 md_lines: List[MDLine]):
        """
        Inicializa el servicio de líneas.

        Args:
            state_manager: Gestor de estados del documento
            md_lines: Lista de líneas del documento
        """
        self.state_manager = state_manager
        self.md_lines = md_lines

        Logger.info("LineService: Initialized")

    # ==========================================================================
    # Activación y Edición
    # ==========================================================================

    def activate_line(self,
                     index: int,
                     enter_edit: bool = False,
                     cursor_pos: Optional[Tuple[int, int]] = None,
                     anim_type: str = 'fade') -> bool:
        """
        Activa una línea para interacción.

        Valida que la línea existe y es editable (si se requiere edición).
        Automáticamente desactiva la línea anterior.

        Args:
            index: Índice de la línea a activar
            enter_edit: Si True, entra en modo edición
            cursor_pos: Posición del cursor para animaciones
            anim_type: Tipo de animación ('fade', 'slide_up', 'slide_down', 'expand_up', 'expand_down')

        Returns:
            bool: True si se activó correctamente, False si no se pudo

        Side Effects:
            - Actualiza StateManager (activa línea, desactiva anterior)
            - Puede cambiar selección

        Example:
            >>> success = service.activate_line(10, enter_edit=True, cursor_pos=(5, 0), anim_type='fade')
            >>> if success:
            ...     print("Línea 10 activada en modo edición")
        """
        # Validar índice
        if not self._is_valid_index(index):
            Logger.warning(f"LineService: Invalid index {index}")
            return False

        # Si se requiere edición, validar que sea editable
        if enter_edit:
            md_line = self.md_lines[index]
            if not self._is_editable(md_line):
                Logger.warning(
                    f"LineService: Line {index} type {md_line.type} is not editable"
                )
                return False

        # Desactivar línea anterior si existe
        prev_active = self.state_manager.get_active_index()
        if prev_active is not None and prev_active != index:
            self._deactivate_line(prev_active, anim_type=anim_type)

        # Activar nueva línea
        self.state_manager.activate_line(
            index,
            enter_edit_mode=enter_edit,
            cursor_pos=cursor_pos,
            anim_type=anim_type
        )

        Logger.info(
            f"LineService: Line {index} activated (edit={enter_edit}, anim={anim_type})"
        )

        return True

    def deactivate_current_line(self, save_changes: bool = True) -> bool:
        """
        Desactiva la línea actualmente activa.

        Args:
            save_changes: Si True, guarda cambios antes de desactivar

        Returns:
            bool: True si se desactivó, False si no había línea activa
        """
        active_index = self.state_manager.get_active_index()

        if active_index is None:
            return False

        if save_changes:
            # Aquí se podría agregar lógica de guardado si es necesario
            pass

        self._deactivate_line(active_index)

        Logger.info(f"LineService: Line {active_index} deactivated")

        return True

    def _deactivate_line(self, index: int, anim_type: str = 'fade'):
        """
        Desactiva una línea (privado).

        Args:
            index: Índice de la línea a desactivar
            anim_type: Tipo de animación para la desactivación
        """
        state = self.state_manager.get_state(index)

        if state.editing:
            # Guardar cambios si estaba editando
            # (Por ahora solo sale de modo edición)
            pass

        self.state_manager.deactivate_line(index, anim_type=anim_type)

    def toggle_edit_mode(self) -> bool:
        """
        Alterna el modo edición de la línea activa.

        Returns:
            bool: True si se alternó, False si no hay línea activa
        """
        active_index = self.state_manager.get_active_index()

        if active_index is None:
            return False

        # Validar que sea editable
        md_line = self.md_lines[active_index]
        if not self._is_editable(md_line):
            Logger.warning(
                f"LineService: Cannot edit line {active_index} type {md_line.type}"
            )
            return False

        # Toggle
        self.state_manager.toggle_edit_mode(active_index)

        state = self.state_manager.get_state(active_index)
        Logger.info(
            f"LineService: Edit mode toggled for line {active_index} -> {state.editing}"
        )

        return True

    # ==========================================================================
    # Movimiento de Líneas
    # ==========================================================================

    def move_line_up(self, index: Optional[int] = None) -> Optional[int]:
        """
        Mueve una línea hacia arriba.

        Args:
            index: Índice de la línea a mover (None = línea activa)

        Returns:
            int: Nuevo índice de la línea, o None si no se pudo mover

        Side Effects:
            - Modifica md_lines
            - Actualiza referencias prev/next
            - Actualiza StateManager (shift indices)
        """
        # Si no se especifica índice, usar línea activa
        if index is None:
            index = self.state_manager.get_active_index()
            if index is None:
                Logger.warning("LineService: No active line to move")
                return None

        # No se puede mover la primera línea hacia arriba
        if index <= 0:
            Logger.debug(f"LineService: Cannot move line {index} up (already at top)")
            return None

        # Validar índice
        if not self._is_valid_index(index):
            return None

        new_index = index - 1

        # Mover en la lista
        self.md_lines[index], self.md_lines[new_index] = \
            self.md_lines[new_index], self.md_lines[index]

        # Actualizar referencias prev/next
        self._update_line_references(new_index)
        self._update_line_references(new_index + 1)

        # Actualizar números de línea
        self.md_lines[new_index].num_line = new_index + 1
        self.md_lines[index].num_line = index + 1

        # Ajustar índices en StateManager
        # Intercambiar estados
        state_old = self.state_manager.get_state(index)
        state_new = self.state_manager.get_state(new_index)

        # Convertir estados a dict para actualizar
        old_dict = asdict(state_old)
        new_dict = asdict(state_new)

        self.state_manager.update_state(new_index, **old_dict)
        self.state_manager.update_state(index, **new_dict)

        Logger.info(f"LineService: Line moved from {index} to {new_index}")

        return new_index

    def move_line_down(self, index: Optional[int] = None) -> Optional[int]:
        """
        Mueve una línea hacia abajo.

        Args:
            index: Índice de la línea a mover (None = línea activa)

        Returns:
            int: Nuevo índice de la línea, o None si no se pudo mover
        """
        # Si no se especifica índice, usar línea activa
        if index is None:
            index = self.state_manager.get_active_index()
            if index is None:
                Logger.warning("LineService: No active line to move")
                return None

        # No se puede mover la última línea hacia abajo
        if index >= len(self.md_lines) - 1:
            Logger.debug(f"LineService: Cannot move line {index} down (already at bottom)")
            return None

        # Validar índice
        if not self._is_valid_index(index):
            return None

        new_index = index + 1

        # Mover en la lista
        self.md_lines[index], self.md_lines[new_index] = \
            self.md_lines[new_index], self.md_lines[index]

        # Actualizar referencias prev/next
        self._update_line_references(index)
        self._update_line_references(new_index)

        # Actualizar números de línea
        self.md_lines[index].num_line = index + 1
        self.md_lines[new_index].num_line = new_index + 1

        # Ajustar estados
        state_old = self.state_manager.get_state(index)
        state_new = self.state_manager.get_state(new_index)

        # Convertir estados a dict para actualizar
        old_dict = asdict(state_old)
        new_dict = asdict(state_new)

        self.state_manager.update_state(new_index, **old_dict)
        self.state_manager.update_state(index, **new_dict)

        Logger.info(f"LineService: Line moved from {index} to {new_index}")

        return new_index

    # ==========================================================================
    # Inserción y Eliminación
    # ==========================================================================

    def insert_line_below(self,
                         index: Optional[int] = None,
                         text: str = "",
                         line_type: MD_LINE_TYPE = MD_LINE_TYPE.TEXT) -> int:
        """
        Inserta una nueva línea debajo del índice especificado.

        Args:
            index: Índice después del cual insertar (None = línea activa)
            text: Texto de la nueva línea
            line_type: Tipo de línea a crear

        Returns:
            int: Índice de la nueva línea

        Side Effects:
            - Modifica md_lines
            - Actualiza referencias prev/next
            - Shift de índices en StateManager
        """
        # Si no se especifica índice, usar línea activa
        if index is None:
            index = self.state_manager.get_active_index()
            if index is None:
                # Si no hay línea activa, insertar al final
                index = len(self.md_lines) - 1

        new_index = index + 1

        # Obtener líneas anterior y siguiente
        prev_line = self.md_lines[index] if 0 <= index < len(self.md_lines) else None
        next_line = self.md_lines[new_index] if new_index < len(self.md_lines) else None

        # Crear nueva línea
        new_line = MDLine(
            md_text=text,
            prev_line=prev_line,
            next_line=next_line,
            type=line_type,
            num_line=new_index + 1
        )

        # Insertar en la lista
        self.md_lines.insert(new_index, new_line)

        # Actualizar referencias
        if prev_line:
            prev_line.next_line = new_line
        if next_line:
            next_line.prev_line = new_line

        # Actualizar números de línea de las líneas posteriores
        for i in range(new_index + 1, len(self.md_lines)):
            self.md_lines[i].num_line = i + 1

        # Shift de índices en StateManager
        self.state_manager.shift_indices(start_index=new_index, delta=1)

        Logger.info(f"LineService: Line inserted at {new_index}")

        return new_index

    def insert_line_above(self,
                         index: Optional[int] = None,
                         text: str = "",
                         line_type: MD_LINE_TYPE = MD_LINE_TYPE.TEXT) -> int:
        """
        Inserta una nueva línea encima del índice especificado.

        Args:
            index: Índice antes del cual insertar (None = línea activa)
            text: Texto de la nueva línea
            line_type: Tipo de línea a crear

        Returns:
            int: Índice de la nueva línea
        """
        # Si no se especifica índice, usar línea activa
        if index is None:
            index = self.state_manager.get_active_index()
            if index is None:
                index = 0

        # Insertar debajo de la línea anterior
        if index > 0:
            return self.insert_line_below(index - 1, text, line_type)
        else:
            # Insertar al principio
            return self._insert_line_at_beginning(text, line_type)

    def _insert_line_at_beginning(self,
                                  text: str = "",
                                  line_type: MD_LINE_TYPE = MD_LINE_TYPE.TEXT) -> int:
        """Inserta línea al principio del documento."""
        next_line = self.md_lines[0] if len(self.md_lines) > 0 else None

        new_line = MDLine(
            md_text=text,
            prev_line=None,
            next_line=next_line,
            type=line_type,
            num_line=1
        )

        self.md_lines.insert(0, new_line)

        if next_line:
            next_line.prev_line = new_line

        # Actualizar números de línea
        for i in range(1, len(self.md_lines)):
            self.md_lines[i].num_line = i + 1

        # Shift de índices
        self.state_manager.shift_indices(start_index=0, delta=1)

        Logger.info("LineService: Line inserted at beginning")

        return 0

    def delete_line(self, index: Optional[int] = None) -> bool:
        """
        Elimina una línea del documento.

        Args:
            index: Índice de la línea a eliminar (None = línea activa)

        Returns:
            bool: True si se eliminó, False si no se pudo

        Side Effects:
            - Modifica md_lines
            - Actualiza referencias prev/next
            - Shift de índices en StateManager
        """
        # Si no se especifica índice, usar línea activa
        if index is None:
            index = self.state_manager.get_active_index()
            if index is None:
                Logger.warning("LineService: No line to delete")
                return False

        # No eliminar si es la última línea
        if len(self.md_lines) <= 1:
            Logger.warning("LineService: Cannot delete last line")
            return False

        # Validar índice
        if not self._is_valid_index(index):
            return False

        # Obtener líneas adyacentes
        prev_line = self.md_lines[index - 1] if index > 0 else None
        next_line = self.md_lines[index + 1] if index < len(self.md_lines) - 1 else None

        # Actualizar referencias
        if prev_line:
            prev_line.next_line = next_line
        if next_line:
            next_line.prev_line = prev_line

        # Eliminar de la lista
        deleted_line = self.md_lines.pop(index)

        # Actualizar números de línea
        for i in range(index, len(self.md_lines)):
            self.md_lines[i].num_line = i + 1

        # Shift de índices en StateManager
        self.state_manager.shift_indices(start_index=index + 1, delta=-1)

        # Remover estado de la línea eliminada
        self.state_manager.remove_state(index)

        Logger.info(f"LineService: Line {index} deleted")

        return True

    # ==========================================================================
    # Utilidades Privadas
    # ==========================================================================

    def _is_valid_index(self, index: int) -> bool:
        """Valida que un índice esté dentro del rango."""
        return 0 <= index < len(self.md_lines)

    def _is_editable(self, md_line: MDLine) -> bool:
        """Verifica si un tipo de línea es editable."""
        return md_line.type in self.EDITABLE_TYPES

    def _update_line_references(self, index: int):
        """
        Actualiza las referencias prev/next de una línea.

        Args:
            index: Índice de la línea a actualizar
        """
        if not self._is_valid_index(index):
            return

        current = self.md_lines[index]

        # Actualizar prev_line
        if index > 0:
            current.prev_line = self.md_lines[index - 1]
        else:
            current.prev_line = None

        # Actualizar next_line
        if index < len(self.md_lines) - 1:
            current.next_line = self.md_lines[index + 1]
        else:
            current.next_line = None

    # ==========================================================================
    # API Pública - Consultas
    # ==========================================================================

    def is_line_editable(self, index: int) -> bool:
        """
        Verifica si una línea puede editarse.

        Args:
            index: Índice de la línea

        Returns:
            bool: True si es editable
        """
        if not self._is_valid_index(index):
            return False

        return self._is_editable(self.md_lines[index])

    def get_line_type(self, index: int) -> Optional[MD_LINE_TYPE]:
        """
        Obtiene el tipo de una línea.

        Args:
            index: Índice de la línea

        Returns:
            MD_LINE_TYPE o None si índice inválido
        """
        if not self._is_valid_index(index):
            return None

        return self.md_lines[index].type

    def get_line_text(self, index: int) -> Optional[str]:
        """
        Obtiene el texto de una línea.

        Args:
            index: Índice de la línea

        Returns:
            str o None si índice inválido
        """
        if not self._is_valid_index(index):
            return None

        return self.md_lines[index].md_text

    def update_line_text(self, index: int, new_text: str) -> bool:
        """
        Actualiza el texto de una línea.

        Args:
            index: Índice de la línea
            new_text: Nuevo texto

        Returns:
            bool: True si se actualizó

        Side Effects:
            - Actualiza md_text
            - Actualiza tipo de línea (si cambia)
        """
        if not self._is_valid_index(index):
            return False

        md_line = self.md_lines[index]
        old_text = md_line.md_text

        # Actualizar texto
        md_line.md_text = new_text

        # Actualizar tipo
        old_type = md_line.type
        md_line.update_type()

        if old_type != md_line.type:
            Logger.info(
                f"LineService: Line {index} type changed {old_type} -> {md_line.type}"
            )

        Logger.debug(f"LineService: Line {index} text updated")

        return True

    def __repr__(self) -> str:
        """Representación legible del servicio."""
        return f"LineService(lines={len(self.md_lines)})"
