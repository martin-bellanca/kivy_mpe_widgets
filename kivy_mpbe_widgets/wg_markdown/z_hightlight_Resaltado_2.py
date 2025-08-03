from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle


class FontBackgroundLabel(Label):
    def __init__(self, **kwargs):
        super(FontBackgroundLabel, self).__init__(**kwargs)
        self.bind(size=self.update_background, pos=self.update_background, text=self.update_background)

    def update_background(self, *args):
        self.canvas.before.clear()
        # Calcula el tamaño del texto
        self.texture_update()
        text_width, text_height = self.texture.size
        txt_x, txt_y = self.texture.get_rect()

        # Dibuja un rectángulo justo detrás del texto
        with self.canvas.before:
            Color(0.8, 0.8, 0.6, 1)  # Color amarillo de fondo
            Rectangle(pos=(self.x, self.center_y - text_height / 2),
                      size=(text_width, text_height))


class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Crear una instancia del widget personalizado con fondo detrás de la fuente
        label = FontBackgroundLabel(text="Texto con fondo en la fuente mas largo ṕara probar", color=(0,0,1,1))

        # Añadir el widget al layout
        layout.add_widget(label)

        return layout


if __name__ == '__main__':
    TestApp().run()
