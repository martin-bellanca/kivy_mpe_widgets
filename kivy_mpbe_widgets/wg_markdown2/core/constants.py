#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constants - Constantes y enumeraciones del módulo wg_markdown2

Este módulo contiene las constantes compartidas por todos los componentes
para evitar importaciones circulares.

Fecha: 2026-02-22
Autor: Martin Pablo Bellanca
"""

from enum import Enum
from helpers_mpbe.markdown_document import MD_LINE_TYPE as MLT
from kivy_mpbe_widgets.wg_markdown2.widgets.md_labels import (
    MDTextLabel, 
    MDSeparatorLabel, 
    MDHeadLabel, 
    MDTaskLabel, 
    MDToDoLabel, 
    MDTableLabel, 
    MDBlockQuoteLabel, 
    MDImageLabel, 
    MDCodeLabel
)


# =============================================================================
# MAPEO DE TIPOS DE LÍNEA A WIDGETS
# =============================================================================
WIDGETS_LABELS = {
    MLT.TEXT: MDTextLabel,
    MLT.TITLE: MDTextLabel,
    MLT.HEAD_TITLE: MDHeadLabel,
    MLT.UNDERLINE_TITLE: MDSeparatorLabel,
    MLT.SEPARATOR: MDSeparatorLabel,
    MLT.LIST: MDTextLabel,
    MLT.ORDER_LIST: MDTextLabel,
    MLT.TASK: MDTaskLabel,
    MLT.TODO: MDToDoLabel,
    # TODO: MDTableLabel no acepta md_text (su __init__ recibe html_table) y no
    # es instanciable desde MDDocumentLine. Mapeado a MDTextLabel hasta portarlo.
    MLT.TABLE: MDTextLabel,
    MLT.BLOCKQUOTE: MDBlockQuoteLabel,
    MLT.IMAGEN: MDImageLabel,
    MLT.CODE: MDCodeLabel,
    MLT.START_CODE: MDCodeLabel,
    MLT.END_CODE: MDCodeLabel,
}


# =============================================================================
# ENUMERACIONES
# =============================================================================
class LineGroup(Enum):
    """
    Grupos de visibilidad para una línea del documento.

    Valores:
        VISIBLE: Línea visible normalmente (default)
        HIDDEN: Línea oculta manualmente por el usuario
        FILTERED: Línea oculta por no coincidir con filtro de búsqueda
    """
    VISIBLE = 'visible'
    HIDDEN = 'hidden'
    FILTERED = 'filtered'


class AnimationType(Enum):
    """
    Tipos de animación para transiciones de estado.

    Valores:
        NONE: Sin animación (cambios inmediatos)
        FADE: Transición suave con opacidad (default, para clicks)
        SLIDE_UP: Desplazamiento hacia arriba (navegación con arrow up)
        SLIDE_DOWN: Desplazamiento hacia abajo (navegación con arrow down)
        EXPAND_UP: Expansión de selección hacia arriba (Shift+Up)
        EXPAND_DOWN: Expansión de selección hacia abajo (Shift+Down)
    """
    NONE = 'none'
    FADE = 'fade'
    SLIDE_UP = 'slide_up'
    SLIDE_DOWN = 'slide_down'
    EXPAND_UP = 'expand_up'
    EXPAND_DOWN = 'expand_down'
