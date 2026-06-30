#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core Package - Componentes centrales de wg_markdown2

Exporta:
    - LineState: Estado mutable de una línea (EventDispatcher)
    - LineGroup: Constantes para valores de group
    - AnimationType: Constantes para tipos de animación
    - DocumentStateManager: Gestor centralizado de estados (EventDispatcher)
    - LineStateEvent: Evento estructural (add/remove/move)
    - EventType: Tipos de evento estructural
    - ListBoxLayout: Layout simple sin reciclaje de widgets
"""

from .line_state import (
    LineState,
    LineGroup,
    AnimationType,
)
from .state_manager import (
    DocumentStateManager,
    LineStateEvent,
    EventType,
)
# from .list_box_layout import ListBoxLayout

__all__ = [
    # Clases de estado
    'LineState',
    'DocumentStateManager',
    'LineStateEvent',
    # Constantes (Enums)
    'LineGroup',
    'AnimationType',
    'EventType',
    # Layouts

]
