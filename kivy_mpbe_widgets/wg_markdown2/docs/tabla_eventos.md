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
| Click | False | Selecciona la línea (anima selección verde desde el click) | 1 | ✅ |
| Click otra | False | Desactiva la anterior, activa la nueva | 1 | ✅ |
| Mouse enter/leave | T/F | Hotlight on/off (2 líneas verticales azules) | 1 | ✅ |
| Doble-click | False | Activa edición de la línea | 2 | ✅ |
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
| Page Up | T/F | Página arriba | `_handle_page_up()` | CHANGED | `_on_navigation()` | ⬜ |
| Page Down | T/F | Página abajo | `_handle_page_down()` | CHANGED | `_on_navigation()` | ⬜ |
| Ctrl+Home | T/F | Ir al inicio del documento | `_handle_home()` | CHANGED | `_on_navigation()` | ⬜ |
| Ctrl+End | T/F | Ir al final del documento | `_handle_end()` | CHANGED | `_on_navigation()` | ⬜ |

> Groundwork del Inc 3a: helper `get_line_widget(index)`, foco de teclado en el
> editor, y scroll para mantener visible la línea activa. Animación de selección
> como *slide* (reusar `GSelectItem.animate_select` con origen en el borde).

## Inc 3b — Modo edición por teclado y saltos entre líneas

| Acción | Modo | Descripción | Método Origen | Estado |
|---|---|---|---|---|
| Enter | False | Entra en modo edición de la línea activa (como F2) | `_handle_enter()` | ⬜ |
| F2 | T/F | Activa/Desactiva edición de la línea activa | `_handle_f2()` | ⬜ |
| ↑ | True | Línea superior manteniendo la columna del cursor | `_handle_arrow_up()` | ⬜ |
| ↓ | True | Línea inferior manteniendo la columna del cursor | `_handle_arrow_down()` | ⬜ |
| ← | True | Si está al inicio, pasa la edición a la línea anterior (cursor al final) | `_handle_arrow_left()` | ⬜ |
| → | True | Si está al final, pasa la edición a la línea siguiente (cursor al inicio) | `_handle_arrow_right()` | ⬜ |

## Inc 3c — Edición estructural (insertar / borrar / mover)

| Acción | Modo | Descripción | Método Origen | EventType | Método Receptor | Estado |
|---|---|---|---|---|---|---|
| Enter | True | **Parte la línea en el cursor**: inserta línea abajo con el texto posterior al cursor; la actual conserva el anterior | `_handle_enter()` | ADDED | `_on_line_added()` | ⬜ |
| Shift+Enter | True | Insertar línea arriba | `_handle_enter(shift)` | ADDED | `_on_line_added()` | ⬜ |
| Backspace | True | Al inicio de línea: borra la línea y mueve el texto al final de la anterior | `_handle_delete()` | REMOVED | `_on_line_removed()` | ⬜ |
| Delete | True | Al inicio de línea: une con la siguiente | `_handle_delete()` | REMOVED | `_on_line_removed()` | ⬜ |
| Delete (multi) | False | Elimina las líneas seleccionadas | `_handle_delete()` | BATCH | `_on_batch_change()` | ⬜ |
| Alt+↑ | T/F | Mover línea arriba | `_handle_arrow_up(alt)` | MOVED | `_on_line_moved()` | ⬜ |
| Alt+↓ | T/F | Mover línea abajo | `_handle_arrow_down(alt)` | MOVED | `_on_line_moved()` | ⬜ |

## Inc 3d — Navegación por títulos

| Acción | Modo | Descripción | Método Origen | Estado |
|---|---|---|---|---|
| Ctrl+↑ | T/F | Mueve la selección al título anterior | `_handle_prev_title()` | ⬜ |
| Ctrl+↓ | T/F | Mueve la selección al título siguiente | `_handle_next_title()` | ⬜ |
| Ctrl+Shift+↑ | T/F | Título anterior del mismo nivel | `_handle_prev_title_level()` | ⬜ |
| Ctrl+Shift+↓ | T/F | Título siguiente del mismo nivel | `_handle_next_title_level()` | ⬜ |
| Alt+Shift+↑ | T/F | Título padre anterior | `_handle_parent_title()` | ⬜ |
| Alt+Shift+↓ | T/F | Título padre posterior | `_handle_parent_title()` | ⬜ |

## Inc 3e — Selección múltiple de líneas

| Acción | Modo | Descripción | Método Origen | EventType | Estado |
|---|---|---|---|---|---|
| Ctrl+A | False | Seleccionar todo | `_handle_select_all()` | BATCH | ⬜ |
| Ctrl+A | True | Sale de edición y selecciona todo | `_handle_select_all()` | BATCH | ⬜ |
| Escape | False | Limpiar selección de líneas | `_handle_escape()` | — | ⬜ |
| Shift+↑ | False | Selecciona líneas hacia arriba | `_handle_shift_up()` | — | ⬜ |
| Shift+↓ | False | Selecciona líneas hacia abajo | `_handle_shift_down()` | — | ⬜ |
| Ctrl+Click | False | Apilar / toggle selección | `_on_click(ctrl)` | `selected` | ⬜ |
| Shift+Click | False | Extender selección | `_on_click(shift)` | `selected` | ⬜ |

---

## Fuera del Inc 3 (features posteriores)

| Grupo | Acciones | Estado | Nota |
|---|---|---|---|
| Undo / Redo | Ctrl+Z, Ctrl+Y | ⬜ | Requiere UndoManager (existe en kivy_mpbe_widgets) |
| Papelera / Portapapeles | Ctrl+C, Ctrl+V, Ctrl+X | ⬜ | Copiar/pegar/cortar líneas |
| Filtros | UI filtro: aplicar / limpiar | 🟡 | Ya integrado a nivel app (FilterService); falta atar al StateManager V2 |
