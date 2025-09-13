# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Testing Individual Components
```bash
# Run specific widget tests
python ./kivy_mpbe_widgets/wg_inputs/_test_editable_label.py
python ./kivy_mpbe_widgets/wg_inputs/_test_input_filter.py
python ./kivy_mpbe_widgets/wg_inputs/_test_input_search.py
python ./kivy_mpbe_widgets/wg_markdown/_test_mardown_document_1.py

# Test other widget categories
python ./kivy_mpbe_widgets/wg_buttons/_test_*.py
python ./kivy_mpbe_widgets/wg_labels/_test_*.py
```

### Development Environment
- Uses virtual environment at `.venv/`
- Main dependencies: Kivy, helpers_mpbe (external helper library)

## Architecture Overview

### Core Widget System
This is a **Kivy-based desktop widget framework** with a hierarchical inheritance structure:
- `ThemeWidget` (base themed container) → `FocusedWidget` (adds focus management) → Specific widgets
- All widgets support theming through `ThemableBehavior` and centralized `Theme` class
- Custom graphics system using `GFace`, `GBorder`, `GFocus`, `GHotLight` components

### Widget Categories
Located in `/kivy_mpbe_widgets/`:
- **`wg_inputs/`**: Text inputs with filtering/search capabilities
- **`wg_buttons/`**: Click and toggle buttons  
- **`wg_labels/`**: Text, icon, and image labels
- **`wg_lists/`**: List views and recycled list widgets
- **`wg_tree_panels/`**: Tree view components
- **`wg_panels/`**: Container and layout panels
- **`wg_markdown/`**: Markdown document system (see below)

### Markdown Document System
Core classes in `/wg_markdown/`:
- **`MDDocument`**: Main document class managing markdown content line-by-line
- **`MDLine`**: Individual markdown lines with auto-detection of types (title, list, task, etc.)
- **Line Types**: `TEXT`, `TITLE`, `HEAD_TITLE`, `SEPARATOR`, `LIST`, `ORDER_LIST`, `TASK`, `TODO`, `TABLE`, `BLOCKQUOTE`, `IMAGEN`, `CODE`
- Uses regex patterns in `TYPE_PATTERNS` for markdown element identification

### Search and Filter Widgets
Recent focus on document filtering/search:
- **`InputFilter`**: Text input with toggle icon for filtering mode
- **`InputSearch`**: Text input with search button and `on_search` events
- **`InputSearchOrFilter`**: Advanced widget combining:
  - Parent selection toggle (`chevron-double-up` icon)
  - Text input field
  - Filter toggle (`filter-outline` icon)
  - Search button (`magnify` icon)

### Command Pattern (Undo/Redo)
**`UndoManager`** implements complete command pattern system:
- `Command` base class with `execute()` and `undo()` methods
- Maintains undo/redo stacks with automatic history tracking
- Recent implementations include `TextModifiedCommand` and delete operations

### Event System
Specialized event dispatchers handle complex interactions:
- `HotlightEventDispatcher`: Mouse hover effects
- `StartEditingEventDispatcher`/`FinishEditingEventDispatcher`: Edit mode transitions
- Focus management and keyboard navigation throughout widget hierarchy

### Resource Structure
- **`/rsrc_themes/`**: Theme definition files (.theme, .style)
- **`/rsrc_fonts/`**: Roboto font family + Material Design icons
- **`/rsrc_images/`**: Toolbar and UI icons  
- **`/rsrc_fonts_icons/`**: Icon font definitions

### Key Patterns
1. **Container Pattern**: Widgets use internal containers for layout management
2. **Event-Driven Design**: Extensive custom event dispatching beyond standard Kivy events  
3. **Theme Consistency**: All widgets inherit theming capabilities from `ThemeWidget`
4. **Command Encapsulation**: All document modifications use command pattern for undo/redo
5. **Linked-List Document Structure**: `MDLine` objects maintain prev/next references for efficient navigation

### Testing Convention
Each widget module includes corresponding `_test_*.py` files for development and verification. Run these directly with Python to test individual components.