# Sistema de Eventos - MDDocumentEditor V2

**Fecha:** 2026-01-31
**Actualizado:** 2026-02-01
**Versión:** 1.1

---

## 1. Clasificación de Eventos

El sistema maneja dos tipos de eventos según su alcance:

### Tipo 1: Eventos de Documento (DocumentStateManager)
- **Alcance:** Afectan al conjunto de líneas o la estructura del documento
- **Origen:** MDDocumentEditor (teclado) → DocumentOperations → DocumentStateManager
- **Emisor:** DocumentStateManager
- **Receptor:** MDDocumentEditor
- **Procesamiento:** Gestión del ScrollView, creación/eliminación de widgets

### Tipo 2: Eventos de Línea (LineState)
- **Alcance:** Afectan a una línea individual
- **Origen:** MDDocumentLineEditor (mouse) → DocumentOperations → StateManager → LineState
- **Emisor:** LineState (vía StateManager)
- **Receptor:** MDDocumentLineEditor correspondiente
- **Procesamiento:** Actualización visual del widget

---

## 2. Tablas de Eventos

### 2.1 Eventos Tipo 1 - Documento (Estructura)

| Acción Usuario | Modo Edición | Evento | Origen | Método Origen | Emisor | EventType | Receptor | Método Receptor |
|----------------|--------------|--------|--------|---------------|--------|-----------|----------|-----------------|
| Enter | True | Insertar línea abajo | MDDocumentEditor | `_handle_enter()` | DocumentStateManager | `ADDED` | MDDocumentEditor | `_on_line_added()` |
| Shift+Enter | True | Insertar línea arriba | MDDocumentEditor | `_handle_enter(shift)` | DocumentStateManager | `ADDED` | MDDocumentEditor | `_on_line_added()` |
| Backspace | True | Si está al inicio, borra línea y mueve texto al final de línea anterior | MDDocumentEditor | `_handle_backspace()` | DocumentStateManager | `REMOVED` | MDDocumentEditor | `_on_line_removed()` |
| Delete | True | Si está al final, borra línea siguiente y mueve texto al final de línea actual | MDDocumentEditor | `_handle_delete()` | DocumentStateManager | `REMOVED` | MDDocumentEditor | `_on_line_removed()` |
| Delete (multi) | False | Eliminar líneas seleccionadas | MDDocumentEditor | `_handle_delete()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_batch_change()` |
| Alt+↑ | True/False | Mover línea arriba | MDDocumentEditor | `_handle_arrow_up(alt)` | DocumentStateManager | `MOVED` | MDDocumentEditor | `_on_line_moved()` |
| Alt+↓ | True/False | Mover línea abajo | MDDocumentEditor | `_handle_arrow_down(alt)` | DocumentStateManager | `MOVED` | MDDocumentEditor | `_on_line_moved()` |
| Ctrl+A | True | Sale del Modo Edición y Seleccionar todo | MDDocumentEditor | `_handle_select_all()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_batch_change()` |
| Ctrl+A | False | Seleccionar todo | MDDocumentEditor | `_handle_select_all()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_batch_change()` |
| Escape | True | Sale del modo edición y anula los cambios | MDDocumentEditor | `_handle_escape()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_batch_change()` |
| Escape | False | Limpiar selección de líneas | MDDocumentEditor | `_handle_escape()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_batch_change()` |
| UI Filtro | True/False | Aplicar filtro | App | `_on_filter_change()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_filter_applied()` |
| UI Filtro | True/False | Limpiar filtro | App | `_on_filter_clear()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_filter_cleared()` |
| Ctrl+C | True/False | Copiar (Papelera) | MDDocumentEditor | `_handle_copy()` | - | - | - | - |
| Ctrl+V | True/False | Pegar (Papelera) | MDDocumentEditor | `_handle_paste()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_batch_change()` |
| Ctrl+X | True/False | Cortar (Papelera) | MDDocumentEditor | `_handle_cut()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_batch_change()` |
| Ctrl+Z | True/False | Undo | MDDocumentEditor | `_handle_undo()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_batch_change()` |
| Ctrl+Y | True/False | Redo | MDDocumentEditor | `_handle_redo()` | DocumentStateManager | `BATCH` | MDDocumentEditor | `_on_batch_change()` |

