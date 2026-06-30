# Alternativa 1: Widgets Dinámicos según Viewport

**Fecha:** 2026-01-12
**Versión:** 1.0
**Tipo:** Aclaración técnica importante

---

## Pregunta Crítica

> **"Por qué la cantidad de widgets de línea es fijo. No debería depender de la altura de RecycleBoxLayout?"**

**Respuesta:** ¡Correcto! La cantidad de widgets **NO es fija**, es **completamente dinámica** y depende de:

1. **viewport_height** (altura de RecycleBoxLayout/MDDocumentEditor)
2. **Alturas individuales de líneas** (NO uniformes)
3. **viewport_buffer** (configuración de líneas extra)

---

## Cálculo Dinámico de Widgets

### Fórmula General

```python
widgets_necesarios = widgets_visibles + widgets_buffer

donde:
    widgets_visibles = suma de líneas que caben en viewport_height
    widgets_buffer = viewport_buffer_arriba + viewport_buffer_abajo
                   = 10 + 10 = 20 (típicamente)
```

**IMPORTANTE:** `widgets_visibles` NO es una división simple porque las alturas de líneas son NO uniformes.

### Algoritmo Real

```python
def get_visible_in_viewport(self, scroll_y: float, viewport_height: float):
    """
    Calcula dinámicamente cuántos widgets se necesitan.

    NO hay número fijo hardcoded.
    """
    # 1. Calcular posición de scroll en pixels absolutos
    scroll_pos = self.total_height * (1.0 - scroll_y)

    # 2. Calcular rango del viewport (DEPENDE de viewport_height)
    buffer_height = self.viewport_buffer * 30  # Estimación inicial
    viewport_start = scroll_pos - buffer_height
    viewport_end = scroll_pos + viewport_height + buffer_height
    #                           ↑ DINÁMICO

    # 3. Buscar líneas que intersectan con este rango
    visible = []
    for index in sorted(self.visible_indices):
        state = self.line_states[index]
        line_top = state.y_position
        line_bottom = line_top + state.height  # Altura NO uniforme

        # ¿Está dentro del viewport?
        if line_bottom >= viewport_start and line_top <= viewport_end:
            visible.append(index)

    # 4. Retornar lista (tamaño VARÍA según viewport_height)
    return visible
```

---

## Ejemplos Según Tamaño de Ventana

### Ventana Pequeña (Laptop 13")

```
viewport_height = 600px
altura_promedio_línea = 30px
viewport_buffer = 10 líneas arriba + 10 abajo

Líneas visibles en viewport: 600 / 30 = 20 líneas
Buffer: 10 + 10 = 20 líneas
TOTAL widgets: ~40

Memoria: 40 widgets × 5KB = 200KB
```

### Ventana Media (Desktop 24")

```
viewport_height = 1000px
altura_promedio_línea = 30px
viewport_buffer = 10 + 10

Líneas visibles: 1000 / 30 = 33 líneas
Buffer: 20 líneas
TOTAL widgets: ~53

Memoria: 53 widgets × 5KB = 265KB
```

### Ventana Grande (4K 27")

```
viewport_height = 2000px
altura_promedio_línea = 30px
viewport_buffer = 10 + 10

Líneas visibles: 2000 / 30 = 66 líneas
Buffer: 20 líneas
TOTAL widgets: ~86

Memoria: 86 widgets × 5KB = 430KB
```

### Fullscreen (4K 32" vertical)

```
viewport_height = 3840px (4K rotado)
altura_promedio_línea = 30px
viewport_buffer = 10 + 10

Líneas visibles: 3840 / 30 = 128 líneas
Buffer: 20 líneas
TOTAL widgets: ~148

Memoria: 148 widgets × 5KB = 740KB
```

---

## Alturas NO Uniformes

La cantidad de widgets también varía según el **contenido** del documento:

### Documento con Líneas Cortas (Código)

```python
# Muchas líneas de código (altura pequeña)
MD_LINE_TYPE.CODE: 22px por línea

viewport_height = 1000px
Líneas que caben: 1000 / 22 = 45 líneas
+ Buffer: 20
TOTAL: ~65 widgets
```

