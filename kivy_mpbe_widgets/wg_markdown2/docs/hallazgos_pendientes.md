# Hallazgos, bugs y pendientes — chequeo del proyecto

**Origen:** revisión completa del módulo `wg_markdown2` (core + widgets + gráficos)
e integración en la app, previa al Inc 3b. **Fecha del chequeo:** 2026-07-03.
**Documento de seguimiento:** acá se registran bugs/hallazgos/deuda técnica con su
estado. Actualizar al corregir o al descubrir nuevos.

**Leyenda:** ✅ corregido · ⬜ pendiente (con incremento sugerido)

---

## Corregidos (2026-07-03)

### ✅ 1. Binds del StateManager a LineState eran no-ops silenciosos
- **Dónde:** `core/state_manager.py` (`_load_document` y `insert_line`).
- **Qué:** se usaba `bind(on_active=...)` para **propiedades** de Kivy. `bind(on_x=...)`
  sólo aplica a *eventos registrados*; para propiedades es `bind(x=...)`. Kivy ignora
  en silencio los `on_*` inexistentes (verificado empíricamente). De los 9 binds sólo
  funcionaba `on_type_changed`; todos los handlers `_on_line_state_*` eran código
  muerto y el flujo "LineState → StateManager re-emite `on_line_state_changed`" no
  operaba.
- **Fix:** binds por nombre de propiedad (`active=...`, `selected=...`, etc.). Las
  firmas `(instance, value)` ya coincidían. Verificado con smoke test headless:
  cambios directos de propiedad ahora re-emiten `on_line_state_changed`.

### ✅ 2. `widget_type` nunca se inicializaba según el tipo de línea
- **Dónde:** `core/line_state.py` (`__init__`), `widgets/md_document_line.py`.
- **Qué:** `_widget_type` nacía siempre `MDTextLabel` y `LineState.update_type()` no
  se llamaba desde ningún lado → TODAS las filas se creaban como `MDTextLabel`
  (`WIDGETS_LABELS` sin uso; separadores como texto "---"). Además, al editar,
  `_on_editor_text` llamaba `md_line.update_type()` directo (no el del LineState),
  con lo que `on_type_changed` nunca disparaba y el label no cambiaba de clase al
  cambiar el tipo tipeando.
- **Fix:** `LineState.__init__` inicializa `_widget_type` desde `WIDGETS_LABELS` según
  `md_line.type`; la edición (texto y Escape) pasa por `line_state.update_type()`; y
  `MDDocumentLine` bindea `on_type_changed` y reemplaza el label en vivo (conservando
  posición y z-order bajo el editor).
- **Descubierto al implementar:** ver pendientes 12 y 13 (labels stub).

### ✅ 3. Fuga de binds de `Window.mouse_pos` (hover) al repoblar
- **Dónde:** `graphics/items_graphics.py` (`GHotlightItem`),
  `widgets/md_document_line.py`, `widgets/md_document_editor.py`.
- **Qué:** cada fila bindeaba `Window.mouse_pos` y nunca se desbindeaba. Al abrir otro
  archivo los binds quedaban vivos: cada movimiento del mouse recorría los hotlight de
  todos los documentos abiertos en la sesión (CPU creciente + callbacks sobre widgets
  muertos).
- **Fix:** `GHotlightItem.release()` (desbindea Window y pos/size), `MDDocumentLine.release()`
  (hotlight + `Window.on_key_down` de edición + binds al LineState) y
  `MDDocumentEditor._release_line_widgets()` llamado desde `initialize_document` y
  `populate_md_lines`.

### ✅ 4. App: `NameError` en primera ejecución (sin sesión previa)
- **Dónde:** `kv_markdown_editor_main_rv_v2.py` (`on_start`).
- **Qué:** `except FileNotFoundError:` sin `as e`, pero el mensaje de log usaba `{e}`.
- **Fix:** `except FileNotFoundError as e:`.

### ✅ 5. Referencias colgadas al repoblar el documento
- **Dónde:** `widgets/md_document_editor.py` (`populate_md_lines`).
- **Qué:** no reseteaba `active_line_widget` (quedaba apuntando a una fila del
  documento anterior; `get_active_line_index()` mentía) ni `_kbd_active`.
- **Fix:** `_release_line_widgets()` resetea `active_line_widget`; `populate_md_lines`
  resetea `_kbd_active = False` (el teclado se re-activa al activar una línea del
  documento nuevo).

