from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class MyApp(App):
    def build(self):
        box = BoxLayout(orientation='vertical')

        # Crear un Label con texto marcado
        label = Label(
            text=(
                'Haga clic en [ref=link1]enlace 1[/ref] o [ref=link2]enlace 2[/ref].'
            ),
            markup=True,
            size_hint=(1, 0.2),
        )

        # Asociar una función al evento 'on_ref_press'
        label.bind(on_ref_press=self.on_ref_press)

        box.add_widget(label)
        return box

    def on_ref_press(self, instance, ref):
        # Mostrar qué referencia fue presionada
        print(f"Referencia presionada: {ref}")

if __name__ == '__main__':
    MyApp().run()
