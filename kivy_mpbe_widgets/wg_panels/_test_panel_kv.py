# -*- coding: utf-8 -*-
#
#  base_widget.py
#
#  Copyright 2018 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

"""------------------------------------------------------------------------"""
"""-- Test Program  -------------------------------------------------------"""
"""------------------------------------------------------------------------"""

# kivy imports --------------------------------------------------------------
# mpbe imports --------------------------------------------------------------
# kivy_dkw ------------------------------------------------------------------
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy_dkw.base_widget import *
from panels import Panel, BoxPanel, GridPanel, StackPanel, TitlePanel
from kivy_dkw.wg_labels.text_labels import TextLabel
from kivy_dkw.wg_buttons.click_buttons import ClickButton





class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Frame Widgets"

    def build(self):
        # Clock.schedule_once(self.app_finish_init, 0)
        Window.clearcolor = self.theme.style['background_app']
        return self.test02()

    def test02(self):
        # grid = GridLayout(cols=2, spacing=6, padding=6)
        # # Box Panel -----------------------------------------------------
        # grid.add_widget(TextLabel(text="BOX PANEL"))
        # bpanel = BoxPanel(spacing=5, padding=10)
        # # bpanel.transparent=True
        # bpanel.container.add_widget(TextLabel(text="bp Label 001",valign='center'))
        # bpanel.container.add_widget(TextLabel(text="bp Label 002",valign='center'))
        # grid.add_widget(bpanel)

        return Builder.load_string('''
GridLayout:
    cols: 2
    spacing: 5
    padding: 5
    BoxPanel:
        spacing: 5
        padding: 5
        TextLabel:
            text: 'bp Label 001'
            valign: 'center'
        TextLabel:
            text: 'bp Label 001'
            valign: 'center'
''')


    def app_finish_init(self, *dt):
        win = self._app_window
        win.bind(on_request_close=self._on_close_app)

    def _on_close_app(self, *largs, **kwargs):
        if 'source' in kwargs and kwargs['source'] == 'keyboard':
            return True
        else:
            return False

if __name__ == "__main__":
    TestApp().run()