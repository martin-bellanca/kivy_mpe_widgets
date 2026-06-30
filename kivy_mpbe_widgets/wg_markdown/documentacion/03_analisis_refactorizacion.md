# Análisis para Refactorización de MDDocumentEditor

**Fecha:** 25/12/2024
**Objetivo:** Crear MDDocumentEditorV2 limpia con StateManager y Service Layer

---

## 📊 Análisis de Código Actual

### Archivo Original
- **Ubicación:** `kivy_mpe_widgets_prj/kivy_mpbe_widgets/wg_markdown/md_recycleview_document_editor.py`
- **Líneas:** 2,373 líneas
- **Clases:**
  - `SelectableRecycleBoxLayout` (100 líneas)
  - `MDDocumentEditor` (2,200+ líneas)

### Problemas Identificados

1. **Código Comentado Masivo**
   - ~30% del código está comentado
   - Funciones obsoletas que nunca se eliminaron
   - Dificulta la lectura y mantenimiento

2. **Estado Fragmentado**
   ```python
   # ❌ Estado disperso en múltiples variables
   self._active_index = -1
   self._selected_indexs = []
   self._mode_editor = False
   self._item_hotlight = None
   ```

3. **Lógica Mezclada**
   - UI y lógica de negocio juntas
   - Métodos de 100+ líneas
   - Difícil de testear

4. **Nomenclatura Inconsistente**
   - `_selected_indexs` (typo: "indexs")
   - Mezcla de español/inglés
   - `data_item`, `data`, `di_state`

---

## 🎯 Métodos Esenciales a Conservar

### Core - Inicialización
```python
✅ __init__()                    # Inicialización
✅ initialize_document()         # Resetear documento
✅ populate_from_md_lines()      # Cargar documento
```

### Core - Gestión de Data
```python
✅ apply_data_items()            # Aplicar filtros al data
✅ on_filter()                   # Callback de filtro
✅ on_filter_txt()               # Callback texto filtro
✅ on_filter_up()                # Callback incluir padres
```

### Utilidades - Conversión de Índices
```python
✅ index_from_data()             # Data dict -> index
✅ index_from_item()             # Widget -> index
✅ index_from_pos()              # Posición -> index
✅ item_from_index()             # Index -> widget
```

### Navegación y Scroll
```python
✅ scroll_to_index()             # Scroll a línea
✅ item_scroll_pos_y()           # Posición Y del item
✅ active_md_editor              # Property para editor activo
```

### Operaciones de Líneas (REFACTORIZAR con LineService)
```python
⚠️ append_line()                # Usar line_service.insert_line_below()
⚠️ insert_line()                # Usar line_service.insert_line_below()
⚠️ remove_line()                # Usar line_service.delete_line()
⚠️ move_line_to()               # Usar line_service.move_line_up/down()
```

### Selección/Activación (REFACTORIZAR con Services)
```python
❌ select_from_item()           # REEMPLAZAR con selection_service
❌ select_from_index()          # REEMPLAZAR con selection_service
❌ activate_from_item()         # REEMPLAZAR con line_service
❌ activate_from_index()        # REEMPLAZAR con line_service
❌ unactivate()                 # REEMPLAZAR con line_service
```

### Navegación por Títulos (REFACTORIZAR con NavigationService)
```python
❌ get_previus_data_title()    # REEMPLAZAR con navigation_service
❌ get_next_data_title()       # REEMPLAZAR con navigation_service
❌ active_to_previus_item()    # REEMPLAZAR con navigation_service
❌ active_to_next_item()       # REEMPLAZAR con navigation_service
```

### Eventos de Teclado
```python
✅ _on_keyboard_up()            # Manejo de teclado (simplificar)
```

---

## 🏗️ Arquitectura Nueva (MDDocumentEditorV2)

### Estructura de Clases

```
MDDocumentEditorV2 (RecycleView)
├── StateManager (gestión de estado)
├── LineService (operaciones de líneas)
├── SelectionService (selección)
├── NavigationService (navegación)
└── Métodos UI mínimos
```

### Variables de Instancia

```python
class MDDocumentEditorV2:
    # ✅ Gestión de Estado (NUEVA)
    state_manager: DocumentStateManager
    line_service: LineService
    selection_service: SelectionService
    navigation_service: NavigationService

    # ✅ Data del Documento
    _md_lines: List[MDLine]
    data_items: dict

    # ✅ Configuración
    filter: bool
    filter_txt: str
    filter_up: bool
    activate_background: bool

    # ✅ Referencias UI
    layout: SelectableRecycleBoxLayout
    undo_manager: UndoManager

    # ❌ ELIMINADAS (ahora en StateManager)
    # _active_index
    # _selected_indexs
    # _mode_editor
    # _item_hotlight
    # _cursor
```

