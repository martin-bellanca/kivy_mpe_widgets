#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  services/__init__.py
#
#  Service Layer para KV Markdown Editor
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
Service Layer Package

Contiene servicios que encapsulan la lógica de negocio,
separándola de la capa de presentación (UI).

Servicios disponibles:
- LineService: Gestión de líneas (activación, edición, movimiento)
- SelectionService: Gestión de selección de líneas
- NavigationService: Navegación por el documento
- FilterService: Filtrado de líneas por texto, tipo y criterios personalizados
"""

from .line_service import LineService
from .selection_service import SelectionService
from .navigation_service import NavigationService
from .filter_service import FilterService

__all__ = [
    'LineService',
    'SelectionService',
    'NavigationService',
    'FilterService'
]
