# MDDocumentEditor V2 - Arquitectura

**Versión:** 2.0
**Basado en:** MDDocumentEditor_V5_Architecture.uxf
**Fecha:** 2026-01-31
**Estado:** Etapa I Completada

---

## 1. Visión General

MDDocumentEditor V2 es una reescritura completa del componente `wg_markdown` utilizando una arquitectura basada en **State Management centralizado** con reciclaje inteligente de widgets.

### Principios de Diseño

1. **Single Source of Truth:** `DocumentStateManager` es la única fuente de verdad para el estado de todas las líneas
2. **Inmutabilidad:** Los estados (`LineState`) son inmutables - cambios generan nuevas instancias
3. **Patrón Observer:** Los widgets observan cambios de estado y reaccionan automáticamente
4. **Operaciones Centralizadas:** Todas las modificaciones pasan por `DocumentOperations`
5. **Reciclaje Inteligente:** Los widgets se reciclan eficientemente basándose en el viewport

---

## 2. Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ARQUITECTURA V2                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────┐                                                        │
│  │    UI WIDGETS        │                                                        │
│  │    (Amarillo)        │                                                        │
│  ├──────────────────────┤    ┌──────────────────────┐    ┌───────────────────┐  │
│  │  MDDocumentEditor    │───▶│   DocumentOperations │───▶│DocumentStateManager│  │
│  │  - ScrollView        │    │      (Naranja)       │    │     (Verde)       │  │
│  │  - FocusBehavior     │    │                      │    │                   │  │
│  │  - Keyboard events   │    │  Activación          │    │  LineState[]      │  │
│  └──────────┬───────────┘    │  CRUD líneas         │    │  Observadores     │  │
│             │                │  Navegación          │    │  Eventos          │  │
│             │ contiene n     │  Selección           │    └─────────┬─────────┘  │
│             ▼                │  Filtrado            │              │            │
│  ┌──────────────────────┐    │  Hotlight            │              │ contiene n │
│  │MDDocumentLineEditor  │────┘                      │              ▼            │
│  │  - Mouse events      │                           │    ┌───────────────────┐  │
│  │  - Visual state      │◀──────────────────────────┼────│    LineState      │  │
│  └──────────────────────┘         observa           │    │   (Inmutable)     │  │
│                                                      │    │                   │  │
│                                                      │    │  md_line: MDLine  │  │
│                                                      │    │  active, editing  │  │
│  ┌──────────────────────────────────────────────────┐    │  selected, hotlight│  │
│  │               MODELO DE DATOS (Magenta)          │    │  visible, cursor  │  │
│  ├──────────────────────────────────────────────────┤    └─────────┬─────────┘  │
│  │                                                  │              │            │
│  │  ┌────────────┐         ┌─────────────────┐     │              │ referencia │
│  │  │ MDDocument │◀────────│ MD_LINE_TYPE    │     │              ▼            │
│  │  │            │         │   (Enum)        │     │    ┌───────────────────┐  │
│  │  │ md_lines[] │         │                 │     │    │     MDLine        │  │
│  │  │ load/save  │         │ TEXT, TITLE,    │     │    │  (helpers_mpbe)   │  │
│  │  └─────┬──────┘         │ LIST, CODE...   │     │    │                   │  │
│  │        │ contiene n     └─────────────────┘     │    │  md_text, type    │  │
│  │        ▼                                        │    │  prev/next_line   │  │
│  │  ┌────────────┐                                 │    └───────────────────┘  │
│  │  │  MDLine    │                                 │                            │
│  │  │            │                                 │                            │
│  │  └────────────┘                                 │                            │
│  └──────────────────────────────────────────────────┘                            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Componentes Principales

### 3.1 State Management (Verde)

#### DocumentStateManager
**Ubicación:** `core/state_manager.py`
**Responsabilidad:** Única fuente de verdad para el estado del documento

