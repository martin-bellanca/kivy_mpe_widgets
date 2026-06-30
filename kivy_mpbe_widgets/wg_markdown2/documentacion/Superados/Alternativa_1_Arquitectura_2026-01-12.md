# Alternativa 1: Arquitectura con RecycleBoxLayout Personalizado

**Fecha:** 2026-01-12
**Versión:** 1.0
**Estado:** Diseño

---

## Resumen Ejecutivo

Esta alternativa propone un **RecycleBoxLayout personalizado** que reemplaza RecycleView estándar de Kivy. La solución combina lo mejor de ambos mundos:

✅ **Reciclaje eficiente** de widgets (como RecycleView)
✅ **Control total** sobre cuándo y cómo reciclar
✅ **Estado persistente** en widgets visibles
✅ **Interacciones directas** sin refresh_view_attrs()
✅ **Alturas no uniformes** soportadas nativamente

---

## Arquitectura General

```
┌──────────────────────────────────────────────────────────────┐
│                  MDDocumentEditor                            │
│        (FocusBehavior, ThemableBehavior, ScrollView)         │
│                                                              │
│  Rol: Coordinador principal                                 │
│  - Maneja eventos de usuario (teclado, mouse, scroll)       │
│  - Coordina StateManager y RecycleBoxLayout                  │
│  - Mantiene referencia al widget activo                      │
│  - Aplica tema global                                        │
│                                                              │
│  Propiedades:                                                │
│    - state_manager: StateManager                             │
│    - recycle_layout: RecycleBoxLayout                        │
│    - active_line_widget: MDDocumentLineEditor                │
│                                                              │
│  Eventos principales:                                        │
│    - on_scroll() → _refresh_visible_widgets()                │
│    - on_keyboard() → navegación con flechas                  │
│    - on_page_up/down() → scroll de página                    │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ contiene
                         ↓
┌──────────────────────────────────────────────────────────────┐
│               RecycleBoxLayout                               │
│                  (BoxLayout vertical)                        │
│                                                              │
│  Rol: Reciclaje inteligente de widgets                      │
│  - Mantiene pool de widgets activos (visibles)              │
│  - Mantiene pool de widgets reciclables                     │
│  - Usa placeholders para líneas no renderizadas             │
│  - Inserta/remueve widgets según viewport                   │
│                                                              │
│  Propiedades:                                                │
│    - state_manager: StateManager (referencia)                │
│    - active_widgets: Dict[int, MDDocumentLineEditor]         │
│    - recycled_pool: List[MDDocumentLineEditor]               │
│    - placeholders: Dict[int, Widget]                         │
│    - last_visible_indices: List[int]                         │
│                                                              │
│  Métodos principales:                                        │
│    - update_visible_range(visible_indices)                   │
│        ↑ FUNCIÓN ÚNICA de actualización                      │
│    - get_widget(index) → Widget | None                       │
│    - _create_or_reuse_widget_at_index(index)                 │
│    - _recycle_widget_at_index(index)                         │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ consulta para decidir qué mostrar
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                    StateManager                              │
│                (Lógica de negocio)                           │
│                                                              │
│  Rol: Single Source of Truth + Lógica                       │
│  - Almacena TODOS los LineState (visible + ocultos)         │
│  - Calcula qué líneas están en viewport                     │
│  - Aplica filtros y búsquedas                               │
│  - Gestiona geometría (posiciones Y, alturas)               │
│  - Operaciones de documento (insert, delete, move)          │
│                                                              │
│  Propiedades:                                                │
│    - line_states: Dict[int, LineState]                       │
│    - visible_indices: Set[int]                               │
│    - filtered_indices: Set[int]                              │
│    - search_matches: Set[int]                                │
│    - total_height: float                                     │
│    - line_y_positions: Dict[int, float]                      │
│    - viewport_buffer: int = 10                               │
│                                                              │
│  Métodos principales:                                        │
│    - load_document(md_lines)                                 │
│    - get_visible_in_viewport(scroll_y, viewport_height)      │
│        → List[int] ← CÁLCULO CLAVE                           │
│    - apply_filter(filter_text)                               │
│    - apply_search(search_text)                               │
│    - insert_line(index, md_line)                             │
│    - delete_line(index)                                      │
│    - update_line_height(index, new_height)                   │
│    - _recalculate_geometry()                                 │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ contiene
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                     LineState                                │
│               (dataclass frozen=True)                        │
│                                                              │
│  Rol: Estado inmutable de una línea                         │
│                                                              │
│  # Identificación                                            │
│  index: int                    - Índice en documento         │
│  md_line: MDLine               - Datos de la línea           │
│                                                              │
│  # Estados de UI                                             │
│  active: bool = False          - Línea activa                │
│  editing: bool = False         - En modo edición             │
│  selected: bool = False        - Seleccionada                │
│  hotlight: bool = False        - Mouse encima                │
│                                                              │
│  # Visibilidad y grupos                                      │
│  visible: bool = True          - ¿Pasa el filtro?            │
│  matched_search: bool = False  - ¿Coincide búsqueda?         │
│  group: str = 'visible'        - 'visible'|'hidden'|'filtered'│
│                                                              │
│  # Geometría (para reciclaje)                                │
│  height: float = 30.0          - Altura en pixels            │
│  y_position: float = 0.0       - Posición Y absoluta         │
│                                                              │
│  # Animaciones                                               │
│  cursor_pos: Tuple[int, int] = (0, 0)                        │
│  anim_type: str = 'fade'                                     │
│                                                              │
│  # Sub-widgets                                               │
│  show_number_line: bool = True                               │
│  show_tree: bool = False                                     │
│  show_infobar: bool = False                                  │
│  alpha_background: float = 0.0                               │
│                                                              │
│  Métodos:                                                    │
│    - with_changes(**kwargs) → LineState nuevo                │
└──────────────────────────────────────────────────────────────┘
```

