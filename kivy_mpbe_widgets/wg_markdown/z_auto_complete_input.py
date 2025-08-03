#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ssss.py
#
"""Ejemplo de auto completado en TextInput"""


# imports del sistema -------------------------------------------------------
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.lang import Builder
# kivy_dkw ------------------------------------------------------------------
# helpers_mpbe --------------------------------------------------------------



Builder.load_string('''
<SelectableLabel>:
    size_hint_y: None
    height: 30
    canvas.before:
        Color:
            rgba: (0, 0, 1, 0.1) if self.selected else (1, 1, 1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
''')



# Define a custom RecycleView view class
class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    text = StringProperty('')

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'left':
                self.selectable = True
                self.selected = not self.selected
                self.parent.parent.select(self.index)
                return True
        return super().on_touch_down(touch)

# Define the main layout class
class Autocomplete(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.suggestions = ['apple', 'banana', 'orange', 'grape', 'pear', 'pineapple']
        self.popup = Popup(size_hint=(0.8, 0.4), auto_dismiss=True)
        self.rv = RecycleView(size_hint=(1, 1), size=(Window.width, Window.height * 0.4))
        self.rv.viewclass = 'SelectableLabel'
        self.rv.data = [{'text': s} for s in self.suggestions]
        self.rv.bind(on_touch_down=self.on_select)
        self.popup.add_widget(self.rv)
        self.bind(text=self.on_text)

    def on_text(self, instance, value):
        self.update_suggestions(value)
        if self.rv.data:
            self.popup.open()
        else:
            self.popup.dismiss()

    def update_suggestions(self, text):
        self.rv.data = [{'text': s} for s in self.suggestions if text.lower() in s.lower()]

    def on_select(self, instance, touch):
        if self.popup.collide_point(*touch.pos):
            selected_index = self.rv.index
            if selected_index is not None:
                self.text = self.rv.data[selected_index]['text']
                self.popup.dismiss()

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.autocomplete = Autocomplete(size_hint=(1, 0.1))
        layout.add_widget(self.autocomplete)
        return layout

if __name__ == '__main__':
    MyApp().run()