```python
class DocumentStateManager:
    """
    ÚNICA FUENTE DE VERDAD
    Gestiona todos los estados de líneas y emite eventos de cambio.
    """

    # Referencias
    md_document: MDDocument          # Referencia externa al documento
    _line_states: List[LineState]    # Estados de todas las líneas
    _active_index: Optional[int]     # Índice de línea activa
    _selected_indices: Set[int]      # Índices de líneas seleccionadas
    _observers: List[Callable]       # Observadores de eventos

    # Inicialización
    def set_document(md_document: MDDocument): ...
    def initialize_states(): ...
    def clear_all(): ...

    # Acceso a Estados
    def get_state(index) -> LineState: ...
    def get_line_state(index) -> LineState: ...
    def get_md_line(index) -> MDLine: ...
    def get_active_index() -> Optional[int]: ...
    def get_selected_indices() -> Set[int]: ...
    def get_line_count() -> int: ...

    # Modificación de Estados (emite eventos)
    def update_state(index, **changes): ...
    def activate_line(index, enter_edit, cursor_pos): ...
    def deactivate_line(index): ...
    def select_line(index, multi): ...
    def select_range(start, end): ...
    def clear_selection(): ...
    def toggle_selection(index): ...
    def set_hotlight(index, value): ...
    def set_visibility(index, visible): ...

    # Operaciones de Documento
    def insert_line(index, md_line) -> LineState: ...
    def remove_line(index): ...
    def move_line(from_index, to_index): ...
    def update_line_text(index, text): ...

    # Observadores
    def subscribe(observer: Callable): ...
    def unsubscribe(observer: Callable): ...
    def _emit_event(event: LineStateEvent): ...
```

#### LineState
**Ubicación:** `core/line_state.py`
**Responsabilidad:** Representación inmutable del estado de una línea

```python
@dataclass(frozen=True)
class LineState:
    """
    Estado inmutable de una línea del documento.
    Los cambios crean nuevas instancias via with_changes().
    """

    # Referencia a datos
    md_line: MDLine              # Referencia al modelo (no copia)
    index: int                   # Índice en el documento

    # Estado de UI
    selected: bool = False       # Línea seleccionada
    active: bool = False         # Línea activa (con foco)
    editing: bool = False        # Modo edición activo
    hotlight: bool = False       # Resaltado por hover
    visible: bool = True         # Visible (pasa filtro)
    cursor_pos: Tuple[int, int] = (0, 0)  # Posición del cursor

    # Métodos
    def with_changes(**kwargs) -> LineState: ...
    def get_md_text() -> str: ...        # Delegado a md_line
    def get_line_type() -> MD_LINE_TYPE: ...  # Delegado a md_line
```

#### LineStateEvent
**Ubicación:** `core/line_state.py`
**Responsabilidad:** Evento emitido cuando cambia un estado

```python
@dataclass
class LineStateEvent:
    """
    Evento emitido por StateManager cuando cambia el estado.
    """
    index: int                      # Índice de la línea
    line_state: LineState           # Nuevo estado
    old_state: LineState            # Estado anterior
    changed_attributes: Set[str]    # Atributos que cambiaron
    event_type: str                 # 'changed', 'added', 'removed'

    def is_activation_change() -> bool: ...
    def is_selection_change() -> bool: ...
    def is_content_change() -> bool: ...
```

---

### 3.2 Operations (Naranja)

#### DocumentOperations
**Ubicación:** `services/document_operations.py` (pendiente)
**Responsabilidad:** Único punto de entrada para modificar el estado

```python
class DocumentOperations:
    """
    Todas las modificaciones del estado pasan por esta clase.
    Los widgets NUNCA acceden directamente a StateManager para modificar.
    """

    state_manager: DocumentStateManager

    # Líneas - Activación
    def activate_line(index, enter_edit, cursor_pos) -> bool: ...
    def deactivate_current() -> bool: ...
    def toggle_edit_mode() -> bool: ...

    # Líneas - CRUD
    def insert_line_below(index, text) -> int: ...
    def insert_line_above(index, text) -> int: ...
    def delete_line(index) -> bool: ...
    def delete_selected_lines() -> int: ...

    # Líneas - Movimiento
    def move_line_up(index) -> bool: ...
    def move_line_down(index) -> bool: ...
    def move_selected_up() -> bool: ...
    def move_selected_down() -> bool: ...

    # Navegación
    def navigate_next() -> Optional[int]: ...
    def navigate_previous() -> Optional[int]: ...
    def navigate_to_next_title() -> Optional[int]: ...
    def navigate_to_parent_title() -> Optional[int]: ...

    # Selección
    def select_line(index, multi) -> bool: ...
    def select_range(start, end) -> int: ...
    def select_all() -> int: ...
    def clear_selection() -> int: ...

    # Hotlight
    def set_hotlight(index, value: bool): ...

    # Filtrado
    def filter_by_text(text, include_parents) -> int: ...
    def clear_filter() -> int: ...

    # Texto
    def update_line_text(index, text) -> bool: ...

    # Consultas
    def is_line_editable(index) -> bool: ...
    def can_delete_line(index) -> bool: ...
```

