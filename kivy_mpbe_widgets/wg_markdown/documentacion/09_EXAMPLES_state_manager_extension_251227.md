# Ejemplos de Uso - StateManager V2 con DataShow/DataThemed

## Autor: Martin Pablo Bellanca
## Fecha: 2025-12-27

---

## Caso de Uso 1: Configuración Inicial del Documento

```python
from kivy_mpbe_widgets.wg_markdown.state_manager import DocumentStateManager

# Crear el gestor de estados
manager = DocumentStateManager()

# Inicializar para un documento de 100 líneas
manager.initialize_states(100)

# Configuración inicial de UI (mostrar números de línea, ocultar árbol e infobar)
manager.set_show_number_line_all(True)   # Mostrar números por defecto
manager.set_show_tree_all(False)         # Ocultar árbol por defecto
manager.set_show_infobar_all(False)      # Ocultar infobar por defecto

# Aplicar patrón zebra para mejorar legibilidad
manager.set_alpha_background_zebra(0.0, 0.08)
```

---

## Caso de Uso 2: Toggle de Números de Línea (Botón UI)

```python
class MyMarkdownEditor:
    def __init__(self):
        self.state_manager = DocumentStateManager()
        self.show_numbers = True  # Estado del toggle

    def on_toggle_line_numbers_clicked(self):
        """Handler del botón para mostrar/ocultar números de línea."""
        self.show_numbers = not self.show_numbers
        self.state_manager.set_show_number_line_all(self.show_numbers)

        # Los observadores recibirán notificaciones automáticamente
        # y actualizarán los widgets correspondientes
```

---

## Caso de Uso 3: Vista de Árbol Jerárquico

```python
def toggle_tree_view(self, show_tree: bool):
    """
    Mostrar/ocultar la vista de árbol jerárquico.

    La vista de árbol muestra la estructura de títulos y listas
    del documento markdown.
    """
    self.state_manager.set_show_tree_all(show_tree)

    # Opcional: ajustar el ancho del panel izquierdo si el árbol está visible
    if show_tree:
        self.left_panel_width = 250  # Más ancho
    else:
        self.left_panel_width = 50   # Más estrecho
```

---

## Caso de Uso 4: Modo Debug/Desarrollador

```python
def enable_developer_mode(self):
    """
    Modo desarrollador: muestra toda la información disponible.
    """
    # Mostrar todos los sub-widgets
    self.state_manager.set_show_number_line_all(True)
    self.state_manager.set_show_tree_all(True)
    self.state_manager.set_show_infobar_all(True)

    # Sin fondo zebra para no distraer
    self.state_manager.set_alpha_background_all(0.0)

    print("Modo desarrollador activado")
    self.state_manager.print_state_summary()

def disable_developer_mode(self):
    """
    Volver al modo normal de usuario.
    """
    # Configuración minimalista
    self.state_manager.set_show_number_line_all(True)
    self.state_manager.set_show_tree_all(False)
    self.state_manager.set_show_infobar_all(False)

    # Fondo zebra sutil
    self.state_manager.set_alpha_background_zebra(0.0, 0.08)
```

---

## Caso de Uso 5: Highlighting de Sección Activa

```python
def highlight_active_section(self, active_index: int):
    """
    Resalta visualmente la sección activa del documento.

    Aumenta el alpha_background de las líneas cercanas a la línea activa
    para crear un efecto de "spotlight".
    """
    # Resetear todo a transparente
    self.state_manager.set_alpha_background_all(0.0)

    # Definir rango de highlight (±5 líneas)
    highlight_range = 5

    for offset in range(-highlight_range, highlight_range + 1):
        index = active_index + offset
        if 0 <= index < len(self.state_manager._states):
            # Alpha más fuerte cerca del centro
            distance = abs(offset)
            alpha = max(0.0, 0.2 - (distance * 0.03))
            self.state_manager.set_alpha_background(index, alpha)
```

---

## Caso de Uso 6: Configuración Personalizada por Tipo de Línea

