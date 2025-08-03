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
from kivy.uix.gridlayout import GridLayout
from kivy_mpbe_widgets.base_widgets import *
from kivy_mpbe_widgets.wg_panels.panels import BoxPanel, GridPanel, StackPanel, TitlePanel
from kivy_mpbe_widgets.wg_labels.text_labels import TextLabel
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButton


class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Frame Widgets"

    def build(self):
        # Clock.schedule_once(self.app_finish_init, 0)
        Window.clearcolor = self.theme.style['background_app']
        return self.test02()

    def test02(self):
        grid = GridLayout(cols=2, spacing=6, padding=6)
        # Box Panel -----------------------------------------------------
        grid.add_widget(TextLabel(text="BOX PANEL"))
        bpanel = BoxPanel(orientation='horizontal')
        # bpanel.transparent=True
        bpanel.container.add_widget(TextLabel(text="bp Label 001",valign='center'))
        bpanel.container.add_widget(TextLabel(text="bp Label 002",valign='center'))
        grid.add_widget(bpanel)

        # Grid Panel -----------------------------------------------------
        grid.add_widget(TextLabel(text="GRID PANEL"))
        gpanel = GridPanel(cols=2, spacing=5, padding=10)
        # gpanel.transparent=True
        gpanel.container.add_widget(TextLabel(text="gp Label 001", valign='center'))
        gpanel.container.add_widget(TextLabel(text="gp Label 002", valign='center'))
        gpanel.container.add_widget(TextLabel(text="gp Label 003", valign='center'))
        grid.add_widget(gpanel)

        # Stack Panel -----------------------------------------------------
        grid.add_widget(TextLabel(text="STACK PANEL"))
        spanel = StackPanel(orientation='tb-lr')
        # gpanel.transparent=True
        spanel.container.add_widget(ClickButton(text="gp Button 001", size_hint=(0.5, 0.4)))
        spanel.container.add_widget(ClickButton(text="gp Label 002", size_hint=(None, 0.4)))
        spanel.container.add_widget(ClickButton(text="gp Button 003", size_hint=(None, 0.4)))
        grid.add_widget(spanel)

        # Title Panel Center -----------------------------------------------------
        tpanel = TitlePanel(title='Title Panel Center', title_align='center', spacing=5, padding=5)
        tpanel.transparent=True
        tpanel.container.add_widget(BoxPanel())
        grid.add_widget(tpanel)

        # Title Panel Left -----------------------------------------------------
        tpanel = TitlePanel(title='Title Panel Left', title_align='left', spacing=5, padding=5)
        tpanel.transparent = True
        tpanel.container.add_widget(ClickButton(text="gp Button 001", size_hint=(1, 1)))
        # tpanel.container.add_widget(ClickButton(text_label="gp Label 002", size_hint=(1, 1)))
        tpanel.container.add_widget(ClickButton(text="gp Button 003", size_hint=(0.5, 1)))
        grid.add_widget(tpanel)

        # Title Panel Right -----------------------------------------------------
        tpanel = TitlePanel(title='Title Panel Right', title_align='right', spacing=5, padding=5)
        tpanel.transparent = True
        tpanel.container.add_widget(ClickButton(text="gp Button 001", size_hint=(1, 1)))
        # tpanel.container.add_widget(ClickButton(text="gp Label 002", size_hint=(1, 1)))
        tpanel.container.add_widget(ClickButton(text="gp Button 003", size_hint=(0.5, 1)))
        grid.add_widget(tpanel)


        return grid

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
