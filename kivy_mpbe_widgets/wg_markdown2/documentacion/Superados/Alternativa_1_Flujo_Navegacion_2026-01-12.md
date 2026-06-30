# Alternativa 1: Flujo de Datos - Navegación con Teclado

**Fecha:** 2026-01-12
**Versión:** 1.0
**Tipo:** Flujos de datos de navegación

---

## Índice

1. [Arrow Up/Down (Navegación Línea a Línea)](#1-arrow-updown)
2. [Page Up/Down (Navegación por Página)](#2-page-updown)
3. [Comparación y Diferencias](#3-comparación)

---

## 1. Arrow Up/Down

### Evento: Usuario Presiona Arrow Up

Navega a la línea anterior con animación `slide_up`.

---

### Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│  USUARIO PRESIONA ARROW UP                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  1. Kivy Window captura evento de teclado                   │
│                                                             │
│     Window.on_key_down(keycode, text, modifiers)            │
│       keycode = 273 (Arrow Up)                              │
│       modifiers = [] (sin Shift/Ctrl/Alt)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  2. MDDocumentEditor recibe evento (tiene FocusBehavior)    │
│                                                             │
│     def keyboard_on_key_down(self, window, keycode,         │
│                              text, modifiers):               │
│                                                             │
│         if keycode[1] == 'up':  # Arrow Up                  │
│             return self._on_arrow_up(modifiers)             │
│                                                             │
│         elif keycode[1] == 'down':  # Arrow Down            │
│             return self._on_arrow_down(modifiers)           │
│                                                             │
│         # ... otros keycodes                                │
│                                                             │
│         return False  # No manejado                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  3. MDDocumentEditor._on_arrow_up(modifiers)                │
│                                                             │
│     def _on_arrow_up(self, modifiers):                      │
│         # Verificar que hay línea activa                    │
│         if not self.active_line_widget:                     │
│             # Activar primera línea visible                 │
│             self._activate_first_visible_line()             │
│             return True                                     │
│                                                             │
│         # Obtener índice actual                             │
│         current_index = self.active_line_widget.index       │
│                                                             │
│         # Calcular índice anterior                          │
│         prev_index = self._get_previous_visible_line(       │
│             current_index                                   │
│         )                                                   │
│                                                             │
│         if prev_index is None:                              │
│             # Ya estamos en la primera línea                │
│             return True                                     │
│                                                             │
│         # Navegar a línea anterior                          │
│         self.navigate_to_line(                              │
│             index=prev_index,                               │
│             anim_type='slide_up',                           │
│             enter_edit=self.active_line_widget.editing      │
│         )                                                   │
│                                                             │
│         return True  # Evento manejado                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  4. StateManager._get_previous_visible_line(current_index)  │
│                                                             │
│     def _get_previous_visible_line(self, current_index):    │
│         """                                                 │
│         Buscar línea visible anterior.                      │
│                                                             │
│         IMPORTANTE: Salta líneas ocultas por filtros.       │
│         """                                                 │
│         # Obtener líneas visibles ordenadas                 │
│         visible_sorted = sorted(self.visible_indices)       │
│                                                             │
│         # Buscar posición actual                            │
│         try:                                                │
│             pos = visible_sorted.index(current_index)       │
│         except ValueError:                                  │
│             return None  # Línea actual no visible          │
│                                                             │
│         # Retornar anterior                                 │
│         if pos > 0:                                         │
│             return visible_sorted[pos - 1]                  │
│         else:                                               │
│             return None  # Ya es la primera                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  5. MDDocumentEditor.navigate_to_line(index, anim_type)     │
│                                                             │
│     def navigate_to_line(self, index, anim_type='fade',     │
│                         enter_edit=True):                   │
│         """                                                 │
│         Navegar a una línea específica.                     │
│                                                             │
│         Pasos:                                              │
│         1. Desactivar línea actual                          │
│         2. Asegurar que nueva línea tenga widget            │
│         3. Activar nueva línea con animación                │
│         4. Scroll si no está visible                        │
│         5. Actualizar estado en StateManager                │
│         """                                                 │
│                                                             │
│         # A) Desactivar línea actual                        │
│         if self.active_line_widget:                         │
│             old_widget = self.active_line_widget            │
│             old_index = old_widget.index                    │
│                                                             │
│             # Animación inversa:                            │
│             # - Si subimos, la actual sale hacia abajo      │
│             # - Si bajamos, la actual sale hacia arriba     │
│             exit_anim = (                                   │
│                 'slide_down' if anim_type == 'slide_up'     │
│                 else 'slide_up'                             │
│             )                                               │
│                                                             │
│             old_widget.activate(                            │
│                 value=False,                                │
│                 show_editor=False,                          │
│                 anim=True,                                  │
│                 anim_type=exit_anim                         │
│             )                                               │
│                                                             │
│             # Actualizar estado                             │
│             self.state_manager.update_state(                │
│                 old_index,                                  │
│                 active=False,                               │
│                 editing=False                               │
│             )                                               │
│                                                             │
│         # B) Asegurar que nueva línea tenga widget          │
│         new_widget = self.recycle_layout.get_widget(index)  │
│                                                             │
│         if not new_widget:                                  │
│             # Línea fuera de viewport, forzar creación      │
│             self._ensure_line_in_viewport(index)            │
│             new_widget = self.recycle_layout.get_widget(    │
│                 index                                       │
│             )                                               │
│                                                             │
│         # C) Activar nueva línea                            │
│         cursor_pos = (0, 0)  # Inicio de línea              │
│                                                             │
│         new_widget.activate(                                │
│             value=True,                                     │
│             show_editor=enter_edit,                         │
│             cursor=cursor_pos,                              │
│             anim=True,                                      │
│             anim_type=anim_type                             │
│         )                                                   │
│                                                             │
│         # Actualizar estado                                 │
│         self.state_manager.update_state(                    │
│             index,                                          │
│             active=True,                                    │
│             editing=enter_edit,                             │
│             cursor_pos=cursor_pos,                          │
│             anim_type=anim_type                             │
│         )                                                   │
│                                                             │
│         # D) Guardar referencia                             │
│         self.active_line_widget = new_widget                │
│                                                             │
│         # E) Scroll si no está completamente visible        │
│         self._scroll_to_ensure_visible(index)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Widget.activate() ejecuta animación 'slide_up'          │
│                                                             │
│     Animación slide_up:                                     │
│     - Widget aparece desde arriba                           │
│     - Opacidad: 0.0 → 1.0                                   │
│     - Posición Y: y - 20 → y                                │
│     - Duración: 0.2 segundos                                │
│     - Easing: 'out_cubic'                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  7. RESULTADO: Nueva línea activa con animación suave       │
│                                                             │
│     Usuario ve:                                             │
│     - Línea actual se desactiva (sale hacia abajo)          │
│     - Nueva línea se activa (entra desde arriba)            │
│     - Transición fluida                                     │
│     - Cursor al inicio de nueva línea                       │
└─────────────────────────────────────────────────────────────┘
```

---

### Evento: Usuario Presiona Arrow Down

Navega a la línea siguiente con animación `slide_down`.

**Flujo idéntico a Arrow Up, con diferencias:**

| Aspecto | Arrow Up | Arrow Down |
|---------|----------|------------|
| Función | `_on_arrow_up()` | `_on_arrow_down()` |
| Buscar línea | `_get_previous_visible_line()` | `_get_next_visible_line()` |
| Animación entrada | `slide_up` (desde arriba) | `slide_down` (desde abajo) |
| Animación salida | `slide_down` (hacia abajo) | `slide_up` (hacia arriba) |
| Scroll | Hacia arriba si necesario | Hacia abajo si necesario |

---

## 2. Page Up/Down

### Evento: Usuario Presiona Page Down

Scrollea una página completa hacia abajo.

---

### Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│  USUARIO PRESIONA PAGE DOWN                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  1. Kivy Window captura evento                              │
│                                                             │
│     keycode = 281 (Page Down)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  2. MDDocumentEditor recibe evento                          │
│                                                             │
│     def keyboard_on_key_down(self, window, keycode,         │
│                              text, modifiers):               │
│                                                             │
│         if keycode[1] == 'pagedown':                        │
│             return self._on_page_down()                     │
│                                                             │
│         elif keycode[1] == 'pageup':                        │
│             return self._on_page_up()                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  3. MDDocumentEditor._on_page_down()                        │
│                                                             │
│     def _on_page_down(self):                                │
│         """                                                 │
│         Scrollear una página completa hacia abajo.          │
│                                                             │
│         Diferencias con Arrow Down:                         │
│         - NO cambia línea activa (solo scroll)              │
│         - NO ejecuta animaciones de activación              │
│         - Scrollea viewport_height pixels                   │
│         - Widgets se reciclan automáticamente               │
│         """                                                 │
│                                                             │
│         # Calcular nuevo scroll_y                           │
│         viewport_height = self.height                       │
│         total_height = self.state_manager.total_height      │
│                                                             │
│         # Calcular cuánto scrollear (en scroll_y units)     │
│         scroll_delta = viewport_height / total_height       │
│                                                             │
│         # Aplicar                                           │
│         new_scroll_y = max(                                 │
│             0.0,                                            │
│             self.scroll_y - scroll_delta                    │
│         )                                                   │
│                                                             │
│         # Animar scroll (suave)                             │
│         Animation(                                          │
│             scroll_y=new_scroll_y,                          │
│             duration=0.3,                                   │
│             transition='out_cubic'                          │
│         ).start(self)                                       │
│                                                             │
│         # _on_scroll() se dispara automáticamente           │
│         # durante la animación                              │
│                                                             │
│         return True                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Animation actualiza scroll_y progresivamente            │
│                                                             │
│     Durante 0.3 segundos:                                   │
│     - scroll_y se actualiza en cada frame                   │
│     - _on_scroll() se llama múltiples veces                 │
│     - _refresh_visible_widgets() actualiza viewport         │
│     - RecycleBoxLayout recicla widgets según scroll         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  5. RESULTADO: Scroll animado de una página                 │
│                                                             │
│     Usuario ve:                                             │
│     - Scroll suave de ~800px                                │
│     - Widgets se reciclan automáticamente                   │
│     - Línea activa NO cambia (si está visible)              │
│     - Línea activa SE DESACTIVA (si sale del viewport)      │
└─────────────────────────────────────────────────────────────┘
```

---

### Caso Especial: Línea Activa Sale del Viewport

```
┌─────────────────────────────────────────────────────────────┐
│  DURANTE PAGE DOWN: Línea activa sale de viewport          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  RecycleBoxLayout intenta reciclar widget activo            │
│                                                             │
│     def _recycle_widget_at_index(self, index):              │
│         widget = self.active_widgets[index]                 │
│                                                             │
│         # ⚠️ PROTECCIÓN                                     │
│         if widget == self.parent.active_line_widget:        │
│             # NO reciclar widget activo                     │
│             # Mantener en memoria aunque no visible         │
│             return                                          │
│                                                             │
│         # ... resto del reciclaje ...                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  OPCIÓN 1: Mantener widget activo (preservar estado)       │
│                                                             │
│     Ventaja:                                                │
│     - No se pierde estado de edición                        │
│     - Cursor se mantiene                                    │
│     - Volver con Page Up restaura exactamente               │
│                                                             │
│     Desventaja:                                             │
│     - 1 widget extra en memoria                             │
└─────────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  OPCIÓN 2: Desactivar y reciclar (perder estado)           │
│                                                             │
│     if widget == self.parent.active_line_widget:            │
│         # Desactivar primero                                │
│         self.parent.deactivate_current_line()               │
│                                                             │
│         # Ahora sí reciclar                                 │
│         self.recycled_pool.append(widget)                   │
│                                                             │
│     Ventaja:                                                │
│     - Memoria más eficiente                                 │
│                                                             │
│     Desventaja:                                             │
│     - Pierde estado de edición                              │
│     - Usuario debe re-activar con click                     │
└─────────────────────────────────────────────────────────────┘
```

**Recomendación:** OPCIÓN 1 (mantener widget activo) para mejor UX.

---

### Evento: Usuario Presiona Page Up

Scrollea una página completa hacia arriba.

**Flujo idéntico a Page Down, con diferencias:**

| Aspecto | Page Down | Page Up |
|---------|-----------|---------|
| Dirección scroll | Hacia abajo (scroll_y ↓) | Hacia arriba (scroll_y ↑) |
| Cálculo | `scroll_y - delta` | `scroll_y + delta` |
| Límite | `max(0.0, ...)` | `min(1.0, ...)` |
| Líneas visibles | Más abajo | Más arriba |

---

## 3. Comparación

### Arrow Up/Down vs Page Up/Down

| Aspecto | Arrow Up/Down | Page Up/Down |
|---------|---------------|--------------|
| **Acción principal** | Cambiar línea activa | Scrollear viewport |
| **Línea activa** | ✅ Cambia | ❌ Se mantiene* |
| **Animación widget** | ✅ slide_up/down | ❌ No |
| **Animación scroll** | ⚠️ Solo si necesario | ✅ Siempre |
| **Distancia** | 1 línea (~30px) | 1 página (~800px) |
| **Reciclaje** | ⚠️ Solo si cambia viewport | ✅ Siempre |
| **Duración** | 0.2s (activación) | 0.3s (scroll) |
| **Cursor** | ✅ Se actualiza | ❌ No cambia |
| **Modo edición** | ✅ Se mantiene | ✅ Se mantiene* |

\* Excepto si sale de viewport (depende de implementación)

---

### Tabla de Teclas y Acciones

| Tecla | Función | Animación | Scroll | Línea Activa |
|-------|---------|-----------|--------|--------------|
| **Arrow Up** | Línea anterior | `slide_up` | Auto si necesario | Cambia |
| **Arrow Down** | Línea siguiente | `slide_down` | Auto si necesario | Cambia |
| **Page Up** | Página arriba | No | Animado 0.3s | Mantiene* |
| **Page Down** | Página abajo | No | Animado 0.3s | Mantiene* |
| **Home** | Primera línea | `fade` | A scroll_y=1.0 | Cambia |
| **End** | Última línea | `fade` | A scroll_y=0.0 | Cambia |
| **Ctrl+Home** | Top documento | No | A scroll_y=1.0 | Mantiene |
| **Ctrl+End** | Bottom documento | No | A scroll_y=0.0 | Mantiene |

---

## Flujos Resumidos

### Arrow Up

```
Key Down → _on_arrow_up() → get_previous_visible_line()
→ navigate_to_line(anim='slide_up')
→ Desactivar actual (slide_down) → Activar anterior (slide_up)
→ Scroll si necesario → UPDATE
```

### Arrow Down

```
Key Down → _on_arrow_down() → get_next_visible_line()
→ navigate_to_line(anim='slide_down')
→ Desactivar actual (slide_up) → Activar siguiente (slide_down)
→ Scroll si necesario → UPDATE
```

### Page Down

```
Key Down → _on_page_down()
→ Calcular scroll_delta → Animation(scroll_y - delta)
→ Durante animación: _on_scroll() múltiples veces
→ _refresh_visible_widgets() → Reciclaje automático
→ UPDATE
```

### Page Up

```
Key Down → _on_page_up()
→ Calcular scroll_delta → Animation(scroll_y + delta)
→ Durante animación: _on_scroll() múltiples veces
→ _refresh_visible_widgets() → Reciclaje automático
→ UPDATE
```

---

## Métricas de Performance

### Arrow Up/Down (por operación)

| Paso | Tiempo |
|------|--------|
| Detectar key | ~0.1ms |
| get_previous/next_visible_line() | ~0.05ms |
| Desactivar widget actual | ~1ms (animación) |
| Asegurar widget nuevo | ~0.3ms |
| Activar widget nuevo | ~1ms (animación) |
| Scroll si necesario | ~0.5ms |
| **Total** | **~3ms lógica + animaciones** |

### Page Up/Down (por operación)

| Paso | Tiempo |
|------|--------|
| Detectar key | ~0.1ms |
| Calcular delta | ~0.01ms |
| Iniciar Animation | ~0.1ms |
| **Total inicial** | **~0.2ms** |
| Durante animación (0.3s) | 18 frames × ~0.6ms = ~11ms |
| **Total animación** | **~11ms distribuidos** |

**Conclusión:** Ambas operaciones son muy fluidas y no bloquean UI.

---

## Resumen

**Arrow Up/Down:**
- Navega línea a línea
- Cambia línea activa
- Animaciones de transición
- Scroll automático para mantener visible

**Page Up/Down:**
- Scrollea viewport completo
- Mantiene línea activa (si visible)
- Sin animaciones de widget
- Reciclaje automático durante scroll

**Arquitectura unificada:**
- Ambos usan `_refresh_visible_widgets()`
- Ambos respetan filtros (solo líneas visibles)
- Ambos reciclan widgets eficientemente