```python
from helpers_mpbe.markdown_document import MD_LINE_TYPE

def configure_line_display(self, index: int, md_line):
    """
    Configura la visibilidad de sub-widgets según el tipo de línea.

    Ejemplo: Mostrar árbol solo en títulos, infobar solo en tablas.
    """
    line_type = md_line.type

    if line_type == MD_LINE_TYPE.TITLE:
        # Títulos: mostrar árbol para navegación
        self.state_manager.set_show_tree(index, True)
        self.state_manager.set_show_infobar(index, False)

    elif line_type == MD_LINE_TYPE.TABLE:
        # Tablas: mostrar infobar con dimensiones
        self.state_manager.set_show_tree(index, False)
        self.state_manager.set_show_infobar(index, True)

    elif line_type == MD_LINE_TYPE.CODE:
        # Código: infobar con lenguaje
        self.state_manager.set_show_tree(index, False)
        self.state_manager.set_show_infobar(index, True)

    else:
        # Otras líneas: configuración por defecto
        self.state_manager.set_show_tree(index, False)
        self.state_manager.set_show_infobar(index, False)
```

---

## Caso de Uso 7: Observer Pattern - Actualización de Widgets

```python
class MDDocumentLineEditor:
    """
    Widget que representa una línea del documento.

    Suscribe al StateManager para recibir actualizaciones automáticas.
    """

    def __init__(self, state_manager, index):
        self.state_manager = state_manager
        self.index = index

        # Suscribirse a cambios de estado
        self.state_manager.subscribe(self.on_state_changed)

    def on_state_changed(self, event):
        """
        Callback llamado cuando cambia el estado de cualquier línea.

        Solo procesamos cambios para nuestro índice.
        """
        if event.index != self.index:
            return  # No es nuestra línea

        # Verificar qué atributos cambiaron
        changed = event.changed_attributes

        if 'show_number_line' in changed:
            self.update_number_line_visibility(event.new_state.show_number_line)

        if 'show_tree' in changed:
            self.update_tree_visibility(event.new_state.show_tree)

        if 'show_infobar' in changed:
            self.update_infobar_visibility(event.new_state.show_infobar)

        if 'alpha_background' in changed:
            self.update_background_opacity(event.new_state.alpha_background)

    def update_number_line_visibility(self, visible: bool):
        """Muestra u oculta el widget de número de línea."""
        if visible:
            self.wg_number_line.opacity = 1.0
            self.wg_number_line.size_hint_x = None
            self.wg_number_line.width = dp(38)
        else:
            self.wg_number_line.opacity = 0.0
            self.wg_number_line.width = 0

    def update_tree_visibility(self, visible: bool):
        """Muestra u oculta el gancho de árbol."""
        if visible:
            self.wg_tree_hook.opacity = 1.0
            self.wg_tree_hook.width = dp(16)
        else:
            self.wg_tree_hook.opacity = 0.0
            self.wg_tree_hook.width = 0

    def update_infobar_visibility(self, visible: bool):
        """Muestra u oculta la barra de información."""
        if visible:
            self.wg_info_bar.opacity = 1.0
            self.wg_info_bar.width = dp(80)
        else:
            self.wg_info_bar.opacity = 0.0
            self.wg_info_bar.width = 0

    def update_background_opacity(self, alpha: float):
        """Actualiza la opacidad del fondo."""
        self.background_color = (0.5, 0.5, 0.5, alpha)  # Gris con opacidad variable
```

---

## Caso de Uso 8: Configuración desde Archivo Config

