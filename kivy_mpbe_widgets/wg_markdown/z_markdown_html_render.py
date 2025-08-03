from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import markdown
import webview
import threading


class WebViewApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Input para Markdown
        self.markdown_input = TextInput(text="# Hola, Mundo!\nEste es un ejemplo de Markdown.", multiline=True)
        self.layout.add_widget(self.markdown_input)

        # Botón para convertir y cargar HTML
        self.load_button = Button(text="Convertir y Cargar HTML")
        self.load_button.bind(on_press=self.load_html)
        self.layout.add_widget(self.load_button)

        return self.layout

    def load_html(self, instance):
        # Convertir Markdown a HTML
        md_text = self.markdown_input.text
        html_content = markdown.markdown(md_text)

        # Crear una ventana webview para mostrar el HTML
        threading.Thread(target=self.create_webview, args=(html_content,)).start()

    def create_webview(self, html_content):
        webview.create_window('Markdown Viewer', html=html_content)


if __name__ == '__main__':
    WebViewApp().run()
