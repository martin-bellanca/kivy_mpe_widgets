# Test Document - wg_markdown2

Este es un documento de prueba para validar la funcionalidad del editor con RecycleBoxLayout.

## Características a Probar

### 1. Scroll Fluido

El editor debe permitir scroll suave sin lag. Los widgets se reciclan automáticamente cuando salen del viewport.

### 2. Reciclaje de Widgets

- Los widgets visibles NO se reciclan
- Los widgets fuera del viewport SÍ se reciclan
- El widget activo NUNCA se recicla

### 3. Alturas No Uniformes

Este documento tiene líneas de diferentes tipos y alturas:

#### Títulos (altura ~40px)

Los títulos ocupan más espacio.

#### Texto Normal (altura ~25px)

El texto normal es más compacto y permite más líneas en pantalla.

#### Listas (altura ~28px)

- Item 1 de lista
- Item 2 de lista
- Item 3 de lista con texto más largo que podría hacer wrap en ventanas pequeñas
- Item 4 de lista

#### Código (altura ~22px)

```python
def ejemplo():
    print("Código de ejemplo")
    return True
```

## Sección con Mucho Contenido

### Párrafo 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

### Párrafo 2

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

### Párrafo 3

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

### Párrafo 4

Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

### Párrafo 5

Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.

## Lista Numerada

1. Primer elemento
2. Segundo elemento
3. Tercer elemento
4. Cuarto elemento
5. Quinto elemento

## Tareas

- [ ] Tarea pendiente 1
- [ ] Tarea pendiente 2
- [x] Tarea completada 1
- [ ] Tarea pendiente 3
- [x] Tarea completada 2

## Citas

> Esta es una cita de ejemplo.
> Puede tener múltiples líneas.
> Y debe renderizarse correctamente.

## Separadores

---

## Más Contenido para Scroll

### Sección A

Contenido de la sección A con texto suficiente para probar el scroll.

### Sección B

Contenido de la sección B con más texto para llenar el documento.

### Sección C

Contenido de la sección C. Este documento debe tener al menos 100 líneas para probar el reciclaje de widgets efectivamente.

### Sección D

Más contenido en la sección D.

### Sección E

Y finalmente la sección E con contenido adicional.

## Líneas Adicionales para Alcanzar 100+

Línea 70
Línea 71
Línea 72
Línea 73
Línea 74
Línea 75
Línea 76
Línea 77
Línea 78
Línea 79
Línea 80
Línea 81
Línea 82
Línea 83
Línea 84
Línea 85
Línea 86
Línea 87
Línea 88
Línea 89
Línea 90
Línea 91
Línea 92
Línea 93
Línea 94
Línea 95
Línea 96
Línea 97
Línea 98
Línea 99
Línea 100

## Final del Documento

Esta es la última sección del documento de prueba.

¡Fin del test!