```python
from configparser import ConfigParser

def load_ui_config_from_file(self, config_path: str):
    """
    Carga configuración de UI desde archivo .ini

    Ejemplo de archivo config.ini:
    [UI]
    show_number_line = True
    show_tree = False
    show_infobar = False
    zebra_pattern = True
    alpha_even = 0.0
    alpha_odd = 0.08
    """
    config = ConfigParser()
    config.read(config_path)

    # Leer configuración
    show_numbers = config.getboolean('UI', 'show_number_line', fallback=True)
    show_tree = config.getboolean('UI', 'show_tree', fallback=False)
    show_infobar = config.getboolean('UI', 'show_infobar', fallback=False)
    zebra = config.getboolean('UI', 'zebra_pattern', fallback=True)
    alpha_even = config.getfloat('UI', 'alpha_even', fallback=0.0)
    alpha_odd = config.getfloat('UI', 'alpha_odd', fallback=0.08)

    # Aplicar configuración
    self.state_manager.set_show_number_line_all(show_numbers)
    self.state_manager.set_show_tree_all(show_tree)
    self.state_manager.set_show_infobar_all(show_infobar)

    if zebra:
        self.state_manager.set_alpha_background_zebra(alpha_even, alpha_odd)
    else:
        self.state_manager.set_alpha_background_all(0.0)

def save_ui_config_to_file(self, config_path: str):
    """Guarda la configuración actual a archivo."""
    config = ConfigParser()

    # Obtener estado de primera línea como referencia (asumiendo configuración global)
    state = self.state_manager.get_state(0)

    config['UI'] = {
        'show_number_line': str(state.show_number_line),
        'show_tree': str(state.show_tree),
        'show_infobar': str(state.show_infobar),
        # Detectar si hay patrón zebra comparando líneas pares e impares
        'zebra_pattern': 'True',  # Simplificado
        'alpha_even': '0.0',
        'alpha_odd': '0.08'
    }

    with open(config_path, 'w') as f:
        config.write(f)
```

---

## Caso de Uso 9: Animación de Transición

```python
from kivy.animation import Animation

def animate_alpha_transition(self, target_alpha: float, duration: float = 0.3):
    """
    Anima la transición de alpha_background de forma suave.

    Nota: StateManager no soporta animaciones directamente,
    pero podemos simularlas con updates incrementales.
    """
    # Obtener valores actuales
    current_alphas = [
        self.state_manager.get_state(i).alpha_background
        for i in range(len(self.state_manager._states))
    ]

    # Calcular steps para la animación
    fps = 60
    frames = int(duration * fps)

    def update_frame(frame_num):
        progress = frame_num / frames

        for i, current_alpha in enumerate(current_alphas):
            # Interpolación lineal
            new_alpha = current_alpha + (target_alpha - current_alpha) * progress
            self.state_manager.set_alpha_background(i, new_alpha)

    # Programar frames de animación
    from kivy.clock import Clock

    for frame in range(frames + 1):
        Clock.schedule_once(lambda dt, f=frame: update_frame(f), frame / fps)
```

---

## Caso de Uso 10: Debugging y Diagnóstico

```python
def diagnose_document_state(self):
    """
    Función de diagnóstico para debugging.

    Imprime información detallada del estado del documento.
    """
    print("\n" + "="*80)
    print("DIAGNÓSTICO DEL DOCUMENTO")
    print("="*80)

    # Resumen general
    self.state_manager.print_state_summary()

    # Verificar invariantes
    print("\nValidación de invariantes:")
    if self.state_manager.validate_invariants():
        print("✓ Todos los invariantes son válidos")
    else:
        print("✗ ADVERTENCIA: Hay invariantes inválidos")

    # Analizar configuración de visibilidad
    print("\nAnálisis de configuración:")

    all_states = self.state_manager.get_all_states()

    # Verificar si la configuración es homogénea
    first_state = all_states[0]
    is_uniform_numbers = all(s.show_number_line == first_state.show_number_line for s in all_states.values())
    is_uniform_tree = all(s.show_tree == first_state.show_tree for s in all_states.values())
    is_uniform_infobar = all(s.show_infobar == first_state.show_infobar for s in all_states.values())

    print(f"  Configuración uniforme de números: {is_uniform_numbers}")
    print(f"  Configuración uniforme de árbol: {is_uniform_tree}")
    print(f"  Configuración uniforme de infobar: {is_uniform_infobar}")

    # Detectar patrón zebra
    alphas = [s.alpha_background for s in all_states.values()]
    is_zebra = len(set(alphas[::2])) == 1 and len(set(alphas[1::2])) == 1 and alphas[0] != alphas[1]

    if is_zebra:
        print(f"  Patrón zebra detectado: even={alphas[0]}, odd={alphas[1]}")
    else:
        print(f"  Sin patrón zebra")

    print("="*80 + "\n")


def find_lines_with_custom_config(self):
    """
    Encuentra líneas con configuración personalizada (no estándar).

    Útil para detectar configuraciones manuales específicas.
    """
    custom_lines = []

    for index, state in self.state_manager.get_all_states().items():
        # Comparar con configuración estándar
        is_custom = (
            state.show_number_line != True or
            state.show_tree != False or
            state.show_infobar != False
        )

        if is_custom:
            custom_lines.append({
                'index': index,
                'show_number_line': state.show_number_line,
                'show_tree': state.show_tree,
                'show_infobar': state.show_infobar,
                'alpha_background': state.alpha_background
            })

    if custom_lines:
        print(f"\nEncontradas {len(custom_lines)} líneas con configuración personalizada:")
        for line in custom_lines:
            print(f"  Línea {line['index']}: {line}")
    else:
        print("\nTodas las líneas usan configuración estándar")

    return custom_lines
```