### ✅ 6. `LineState.update_type()` crasheaba con `md_line=None`
- **Dónde:** `core/line_state.py`.
- **Qué:** al guard le faltaba el `return`; seguía y hacía `self.md_line.update_type()`
  → `AttributeError`. Latente (no se llamaba, ver #2).
- **Fix:** `return None` temprano.

### ✅ 11a. Imports basura en `md_document_editor.py`
- **Qué:** `from pygments.unistring import No` (autocompletado accidental) y
  `from logging import ERROR` sin uso. Eliminados.

---

## Pendientes

### ⬜ 7. Geometría del StateManager desconectada de la realidad → **Inc 5**
- `state.height` queda en la estimación inicial (`_estimate_line_height`); nadie llama
  `update_line_height` cuando el label real cambia de altura. `y_position`,
  `total_height` y `get_visible_in_viewport()` — la base del reciclado propio —
  devuelven valores irreales. Hoy no afecta (el BoxLayout mide solo).
- **Acción:** cablear la altura real de `MDDocumentLine` al estado (ya bindea
  `label.height`; falta propagar a `state_manager.update_line_height`) antes o al
  comenzar el Inc 5.

### ⬜ 8. `move_line` no reindexa los sets intermedios → **antes de 3c/3e**
- `core/state_manager.py`: al mover una línea, los índices de las líneas intermedias
  se corren, pero `_visible/_filtered/_selected/_search_matches` sólo corrigen la
  línea movida. Con filtros activos o selección múltiple corrompe los sets.
- **Acción:** reindexar los sets completos (como hacen `insert_line`/`remove_line`)
  al implementar Alt+↑↓ (3c).

### ⬜ 9. El editor no escucha los eventos estructurales → **Inc 3c**
- Nadie bindea `on_line_added/removed/moved`; ni `MDDocumentLine.index` ni el mapa
  `_line_widgets` siguen las reindexaciones del StateManager.
- **Acción:** diseñarlo en 3c (el editor bindea los 3 eventos y ajusta filas/mapa;
  o las filas derivan su índice de `line_state.index`).

### ⬜ 10. La edición bypasea al StateManager → **decisión de diseño (3c)**
- `_on_editor_text` escribe `md_line.md_text` directo en vez de
  `state_manager.update_line_text(index, text)`. Funciona (MDLine compartido) pero
  rompe la convención de única fuente de verdad y el StateManager no se entera de los
  cambios (relevante para undo / guardado sucio futuros).
- **Acción propuesta:** canalizar por `update_line_text` cuando se toque 3c.

### ⬜ 11b. Menores / limpieza
- `md_inputs.py`: el kv declara `<MDLineTextInput@TextInput>` como *dynamic class*
  duplicando la clase Python homónima (frágil; `multiline` definido en ambos lados).
- `md_document_editor.load_document()`: camino muerto y roto (llama
  `state_manager._load_document(md_lines)` con un argumento que ya no existe).
  Unificar con `populate_md_lines` o eliminar. (Ya anotado en arquitectura.md.)
- `__repr__` del editor nunca sale de "initializing..." vía `populate_md_lines`
  porque `self.md_document` sólo se setea en el camino muerto `load_document()`.
- Hover puede activarse en filas scrolleadas fuera del viewport (colisión por
  coordenadas de ventana; el stencil del ScrollView oculta el dibujo, pero el estado
  `hotlight` cambia). Se resuelve naturalmente con el reciclado (Inc 5).

### ⬜ 12. `MDTableLabel` no es instanciable desde las filas → **portar label**
- `md_labels.py`: su `__init__` sólo recibe `html_table` (no `md_text`) → `TypeError`
  al usarlo como los demás labels (verificado). Mientras tanto `WIDGETS_LABELS` mapea
  `TABLE → MDTextLabel` (mismo aspecto que antes del fix #2).
- **Acción:** portar/adaptar el label de tablas y restaurar el mapeo.

### ⬜ 13. `MDHeadLabel` era un stub sin render → **mejora visual pendiente**
- Era `Label + BaseMDLabel` con `pass`: no traducía markdown (mostraba texto vacío) y
  un cambio de `md_text` crasheaba (`update()` abstracto). Se lo hizo heredar de
  `MDTextLabel` (funcional, renderiza como texto). Falta el diseño real ("resaltar
  fondo" del head title).
