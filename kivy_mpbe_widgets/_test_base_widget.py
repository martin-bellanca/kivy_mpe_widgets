# -*- coding: utf-8 -*-
#
#  base_widgets.py
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



# kivy imports --------------------------------------------------------------
import kivy
from kivy.uix.boxlayout import BoxLayout

kivy.require('1.10.1')
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window

from kivy.uix.gridlayout import GridLayout
# mpbe imports --------------------------------------------------------------
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.base_widgets import *
from kivy_mpbe_widgets.theming import Theme


class BaseWidgetApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Test Base Widgets"

    def build(self):
        Clock.schedule_once(self.app_finish_init, 0)
        Window.clearcolor = self.theme.style['background_app']
        return self.test02()

    def test02(self):
        grid = GridLayout(cols=4, spacing=6, padding=6)
        # grid = BoxLayout(orientation='vertical')
        # FrameUnfocused ---------------------------------------------------
        self.fuf01 = FrameUnfocused(size_hint=(0.5,0.5))
        grid.add_widget(self.fuf01)


        self.fuf02 = FrameUnfocused(radius=(-1, 30, 0, 15), draw_borders=(True, True, True, True))
        grid.add_widget(self.fuf02)

        self.fuf03 = FrameUnfocused(transparent=True, radius=(0, 0, 0, 0), draw_borders=(True, False, True, False))
        grid.add_widget(self.fuf03)

        self.fuf04 = FrameUnfocused(disabled=True)
        grid.add_widget(self.fuf04)

        # FrameFocused ---------------------------------------------------
        self.ff01 = FrameFocused(size_hint=(1, None), height=30)
        grid.add_widget(self.ff01)

        self.ff02 = FrameFocused(flat=True)
        grid.add_widget(self.ff02)

        self.ff03 = FrameFocused(transparent=True, radius=(10, 0, 10, 10))
        self.ff03.bind(on_hotlight=self.on_hotlight)
        grid.add_widget(self.ff03)

        self.ff04 = FrameFocused(disabled=True, draw_borders=(True, False, True, False))
        grid.add_widget(self.ff04)
        # --------------------------------------------------
        return grid

    def app_finish_init(self, *dt):
        win = self._app_window
        win.bind(on_request_close=self._on_close_app)

    def _on_close_app(self, *largs, **kwargs):
            if 'source' in kwargs and kwargs['source'] == 'keyboard':
                return True
            else:
                return False

    def on_hotlight(self, instance, state, mp):
        print(f'Hot Light {instance.ids} {state}')

if __name__ == "__main__":
    BaseWidgetApp().run()