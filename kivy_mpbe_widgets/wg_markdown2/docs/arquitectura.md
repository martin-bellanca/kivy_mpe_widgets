# MDDocumentEditor V2 — Arquitectura (documento vivo)

**Módulo:** `kivy_mpbe_widgets/wg_markdown2`
**Última actualización:** 2026-06-30
**Estado:** Etapa I completa · Etapa II (edición) en progreso

Este es el documento **vivo**: refleja el código real y se actualiza en cada
incremento. El diseño original (con detalles ya superados) está en
[MDDocumentEditor_V2_Arquitectura.md](MDDocumentEditor_V2_Arquitectura.md).

> Los diagramas son **Mermaid**. Se renderizan en GitHub y en VS Code con la
> extensión *Markdown Preview Mermaid Support*.

---

## 1. Diagrama de clases (estado real)

```mermaid
classDiagram
    direction LR

    class MDDocumentEditor {
        <<ScrollView · FocusBehavior · ThemableBehavior>>
        +state_manager: DocumentStateManager
        +doc_lines_layout: BoxLayout
        +active_line_widget
        +populate_md_lines(md_document)
        +load_document(md_document)
        +activate_line(index, enter_edit_mode)
        +deactivate_current_line()
        +keyboard_on_key_down() placeholder
        -_refresh_visible_widgets()
    }

    class DocumentStateManager {
        <<EventDispatcher>>
        +set_document(md_document)
        +get_line_states() List~LineState~
        +get_state(index) LineState
        +get_active_index() int
        +update_state(index, **changes)
        +activate_line(index)
        +update_line_text(index, text)
        +insert_line(index, md_line)
        +remove_line(index)
        +move_line(from, to)
        +get_visible_in_viewport(scroll_y, h)
        +on_line_added() event
        +on_line_removed() event
        +on_line_moved() event
        +on_line_state_changed() event
    }

    class LineState {
        <<EventDispatcher>>
        +index: int
        +md_line: MDLine
        +active: bool
        +editing: bool
        +selected: bool
        +hotlight: bool
        +visible: bool
        +height / y_position
        +cursor_col / cursor_row
        +widget_type
        +get_md_text()
        +get_line_type()
        +update_type()
        +on_type_changed() event
    }

    class MDDocumentLine {
        <<BoxLayout · Inc 0>>
        +index: int
        +line_state: LineState
        +label: BaseMDLabel
    }

    class MDDocumentLineEditor {
        <<BoxLayout · ThemableBehavior · edit stack>>
        +line: MDLine
        +hotlight: bool
        +focused: bool
        +mode_editor: bool
        +wg_line_editor: MDLineEditor
        +wg_number_line / wg_drag_hook / wg_space
    }

    class MDLineEditor {
        <<FloatLayout>>
        +line: MDLine
        +md_editor: MDLineTextInput
        +active_label: BaseMDLabel
        +mode_editor: bool
        +show_editor(show, cursor)
        +show_anim_editor(show, cursor)
        +update_type()
    }

    class BaseMDLabel {
        <<Label>>
        +md_text
    }
    class MDTextLabel
    class MDHeadLabel
    class MDTableLabel
    class MDSeparatorLabel

    class MDDocument {
        <<helpers_mpbe>>
        +md_lines: list~MDLine~
        +load() / save()
    }
    class MDLine {
        <<helpers_mpbe>>
        +md_text
        +type
        +prev_line / next_line
    }

    MDDocumentEditor --> DocumentStateManager : usa (1)
    MDDocumentEditor *-- "n" MDDocumentLine : doc_lines_layout
    DocumentStateManager o-- "n" LineState : contiene
    LineState --> MDLine : referencia
    MDDocument o-- "n" MDLine : contiene

    MDDocumentLine *-- BaseMDLabel : label
    MDDocumentLine ..> LineState : observa (Inc 1/2)
    MDDocumentLine ..> MDLineEditor : embeberá (Inc 2)

    MDDocumentLineEditor *-- MDLineEditor
    MDLineEditor *-- BaseMDLabel : active_label
    BaseMDLabel <|-- MDTextLabel
    BaseMDLabel <|-- MDHeadLabel
    BaseMDLabel <|-- MDTableLabel
    BaseMDLabel <|-- MDSeparatorLabel

    LineState ..> BaseMDLabel : widget_type
```

