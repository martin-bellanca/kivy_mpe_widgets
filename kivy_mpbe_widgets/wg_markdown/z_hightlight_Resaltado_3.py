from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel


class HighlightedTextLabel(Widget):
    def init(self, text, highlight_text, **kwargs):
        super().init(**kwargs)
        self.text = text
        self.highlight_text = highlight_text
        self.draw_highlighted_text()

    def draw_highlighted_text(self):
        # Crear CoreLabel para medir el tamaño y posición del texto con markup
        core_label = CoreLabel(text=self.text, font_size=24, markup=True)
        core_label.refresh()

        # Usar canvas para dibujar el fondo solo para la palabra resaltada
        with self.canvas:
            Color(0.8, 0.3, 0.3, 0.5)  # Color de fondo del resaltado

            # Dividir el texto por la palabra resaltada
            words = self.text.split(self.highlight_text)
            x_offset = 0

            for i, word in enumerate(words):
                # Medir y posicionar cada parte del texto
                word_label = CoreLabel(text=word, font_size=24, markup=True)
                word_label.refresh()

                # Actualizar el desplazamiento de x para la palabra resaltada
                x_offset += word_label.texture.size[0]

                # Dibujar fondo para el texto resaltado
                if i < len(words) - 1:
                    highlight_label = CoreLabel(text=self.highlight_text, font_size=24, markup=True)
                    highlight_label.refresh()

                    Rectangle(
                        pos=(self.x + x_offset, self.y),
                        size=(highlight_label.texture.size[0], highlight_label.texture.size[1])
                    )

                    # Agregar tamaño del texto resaltado al desplazamiento
                    x_offset += highlight_label.texture.size[0]

        # Agregar el texto completo como un Label encima del fondo
        self.add_widget(Label(text=self.text, font_size=24, markup=True, pos=(self.x, self.y)))


class HighlightApp(App):
    def build(self):
        return HighlightedTextLabel(
            text="Este es un [color=ff3333][b]ejemplo[/b][/color] de texto con resaltado.",
            highlight_text="[color=ff3333][b]ejemplo[/b][/color]"
        )


if __name__ == "main":
    HighlightApp().run()