### Documento con Títulos (Documentación)

```python
# Muchos títulos grandes
MD_LINE_TYPE.TITLE: 40px por línea

viewport_height = 1000px
Líneas que caben: 1000 / 40 = 25 líneas
+ Buffer: 20
TOTAL: ~45 widgets
```

### Documento con Text Wrapping

```python
# Líneas largas que hacen wrap
Línea corta (40 chars): 25px
Línea media (80 chars): 25px
Línea larga (120 chars): 50px (2 líneas de wrap)
Línea muy larga (200 chars): 75px (3 líneas de wrap)

viewport_height = 1000px
Altura promedio con wrapping: 40px
Líneas que caben: 1000 / 40 = 25 líneas
+ Buffer: 20
TOTAL: ~45 widgets
```

**Conclusión:** El número de widgets varía según el tipo de contenido.

---

## Actualización Dinámica al Resize

Cuando el usuario redimensiona la ventana, la cantidad de widgets se ajusta automáticamente:

```python
class MDDocumentEditor(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ...

        # Bind a cambios de tamaño
        self.bind(size=self._on_size_changed)

    def _on_size_changed(self, instance, value):
        """
        Evento disparado cuando cambia el tamaño de la ventana.

        Recalcula automáticamente widgets visibles.
        """
        new_width, new_height = value

        # viewport_height cambió → Recalcular
        self._refresh_visible_widgets()
```

### Ejemplo de Resize en Acción

```
ESTADO 1: Ventana pequeña
viewport_height = 600px
visible_indices = [10, 11, 12, ..., 29]  # 20 líneas visibles
+ buffer = [0-9, 30-39]                  # 20 líneas buffer
TOTAL = 40 widgets activos
recycled_pool = [] (vacío)

↓ Usuario MAXIMIZA ventana ↓

ESTADO 2: Ventana maximizada
viewport_height = 1200px
visible_indices = [10, 11, 12, ..., 49]  # 40 líneas visibles
+ buffer = [0-9, 50-59]                  # 20 líneas buffer
TOTAL = 60 widgets activos
recycled_pool = [] (vacío)

Cambios aplicados por update_visible_range():
- to_add = {30, 31, ..., 59}  (30 nuevas líneas)
- to_remove = {}               (nada se fue)
- Se crearon 30 widgets nuevos

↓ Usuario MINIMIZA ventana ↓

ESTADO 3: Ventana pequeña nuevamente
viewport_height = 600px
visible_indices = [10, 11, 12, ..., 29]  # 20 líneas visibles
+ buffer = [0-9, 30-39]                  # 20 líneas buffer
TOTAL = 40 widgets activos
recycled_pool = [20 widgets] (reciclados)

Cambios aplicados:
- to_add = {}                  (nada nuevo)
- to_remove = {40, 41, ..., 59} (20 líneas fuera)
- Se reciclaron 20 widgets al pool
```

---

## Comparación: Fijo vs Dinámico

### Diseño Incorrecto (Hardcoded)

```python
# ❌ MAL: Número fijo
MAX_WIDGETS = 50

def update_visible_range(self, visible_indices):
    # Limitar artificialmente
    visible_indices = visible_indices[:MAX_WIDGETS]
    # ...

Problemas:
- Ventana grande → Solo usa 50 widgets, desperdicia espacio
- Ventana pequeña → Crea 50 widgets, desperdicia memoria
- Resize → NO se adapta
```

### Diseño Correcto (Dinámico) ✅

```python
# ✅ BIEN: Número dinámico
def update_visible_range(self, visible_indices):
    # visible_indices ya tiene el tamaño correcto
    # Calculado por StateManager según viewport_height

    # Crear/reciclar tantos widgets como sean necesarios
    for index in to_add:
        if self.recycled_pool:
            widget = self.recycled_pool.pop()
        else:
            widget = MDDocumentLineEditor()  # Sin límite artificial

    # ...

Ventajas:
- Ventana grande → Más widgets automáticamente
- Ventana pequeña → Menos widgets automáticamente
- Resize → Se adapta instantáneamente
- Sin límites arbitrarios
```

---

