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
from kivy_dkw.base_widget import *
from panels import BoxPanel
from kivy_dkw.wg_labels.text_labels import TextLabel
from kivy_dkw.wg_buttons.toggle_buttons import ToggleButton
from kivy_dkw.wg_buttons.click_buttons import ClickButton


class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Frame Widgets"

    def build(self):
        # Clock.schedule_once(self.app_finish_init, 0)
        Window.clearcolor = self.theme.style['background_app']
        return self.test02()

    def test02(self):
        # Box Panel -----------------------------------------------------
        bpanel = BoxPanel(spacing=5, padding=10)
        # bpanel.transparent=True
        for ii in range(1, 10):
            tb = ToggleButton(text_label="bp Toggle Label 00" + str(ii), text_halign='left', size_hint=(1, None))
            tb.height = 26
            bpanel.container.add_widget(tb)




        return bpanel

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