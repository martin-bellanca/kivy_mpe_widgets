#!/usr/bin/env python
# -*- coding: utf-8 -*-


from helpers_mpbe.python import compose_dict, compose
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import BooleanProperty, StringProperty, OptionProperty
from kivy.clock import Clock
# from kivy.uix.label import Label
# kivy_dkw ------------------------------------------------------------------
from kivy_dkw.wg_markdown.md_labels import MDTextLabel, MDTableLabel, MDSeparatorLabel
from kivy_dkw.wg_markdown.md_document import MDDocument, MDLine




class MarkdownRowTextInputWLabel(FloatLayout):  # ToDo: Esta se reemplaza por MDLineEditor
    mode_editor = BooleanProperty(defaultvalue=False)
    # type_editor = Lista o con 'Label, Image, Sepator, Table, etc.'

    def __init__(self, **kwargs):
        super(MarkdownRowTextInputWLabel, self).__init__(size_hint_y=None)
        self.md_label = MDTextLabel(pos_hint={'x': 0, 'center_y': 0.5})
        self.md_label.bind(size=self.update_height)
        self.add_widget(self.md_label)
        self.md_editor = MDLineTextInput(background_color = (0.8, 0.8, 0.8, 0.80),
                                         size_hint_y = None,
                                         pos_hint = {'x': 0, 'center_y': 0.5},
                                         opacity=0)
        self.md_editor.bind(text=self.on_txt_change)
        self.md_editor.bind(focus=self.on_focus)
        self.add_widget(self.md_editor)
        self.md_text = compose_dict(kwargs,'md_text',str,'')
        Window.bind(on_key_up=self.on_key_up)
    # Properties --------------------------------------------------------
    def _get_md_text(self):
        return self.md_label.md_text
    def _set_md_text(self, value):
        self.md_label.md_text = value
        self.md_editor.text = value
    md_text = property(_get_md_text, _set_md_text)

    # funtions events ---------------------------------------------------
    def on_mode_editor(self, instance, value):
        if value and value == self.mode_editor:
            self.md_editor.opacity = 1
            # self.md_editor.cursor = (2,0)
            # self.md_editor.select_all()
            self.md_editor.focus = True
        else:
            self.md_editor.opacity = 0

    def on_txt_change(self, instance, value):
        self.md_label.md_text = value

    def update_height(self, instance, value):
        if self.md_label.height > 0:
            self.height = self.md_label.height
        else:
            self.height = self.md_label.font_size+4

    def on_touch_up(self, touch):
        if touch.button == 'left':
            if self.collide_point(touch.x, touch.y):
                self.mode_editor = True
            else:
                self.mode_editor = False
            return False
        # super().on_touch_up(touch)

    def on_key_up(self, window, keycode, scancode):
        # Detectar si se presionó la tecla Escape
        if self.mode_editor == True:
            if keycode == 27:
                self.mode_editor=False
                return False  # True Evitar que otros controladores manejen la tecla
        return False  # Permitir que otros controladores manejen la tecla

    def on_focus(self, instance, value):
        if not value:  # Cuando pierde el foco
            self.mode_editor = False
            return True
        else:  # Cuando gana el foco
            pass