> **Estado (Inc 0):** el coordinador ya instancia un `MDDocumentLine` por línea
> (fila liviana que envuelve el label de render y guarda su `LineState`).
> **Falta para editar:** que `MDDocumentLine` **observe** su `LineState`
> (reaccionar a `active` en Inc 1 y a `editing` en Inc 2, embebiendo el
> `MDLineEditor` existente). Esa es la conexión punteada aún pendiente.

---

## 2. Estados de una línea (UI)

Estado combinado de las propiedades `hotlight`, `active` y `editing` de
`LineState`. La transición a `editing` reusa `MDLineEditor.show_editor()`.

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> Hotlight : mouse_enter
    Hotlight --> Idle : mouse_leave

    Idle --> Active : click
    Hotlight --> Active : click
    Active --> Idle : click en otra línea / Esc

    Active --> Editing : Enter o doble click (editing=True, show_editor)
    Editing --> Active : Esc cancela / Enter o foco fuera confirma

    note right of Active
        active=True
        highlight visual
    end note
    note right of Editing
        editing=True
        TextInput visible y con foco
        texto sincroniza a MDLine
    end note
```

---

## 3. Flujo: click → activar → editar (objetivo Etapa II)

```mermaid
sequenceDiagram
    actor U as Usuario
    participant LW as MDDocumentLineEditor
    participant SM as DocumentStateManager
    participant LS as LineState
    participant ED as MDLineEditor

    U->>LW: click en la línea i
    LW->>SM: activate_line(i)
    SM->>LS: active=True (línea i)
    SM-->>LS: active=False (línea previa)
    LS-->>LW: evento on_active → highlight
    U->>LW: Enter / doble click
    LW->>SM: update_state(i, editing=True)
    SM->>LS: editing=True
    LS-->>ED: evento on_editing → show_editor(True)
    U->>ED: edita texto
    ED->>SM: update_line_text(i, texto)
    SM->>LS: md_line.md_text = texto
```

---

## 4. Roadmap de incrementos (Etapa II — edición)

Avanzamos **de a uno**, verificando en la app antes de seguir.

```mermaid
flowchart TD
    E1["Etapa I: render + scroll<br/>(labels solo lectura)"]:::done
    I0["Inc 0: render bound a LineState<br/>+ arreglar duplicación de widgets"]:::done
    I1["Inc 1: activación por click<br/>(activate_line + highlight)"]:::wip
    I2["Inc 2: modo edición<br/>(editing → show_editor)"]:::todo
    I3["Inc 3: salir/commit + teclado<br/>(Esc/Enter/flechas)"]:::todo

    E1 --> I0 --> I1 --> I2 --> I3

    classDef done fill:#bce6bc,stroke:#2e7d32,color:#000;
    classDef wip fill:#ffe9a8,stroke:#b8860b,color:#000;
    classDef todo fill:#eeeeee,stroke:#999,color:#333;
```

| # | Incremento | Estado | Verificación |
|---|-----------|--------|--------------|
| I | Render + scroll (labels) | ✅ Hecho | El documento se ve renderizado |
| 0 | Render bound a `LineState` + fix duplicación | ✅ Hecho | Cada línea es un `MDDocumentLine` atado a su `LineState`; el scroll ya no duplica |
| 1 | Activación por click | 🟡 En curso | Click resalta la línea; la anterior se apaga |
| 2 | Modo edición (`editing` → `show_editor`) | ⬜ Pendiente | Se puede tipear; el texto queda en el documento |
| 3 | Salir/commit + teclado | ⬜ Pendiente | Esc cancela, Enter confirma, flechas navegan |

### Bugs/incompletos conocidos
- ✅ ~~`populate_md_lines` y `_refresh_visible_widgets` duplican widgets~~ → resuelto en Inc 0 (construcción única + `_refresh_visible_widgets` no-op).
- ✅ ~~`initialize_document` usa atributos no inicializados~~ → resuelto en Inc 0 (limpieza segura).
- `activate_line` llama `doc_lines_layout.get_widget(index)`, pero `doc_lines_layout` es un `BoxLayout` plano sin ese método → **Inc 1** (usar el mapa `_line_widgets`).
- `load_document()` (camino alternativo, no usado por la app) llama `state_manager._load_document(md_lines)` con argumento, pero el método ya no lo recibe → revisar si se unifica con `populate_md_lines`.
