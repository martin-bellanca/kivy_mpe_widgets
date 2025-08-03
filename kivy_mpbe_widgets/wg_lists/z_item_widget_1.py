from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, StringProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

class EditableLabel(Label):
    editable = BooleanProperty(False)
    text_temp = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.bind(on_double_tap=self.on_double_click)

    def on_touch_up(self, *args):
        # Activar modo edición
        if not self.editable:
            self.editable = True
            self.text_temp = self.text
            ti = TextInput(text=self.text, on_text_validate=self.finish_editing)
            self.parent.add_widget(ti)
            ti.focus

    def finish_editing(self, instance):
        # Guardar el texto editado y desactivar edición
        self.text = instance.text
        self.editable = False
        self.parent.remove_widget(instance)

class CustomWidget(BoxLayout):
    has_focus = BooleanProperty(False)
    hover = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = [10, 5]
        self.spacing = 5
        self.size_hint_y = None
        self.height = 50
        self.background_color = [0.9, 0.9, 0.9, 1]  # Fondo gris claro
        self.canvas.add(Color(0.5, 0.5, 0.5, 1))
        self.canvas.add(Rectangle(size=(self.width, 1), pos=self.pos))  # Borde inferior gris oscuro

        # Agregar elementos: Label y botones
        self.label = EditableLabel(text="Doble clic para editar")
        self.button_focused = Button(text="Botón de Foco", size_hint_x=None, width=100, opacity=0)
        self.button_hover = Button(text="Botón de Hover", size_hint_x=None, width=100, opacity=0)

        self.add_widget(self.label)
        self.add_widget(self.button_hover)
        self.add_widget(self.button_focused)

        self.bind(has_focus=self.animate_button_focused)
        self.bind(hover=self.animate_button_hover)
        self.bind(on_touch_down=self.on_focus)

    def animate_button_focused(self, instance, value):
        anim = Animation(opacity=1 if value else 0, duration=0.2)
        anim.start(self.button_focused)

    def animate_button_hover(self, instance, value):
        anim = Animation(opacity=1 if value else 0, duration=0.2)
        anim.start(self.button_hover)

    def on_focus(self, instance, touch):
        if self.collide_point(*touch.pos):
            self.has_focus = not self.has_focus
            return True
        return False

    def on_hover(self, instance, value):
        print("Hover")
        self.animate_button_hover()

    def on_enter(self, *args):
        print("Enter")
        self.hover = True

    def on_leave(self, *args):
        print("Leave")
        self.hover = False

class MyApp(App):
    def build(self):
        root = CustomWidget()
        return root

if __name__ == "__main__":
    MyApp().run()
