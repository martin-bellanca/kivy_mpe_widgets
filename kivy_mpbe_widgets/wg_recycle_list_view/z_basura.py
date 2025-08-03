from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class RemovableButton(Button):
    def on_press(self):
        """Eliminar este widget de su layout contenedor."""
        if self.parent:
            self.parent.remove_widget(self)  # Remueve este widget del layout


class MainApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10)

        # Agregar botones al layout
        for i in range(5):
            btn = RemovableButton(text=f"Botón {i+1}")
            layout.add_widget(btn)

        return layout


if __name__ == "__main__":
    MainApp().run()
