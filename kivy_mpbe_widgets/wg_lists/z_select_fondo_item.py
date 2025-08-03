from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
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
            rgba: 0, 0, 1, 1  # Color azul opaco
        # Línea vertical que crece hacia arriba y abajo desde el clic
        Rectangle:
            size: 1, self.vertical_end - self.vertical_start
            pos: self.click_x, self.vertical_start

        # Expansión horizontal hacia la izquierda y derecha desde la línea central
        Rectangle:
            size: self.horizontal_end - self.horizontal_start, self.height
            pos: self.horizontal_start, self.y
""")

class AnimatedBox(BoxLayout):
    vertical_start = NumericProperty(0)  # Punto de inicio de la línea vertical
    vertical_end = NumericProperty(0)  # Punto de fin de la línea vertical
    horizontal_start = NumericProperty(0)  # Punto de inicio de la línea horizontal
    horizontal_end = NumericProperty(0)  # Punto de fin de la línea horizontal
    click_x = NumericProperty(0)  # Posición X del clic
    click_y = NumericProperty(0)  # Posición Y del clic

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Almacenar la posición del clic
            self.click_x = touch.x
            self.click_y = touch.y
            # Iniciar animación desde el clic
            self.start_vertical_animation()
            return True
        return super().on_touch_down(touch)

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
        return AnimatedBox()

if __name__ == "__main__":
    AnimatedBoxApp().run()