---

## Componentes Detallados

### 1. LineState (Datos Inmutables)

**Características:**
- `frozen=True` → Inmutable, thread-safe
- Contiene MDLine + estado UI + geometría
- Método `with_changes()` para crear nuevas versiones
- Campo `group` para clasificación: 'visible', 'hidden', 'filtered'

**Geometría:**
- `height`: Altura del widget (NO uniforme)
- `y_position`: Posición Y absoluta en el layout completo
- Se recalcula después de insert/delete/filtro

**Por qué inmutable:**
- Previene modificaciones accidentales
- Facilita detección de cambios
- Permite cache seguro
- Simplifica debugging

### 2. StateManager (Lógica Central)

**Responsabilidades principales:**

#### A) Almacenamiento
```python
line_states: Dict[int, LineState]  # TODAS las líneas
visible_indices: Set[int]           # Índices visibles (pasan filtro)
filtered_indices: Set[int]          # Índices ocultos (no pasan filtro)
```

#### B) Geometría
```python
total_height: float                 # Altura total de líneas visibles
line_y_positions: Dict[int, float]  # Posición Y de cada línea visible
```

**Cálculo de alturas:**
- Estimación inicial basada en tipo de línea y longitud
- Actualización cuando widget se renderiza y se conoce altura real
- `_recalculate_geometry()` reconstruye todas las posiciones Y

#### C) Viewport
```python
def get_visible_in_viewport(scroll_y, viewport_height) -> List[int]:
    """
    FUNCIÓN CLAVE: Calcula qué líneas renderizar.

    1. Convierte scroll_y (0.0-1.0) a posición absoluta
    2. Calcula rango viewport con buffer
    3. Busca líneas que intersectan con viewport
    4. Retorna lista de índices ordenados
    """
```

**Buffer:**
- `viewport_buffer = 10` líneas extra arriba y abajo
- Previene "pop-in" al hacer scroll
- Suaviza experiencia de usuario

#### D) Filtros y Búsqueda
```python
def apply_filter(filter_text):
    """
    - Marca líneas como visible=True/False
    - Actualiza visible_indices y filtered_indices
    - Recalcula geometría (total_height cambia)
    """

def apply_search(search_text):
    """
    - Marca líneas con matched_search=True/False
    - NO oculta líneas (solo resalta)
    - NO recalcula geometría
    """
```

