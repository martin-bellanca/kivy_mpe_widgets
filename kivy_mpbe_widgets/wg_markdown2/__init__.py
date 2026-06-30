#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wg_markdown2 - Editor de Markdown con RecycleBoxLayout personalizado

Componentes principales:
- MDDocumentEditor: Widget principal (ScrollView)
- RecycleBoxLayout: Layout con reciclaje inteligente
- StateManager: Gestión de estados y lógica
- LineState: Estado inmutable de líneas

Versión: Etapa I - Funcionalidad básica
Fecha: 2026-01-12
Autor: Martin Pablo Bellanca
"""

# Imports del módulo --------------------------------------------------------------------
from .widgets.md_document_editor import MDDocumentEditor
from .core.line_state import LineState
from .core.state_manager import DocumentStateManager
from .core.recycle_box_layout import RecycleBoxLayout
from .core.constants import WIDGETS_LABELS, LineGroup, AnimationType

__version__ = '0.1.0-etapa1'
__all__ = [
    'MDDocumentEditor',
    'LineState',
    'DocumentStateManager',
    'RecycleBoxLayout',
    'WIDGETS_LABELS',
    'LineGroup',
    'AnimationType',
]