### 2.2 Eventos Tipo 1 - Documento (Navegación)

| Acción Usuario | Modo Edición | Evento | Origen | Método Origen | Emisor | EventType | Receptor | Método Receptor |
|----------------|--------------|--------|--------|---------------|--------|-----------|----------|-----------------|
| F2 | True/False | Activa/Desactiva Edición | MDDocumentEditor | `_handle_f2()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| ↑ | True/False | Navegar arriba | MDDocumentEditor | `_handle_arrow_up()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| ↓ | True/False | Navegar abajo | MDDocumentEditor | `_handle_arrow_down()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| ← | True | Si está al principio, pasa edición a línea anterior (cursor al final) | MDDocumentEditor | `_handle_arrow_left()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| → | True | Si está al final, pasa edición a línea posterior (cursor al inicio) | MDDocumentEditor | `_handle_arrow_right()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Page Up | True/False | Página arriba | MDDocumentEditor | `_handle_page_up()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Page Down | True/False | Página abajo | MDDocumentEditor | `_handle_page_down()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Ctrl+Home | True/False | Ir al inicio del documento | MDDocumentEditor | `_handle_home()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Ctrl+End | True/False | Ir al final del documento | MDDocumentEditor | `_handle_end()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Shift+↑ | False | Selecciona líneas hacia arriba | MDDocumentEditor | `_handle_arrow_up(shift)` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_selection_change()` |
| Shift+↓ | False | Selecciona líneas hacia abajo | MDDocumentEditor | `_handle_arrow_down(shift)` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_selection_change()` |
| Ctrl+↑ | True/False | Mover selección al Título anterior | MDDocumentEditor | `_handle_prev_title()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Ctrl+↓ | True/False | Mover selección al Título siguiente | MDDocumentEditor | `_handle_next_title()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Ctrl+Shift+↑ | True/False | Mover selección al Título anterior del mismo nivel | MDDocumentEditor | `_handle_prev_sibling_title()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Ctrl+Shift+↓ | True/False | Mover selección al Título siguiente del mismo nivel | MDDocumentEditor | `_handle_next_sibling_title()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Alt+Shift+↑ | True/False | Mover selección al Título padre anterior | MDDocumentEditor | `_handle_parent_title()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |
| Alt+Shift+↓ | True/False | Mover selección al Título padre posterior | MDDocumentEditor | `_handle_parent_title_next()` | DocumentStateManager | `CHANGED` | MDDocumentEditor | `_on_navigation()` |

### 2.3 Eventos Tipo 2 - Línea Individual

| Acción Usuario | Modo Edición | Evento | Origen | Método Origen | Emisor | Atributo Cambiado | Receptor | Método Receptor |
|----------------|--------------|--------|--------|---------------|--------|-------------------|----------|-----------------|
| Click | True/False | Activar línea | MDDocumentLineEditor | `_on_click()` | LineState | `active`, `editing` | MDDocumentLineEditor | `_on_line_state_changed()` |
| Click otra | False | Desactivar línea | MDDocumentLineEditor | `_on_click()` | LineState | `active`, `editing` | MDDocumentLineEditor | `_on_line_state_changed()` |
| Mouse enter | True/False | Hotlight on | MDDocumentLineEditor | `_on_mouse_enter()` | LineState | `hotlight` | MDDocumentLineEditor | `_on_line_state_changed()` |
| Mouse leave | True/False | Hotlight off | MDDocumentLineEditor | `_on_mouse_leave()` | LineState | `hotlight` | MDDocumentLineEditor | `_on_line_state_changed()` |
| Edición | True | Cambiar texto | MDDocumentLineEditor | `_on_text_changed()` | LineState | `md_line` | MDDocumentLineEditor | `_on_line_state_changed()` |
| Ctrl+Click | False | Seleccionar (toggle) | MDDocumentLineEditor | `_on_click(ctrl)` | LineState | `selected` | MDDocumentLineEditor | `_on_line_state_changed()` |
| Shift+Click | False | Extender selección (rango) | MDDocumentLineEditor | `_on_click(shift)` | LineState | `selected` | MDDocumentLineEditor | `_on_line_state_changed()` |
| Ctrl+Click (sel) | False | Toggle selección | MDDocumentLineEditor | `_on_click(ctrl)` | LineState | `selected` | MDDocumentLineEditor | `_on_line_state_changed()` |

