# Changelog - StateManager V2 Extensions

## Fecha: 2025-12-27
## Autor: Martin Pablo Bellanca (con asistencia de Claude Code)

---

## Resumen de Cambios

Se agregaron **4 nuevas variables de estado** al módulo `state_manager.py` para soportar la migración completa desde las clases obsoletas `DataShow` y `DataThemed` a la arquitectura V2.

### Variables Agregadas a `LineState`

#### 1. Variables de Visibilidad de Sub-widgets (reemplazan `DataShow`)

```python
show_number_line: bool = True   # Muestra el número de línea
show_tree: bool = False          # Muestra el gancho de árbol
show_infobar: bool = False       # Muestra la barra de información
```

#### 2. Variables de Tema (reemplazan `DataThemed`)

```python
alpha_background: float = 0.0    # Opacidad del fondo (0.0-1.0)
```

---

## Cambios Detallados

### 1. Clase `LineState` (líneas 40-132)

**Modificaciones:**
- Agregados 4 nuevos atributos al dataclass frozen
- Actualizado `__repr__()` para mostrar configuración de sub-widgets y tema
- Las nuevas variables funcionan con `with_changes()` (inmutabilidad mantenida)

**Ejemplo de salida:**
```python
LineState[5](SEL|ACT|TREE|INFO|BG:0.5)
# SEL = seleccionada
# ACT = activa
# TREE = show_tree activado
# INFO = show_infobar activado
# BG:0.5 = alpha_background = 0.5
```

### 2. Clase `StateChangeEvent` (líneas 156-174)

**Modificaciones:**
- `changed_attributes` property actualizado para detectar cambios en las 4 nuevas variables
- Soporte completo para notificaciones de observadores

**Atributos detectados:**
- `show_number_line`
- `show_tree`
- `show_infobar`
- `alpha_background`

### 3. Clase `DocumentStateManager` - Nuevos Métodos

#### Sección: Visibilidad de Sub-widgets (líneas 472-555)

**Métodos individuales:**
```python
set_show_number_line(index, value)  # Configurar línea específica
set_show_tree(index, value)
set_show_infobar(index, value)
```

**Métodos globales:**
```python
set_show_number_line_all(value)     # Aplicar a TODAS las líneas
set_show_tree_all(value)
set_show_infobar_all(value)
```

#### Sección: Tema (líneas 557-614)

**Métodos individuales:**
```python
set_alpha_background(index, alpha)  # Configurar línea específica
                                    # Validación automática: 0.0 ≤ alpha ≤ 1.0
```

**Métodos globales:**
```python
set_alpha_background_all(alpha)     # Aplicar a TODAS las líneas

set_alpha_background_zebra(         # Patrón zebra (cebra)
    alpha_even=0.0,                 # Opacidad líneas pares
    alpha_odd=0.1                   # Opacidad líneas impares
)
```

**Ejemplo de uso del patrón zebra:**
```python
manager.set_alpha_background_zebra(0.0, 0.15)
# Líneas pares: fondo transparente (0.0)
# Líneas impares: fondo 15% opaco (0.15)
# Mejora legibilidad en documentos largos
```

### 4. Método `print_state_summary()` (líneas 789-831)

**Modificaciones:**
- Nueva sección "Sub-widget visibility" con estadísticas:
  - Cantidad de líneas con `show_number_line` activo
  - Cantidad de líneas con `show_tree` activo
  - Cantidad de líneas con `show_infobar` activo

- Nueva sección "Theme" con estadísticas:
  - Promedio de `alpha_background` en todas las líneas
  - Cantidad de líneas con alpha > 0.0

**Ejemplo de salida:**
```
Sub-widget visibility:
  show_number_line: 10
  show_tree: 2
  show_infobar: 1

Theme:
  avg alpha_background: 0.07
  lines with alpha > 0: 5
```

---

## Testing

Se creó `test_state_manager.py` con **8 tests comprehensivos**:

1. ✓ Valores por defecto de `LineState`
2. ✓ Modificación con `with_changes()`
3. ✓ Métodos individuales del `DocumentStateManager`
4. ✓ Métodos globales (`*_all`)
5. ✓ Patrón zebra para `alpha_background`
6. ✓ Sistema de observadores con nuevas variables
7. ✓ `print_state_summary()` con nuevas secciones
8. ✓ `validate_invariants()` con nuevas variables

**Resultado:** ✓✓✓ **TODOS LOS TESTS PASARON EXITOSAMENTE** ✓✓✓

---

## API Summary

### Acceso desde LineState (lectura)

