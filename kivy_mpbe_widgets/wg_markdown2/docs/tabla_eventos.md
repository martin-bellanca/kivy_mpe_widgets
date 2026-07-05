# Tabla de Eventos / Teclado — seguimiento

Convertido desde `Tablas de Eventos.ods`. Es la especificación de **todas las
combinaciones de teclado/mouse** del editor V2, con columnas de **sub-tarea** y
**estado** para seguir el avance.

**Leyenda de estado:** ✅ hecho · 🟡 en curso · ⬜ pendiente

**Notas de nomenclatura (spec → implementación actual):**
- La spec dice `MDDocumentLineEditor` para el widget de línea; en V2 se implementó
  como **`MDDocumentLine`**.
- La spec usa métodos `_handle_*` / `_on_*`; hoy la lógica equivalente está en
  `MDDocumentEditor` (`on_touch_up`, `activate_line`, `edit_line`) y en
  `MDDocumentLine`. Los nombres `_handle_*` son la meta de esta etapa.
- Flujo general salvo aclaración: **Origen** `MDDocumentEditor` → **Emisor**
  `DocumentStateManager` → **Receptor** `MDDocumentEditor`.

---

## Ya implementado (Inc 1–2)

| Acción | Modo | Descripción | Inc | Estado |
|---|---|---|---|---|
| Click en línea no seleccionada | False | La selecciona (anima selección verde desde el click) | 1 | ✅ |
| Click otra | False | Desactiva la anterior, activa la nueva | 1 | ✅ |
| Mouse enter/leave | T/F | Hotlight on/off (2 líneas verticales azules) | 1 | ✅ |
| Click en línea seleccionada | False | Activa edición de la línea con el **cursor en el punto del click** (reemplazó al doble-click, 2026-07-03) | 2 | ✅ |
| Click en el texto en edición | True | Mueve el cursor al punto del click (nativo del TextInput; el editor no roba el foco) | 2 | ✅ |
| Click en otra línea | True | **Mantiene el modo edición**: la actual confirma y la nueva entra a editar con el cursor en el click | 2 | ✅ |
| Edición (tipear) | True | Cambia texto → persiste en MDLine + render en vivo | 2 | ✅ |
| Escape | True | Sale de edición y **anula** los cambios (restaura) | 2 | ✅ |

> ⚠️ **A reconciliar en 3c:** hoy **Enter (en edición)** *confirma*. La conducta
> definitiva será **partir la línea en el cursor**: inserta una línea abajo con
> el texto **posterior** al cursor y la línea actual conserva el **anterior**
> (comportamiento estándar de editor). Se cambia al implementar 3c.

---

## Inc 3a — Navegación básica (sin editar)

| Acción | Modo | Descripción | Método Origen | EventType | Método Receptor | Estado |
|---|---|---|---|---|---|---|
| ↑ | False | Selecciona la línea superior, deselecciona la actual (slide up) | `_navigate(-1)` | CHANGED | `activate_line()` | ✅ |
| ↓ | False | Selecciona la línea inferior, deselecciona la actual (slide down) | `_navigate(+1)` | CHANGED | `activate_line()` | ✅ |
| Page Up | False | Página arriba | `_navigate(-page)` | CHANGED | `activate_line()` | ✅ |
| Page Down | False | Página abajo | `_navigate(+page)` | CHANGED | `activate_line()` | ✅ |
| Ctrl+Home | False | Ir al inicio del documento | `_go_to_line(0)` | CHANGED | `activate_line()` | ✅ |
| Ctrl+End | False | Ir al final del documento | `_go_to_line(last)` | CHANGED | `activate_line()` | ✅ |

> Teclado a nivel `Window` (`_on_window_key_down`), gateado por `_kbd_active` y
> `not _is_editing()`. Enfoque robusto tomado del editor viejo: la navegación no
> depende de que el widget tenga el foco de Kivy (por eso funciona tras salir de
> edición con Escape/Enter).

> Groundwork del Inc 3a: helper `get_line_widget(index)`, foco de teclado en el
> editor, y scroll para mantener visible la línea activa. Animación de selección
> como *slide* (reusar `GSelectItem.animate_select` con origen en el borde).

## Inc 3b — Modo edición por teclado y saltos entre líneas

| Acción | Modo | Descripción | Método Origen | Estado |
|---|---|---|---|---|
| Enter | False | Entra en modo edición de la línea activa (como F2) | `_edit_active_line()` (Window) | ✅ |
| F2 | False | Entra en modo edición de la línea activa | `_edit_active_line()` (Window) | ✅ |
| F2 | True | Sale de edición (toggle, confirma) | `_on_editor_nav()` (input) | ✅ |
| ↑ | True | Línea superior manteniendo la columna del cursor | `_on_editor_nav()`→`_on_line_edit_nav()` | ✅ |
| ↓ | True | Línea inferior manteniendo la columna del cursor | `_on_editor_nav()`→`_on_line_edit_nav()` | ✅ |
| ← | True | Si está al inicio, pasa la edición a la línea anterior (cursor al final) | `_on_editor_nav()`→`_on_line_edit_nav()` | ✅ |
| → | True | Si está al final, pasa la edición a la línea siguiente (cursor al inicio) | `_on_editor_nav()`→`_on_line_edit_nav()` | ✅ |

