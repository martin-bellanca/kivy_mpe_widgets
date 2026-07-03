#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  text_labels.py
#
#  Copyright 2012 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

'''
Created on 15/09/2019

@author: mpbe
'''

# imports del sistema -------------------------------------------------------
from helpers_mpbe.python import compose_dict
# Kivy imports --------------------------------------------------------------
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.behaviors import FocusBehavior
from kivy.core.text import Label as CTLabel
from kivy.core.text.text_layout import layout_text as LText
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.label import Label as KVLabel
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import OptionProperty

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
import kivy_mpbe_widgets.rsrc_themes
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.base_widgets import ThemeWidget
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickIcon
from kivy_mpbe_widgets.wg_buttons.toggle_buttons import ToggleIcon
from kivy_mpbe_widgets.events.input_events import StartEditingEventDispatcher, FinishEditingEventDispatcher

# Works Dirs ----------------------------------------------------------------
KV_DIRECTORY = kivy_mpbe_widgets.DIR_BASE + '/wg_labels/'
Builder.load_string("""
<EditableTextLabel>:
    size_hint_y: None
    height: 30
""")


class EditableTextLabel(FocusBehavior, BoxLayout, StartEditingEventDispatcher, FinishEditingEventDispatcher):
    editable = BooleanProperty(True)
    text = StringProperty(defaultvalue="")
    padding_x = NumericProperty(0)

    def __init__(self, text, style='body',padding_x=0, **kwargs):
        FocusBehavior.__init__(self)
        BoxLayout.__init__(self)
        StartEditingEventDispatcher.__init__(self)
        FinishEditingEventDispatcher.__init__(self)
        self._padding_x = padding_x
        self._label = TextLabel(text=text, valign='center', style=style, padding_x=padding_x)
        self._text_input = None
        self.text = text
        self.add_widget(self._label)
        self._label.font_size = 16
        self.in_edition = False
        self.back_text = None
        self.bind(on_touch_up=self._on_label_touch_up)

    '''Funciones de Edición -----------------------------------------------------------'''
    def _init_edition(self, dt):
        self._text_input.cursor = (1000, 0)
        self._text_input.select_all()

    def start_editing(self):
        '''Inicia la edición del texto'''
        if not self.in_edition:
            self.in_edition = True
            self.back_text = self.text
            StartEditingEventDispatcher.do_something(self, self.text)
            self._text_input = TextInput(text=self.text, multiline=False, padding_x=self._padding_x
                                         , on_text_validate=self.finish_editing)
            self._text_input.focus = True
            self.remove_widget(self._label)
            self.add_widget(self._text_input)
            # Escuchar teclado (Escape/Enter) solo mientras dura la edición
            Window.bind(on_key_down=self._on_keyboard_down)
            Clock.schedule_once(self._init_edition, 0.4)
            return True
        return False

    def finish_editing(self, instance):
        '''Guarda el texto editado y desactivar edición'''
        if self.in_edition:
            # Dejar de escuchar el teclado global al salir de edición
            Window.unbind(on_key_down=self._on_keyboard_down)
            self._label.text = self._text_input.text
            self.text = self._text_input.text
            # self.editable = False
            self.remove_widget(self._text_input)
            self.add_widget(self._label)
            self._text_input = None
            self.in_edition = False
            FinishEditingEventDispatcher.do_something(self, new_text=instance.text)

    '''Eventos -----------------------------------------------------------------------'''
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # Solo dispara en el label que tiene el foco (FocusBehavior)
        if not self.in_edition and self.editable and keycode[0] == 283:  # Tecla F2
            self.start_editing()
            return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def _on_keyboard_down(self, window, keycode, modifier, char, special_keys):
        # Enganchado a Window solo durante la edición (Escape / Enter)
        if self.in_edition:
            if keycode == 27:  # Tecla Escape
                self.text = self.back_text
                self._text_input.text = self.back_text
                self.finish_editing(self._text_input)
                return True
            elif keycode in [13, 271]:  # Tecla Return
                self.finish_editing(self._text_input)
                return True
            return False

    def _on_label_touch_up(self, instance, mouse):
        if self.editable and mouse.button=='right' and self.collide_point(mouse.x, mouse.y):
            self.start_editing()
            return True

    def on_text(self,instance, value):
        self._label.text = value

    def on_padding_x(self, instance, value):
        self._padding_x = value


