from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy_dkw.wg_markdown.md_editors import MDLineTextInput
from kivy_dkw.wg_markdown.md_labels_viejo import MarkdownLabel

# Definir el archivo KV en un string
kv = """
<CustomWidget>:
    label_widget: md_label
    MarkdownLabel:
        id: md_label
        text: root.input_text
        size_hint: 1, None
        halign: 'left'
        width: self.texture_size[0] if self.size_hint_x == None else self.size_hint_x * root.width
        # height: self.texture_size[1] if self.size_hint_y == None else self.size_hint_y * root.height
        pos_hint: {'x': 0, 'center_y': 0.5}
        opacity: 0.8  # Hacer el fondo del Label translúcido
        # background_color: (0.5, 0, 0, 0.5)

    MarkdownRowTextInput:
        size_hint: 1, None
        height: 26 if md_label.height == 0 else md_label.height * 2 # Altura del TextInput igual a la del Label
        pos_hint: {'x': 0, 'center_y': 0.5}
        multiline: False
        opacity: 0.5  # Hacer el TextInput translúcido
        # background_color: (0.5, 0, 0, 0.5)
        on_text: md_label = self.text

"""
Builder.load_string(kv)


class CustomWidget(FloatLayout):
    input_text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

class MyApp(App):
    def build(self):
        return CustomWidget()

if __name__ == '__main__':
    MyApp().run()
