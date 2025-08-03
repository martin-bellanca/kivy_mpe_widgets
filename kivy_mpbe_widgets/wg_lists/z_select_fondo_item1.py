from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, BooleanProperty
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView

# Cargar el archivo KV
Builder.load_string("""
<AnimatedBox>:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    canvas.before:
        Color:
            rgba: 0, 0, 1, self.bg_alpha  # Fondo azul con opacidad controlada por bg_alpha
        # Línea vertical que crece hacia arriba y abajo desde el clic
        Rectangle:
            size: 1, self.vertical_end - self.vertical_start
            pos: self.x + self.click_x, self.vertical_start + self.y

        # Expansión horizontal hacia la izquierda y derecha desde la línea central
        Rectangle:
            size: self.horizontal_end - self.horizontal_start, self.height
            pos: self.x + self.horizontal_start, self.y
""")


class AnimatedBox(BoxLayout):
    selected = BooleanProperty(False)  # Indica si el fondo está seleccionado
    bg_alpha = NumericProperty(0)  # Controla la opacidad del fondo azul
    vertical_start = NumericProperty(0)
    vertical_end = NumericProperty(0)
    horizontal_start = NumericProperty(0)
    horizontal_end = NumericProperty(0)
    click_x = NumericProperty(0)
    click_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Vincular el cambio de tamaño para actualizar el fondo cuando esté seleccionado
        self.bind(size=self.on_size_update)

    def on_size_update(self, *args):
        if self.selected:
            # Asegurarse de que el fondo cubre todo el área si está seleccionado
            self.horizontal_start = 0
            self.horizontal_end = self.width

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Convertir las coordenadas globales del clic a coordenadas relativas al widget
            self.click_x = touch.x - self.x
            self.click_y = touch.y - self.y
            # Alternar el estado de `selected`
            if self.selected:
                self.deselect()
            else:
                self.select()
            return True
        return super().on_touch_down(touch)

    def select(self):
        self.selected = True
        self.bg_alpha = 1  # Asegurar que el fondo está completamente opaco
        self.start_vertical_animation()

    def deselect(self):
        self.selected = False
        # Animación para desvanecer el fondo
        anim = Animation(bg_alpha=0, duration=0.5)
        anim.start(self)

    def start_vertical_animation(self):
        # Configurar la animación para la línea vertical
        self.vertical_start = self.click_y
        self.vertical_end = self.click_y
        anim = Animation(vertical_start=0, vertical_end=self.height, duration=0.5)
        anim.bind(on_complete=lambda *args: self.start_horizontal_animation())
        anim.start(self)

    def start_horizontal_animation(self):
        # Configurar la animación para la expansión horizontal
        self.horizontal_start = self.click_x
        self.horizontal_end = self.click_x
        anim = Animation(horizontal_start=0, horizontal_end=self.width, duration=0.5)
        anim.start(self)


class AnimatedBoxApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical")
        scroll = ScrollView()
        box_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter("height"))

        # Agregar varios AnimatedBox al ScrollView
        for _ in range(5):
            animated_box = AnimatedBox(size_hint_y=None, height=100)
            box_layout.add_widget(animated_box)

        scroll.add_widget(box_layout)
        root.add_widget(scroll)

        return root


if __name__ == "__main__":
    AnimatedBoxApp().run()
