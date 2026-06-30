#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  run_service_tests.py
#
#  Script para ejecutar todos los tests de servicios
#
#  Created on 25/12/2024
#  @author: mpbe
#

"""
Test Runner para Service Layer

Ejecuta todos los tests de servicios:
- test_line_service.py
- test_selection_service.py
- test_navigation_service.py

Configura correctamente el PYTHONPATH para acceder a
helpers_mpbe y kivy_mpbe_widgets.
"""

import sys
import unittest
from pathlib import Path

# Configurar paths
project_root = Path(__file__).parent.parent.parent
helpers_root = Path.home() / 'Documentos' / 'Programacion' / 'Programacion_lin' / 'Visual_Studio_Code' / 'helpers_mpbe_prj'
widgets_root = Path.home() / 'Documentos' / 'Programacion' / 'Programacion_lin' / 'Visual_Studio_Code' / 'kivy_mpe_widgets_prj'

# Agregar a sys.path
for path in [project_root, helpers_root, widgets_root]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Importar módulos de test
from test_line_service import (
    TestLineServiceActivation,
    TestLineServiceMovement,
    TestLineServiceInsertion,
    TestLineServiceDeletion,
    TestLineServiceQueries,
    TestLineServiceEdgeCase,
)

from test_selection_service import (
    TestSelectionServiceSingle,
    TestSelectionServiceMulti,
    TestSelectionServiceRange,
    TestSelectionServiceToggle,
    TestSelectionServiceDeselection,
    TestSelectionServiceSmart,
    TestSelectionServiceExtension,
    TestSelectionServiceQueries,
    TestSelectionServiceEdgeCases,
)

from test_navigation_service import (
    TestNavigationServiceSequential,
    TestNavigationServiceTitles,
    TestNavigationServiceByType,
    TestNavigationServiceSearch,
    TestNavigationServiceVisibility,
    TestNavigationServiceUtilities,
    TestNavigationServiceEdgeCases,
)

from test_filter_service import (
    TestFilterByText,
    TestFilterWithParents,
    TestFilterByType,
    TestFilterByPredicate,
    TestApplyFilter,
    TestPresetFilters,
    TestFilterQueries,
)


def run_all_tests():
    """Ejecuta todos los tests de servicios."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # ===== LineService Tests =====
    print("\n" + "=" * 80)
    print("LINESERVICE TESTS")
    print("=" * 80)
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceActivation))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceMovement))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceInsertion))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceDeletion))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceQueries))
    suite.addTests(loader.loadTestsFromTestCase(TestLineServiceEdgeCase))

    # ===== SelectionService Tests =====
    print("\n" + "=" * 80)
    print("SELECTIONSERVICE TESTS")
    print("=" * 80)
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceSingle))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceMulti))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceRange))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceToggle))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceDeselection))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceSmart))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceExtension))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceQueries))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionServiceEdgeCases))

    # ===== NavigationService Tests =====
    print("\n" + "=" * 80)
    print("NAVIGATIONSERVICE TESTS")
    print("=" * 80)
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceSequential))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceTitles))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceByType))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceSearch))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceVisibility))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationServiceEdgeCases))

    # ===== FilterService Tests (FASE 3) =====
    print("\n" + "=" * 80)
    print("FILTERSERVICE TESTS (FASE 3)")
    print("=" * 80)
    suite.addTests(loader.loadTestsFromTestCase(TestFilterByText))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterWithParents))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterByType))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterByPredicate))
    suite.addTests(loader.loadTestsFromTestCase(TestApplyFilter))
    suite.addTests(loader.loadTestsFromTestCase(TestPresetFilters))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterQueries))

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallidos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print("=" * 80)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