---

### 3.3 UI Widgets (Amarillo)

#### MDDocumentEditor
**Ubicación:** `widgets/md_document_editor.py`
**Responsabilidad:** Widget contenedor principal, gestión de teclado

```python
class MDDocumentEditor(FocusBehavior, ThemableBehavior, ScrollView):
    """
    Widget principal del editor.
    - Detecta eventos de teclado y los envía a operations
    - Observa eventos de StateManager para actualizaciones de lista
    """

    # Referencias
    state_manager: DocumentStateManager
    operations: DocumentOperations
    _line_widgets: List[MDDocumentLineEditor]

    # Layout
    content_layout: BoxLayout     # Contiene los widgets de línea

    # Teclado (detecta y envía a operations)
    def _on_key_down(key, modifiers): ...
    def _handle_arrow_up(modifiers): ...
    def _handle_arrow_down(modifiers): ...
    def _handle_enter(modifiers): ...
    def _handle_delete(): ...
    def _handle_backspace(): ...
    def _handle_tab(modifiers): ...
    def _handle_escape(): ...

    # Gestión de Widgets
    def create_line_widgets(): ...
    def add_line_widget(index) -> MDDocumentLineEditor: ...
    def remove_line_widget(index): ...
    def scroll_to_index(index): ...

    # Observer de StateManager
    def _on_line_state_event(event: LineStateEvent): ...
    def _on_line_added(event): ...
    def _on_line_removed(event): ...

    # API Pública
    def load_document(md_document: MDDocument): ...
    def get_widget_at_index(index) -> MDDocumentLineEditor: ...
```

#### MDDocumentLineEditor
**Ubicación:** `widgets/md_line_editor.py` (pendiente crear)
**Responsabilidad:** Widget individual de línea, gestión de mouse

```python
class MDDocumentLineEditor(ThemeWidget):
    """
    Widget para una línea del documento.
    - Detecta eventos de mouse y los envía a operations
    - Observa LineState para actualizaciones visuales
    """

    # Referencias
    line_state: LineState                # Observa cambios
    operations: DocumentOperations       # TODAS las acciones van aquí
    index: int

    # Estado Local (sincronizado con LineState)
    selected: bool
    active: bool
    editing: bool
    hotlight: bool

    # Sub-widgets
    wg_line_editor: MDLineEditor
    wg_number_line: Optional[MDDLNumberLine]

    # Eventos Detectados → Operations (TODOS)
    def _on_click(touch): ...            # → operations.activate_line()
    def _on_text_changed(text): ...      # → operations.update_line_text()
    def _on_mouse_enter(): ...           # → operations.set_hotlight(index, True)
    def _on_mouse_leave(): ...           # → operations.set_hotlight(index, False)

    # Observer de LineState
    def _on_line_state_changed(event: LineStateEvent): ...
    def _apply_state_changes(changed_attrs: Set[str]): ...

    # Visualización
    def show_editor(show, cursor): ...
    def update_selection_visual(selected, anim_type): ...
    def update_active_visual(active): ...
    def update_hotlight_visual(hotlight): ...
```

---

### 3.4 Modelo de Datos (Magenta)

> **Nota:** Estos componentes provienen de `helpers_mpbe` y no se modifican.

#### MDDocument
**Ubicación:** `helpers_mpbe/markdown_document/md_document.py`

