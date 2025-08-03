#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from markdown import markdown


class MarkdownEditor(BoxLayout):
    markdown_text = StringProperty("")

    def init(self, **kwargs):
        super(MarkdownEditor, self).init(**kwargs)
        self.orientation = 'vertical'

        self.text_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=200,
            hint_text='Enter Markdown text here...',
            on_text_validate=self.update_preview
        )
        self.text_input.bind(text=self.update_preview)

        self.add_widget(self.text_input)

        self.preview_label = Label(
            text='',
            size_hint_y=None,
            height=200,
            markup=True
        )

        self.preview_scroll = ScrollView(size_hint=(1, None), size=(400, 200))
        self.preview_scroll.add_widget(self.preview_label)

        self.add_widget(self.preview_scroll)

    def update_preview(self, instance, value):
        md_text = self.text_input.text
        self.markdown_text = markdown(md_text)
        self.preview_label.text = self.markdown_text


class MarkdownApp(App):
    def build(self):
        return MarkdownEditor()


if __name__ == '__main__':
    MarkdownApp().run()