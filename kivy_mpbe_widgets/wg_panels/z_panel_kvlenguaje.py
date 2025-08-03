from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.lang import Builder

# Cargar el archivo KV
Builder.load_string('''
<Panel>:
    orientation: 'vertical'
    # Este es el contenedor donde se agregarán los widgets
    container: container

    BoxLayout:
        id: container
        orientation: 'vertical'
    
    Button:
        text: 'This is part of the Panel'
        size_hint_y: None
        height: 50

# Derivado de Panel, que agrega un botón adicional al contenedor
<MyDerivedPanel@Panel>:
    Button:
        text: 'Button added in KV'
        size_hint_y: None
        height: 50

# Usando el widget derivado en la raíz de la aplicación
<MyDerivedPanel>:

''')

class Panel(BoxLayout):
    container = ObjectProperty(None)  # Propiedad que hace referencia al contenedor

class MyApp(App):
    def build(self):
        return Panel()

if __name__ == '__main__':
    MyApp().run()