---

## 3. Flujo de Eventos

### 3.1 Flujo Tipo 1 (Documento)

```
┌─────────────────────┐
│  Acción Usuario     │
│  (Teclado)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MDDocumentEditor   │
│  _on_key_down()     │
│  _handle_xxx()      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ DocumentOperations  │
│  (valida, procesa)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│DocumentStateManager │
│  (modifica estado)  │
│  _emit_event()      │◄─────── Emite LineStateEvent
└──────────┬──────────┘         con EventType:
           │                    ADDED, REMOVED,
           ▼                    MOVED, BATCH, CHANGED
┌─────────────────────┐
│  MDDocumentEditor   │
│  _on_line_xxx()     │◄─────── Observa StateManager
│  (gestiona widgets) │
└─────────────────────┘
```

### 3.2 Flujo Tipo 2 (Línea)

```
┌─────────────────────┐
│  Acción Usuario     │
│  (Mouse)            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│MDDocumentLineEditor │
│  _on_click()        │
│  _on_mouse_xxx()    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ DocumentOperations  │
│  (valida, procesa)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│DocumentStateManager │
│  update_state()     │
│  (modifica estado)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     LineState       │
│  with_changes()     │◄─────── Estado inmutable
│  (nuevo estado)     │         actualizado
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│MDDocumentLineEditor │
│_on_line_state_changed│◄────── Observa su LineState
│  (actualiza visual) │
└─────────────────────┘
```

---

## 4. Comportamiento según Modo Edición

### 4.1 Teclas con comportamiento diferente

| Tecla | Modo Edición = True | Modo Edición = False |
|-------|---------------------|----------------------|
| Enter | Insertar línea abajo | - |
| Shift+Enter | Insertar línea arriba | - |
| Backspace | Unir con línea anterior (si cursor al inicio) | - |
| Delete | Unir con línea siguiente (si cursor al final) | Eliminar líneas seleccionadas |
| Escape | Cancelar edición, restaurar texto | Limpiar selección |
| Ctrl+A | Salir de edición + seleccionar todo | Seleccionar todo |
| ← | Navegar en texto (o línea anterior si inicio) | - |
| → | Navegar en texto (o línea siguiente si final) | - |
| Shift+↑/↓ | - | Extender selección |
| Click | Posicionar cursor | Activar línea |

### 4.2 Teclas con comportamiento idéntico

| Tecla | Comportamiento |
|-------|----------------|
| ↑/↓ | Navegar entre líneas |
| Alt+↑/↓ | Mover línea |
| Ctrl+↑/↓ | Navegar a título anterior/siguiente |
| Page Up/Down | Navegar página |
| Ctrl+Home/End | Ir a inicio/fin documento |
| Ctrl+C/V/X | Copiar/Pegar/Cortar |
| Ctrl+Z/Y | Undo/Redo |
| F2 | Toggle modo edición |
| Mouse enter/leave | Hotlight |

---

## 5. Atributos de LineStateEvent

### 5.1 Para Eventos Tipo 1