class InputFilter(BoxLayout):
    """
    Un widget que combina un TextInput con un ToggleIcon a la derecha.
    Cuando el ToggleIcon está en estado 'toggled', el TextInput se deshabilita.
    """
    text = StringProperty('')
    state = OptionProperty('untoggled', options=['toggled', 'untoggled'])

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', spacing=5, padding=(0, 0, 5, 0), **kwargs)
        self.size_hint_y = None
        self.height = 36  # Altura por defecto razonable

        self.text_input = TextInput(
            size_hint_x=1,
            multiline=False
        )
        self.add_widget(self.text_input)

        self.toggle_icon = ToggleIcon(
            icon_name='filter-outline',
            icon_size=24
        )

        icon_container = AnchorLayout(
            anchor_x='center', anchor_y='center',
            size_hint_x=None, width=self.height
        )
        icon_container.add_widget(self.toggle_icon)
        self.add_widget(icon_container)

        # Bindings
        self.text_input.bind(text=self._on_text_input_change)
        self.toggle_icon.bind(state=self._on_toggle_icon_state_change)
        self.bind(text=self._on_text_change, state=self._on_state_change)

        # Establecer estado inicial
        self._update_text_input_disabled()

    def _on_text_input_change(self, instance, value):
        self.text = value

    def _on_text_change(self, instance, value):
        if self.text_input.text != value:
            self.text_input.text = value

    def _on_toggle_icon_state_change(self, instance, state):
        self.state = state

    def _on_state_change(self, instance, value):
        if self.toggle_icon.state != value:
            self.toggle_icon.state = value
        self._update_text_input_disabled()

    def _update_text_input_disabled(self):
        self.text_input.disabled = (self.state == 'toggled')


class InputSearch(BoxLayout):
    """
    Un widget que combina un TextInput con un ClickIcon de búsqueda a la derecha.
    """
    text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', spacing=5, padding=(0, 0, 5, 0), **kwargs)
        self.register_event_type('on_search')
        self.size_hint_y = None
        self.height = 36  # Altura por defecto razonable

        self.text_input = TextInput(
            size_hint_x=1,
            multiline=False
        )
        self.add_widget(self.text_input)

        self.search_icon = ClickIcon(
            icon_name='magnify',
            icon_size=24
        )

        icon_container = AnchorLayout(
            anchor_x='center', anchor_y='center',
            size_hint_x=None, width=self.height
        )
        icon_container.add_widget(self.search_icon)
        self.add_widget(icon_container)

        # Bindings
        self.text_input.bind(text=self._on_text_input_change)
        self.search_icon.bind(on_click=self._on_search_click)
        self.bind(text=self._on_text_change)

    def _on_text_input_change(self, instance, value):
        self.text = value

    def _on_text_change(self, instance, value):
        if self.text_input.text != value:
            self.text_input.text = value

    def _on_search_click(self, instance, touch, keycode):
        self.dispatch('on_search', self.text)

    def on_search(self, search_text):
        # This is the event handler that can be bound by the user.
        pass


class InputSearchOrFilter(BoxLayout):
    """
    Un widget que combina un TextInput con:
    - Un ToggleIcon a la izquierda para selección de items padres.
    - Un ToggleIcon a la derecha para filtrar.
    - Un ClickIcon a la derecha para buscar.
    """
    text = StringProperty('')
    filter_state = OptionProperty('untoggled', options=['toggled', 'untoggled'])
    parent_selection_state = OptionProperty('untoggled', options=['toggled', 'untoggled'])

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)  # , spacing=5, padding=(5, 0, 5, 0)
        self.register_event_type('on_search')
        self.size_hint_y = None
        self.height = 36  # Altura por defecto razonable

        # 1. Left ToggleIcon (Parent Selection)
        self.include_parents_toggle = ToggleIcon(
            icon_name='chevron-double-up', # Icon for parent selection
            icon_size=24
        )
        parent_icon_container = AnchorLayout(
            anchor_x='center', anchor_y='center',
            size_hint_x=None, width=self.height
        )
        parent_icon_container.add_widget(self.include_parents_toggle)
        self.add_widget(parent_icon_container)

        # 2. Center TextInput
        self.text_input = TextInput(
            size_hint_x=1,
            multiline=False
        )
        self.add_widget(self.text_input)

        # 3. Right-side buttons
        # Filter ToggleIcon
        self.filter_toggle = ToggleIcon(
            icon_name='filter-outline',
            icon_size=24
        )
        filter_icon_container = AnchorLayout(
            anchor_x='center', anchor_y='center',
            size_hint_x=None, width=self.height
        )
        filter_icon_container.add_widget(self.filter_toggle)
        self.add_widget(filter_icon_container)

        # Search ClickIcon
        self.search_button = ClickIcon(
            icon_name='magnify',
            icon_size=24
        )
        search_icon_container = AnchorLayout(
            anchor_x='center', anchor_y='center',
            size_hint_x=None, width=self.height
        )
        search_icon_container.add_widget(self.search_button)
        self.add_widget(search_icon_container)

        # Bindings
        self.text_input.bind(text=self.setter('text'))
        self.bind(text=lambda i, v: setattr(self.text_input, 'text', v) if self.text_input.text != v else None)
        self.search_button.bind(on_click=lambda i, t, k: self.dispatch('on_search', self.text))
        self.filter_toggle.bind(state=self.setter('filter_state'))
        self.bind(filter_state=self._on_filter_state_change)
        # self.include_parents_toggle.bind(state=self.setter('include_parents_state'))
        self.bind(parent_selection_state=lambda i, v: setattr(self.include_parents_toggle, 'state', v) if self.include_parents_toggle.state != v else None)

        # Initial state
        self._on_filter_state_change(self, self.filter_state)

    def on_search(self, search_text):
        pass

    def _on_filter_state_change(self, instance, value):
        if self.filter_toggle.state != value:
            self.filter_toggle.state = value
        is_filtered = (value == 'toggled')
        self.text_input.disabled = is_filtered
        self.search_button.disabled = is_filtered