## Inc 3c — Edición estructural (insertar / borrar / mover)

| Acción | Modo | Descripción | Método Origen | EventType | Método Receptor | Estado |
|---|---|---|---|---|---|---|
| Enter | True | **Parte la línea en el cursor**: inserta línea abajo con el texto posterior al cursor; la actual conserva el anterior | `_on_editor_nav()`→`_on_line_edit_split()` | ADDED | `_on_line_added()` | ✅ |
| Shift+Enter | True | Insertar línea vacía arriba y editarla (la actual baja sin cambios) | `_on_editor_nav()`→`_on_line_edit_insert_above()` | ADDED | `_on_line_added()` | ✅ |
| Backspace | True | Al inicio de línea: une con la de arriba (el texto va al final de la anterior; cursor en el punto de unión) | `_on_editor_nav()`→`_on_line_edit_merge(-1)` | REMOVED | `_on_line_removed()` | ✅ |
| Delete | True | Al final de línea: une con la de abajo (el texto de la siguiente va al final de la actual; cursor en el punto de unión) | `_on_editor_nav()`→`_on_line_edit_merge(+1)` | REMOVED | `_on_line_removed()` | ✅ |
| Delete (multi) | False | Elimina las líneas seleccionadas | `_handle_delete()` | BATCH | `_on_batch_change()` | ⬜ |
| Alt+↑ | T/F | Mover línea arriba | `move_active_line(-1)` (sel) · `_on_line_edit_move_line` (edic) | MOVED | `_on_line_moved()` | ✅ |
| Alt+↓ | T/F | Mover línea abajo | `move_active_line(+1)` (sel) · `_on_line_edit_move_line` (edic) | MOVED | `_on_line_moved()` | ✅ |

## Inc 3d — Navegación por títulos

| Acción | Modo | Descripción | Método Origen | Estado |
|---|---|---|---|---|
| Ctrl+↑ | T/F | Mueve la selección al título anterior (cualquier nivel) | `_go_to_title(-1,'any')` | ✅ |
| Ctrl+↓ | T/F | Mueve la selección al título siguiente (cualquier nivel) | `_go_to_title(+1,'any')` | ✅ |
| Ctrl+Shift+↑ | T/F | Título anterior del mismo nivel | `_go_to_title(-1,'same')` | ✅ |
| Ctrl+Shift+↓ | T/F | Título siguiente del mismo nivel | `_go_to_title(+1,'same')` | ✅ |
| Alt+Shift+↑ | T/F | Título padre anterior (primer título de nivel superior hacia arriba) | `_go_to_title(-1,'parent')` | ✅ |
| Alt+Shift+↓ | T/F | Título padre posterior (primer título de nivel superior hacia abajo) | `_go_to_title(+1,'parent')` | ✅ |

> Nota: el padre queda en **Alt+Shift+↑↓** (no Ctrl+Alt) porque en Linux el
> escritorio suele reservar Ctrl+Alt+flechas para cambiar de workspace.

## Inc 3e — Selección múltiple de líneas

> **Alcance (esta versión):** selección **contigua**, sólo **Shift+↑↓** y
> **Shift+Click**, en modo visualización (desde edición, Shift+flecha/click sale
> a visualización y selecciona). Sin Ctrl+A ni Ctrl+Click en esta etapa. La
> selección es para aplicar **acciones** al bloque (ver 3e.3+).

| Acción | Modo | Descripción | Método Origen | Estado |
|---|---|---|---|---|
| Shift+↑ | False | Extiende la selección contigua hacia arriba | `extend_selection(-1)` | ✅ |
| Shift+↓ | False | Extiende la selección contigua hacia abajo | `extend_selection(+1)` | ✅ |
| Shift+↑↓ | True | Sale de edición a visualización y extiende la selección | `_on_line_edit_select()` | ✅ |
| Escape | False | Colapsa la selección múltiple a la línea activa | `clear_multi_selection()` | ✅ |
| Shift+Click | False | Extiende la selección hasta la línea clickeada | `_on_click(shift)` | ⬜ 3e.2 |
| Delete | False | Borra las líneas seleccionadas | `_handle_delete()` | ⬜ 3e.3 |
| Alt+↑↓ | False | Mueve el bloque seleccionado | `move_selection()` | ⬜ 3e.3 |
| Ctrl+C/X/V | False | Copiar/cortar/pegar el bloque | — | ⬜ 3e.4 |
| Ctrl+D | False | Duplicar el bloque | — | ⬜ 3e.5 |
| Tab / Shift+Tab | False | Indentar / desindentar el bloque | — | ⬜ 3e.6 |
| Toggle tarea | False | `[ ]`↔`[x]` sobre el bloque | — | ⬜ 3e.7 |

---

## Fuera del Inc 3 (features posteriores)

| Grupo | Acciones | Estado | Nota |
|---|---|---|---|
| Undo / Redo | Ctrl+Z, Ctrl+Y | ⬜ | Requiere UndoManager (existe en kivy_mpbe_widgets) |
| Papelera / Portapapeles | Ctrl+C, Ctrl+V, Ctrl+X | ⬜ | Copiar/pegar/cortar líneas |
| Filtros | UI filtro: aplicar / limpiar | 🟡 | Ya integrado a nivel app (FilterService); falta atar al StateManager V2 |