| EventType | index | line_state | old_state | changed_attributes |
|-----------|-------|------------|-----------|-------------------|
| `ADDED` | nuevo índice | nuevo LineState | `None` | `set()` |
| `REMOVED` | índice eliminado | `None` | LineState eliminado | `set()` |
| `MOVED` | nuevo índice | LineState movido | LineState original | `{'index'}` |
| `BATCH` | -1 | `None` | `None` | atributos afectados |
| `CHANGED` | índice | nuevo LineState | LineState anterior | atributos cambiados |

### 5.2 Para Eventos Tipo 2

| Cambio | changed_attributes | Método verificación |
|--------|-------------------|---------------------|
| Activación | `{'active'}` o `{'active', 'editing'}` | `is_activation_change()` |
| Selección | `{'selected'}` | `is_selection_change()` |
| Hotlight | `{'hotlight'}` | `is_hotlight_change()` |
| Edición | `{'editing'}` | `is_editing_change()` |
| Contenido | `{'md_line'}` | `is_content_change()` |
| Visibilidad | `{'visible'}` | `is_visibility_change()` |
| Geometría | `{'height'}` o `{'y_position'}` | `is_geometry_change()` |

---

## 6. Observadores

### 6.1 MDDocumentEditor observa DocumentStateManager

```python
class MDDocumentEditor:
    def __init__(self):
        self.state_manager.subscribe(self._on_state_manager_event)

    def _on_state_manager_event(self, event: LineStateEvent):
        if event.event_type == EventType.ADDED:
            self._on_line_added(event)
        elif event.event_type == EventType.REMOVED:
            self._on_line_removed(event)
        elif event.event_type == EventType.MOVED:
            self._on_line_moved(event)
        elif event.event_type == EventType.BATCH:
            self._on_batch_change(event)
        elif event.is_activation_change():
            self._on_navigation(event)
```

### 6.2 MDDocumentLineEditor observa su LineState

```python
class MDDocumentLineEditor:
    def bind_to_state(self, line_state: LineState):
        self.state_manager.subscribe_line(self.index, self._on_line_state_changed)

    def _on_line_state_changed(self, event: LineStateEvent):
        if event.index != self.index:
            return

        for attr in event.changed_attributes:
            if attr == 'active':
                self.update_active_visual(event.line_state.active)
            elif attr == 'selected':
                self.update_selection_visual(event.line_state.selected)
            elif attr == 'hotlight':
                self.update_hotlight_visual(event.line_state.hotlight)
            elif attr == 'editing':
                self.show_editor(event.line_state.editing)
```

---

## 7. Resumen de Responsabilidades

| Componente | Genera Eventos | Observa Eventos | Responsabilidad |
|------------|----------------|-----------------|-----------------|
| MDDocumentEditor | Teclado → Operations | StateManager (estructura) | Crear/eliminar widgets, scroll |
| MDDocumentLineEditor | Mouse → Operations | LineState (visual) | Actualizar visualización |
| DocumentOperations | - | - | Validar y ejecutar operaciones |
| DocumentStateManager | LineStateEvent | - | Gestionar estados, emitir eventos |
| LineState | - | - | Almacenar estado inmutable |

---

## 8. Notas de Implementación

1. **Inmutabilidad:** LineState es inmutable. Los cambios crean nuevos objetos vía `with_changes()`.

2. **Single Source of Truth:** DocumentStateManager es la única fuente de verdad. Todos los cambios pasan por él.

3. **Observador Selectivo:** MDDocumentLineEditor solo procesa eventos de su propio índice para eficiencia.

4. **Eventos en Cascada:** Un click puede generar múltiples eventos (desactivar anterior + activar nueva).

5. **Animaciones:** El `anim_type` en LineState indica qué animación usar para la transición visual.

6. **Modo Edición:** El comportamiento de varias teclas cambia según el modo edición esté activo o no.

7. **Navegación por Títulos:** Las funciones de navegación por títulos usan la estructura de linked-list de MDLine.