```python
state = manager.get_state(index)

# Visibilidad de sub-widgets
if state.show_number_line:
    # Mostrar número de línea
if state.show_tree:
    # Mostrar gancho de árbol
if state.show_infobar:
    # Mostrar barra de información

# Tema
opacity = state.alpha_background  # 0.0 - 1.0
```

### Modificación individual

```python
manager.set_show_number_line(5, False)
manager.set_show_tree(3, True)
manager.set_show_infobar(7, True)
manager.set_alpha_background(2, 0.5)
```

### Modificación global (todo el documento)

```python
# Ocultar números de línea en todo el documento
manager.set_show_number_line_all(False)

# Mostrar árbol en todo el documento
manager.set_show_tree_all(True)

# Mostrar infobar en todo el documento
manager.set_show_infobar_all(True)

# Fondo semi-transparente en todo el documento
manager.set_alpha_background_all(0.2)

# Patrón zebra para mejorar legibilidad
manager.set_alpha_background_zebra(0.0, 0.15)
```

### Notificaciones (Observer Pattern)

```python
def on_state_changed(event):
    if 'show_number_line' in event.changed_attributes:
        # Actualizar widget de número de línea
    if 'show_tree' in event.changed_attributes:
        # Actualizar widget de árbol
    if 'show_infobar' in event.changed_attributes:
        # Actualizar widget de infobar
    if 'alpha_background' in event.changed_attributes:
        # Actualizar opacidad del fondo

manager.subscribe(on_state_changed)
```

---

## Compatibilidad

### ✓ Mantiene compatibilidad con variables existentes

Todas las variables y métodos existentes siguen funcionando:
- `selected`, `active`, `editing`, `hotlight`, `visible`, `cursor_pos`
- Métodos de selección, activación, navegación, etc.

### ✓ Mantiene inmutabilidad

`LineState` sigue siendo inmutable (`frozen=True`):
```python
state = LineState(index=5, show_tree=False)
# state.show_tree = True  # ❌ ERROR: No se puede modificar

# ✓ Usar with_changes()
new_state = state.with_changes(show_tree=True)
```

### ✓ Mantiene validación de invariantes

`validate_invariants()` funciona correctamente con las nuevas variables.

---

## Migración desde DataShow/DataThemed

### Antes (Legacy):

```python
# DataShow
data_show = DataShow(
    show_number_line=True,
    show_tree=False,
    show_infobar=False
)

# DataThemed
data_themed = DataThemed(
    alpha_background=0.0
)

# Empaquetar en DataLineMDD
data_item = DataLineMDD(md_line, data_themed, data_show, data_state)
dict_item = data_item.to_dict()
```

### Después (V2):

```python
# Todo en LineState
state = manager.get_state(index)

# Acceso directo
state.show_number_line
state.show_tree
state.show_infobar
state.alpha_background

# Modificación
manager.set_show_number_line(index, True)
manager.set_alpha_background(index, 0.5)
```

---

## Ventajas de la Nueva Arquitectura

1. **Single Source of Truth**: Una sola clase `LineState` para todo el estado
2. **Inmutabilidad**: Previene modificaciones accidentales
3. **Observers**: Notificaciones automáticas de cambios
4. **Validación**: Rango de `alpha_background` validado automáticamente (0.0-1.0)
5. **Debugging**: `print_state_summary()` incluye toda la información
6. **Métodos globales**: Fácil aplicar cambios a todo el documento
7. **Patrón zebra**: Built-in para mejorar legibilidad

---

## Próximos Pasos (Sugeridos)

1. Actualizar `MDDocumentLineEditor` para usar `state.show_*` en lugar de `DataShow`
2. Actualizar `MDDocumentLineEditor` para usar `state.alpha_background` en lugar de `DataThemed`
3. Eliminar clases obsoletas `DataShow` y `DataThemed` de `md_recycleview_le_data_item.py`
4. Actualizar `MDDocumentEditorV2` para usar los nuevos métodos globales

---

## Notas Técnicas

- **Complejidad temporal** de métodos `*_all()`: O(n) donde n = cantidad de líneas
- **Notificaciones**: Cada línea genera un evento individual (útil para actualización granular)
- **Validación de alpha**: `max(0.0, min(1.0, alpha))` garantiza rango válido
- **Patrón zebra**: Usa `index % 2` para determinar par/impar

---

## Versión

- **StateManager V2**: Extensión con soporte DataShow/DataThemed
- **Líneas de código agregadas**: ~180
- **Tests agregados**: 8 (100% cobertura de nuevas funcionalidades)
- **Compatibilidad**: 100% backward compatible

---

**Fin del Changelog**