#### E) Operaciones de Documento
```python
def insert_line(index, md_line):
    """
    1. Crear nuevo LineState
    2. Re-indexar líneas posteriores (index + 1)
    3. Recalcular geometría
    """

def delete_line(index):
    """
    1. Eliminar LineState
    2. Re-indexar líneas posteriores (index - 1)
    3. Recalcular geometría
    """

def update_line_height(index, new_height):
    """
    Después de edición que cambia altura:
    1. Actualizar LineState.height
    2. Recalcular geometría
    """
```

### 3. RecycleBoxLayout (Reciclaje de Widgets)

**Pools de widgets:**

```python
active_widgets: Dict[int, MDDocumentLineEditor]
    # Widgets actualmente renderizados
    # Key = índice de línea
    # Value = instancia de widget

recycled_pool: List[MDDocumentLineEditor]
    # Widgets disponibles para reutilización
    # No tienen índice asignado
    # Están "limpios" y listos

placeholders: Dict[int, Widget]
    # Widgets dummy para líneas no renderizadas
    # Mantienen espacio en layout
    # Tamaño = LineState.height
```

**Función central:**

```python
def update_visible_range(visible_indices: List[int]):
    """
    ÚNICA función que actualiza widgets.

    Llamada desde MDDocumentEditor en:
    - Scroll
    - Insert/Delete línea
    - Aplicar filtro
    - Page Up/Down
    - Arrow Up/Down

    Algoritmo:
    1. Comparar visible_indices con last_visible_indices
    2. Calcular: to_add = nuevos, to_remove = viejos
    3. Reciclar widgets en to_remove
    4. Crear/reutilizar widgets en to_add
    5. Actualizar last_visible_indices
    """
```

**Reciclaje vs Creación:**

```python
def _create_or_reuse_widget_at_index(index):
    if self.recycled_pool:
        widget = self.recycled_pool.pop()  # Reutilizar
    else:
        widget = MDDocumentLineEditor()    # Crear nuevo

    # Asignar datos del StateManager
    state = self.state_manager.get_state(index)
    widget.index = index
    widget.md_line = state.md_line
    widget.line_state = state

    # Sincronizar visual (SIN animación, es reciclaje)
    widget.active = state.active
    widget.selected = state.selected

    # Insertar en layout
    self._insert_widget_in_layout(index, widget)
```

**Placeholders:**
- Widgets dummy (Widget vacío)
- Altura = LineState.height
- Mantienen layout correcto cuando widget se recicla
- Reemplazados cuando widget vuelve a viewport

### 4. MDDocumentEditor (Coordinador)

**Responsabilidades:**

#### A) Inicialización
```python
def __init__(self):
    # Crear StateManager
    self.state_manager = StateManager()

    # Crear RecycleBoxLayout (pasa referencia al StateManager)
    self.recycle_layout = RecycleBoxLayout(
        state_manager=self.state_manager
    )
    self.add_widget(self.recycle_layout)

    # Bind eventos
    self.bind(scroll_y=self._on_scroll)
```

#### B) Carga de documento
```python
def load_document(self, md_document):
    # Cargar en StateManager
    self.state_manager.load_document(md_document.md_lines)

    # Renderizar inicial
    self._refresh_visible_widgets()
```

#### C) Evento de scroll
```python
def _on_scroll(self, instance, value):
    self._refresh_visible_widgets()

def _refresh_visible_widgets(self):
    """FUNCIÓN ÚNICA de actualización."""
    # Preguntar a StateManager qué mostrar
    visible_indices = self.state_manager.get_visible_in_viewport(
        scroll_y=self.scroll_y,
        viewport_height=self.height
    )

    # Actualizar layout
    self.recycle_layout.update_visible_range(visible_indices)
```