### Métodos Nuevos/Refactorizados

```python
# ✅ NUEVOS
def _initialize_services()           # Crear servicios
def _on_line_state_changed(event)    # Callback StateManager
def _refresh_data_with_states()      # Actualizar RecycleView.data

# ✅ REFACTORIZADOS (usar servicios)
def handle_touch_left_up_event()     # Usar line_service.activate_line()
def handle_hotlight_event()          # Usar state_manager.set_hotlight()
def on_keyboard_arrow_down()         # Usar navigation_service
def on_keyboard_arrow_up()           # Usar navigation_service
def on_keyboard_enter()              # Usar line_service.insert_line_below()
def on_keyboard_delete()             # Usar line_service.delete_line()

# ✅ API PÚBLICA SIMPLIFICADA
def activate_line(index, enter_edit)
def select_lines(indices)
def navigate_next()
def navigate_previous()
def insert_line_at(index, text)
def delete_line(index)
```

---

## 📝 Plan de Migración

### Fase 1: Crear Esqueleto (30 min)
1. Crear `MDDocumentEditorV2` en mismo archivo
2. Renombrar clase antigua a `MDDocumentEditorLegacy`
3. Copiar imports necesarios
4. Definir `__init__` con StateManager y Services

### Fase 2: Migrar Core (1 hora)
1. `initialize_document()`
2. `populate_from_md_lines()` + integración StateManager
3. `apply_data_items()` (filtros)
4. Callbacks de filtro

### Fase 3: Migrar Utilidades (30 min)
1. Conversión de índices
2. Scroll
3. Properties

### Fase 4: Refactorizar con Services (2 horas)
1. Eventos de touch → LineService
2. Eventos de teclado → NavigationService
3. Selección → SelectionService
4. Operaciones de líneas → LineService

### Fase 5: Testing (1 hora)
1. Cargar documento
2. Activar líneas
3. Selección múltiple
4. Navegación por teclado
5. Insertar/eliminar líneas

### Fase 6: Cleanup (30 min)
1. Eliminar código comentado
2. Documentar métodos públicos
3. Validar con `state_manager.validate_invariants()`

---

## 🚫 Código a ELIMINAR Definitivamente

### Métodos Comentados (no copiar)
- `set_active_item()` (comentado)
- `set_select_item()` (comentado)
- `add_select_item()` (comentado)
- `handle_hotlight_event()` (comentado)
- `animate_range_selection()` (comentado)
- `update_data_index()` (comentado)
- `unactivate_from_item()` (comentado)
- ... y muchos más

### Variables Obsoletas
- `_active_index` → StateManager
- `_selected_indexs` → StateManager
- `_mode_editor` → StateManager
- `_item_hotlight` → StateManager
- `_cursor` → StateManager (cursor_pos)
- `_old_text_line` → UndoManager

---

## ✅ Checklist de Creación

### Estructura Base
- [ ] Crear clase `MDDocumentEditorV2`
- [ ] Agregar `StateManager` en `__init__`
- [ ] Agregar servicios en `__init__`
- [ ] Suscribirse a cambios de estado

### Core Functionality
- [ ] `initialize_document()`
- [ ] `populate_from_md_lines()` con StateManager
- [ ] `_refresh_data_with_states()`
- [ ] `_on_line_state_changed(event)`

### Eventos
- [ ] `handle_touch_left_up_event()` con LineService
- [ ] `handle_hotlight_event()` con StateManager
- [ ] `_on_keyboard_up()` con NavigationService

### Operaciones
- [ ] `activate_line()` público
- [ ] `select_lines()` público
- [ ] `navigate_next/previous()` públicos
- [ ] `insert_line_at()` público
- [ ] `delete_line()` público

### Utilidades
- [ ] Conversión de índices
- [ ] Scroll
- [ ] Validación de estado

### Testing
- [ ] Cargar documento de prueba
- [ ] Activar líneas por click
- [ ] Navegar con teclado
- [ ] Validar invariantes

---

## 📐 Métricas Esperadas

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Líneas totales | 2,373 | ~800 | -66% |
| Métodos | ~80 | ~30 | -62% |
| Código comentado | ~700 | 0 | -100% |
| Variables de estado | 7 | 0 | -100% |
| Complejidad ciclomática | ~20 | ~8 | -60% |

---

## 🎓 Beneficios Esperados

1. **Mantenibilidad**: Código limpio y fácil de entender
2. **Testabilidad**: Lógica separada de UI
3. **Confiabilidad**: Estado centralizado y validable
4. **Extensibilidad**: Fácil agregar nuevas features
5. **Performance**: Menos código = más rápido
6. **Documentación**: Código auto-documentado

---

**¡Listo para comenzar la refactorización!** 🚀