```python
class MDDocument:
    """Modelo del documento Markdown completo."""

    document: str              # Contenido completo
    path_doc: str              # Ruta del directorio
    doc_name: str              # Nombre del archivo
    md_lines: List[MDLine]     # Lista de líneas

    def load_doc(path, name): ...
    def save_doc(): ...
    def separate_lines(): ...
    def join_lines(): ...
    def append_line(text): ...
    def insert_line(index, text): ...
    def remove_line(md_line): ...
```

#### MDLine
**Ubicación:** `helpers_mpbe/markdown_document/md_document.py`

```python
class MDLine:
    """Modelo de una línea Markdown con navegación linked-list."""

    md_text: str               # Texto markdown
    type: MD_LINE_TYPE         # Tipo de línea
    num_line: int              # Número de línea
    prev_line: MDLine          # Línea anterior (linked list)
    next_line: MDLine          # Línea siguiente (linked list)

    def get_markup_text() -> str: ...
    def update_type(): ...
    def get_title_level() -> int: ...

    # Navegación
    def get_title_parent() -> MDLine: ...
    def get_title_next() -> MDLine: ...
    def get_list_parent() -> MDLine: ...
```

#### MD_LINE_TYPE
**Ubicación:** `helpers_mpbe/markdown_document/__init__.py`

```python
class MD_LINE_TYPE(Enum):
    TEXT = 0              # Texto normal
    TITLE = 1             # Título con # (# Title)
    HEAD_TITLE = 2        # Título subrayado
    UNDERLINE_TITLE = 3   # Línea de subrayado
    SEPARATOR = 4         # Separador (---)
    LIST = 5              # Lista desordenada (- Item)
    ORDER_LIST = 6        # Lista ordenada (1. Item)
    TASK = 7              # Tarea (- [ ] Task)
    TODO = 8              # TODO (- [x] Done)
    TABLE = 9             # Tabla (| col |)
    BLOCKQUOTE = 10       # Cita (> Text)
    IMAGEN = 11           # Imagen (![alt](url))
    CODE = 12             # Bloque de código
    START_CODE = 13       # Inicio código (```)
    END_CODE = 14         # Fin código (```)
```

---

## 4. Flujos de Datos

### 4.1 Click en Línea

```
1. MDDocumentLineEditor._on_click(touch)
      │
      ▼
2. operations.activate_line(index, cursor_pos)
      │
      ▼
3. state_manager.activate_line(index, ...)
      │
      ├── Desactiva línea anterior (si existe)
      └── Activa nueva línea
      │
      ▼
4. state_manager._emit_event(LineStateEvent)
      │
      ▼
5. MDDocumentLineEditor._on_line_state_changed()
      │
      ▼
6. Widget actualiza visualización
```

### 4.2 Tecla Enter (Nueva Línea)

```
1. MDDocumentEditor._handle_enter()
      │
      ▼
2. operations.insert_line_below(active_index, "")
      │
      ▼
3. state_manager.insert_line(index, new_md_line)
      │
      ├── Crea nuevo LineState
      └── Recalcula índices
      │
      ▼
4. state_manager._emit_event(type='added')
      │
      ▼
5. MDDocumentEditor._on_line_added()
      │
      ▼
6. Crea nuevo MDDocumentLineEditor
```

### 4.3 Hotlight (Mouse Enter/Leave)

```
1. MDDocumentLineEditor._on_mouse_enter()
      │
      ▼
2. operations.set_hotlight(index, True)
      │
      ▼
3. state_manager.set_hotlight(index, True)
      │
      ▼
4. state_manager._emit_event(LineStateEvent)
      │
      ▼
5. MDDocumentLineEditor._on_line_state_changed()
      │
      ▼
6. widget.update_hotlight_visual(True)
```

### 4.4 Cambio de Texto

```
1. MDDocumentLineEditor._on_text_changed(new_text)
      │
      ▼
2. operations.update_line_text(index, new_text)
      │
      ▼
3. state_manager.update_line_text(index, text)
      │
      ├── md_line.md_text = text (actualiza MDLine)
      └── md_line.update_type() (detecta nuevo tipo)
```

### 4.5 Filtrar por Texto

```
1. InputSearchOrFilter.filter_toggle → state='toggled'
      │
      ▼