## Ventaja del Buffer Dinámico

El buffer también puede ser dinámico:

```python
class StateManager:
    def __init__(self):
        # Buffer fijo (simple)
        self.viewport_buffer = 10  # Líneas

        # O buffer dinámico (avanzado)
        self.viewport_buffer_ratio = 0.3  # 30% del viewport

    def get_visible_in_viewport(self, scroll_y, viewport_height):
        # Buffer dinámico según tamaño de viewport
        if hasattr(self, 'viewport_buffer_ratio'):
            buffer_height = viewport_height * self.viewport_buffer_ratio
        else:
            buffer_height = self.viewport_buffer * 30  # Fijo

        viewport_start = scroll_pos - buffer_height
        viewport_end = scroll_pos + viewport_height + buffer_height

        # ...
```

### Comparación de Buffers

| Tamaño Ventana | Buffer Fijo (10 líneas) | Buffer Dinámico (30%) |
|----------------|------------------------|----------------------|
| 600px | 300px (10 × 30) | 180px (600 × 0.3) |
| 1000px | 300px | 300px |
| 2000px | 300px | 600px ✅ Mejor |

**Buffer dinámico** es mejor para ventanas grandes (más suavidad).

---

## Métricas Reales

### Memoria Según Tamaño de Ventana

| Ventana | viewport_height | Widgets | Memoria |
|---------|----------------|---------|---------|
| Móvil | 400px | ~30 | 150KB |
| Laptop 13" | 600px | ~40 | 200KB |
| Laptop 15" | 800px | ~47 | 235KB |
| Desktop 24" | 1000px | ~53 | 265KB |
| Desktop 27" | 1200px | ~60 | 300KB |
| 4K 32" | 2000px | ~86 | 430KB |
| 4K vertical | 3840px | ~148 | 740KB |

**Observación:** Incluso en 4K, solo 740KB de memoria para widgets. Excelente escalabilidad.

### Comparación con Alternativas

| Solución | Ventana Pequeña | Ventana 4K | Adaptable |
|----------|----------------|-----------|-----------|
| RecycleView estándar | ~20 widgets (100KB) | ~20 widgets (100KB) | ❌ No |
| ScrollView puro | 1000 widgets (5MB) | 1000 widgets (5MB) | ❌ No |
| **RecycleBoxLayout** | **~40 widgets (200KB)** | **~86 widgets (430KB)** | **✅ Sí** |

---

## Configuración Recomendada

```python
class StateManager:
    def __init__(self):
        # Buffer configurables
        self.viewport_buffer_lines = 10      # Líneas fijas arriba/abajo
        self.viewport_buffer_ratio = None    # O ratio (ej: 0.3)

        # Alturas estimadas (para cálculos iniciales)
        self.default_line_height = 30.0

        # Alturas por tipo (refinadas después de renderizar)
        self.line_type_heights = {
            MD_LINE_TYPE.TITLE: 40.0,
            MD_LINE_TYPE.TEXT: 25.0,
            MD_LINE_TYPE.CODE: 22.0,
            MD_LINE_TYPE.LIST: 28.0,
            MD_LINE_TYPE.TABLE: 35.0,
            # ...
        }
```

---

## Conclusión

### ✅ Correcto

- Cantidad de widgets es **completamente dinámica**
- Depende de `viewport_height` (altura de RecycleBoxLayout)
- Depende de alturas individuales de líneas (NO uniformes)
- Se ajusta automáticamente al resize
- Sin límites arbitrarios hardcoded

### ❌ Incorrecto (error en documentación original)

- "Total widgets necesarios: ~50 widgets" ← Número fijo
- Debió decir: "Widgets necesarios: DINÁMICO (30-150 según ventana)"

### Fórmula Final

```python
widgets_activos = len(get_visible_in_viewport(scroll_y, viewport_height))

donde:
    viewport_height = altura actual de RecycleBoxLayout
    scroll_y = posición actual de scroll

→ Resultado varía continuamente
→ Se recalcula en cada scroll y resize
→ Sin límites artificiales
```

**Esta arquitectura se adapta perfectamente a cualquier tamaño de ventana.**
