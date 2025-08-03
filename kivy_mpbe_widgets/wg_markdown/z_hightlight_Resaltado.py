
from kivy.app import App
from kivy.uix.label import Label

class HighlightApp(App):
    def build(self):
        text = "Este es un ejemplo de texto con [b][color=ff3333]resaltado[/color][b]."
        label = Label(text=text, markup=True)
        return label

if __name__ == '__main__':
    HighlightApp().run()