2. App._on_filter_state_change(instance, state)
      │
      ▼
3. operations.filter_by_text(text, include_parents)
      │
      ▼
4. Para cada línea:
      ├── coincide: state_manager.set_visibility(index, True)
      └── no coincide: state_manager.set_visibility(index, False)
      │
      ▼
5. state_manager._emit_event(LineStateEvent)
      │
      ▼
6. MDDocumentLineEditor._on_line_state_changed()
      │
      ▼
7. widget.visible = line_state.visible
```

### 4.6 Limpiar Filtro

```
1. InputSearchOrFilter.filter_toggle → state='untoggled'
      │
      ▼
2. App._on_filter_state_change(instance, state)
      │
      ▼
3. operations.clear_filter()
      │
      ▼
4. Para cada línea: state_manager.set_visibility(index, True)
      │
      ▼
5. state_manager._emit_event(LineStateEvent)
      │
      ▼
6. widget.visible = True (muestra todos)
```

### 4.7 Búsqueda (Navegar a Coincidencia)

```
1. InputSearchOrFilter.search_button → on_click
      │
      ▼
2. dispatch('on_search', text)
      │
      ▼
3. App._on_search_event(instance, text)
      │
      ▼
4. operations.search_and_navigate(text, direction=1)
      │
      ├── Buscar siguiente línea con text desde active_index
      ├── state_manager.activate_line(found_index)
      └── MDDocumentEditor.scroll_to_index(found_index)
      │
      ▼
5. state_manager._emit_event(LineStateEvent)
      │
      ▼
6. Widget activa + scroll visible
```

---

## 5. Estructura de Directorios

```
wg_markdown2/
├── __init__.py                    # Exports públicos
├── README.md                      # Documentación general
│
├── core/                          # Componentes centrales
│   ├── __init__.py
│   ├── line_state.py              # LineState, LineStateEvent [COMPLETO]
│   ├── state_manager.py           # DocumentStateManager [COMPLETO]
│   └── recycle_box_layout.py      # RecycleBoxLayout [COMPLETO]
│
├── widgets/                       # Widgets de UI
│   ├── __init__.py
│   ├── md_document_editor.py      # MDDocumentEditor [COMPLETO]
│   └── md_line_editor.py          # MDDocumentLineEditor [PENDIENTE]
│
├── services/                      # Servicios y operaciones
│   ├── __init__.py
│   └── document_operations.py     # DocumentOperations [PENDIENTE]
│
├── tests/                         # Tests y app de prueba
│   ├── __init__.py
│   ├── test_app.py                # App de prueba gráfica [COMPLETO]
│   ├── test_state_manager.py      # Tests unitarios [COMPLETO]
│   ├── test_document.md           # Documento de prueba [COMPLETO]
│   └── run_test.sh                # Script de ejecución
│
├── documentacion/                 # Documentación técnica
│   ├── MDDocumentEditor_V2_Arquitectura.md    # Este documento
│   ├── MDDocumentEditor_V5_Architecture.uxf   # Diagrama UMLet original
│   └── Superados/                 # Documentos históricos
│
└── ia_pronts/                     # Prompts de IA
    ├── 1_Configuracion_del_modulo.txt
    └── 1_Etapa 1
