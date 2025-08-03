from kivy.app import App
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Line
from kivy.properties import ListProperty, BooleanProperty


class BorderedGridLayout(GridLayout):
    # Propiedades para seleccionar los bordes a dibujar
    draw_top = BooleanProperty(True)
    draw_bottom = BooleanProperty(True)
    draw_left = BooleanProperty(True)
    draw_right = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(children=self.update_borders)
        self.bind(size=self.update_borders, pos=self.update_borders)
        Clock.schedule_once(self.update_borders, 0.3)

    def update_borders(self, *args):
        # Limpia el canvas antes de redibujar
        self.canvas.before.clear()

        # Dibuja los bordes en cada celda
        for child in self.children:
            with self.canvas.before:
                # Coordenadas y tamaño del widget
                x, y = child.pos
                w, h = child.size

                # Dibujar los bordes
                if self.draw_top:
                    Line(points=[x, y + h, x + w, y + h], width=1)
                if self.draw_bottom:
                    Line(points=[x, y, x + w, y], width=1)
                if self.draw_left:
                    Line(points=[x, y, x, y + h], width=1)
                if self.draw_right:
                    Line(points=[x + w, y, x + w, y + h], width=1)


class TestApp(App):
    def build(self):
        layout = BorderedGridLayout(cols=3, row_force_default=True, row_default_height=100)

        # Ajustar bordes según se necesite
        layout.draw_top = True
        layout.draw_bottom = True
        layout.draw_left = True
        layout.draw_right = True

        # Añadir celdas de ejemplo
        for i in range(9):
            layout.add_widget(Label(text=f'Celda {i + 1}', size_hint=(None, None), size=(100, 100)))

        return layout


if __name__ == '__main__':
    TestApp().run()
