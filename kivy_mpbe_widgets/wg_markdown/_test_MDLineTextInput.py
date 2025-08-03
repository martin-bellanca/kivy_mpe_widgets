

# Kivy imports -------------------------------------------------------------
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
# Kivy_dkw imports -------------------------------------------------------------
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_markdown.md_editors import MDLineTextInput as MRTI



class MyApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Markdown Row Editor"
    def build(self):
        Window.clearcolor = self.theme.style['background_app']
        layout = BoxLayout(orientation='vertical')
        self.input = MRTI(size_hint=(1, 0.1))
        layout.add_widget(self.input)
        return layout

if __name__ == '__main__':
    MyApp().run()
