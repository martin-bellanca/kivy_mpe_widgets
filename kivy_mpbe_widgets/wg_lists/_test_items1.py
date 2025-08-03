"""------------------------------------------------------------------------"""
"""-- Test Program  -------------------------------------------------------"""
"""------------------------------------------------------------------------"""

# imports del sistema -------------------------------------------------------
import os
import sys
import datetime
print(sys.path)
from helpers_mpbe.python import compose, compose_dict
# Kivy imports --------------------------------------------------------------
import kivy
kivy.require('1.10.1')
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_inputs.inputs import EditableTextLabel
from kivy_mpbe_widgets.wg_lists.list_view import ListView, ListView
from kivy_mpbe_widgets.wg_lists.items_1 import BaseItem, TextItem, EditableItem
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButton


print(sys.path)


class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "List View Test"

    def build(self):
        Clock.schedule_once(self.app_finish_init, 0)
        Window.size = (476, 800)
        Window.clearcolor = self.theme.style['background_app']
        return self.test01()


    def test01(self):
        # Base Layout
        pply = BoxLayout(orientation="vertical", size_hint=(1,1), spacing=4, padding=4)
        boxh = BoxLayout(orientation='horizontal')
        pply.add_widget(boxh)
        # ListView - BaseItem ----------------------------------------------------------------------
        it_list = list()
        for it in range(1, 15, 1):
            text = 'Item de List nro {}'.format(it)
            ss = it / 2 - int(it / 2)
            if it/2-int(it/2) > 0:
                ab = False
            else:
                ab = True
            tit = BaseItem(active_background=ab)
            it_list.append(tit)
        self.lv = ListView(items_list=it_list,
                           multi_select=False)
        self.lv.transparent = True
        boxh.add_widget(self.lv)
        # self.lv.bind(on_select_list_item=self.on_select)

        # ListView - EditableItem ----------------------------------------------------------------------
        it_list = list()
        for it in range(1, 15, 1):
            text = 'Editable Item nro {}'.format(it)
            ss = it / 2 - int(it / 2)
            if it / 2 - int(it / 2) > 0:
                ab = False
            else:
                ab = True
            tit = EditableItem(active_background=ab, text=text)
            it_list.append(tit)
            tit.bind(on_start_editing=self._on_start_editing,
                     on_finish_editing=self._on_finish_editing)
        self.lv = ListView(items_list=it_list,
                           multi_select=False)
        self.lv.transparent = True
        boxh.add_widget(self.lv)
        # self.lv.bind(on_select_list_item=self.on_select)

        # ListView - TextItem ----------------------------------------------------------------------
        it_list = list()
        for it in range(1, 15, 1):
            text = 'Item de List nro {}'.format(it)
            ss = it / 2 - int(it / 2)
            if it / 2 - int(it / 2) > 0:
                ab = False
            else:
                ab = True
            tit = TextItem(active_background=ab, text=text)
            it_list.append(tit)
        self.lv = ListView(items_list=it_list,
                           multi_select=False)
        self.lv.transparent = True
        boxh.add_widget(self.lv)
        # self.lv.bind(on_select_list_item=self.on_select)



        # BaseListItem -------------------------------------------------------------------
        edt_lbl = EditableTextLabel(text="Texto de Prueba para Editar")
        pply.add_widget(edt_lbl)

        it_base = BaseItem(alpha_background=0.0)
        pply.add_widget(it_base)
        it_base = BaseItem(alpha_background=0.0)
        pply.add_widget(it_base)


        # self.lv.bind(on_select_list_item=self.on_select)

        # BOTONES DE PRUEBAS -------------------------------------------------------
        # Boton Selct
        btn = ClickButton(name="Select item 2", text_label="Select item 2", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self._on_selection)
        pply.add_widget(btn)

        return pply

    def app_finish_init(self, *dt):
        win = self._app_window
        win.bind(on_request_close=self._on_close_app)

    def _on_close_app(self, *largs, **kwargs):
        if 'source' in kwargs and kwargs['source'] == 'keyboard':
            return True
        else:
            return False

    def _on_selection(self, instance, value, key):
        pass

    def _on_start_editing(self, instance):
        print(f"Start Editing in Test")

    def _on_finish_editing(self, instance, text):
        print(f"Finish Editing in Test: {text}")



if __name__ == '__main__':
    TestApp().run()