---

## Caso de Uso 11: Perfiles de Configuración

```python
class UIProfile:
    """Clase para manejar perfiles de configuración de UI."""

    PROFILES = {
        'minimal': {
            'show_number_line': False,
            'show_tree': False,
            'show_infobar': False,
            'alpha_background': 0.0
        },
        'standard': {
            'show_number_line': True,
            'show_tree': False,
            'show_infobar': False,
            'zebra': (0.0, 0.08)
        },
        'developer': {
            'show_number_line': True,
            'show_tree': True,
            'show_infobar': True,
            'alpha_background': 0.0
        },
        'presentation': {
            'show_number_line': False,
            'show_tree': True,
            'show_infobar': False,
            'zebra': (0.0, 0.12)
        }
    }

    @staticmethod
    def apply_profile(state_manager, profile_name: str):
        """Aplica un perfil de configuración predefinido."""
        if profile_name not in UIProfile.PROFILES:
            raise ValueError(f"Perfil '{profile_name}' no existe")

        profile = UIProfile.PROFILES[profile_name]

        # Aplicar configuración
        state_manager.set_show_number_line_all(
            profile.get('show_number_line', True)
        )
        state_manager.set_show_tree_all(
            profile.get('show_tree', False)
        )
        state_manager.set_show_infobar_all(
            profile.get('show_infobar', False)
        )

        # Aplicar alpha
        if 'zebra' in profile:
            even, odd = profile['zebra']
            state_manager.set_alpha_background_zebra(even, odd)
        else:
            alpha = profile.get('alpha_background', 0.0)
            state_manager.set_alpha_background_all(alpha)

        print(f"Perfil '{profile_name}' aplicado")


# Uso
UIProfile.apply_profile(manager, 'developer')
```

---

## Caso de Uso 12: Migración desde Legacy Code

```python
def migrate_from_legacy_data_items(self, legacy_data_items: list):
    """
    Migra desde el formato legacy (DataShow/DataThemed) al StateManager V2.

    Args:
        legacy_data_items: Lista de diccionarios con formato legacy
    """
    # Inicializar states
    self.state_manager.initialize_states(len(legacy_data_items))

    # Migrar cada item
    for index, item in enumerate(legacy_data_items):
        # Extraer valores legacy
        show = item.get('show', {})
        themed = item.get('themed', {})

        # Aplicar a StateManager V2
        if 'show_number_line' in show:
            self.state_manager.set_show_number_line(index, show['show_number_line'])

        if 'show_tree' in show:
            self.state_manager.set_show_tree(index, show['show_tree'])

        if 'show_infobar' in show:
            self.state_manager.set_show_infobar(index, show['show_infobar'])

        if 'alpha_background' in themed:
            self.state_manager.set_alpha_background(index, themed['alpha_background'])

    print(f"Migración completada: {len(legacy_data_items)} líneas")
    self.state_manager.print_state_summary()
```

---

## Resumen de Patrones Comunes

### 1. Configuración Global
```python
manager.set_show_*_all(value)          # Aplicar a todo el documento
manager.set_alpha_background_all(alpha) # Opacidad uniforme
```

### 2. Configuración Individual
```python
manager.set_show_*(index, value)       # Configurar línea específica
manager.set_alpha_background(index, alpha)
```

### 3. Patrón Zebra
```python
manager.set_alpha_background_zebra(even, odd)  # Alternar pares/impares
```

### 4. Observer Pattern
```python
def callback(event):
    if 'show_*' in event.changed_attributes:
        # Actualizar UI

manager.subscribe(callback)
```

### 5. Estado de Línea
```python
state = manager.get_state(index)
if state.show_number_line:
    # ...
```

---

**Fin de Ejemplos de Uso**