```

---

## 6. Estado Actual de Implementación

### Etapa I - COMPLETADA

| Componente | Archivo | Líneas | Estado |
|------------|---------|--------|--------|
| LineState | `core/line_state.py` | 232 | COMPLETO |
| StateManager | `core/state_manager.py` | 404 | COMPLETO |
| RecycleBoxLayout | `core/recycle_box_layout.py` | 468 | COMPLETO |
| MDDocumentEditor | `widgets/md_document_editor.py` | 394 | COMPLETO |
| Test App | `tests/test_app.py` | 283 | COMPLETO |
| Test StateManager | `tests/test_state_manager.py` | 360 | COMPLETO |

**Total código productivo Etapa I:** ~1,945 líneas

### Etapa II - PENDIENTE

| Componente | Archivo | Estado |
|------------|---------|--------|
| DocumentOperations | `services/document_operations.py` | PENDIENTE |
| MDDocumentLineEditor | `widgets/md_line_editor.py` | PENDIENTE (usar de wg_markdown) |
| Navegación teclado | `widgets/md_document_editor.py` | PENDIENTE |
| Filtros | `services/filter_service.py` | PENDIENTE |
| Búsqueda | `services/search_service.py` | PENDIENTE |
| Animaciones | varios | PENDIENTE |

---

## 7. Principio Clave

> **TODOS los eventos de UI pasan por DocumentOperations**

```
• click       → operations.activate_line()
• text_changed → operations.update_line_text()
• mouse_enter  → operations.set_hotlight(True)
• mouse_leave  → operations.set_hotlight(False)
• key_enter    → operations.insert_line_below()
• key_delete   → operations.delete_line()
• key_arrow    → operations.navigate_next/prev()
```

**DocumentOperations es el ÚNICO punto de entrada para modificar el estado.**

**Widgets NUNCA acceden directamente a StateManager para modificar.**

---

## 8. Notas de Diseño

### 8.1 Observaciones

1. **MDDocumentLineEditor** gestiona eventos del mouse hacia DocumentOperations
2. **MDDocumentEditor** gestiona eventos del teclado hacia DocumentOperations
3. **MDDocumentEditor** observa eventos de modificación de lista en DocumentStateManager
4. **MDDocumentLineEditor** observa eventos de estado de LineState

### 8.2 Reciclaje de Widgets

- Widgets visibles: NO se reciclan
- Widgets fuera de viewport: SÍ se reciclan
- Widget activo: NUNCA se recicla (preserva estado de edición)
- Pool de reciclaje eficiente

### 8.3 Alturas No Uniformes

Estimación por tipo de línea:
- TITLE: 40px
- HEAD_TITLE: 45px
- TEXT: 25px
- LIST/ORDER_LIST: 28px
- TASK/TODO: 30px
- CODE: 22px
- BLOCKQUOTE: 30px
- TABLE: 35px
- SEPARATOR: 20px
- IMAGEN: 100px

---

## 9. Dependencias Externas

### De `helpers_mpbe`:
- `MDDocument` - Modelo de documento
- `MDLine` - Modelo de línea con linked list
- `MD_LINE_TYPE` - Enum de tipos de línea

### De `kivy_mpbe_widgets`:
- `ThemableBehavior`, `Theme` - Sistema de temas
- `MDDocumentLineEditor` - Widget de línea individual (de `wg_markdown.md_line_editors_v2`)

### De Kivy:
- `ScrollView`, `BoxLayout`, `Widget`
- `FocusBehavior`
- `ObjectProperty`, `StringProperty`
- `Logger`, `Clock`, `Config`

---

## 10. Próximos Pasos (Etapa II)

1. **Crear DocumentOperations** (`services/document_operations.py`)
   - Implementar todos los métodos de activación, CRUD, navegación
   - Conectar con StateManager

2. **Integrar MDDocumentLineEditor**
   - Adaptar o crear widget de línea individual
   - Conectar eventos de mouse con operations

3. **Implementar Navegación con Teclado**
   - Arrow Up/Down
   - Page Up/Down
   - Home/End
   - Enter (nueva línea)
   - Delete/Backspace

4. **Implementar Modo Edición**
   - Activar TextInput en línea
   - Gestionar cursor
   - Sincronizar cambios de texto

5. **Implementar Filtros y Búsqueda**
   - Crear servicios de filtro y búsqueda
   - Conectar con UI existente

6. **Agregar Animaciones**
   - Transiciones de activación
   - Slide up/down
   - Fade in/out

---

## 11. Leyenda de Colores (del diagrama UML)

| Color | Significado |
|-------|-------------|
| 🟢 Verde | State Management (StateManager, LineState, Event) |
| 🟠 Naranja | Operaciones (DocumentOperations) |
| 🟡 Amarillo | Widgets UI (MDDocumentEditor, MDDocumentLineEditor) |
| 🟣 Magenta | Modelo de Datos (MDDocument, MDLine) |
| 🔵 Cyan | Enumeraciones (MD_LINE_TYPE) |