#### D) Interacciones directas
```python
def activate_line(self, index, enter_edit=True, anim_type='fade'):
    """
    Activar línea - DIRECTO al widget.

    1. Desactivar widget anterior (si existe)
    2. Asegurar que nueva línea tenga widget
    3. Llamar widget.activate() directamente
    4. Actualizar estado en StateManager
    5. Scroll si no está visible
    """
    # Desactivar anterior
    if self.active_line_widget:
        self.active_line_widget.activate(
            value=False,
            anim=True,
            anim_type=anim_type
        )

    # Asegurar widget existe
    widget = self.recycle_layout.get_widget(index)
    if not widget:
        # Forzar creación si está fuera de viewport
        self._ensure_widget_at_index(index)
        widget = self.recycle_layout.get_widget(index)

    # Activar directamente
    widget.activate(
        value=True,
        show_editor=enter_edit,
        anim=True,
        anim_type=anim_type
    )

    # Actualizar estado
    self.state_manager.update_state(
        index,
        active=True,
        editing=enter_edit
    )

    self.active_line_widget = widget
```

---

## Ventajas de Esta Arquitectura

### 1. Reciclaje Eficiente
- Solo widgets fuera de viewport se reciclan
- Widgets visibles mantienen estado completo
- Widget activo NUNCA se recicla

### 2. Estado Persistente
- Widgets visibles no pierden estado
- Edición, cursor, animaciones persisten
- No hay "saltos" visuales

### 3. Interacciones Directas
- Click → widget.activate() directo
- NO pasa por refresh_view_attrs()
- NO depende de RecycleView.data

### 4. Control Total
- Decides cuándo reciclar
- Decides cuándo crear widgets
- Decides buffer size

### 5. Alturas No Uniformes
- Cada LineState tiene su propia altura
- Cálculo de viewport considera alturas reales
- Placeholders con altura correcta

### 6. Código Más Simple
- Una sola función actualiza widgets: `update_visible_range()`
- No hay refresh_view_attrs() complejo
- No hay sincronización automática que falle

### 7. Debugging Fácil
- Puedes ver qué widgets existen: `active_widgets.keys()`
- Puedes acceder a widget por índice: `get_widget(5)`
- Estado en StateManager, rendering en RecycleBoxLayout (separado)

---

## Limitaciones y Consideraciones

### 1. Memoria
- Más memoria que RecycleView estándar
- ~50 widgets en memoria vs ~20 de RecycleView
- Aceptable para documentos < 50,000 líneas

### 2. Complejidad Implementación
- Más código que ScrollView puro
- Menos código que RecycleView + StateManager actual
- Complejidad media

### 3. Geometría Manual
- Debes calcular posiciones Y manualmente
- Debes estimar alturas iniciales
- Recalcular después de cambios

### 4. Widget Activo Fuera de Viewport
- Si widget activo sale de viewport, NO se recicla
- Puede tener 1 widget extra en memoria
- Beneficio: no pierdes estado de edición

---

## Comparación con Alternativas

| Aspecto | RecycleView Estándar | ScrollView Puro | **Alternativa 1** |
|---------|---------------------|-----------------|-------------------|
| Memoria | ✅ Muy baja (~20 widgets) | ❌ Alta (1 × línea) | ✅ Baja (~50 widgets) |
| Estado local | ❌ Se pierde | ✅ Persiste | ✅ Persiste (visibles) |
| Interacción | ❌ Indirecta | ✅ Directa | ✅ Directa |
| Alturas no uniformes | ⚠️ Complicado | ✅ Natural | ✅ Natural |
| Límite líneas | Millones | ~5,000 | ~50,000 |
| Complejidad | ❌ Alta | ✅ Baja | ⚠️ Media |
| Control | ❌ Poco | ✅ Total | ✅ Total |
| Animaciones | ❌ Difíciles | ✅ Triviales | ✅ Triviales |

---

## Siguiente Paso

Ver documentos de flujos de datos:
- **Flujo de Scroll**: `Alternativa_1_Flujo_Scroll_2026-01-12.md`
- **Flujo de Navegación**: `Alternativa_1_Flujo_Navegacion_2026-01-12.md`

---

**Conclusión**: Esta arquitectura ofrece el mejor balance entre performance, simplicidad y funcionalidad para un editor de Markdown interactivo.
