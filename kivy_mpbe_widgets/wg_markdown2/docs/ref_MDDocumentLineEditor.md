# Referencia — `MDDocumentLineEditor` (stack de edición completo)

Diagrama de clases del **widget de línea editable completo** de `wg_markdown2`
(`widgets/md_line_editor.py` + `widgets/md_line_widgets.py` + `widgets/md_inputs.py`
+ labels de `helpers_mpbe.markdown_document.md_labels`).

Sirve de **referencia** para reusar sus piezas y animaciones al codificar la
edición/navegación en el `MDDocumentEditor` V2 (que hoy usa el `MDDocumentLine`
liviano). Se renderiza con la extensión *Markdown Preview Mermaid Support*.

```mermaid
classDiagram
    direction LR

    class MDDocumentLineEditor {
        <<BoxLayout · ThemableBehavior>>
        +line: MDLine
        +num_line: int
        +hidden_line: bool
        +hotlight: bool
        +focused: bool
        +mode_editor: bool
        +md_text: str
        +type: MD_LINE_TYPE
        +wg_drag_hook: MDDLDrag
        +wg_number_line: MDDLNumberLine
        +wg_tree_hook: MDDLTree_hook
        +wg_info_bar: MDDLInfoBar
        +wg_space: MDDLSpace
        +wg_line_editor: MDLineEditor
        +show_number_line(value, number)
        +show_tree_hook(value)
        +show_info_bar(value)
        +on_mouse_move(instance, mp)
        +on_mode_editor(instance, value)
        -_update_height()
    }

    class MDLineEditor {
        <<FloatLayout>>
        +line: MDLine
        +md_editor: MDLineTextInput
        +active_label: BaseMDLabel
        +mode_editor: bool
        +md_text: str
        +type: MD_LINE_TYPE
        +show_editor(show, cursor)
        +show_anim_editor(show, cursor)
        +opacity_editor(value)
        +update_type()
        +md_editor_focus(cursor)
        +on_txt_change(instance, value)
        +on_key_up(win, keycode, scancode)
        +on_focus(instance, value)
    }

    class MDLineTextInput {
        <<TextInput>>
        +insert_text(substring)
        +do_insert_pair(pair, offset)
        +do_replace_start(new, old)
    }

    class MDDLDrag {
        <<Widget · w=10>>
    }
    class MDDLNumberLine {
        <<Label · w=38>>
    }
    class MDDLTree_hook {
        <<Widget · w=16>>
    }
    class MDDLInfoBar {
        <<StackLayout · w=80>>
    }
    class MDDLSpace {
        <<Widget · w=6>>
    }

    class BaseMDLabel {
        <<EventDispatcher>>
        +md_text: str
        +on_md_text(instance, value)
    }
    class MDTextLabel {
        <<Label>>
    }
    class MDHeadLabel
    class MDSeparatorLabel {
        <<Widget>>
    }
    class MDTableLabel {
        <<GridLayout>>
    }
    class MDTaskLabel
    class MDToDoLabel
    class MDCodeLabel
    class MDImageLabel
    class MDBlockQuoteLabel

    class MDLine {
        <<helpers_mpbe>>
        +md_text
        +type
        +prev_line / next_line
    }

    MDDocumentLineEditor *-- MDDLDrag
    MDDocumentLineEditor *-- MDDLNumberLine
    MDDocumentLineEditor *-- MDDLTree_hook
    MDDocumentLineEditor *-- MDDLInfoBar
    MDDocumentLineEditor *-- MDDLSpace
    MDDocumentLineEditor *-- MDLineEditor
    MDDocumentLineEditor --> MDLine : line

    MDLineEditor *-- MDLineTextInput : md_editor
    MDLineEditor *-- BaseMDLabel : active_label
    MDLineEditor --> MDLine : line

    BaseMDLabel <|-- MDTextLabel
    BaseMDLabel <|-- MDHeadLabel
    BaseMDLabel <|-- MDSeparatorLabel
    BaseMDLabel <|-- MDTableLabel
    MDTextLabel <|-- MDTaskLabel
    MDTextLabel <|-- MDToDoLabel
    MDTextLabel <|-- MDCodeLabel
    MDTextLabel <|-- MDImageLabel
    MDTextLabel <|-- MDBlockQuoteLabel
```

## Composición visual de la fila (izquierda → derecha)

```
[MDDLDrag][MDDLNumberLine][MDDLTree_hook][MDDLInfoBar][MDDLSpace][ MDLineEditor .......... ]
   w=10        w=38            w=16          w=80        w=6      (label render + input overlay)
```

- `MDDLDrag`: manija para arrastrar/reordenar (drag & drop).
- `MDDLNumberLine`: número de línea (bordes verticales).
- `MDDLTree_hook`: gancho del árbol/jerarquía de títulos.
- `MDDLInfoBar`: barra de información.
- `MDDLSpace`: separador.
- `MDLineEditor`: el editor real (label de render + `MDLineTextInput` superpuesto,
  con `show_editor()` / `show_anim_editor()` y sincronización de texto en vivo).

## Qué reusar en V2

- **`MDLineTextInput`**: ya reusado en `MDDocumentLine` (Inc 2).
- **`MDLineEditor.show_editor` / `show_anim_editor`**: mecánica de overlay + fade
  (referencia para pulir la animación de entrada/salida de edición).
- **Sub-widgets** (`MDDLNumberLine`, `MDDLTree_hook`, `MDDLInfoBar`, `MDDLDrag`):
  candidatos a incorporar a `MDDocumentLine` cuando se agreguen número de línea,
  árbol de títulos, drag & drop, etc.
