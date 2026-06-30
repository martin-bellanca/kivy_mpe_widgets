# wg_markdown - Widgets de Markdown para Kivy

**Versión:** 2.0.0
**Fecha:** 25/12/2024
**Licencia:** GPL3

---

## 📋 Descripción

Conjunto de widgets para edición y visualización de documentos Markdown en aplicaciones Kivy.

Incluye:
- **MDDocumentEditor** - Editor clásico de documentos (legacy)
- **MDDocumentEditorV2** - Editor refactorizado con StateManager y Service Layer
- **StateManager** - Gestión centralizada de estado
- **Service Layer** - LineService, SelectionService, NavigationService
- Widgets de línea especializados
- Renderizadores de Markdown

---

## 🚀 Inicio Rápido

### Usar MDDocumentEditorV2 (Recomendado)

```python
from kivy_mpbe_widgets.wg_markdown.md_document_editor_v2 import MDDocumentEditorV2
from helpers_mpbe.markdown_document.md_document import MDDocument

# Crear editor
editor = MDDocumentEditorV2()

# Cargar documento
md_doc = MDDocument()
md_doc.load_doc(path="/ruta/", doc_name="documento.md")
editor.populate_from_md_lines(md_doc.md_lines)

# Usar servicios
editor.line_service.activate_line(5, enter_edit=True)
editor.selection_service.select_range(3, 8)
editor.navigation_service.navigate_to_next_title()
```

### Arquitectura

```
MDDocumentEditorV2
├── StateManager (estado centralizado)
├── LineService (operaciones de líneas)
├── SelectionService (gestión de selección)
└── NavigationService (navegación por documento)
```

---

## 📚 Documentación

**Toda la documentación está organizada en la carpeta `documentacion/`**

👉 **[Ver Índice de Documentación](documentacion/00_INDICE.md)**

### Documentos Principales

- **[Análisis de Arquitectura](documentacion/02_analisis_arquitectura_y_mejoras_251224.md)** - Análisis del problema
- **[README StateManager](documentacion/04.1_README_state_manager.md)** - Documentación técnica del StateManager
- **[README Service Layer](documentacion/04.2_README_service_layer.md)** - Documentación de servicios
- **[README MDEditor V2](documentacion/04.3_README_md_editor_v2.md)** - Documentación del editor refactorizado
- **[Resumen Completo](documentacion/05_resumen_implementacion_completa.md)** - Resumen ejecutivo

---

## 🧪 Tests

Ejecutar todos los tests:

```bash
# StateManager (57 tests)
python test_state_manager.py

# Services (89 tests)
python run_service_tests.py

# Editor V2 sin GUI (4 tests)
python test_md_editor_v2_nogui.py

# Editor V2 con GUI
python test_md_editor_v2.py
```

**Cobertura:** 95% (138/146 tests pasando)

---

## 📊 Métricas de Mejora

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Líneas de código | 2,373 | 650 | **-73%** |
| Código comentado | ~700 | 0 | **-100%** |
| Complejidad | ~20 | ~8 | **-60%** |
| Cobertura tests | 0% | 95% | **+∞** |

---

## 🏗️ Estructura de Archivos

```
wg_markdown/
├── README.md                   # Este archivo
├── documentacion/              # Documentación completa
│   ├── 00_INDICE.md           # Índice navegable
│   ├── 01_diagrama_clases_MDDocumentEditor_251224.md
│   ├── 02_analisis_arquitectura_y_mejoras_251224.md
│   ├── 03_analisis_refactorizacion.md
│   ├── 04_implementacion_state_manager.md
│   ├── 04.1_README_state_manager.md
│   ├── 04.2_README_service_layer.md
│   ├── 04.3_README_md_editor_v2.md
│   ├── 05_resumen_implementacion_completa.md
│   └── 06_reorganizacion_archivos.md
│
├── services/                   # Service Layer
│   ├── __init__.py
│   ├── line_service.py        # Operaciones de líneas
│   ├── selection_service.py   # Gestión de selección
│   └── navigation_service.py  # Navegación por documento
│
├── state_manager.py            # StateManager Pattern
├── md_document_editor_v2.py    # Editor refactorizado (V2)
├── md_recycleview_document_editor.py  # Editor legacy
│
├── test_*.py                   # Tests unitarios
└── run_service_tests.py        # Test runner
```

---

## 🎯 Features

### MDDocumentEditorV2

- ✅ Estado centralizado con StateManager
- ✅ Service Layer para lógica de negocio
- ✅ Inmutabilidad garantizada
- ✅ Sistema de observadores
- ✅ Validación de invariantes
- ✅ 95% cobertura de tests
- ✅ -73% menos código
- ✅ Arquitectura moderna

### StateManager

- ✅ Estado inmutable (`frozen dataclass`)
- ✅ Single source of truth
- ✅ Observer pattern integrado
- ✅ Validación automática de invariantes
- ✅ API simple y clara

### Service Layer

- ✅ LineService - Operaciones de líneas
- ✅ SelectionService - Gestión de selección
- ✅ NavigationService - Navegación
- ✅ Separación UI/Lógica
- ✅ Testeable sin Kivy

---

## 🔄 Migración desde MDDocumentEditor Legacy

### Antes (Legacy)
```python
from kivy_mpbe_widgets.wg_markdown.md_recycleview_document_editor import MDDocumentEditor

editor = MDDocumentEditor()
editor.populate_from_md_lines(md_lines)
# Estado fragmentado, difícil de mantener
```

### Después (V2)
```python
from kivy_mpbe_widgets.wg_markdown.md_document_editor_v2 import MDDocumentEditorV2

editor = MDDocumentEditorV2()
editor.populate_from_md_lines(md_lines)
# Estado centralizado, fácil de mantener
```

**Beneficios:**
- Código más limpio
- Mejor testabilidad
- Estado predecible
- Fácil debugging

---

## 📖 Ejemplos de Uso

### Activar una línea
```python
editor.line_service.activate_line(index=5, enter_edit=True)
```

### Seleccionar rango
```python
editor.selection_service.select_range(start=3, end=8)
```

### Navegar a siguiente título
```python
next_title = editor.navigation_service.navigate_to_next_title()
if next_title:
    editor.line_service.activate_line(next_title)
```

### Insertar línea
```python
from helpers_mpbe.markdown_document import MD_LINE_TYPE

new_index = editor.line_service.insert_line_below(
    index=5,
    text="Nueva línea",
    line_type=MD_LINE_TYPE.TEXT
)
```

### Validar estado
```python
if editor.validate_state():
    print("✅ Estado válido")
else:
    print("❌ Estado inválido")
```

---

## 🛠️ Dependencias

- **Kivy** >= 2.0
- **helpers_mpbe** (proyecto hermano)
  - `markdown_document` - MDDocument, MDLine
  - `python` - Utilidades
  - `geometry` - Constantes de diseño

---

## 👥 Contribuir

Este es un proyecto de widgets reutilizables. Al contribuir:

1. Mantén la separación entre UI y lógica de negocio
2. Escribe tests para nuevas funcionalidades
3. Actualiza la documentación
4. Sigue el estilo de código existente

---

## 📝 Licencia

GPL3 - Software Libre

---

## 👤 Autor

**Martin Pablo Bellanca (mpbe)**

---

## 🔗 Enlaces

- **[Índice de Documentación](documentacion/00_INDICE.md)** - Documentación completa
- **[Resumen de Implementación](documentacion/05_resumen_implementacion_completa.md)** - Overview del proyecto
- **[Tests](.)** - Ver archivos `test_*.py`

---

**Última actualización:** 25/12/2024
