from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import NumericProperty, BooleanProperty
from kivy.animation import Animation
from kivy.lang import Builder

# Cargar el archivo KV
Builder.load_string("""
<AnimatedBox>:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    canvas.before:
        Color:
            rgba: 0, 0, 1, self.bg_alpha  # Fondo azul con opacidad controlada por bg_alpha
        Rectangle:
            size: 1, self.vertical_end - self.vertical_start
            pos: self.x + self.click_x, self.vertical_start + self.y
        Rectangle:
            size: self.horizontal_end - self.horizontal_start, self.height
            pos: self.x + self.horizontal_start, self.y

""")


class AnimatedBox(BoxLayout):
    selected = BooleanProperty(False)
    bg_alpha = NumericProperty(0)  # Controla la opacidad del fondo azul
    vertical_start = NumericProperty(0)
    vertical_end = NumericProperty(0)
    horizontal_start = NumericProperty(0)
    horizontal_end = NumericProperty(0)
    click_x = NumericProperty(0)
    click_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.on_size_update)

    def on_size_update(self, *args):
        if self.selected:
            self.horizontal_start = 0
            self.horizontal_end = self.width

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.click_x = touch.x - self.x
            self.click_y = touch.y - self.y
            if self.selected:
                self.deselect()
            else:
                self.select()
            return True
        return super().on_touch_down(touch)

    def select(self):
        self.selected = True
        self.bg_alpha = 1  # Asegura que el fondo esté completamente opaco
        self.start_vertical_animation()

    def deselect(self):
        self.selected = False
        anim = Animation(bg_alpha=0, duration=0.5)
        anim.start(self)

    def start_vertical_animation(self):
        self.vertical_start = self.click_y
        self.vertical_end = self.click_y
        anim = Animation(vertical_start=0, vertical_end=self.height, duration=0.5)
        anim.bind(on_complete=lambda *args: self.start_horizontal_animation())
        anim.start(self)

    def start_horizontal_animation(self):
        self.horizontal_start = self.click_x
        self.horizontal_end = self.click_x
        anim = Animation(horizontal_start=0, horizontal_end=self.width, duration=0.5)
        anim.start(self)


class AnimatedBoxApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical")

        # Configuración del ScrollView con tamaño reducido
        scroll = ScrollView(size_hint_y=0.7)  # Ocupa el 70% de la pantalla en altura
        box_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter("height"))

        # Añadir varios AnimatedBox al ScrollView
        for _ in range(5):
            animated_box = AnimatedBox(size_hint_y=None, height=100)
            box_layout.add_widget(animated_box)

        scroll.add_widget(box_layout)
        root.add_widget(scroll)

        # Añadir un widget debajo del ScrollView
        footer = Label(text="Footer debajo del ScrollView", size_hint_y=0.3)  # Ocupa el 30% de la pantalla en altura
        root.add_widget(footer)

        return root


if __name__ == "__main__":
    AnimatedBoxApp().run()
