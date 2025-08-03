#!/usr/bin/env python
# -*- coding: utf-8 -*-


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from markdown import markdown
from kivy_dkw.wg_markdown.markdown_extension import TaskListMDExtension


class TaskListViewer(BoxLayout):
    def init(self, html_text, **kwargs):
        super(TaskListViewer, self).init(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text=html_text, markup=True, size_hint_y=None, height=200))

class TaskListApp(App):
    def build(self):
        md_text = """
## Titulo
**Prueba**
- item 1
- item 2
**Prueba**
- [ ] Tarea sin iniciar
- [x] Tarea completada
[>] Tarea en proceso
[o] Tarea paralizada
[-] Tarea anulada
"""
        html = markdown(md_text, extensions=[TaskListMDExtension()])
        # tkl = TaskListViewer(html_text=html)
        # html = md_text
        print(html)

        tkl = BoxLayout(orientation='vertical', size_hint=(1,1))
        tkl.add_widget(Label(text=html, markup=True, size_hint_y=None, height=200))

        # tkl = Label(text=html, markup=True, size_hint=(1,1), halign='left', valign='top')

        return tkl

if __name__ == '__main__':
    TaskListApp().run()
