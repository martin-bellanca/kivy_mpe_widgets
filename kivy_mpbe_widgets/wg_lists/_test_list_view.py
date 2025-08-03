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
from kivy_mpbe_widgets.wg_lists.list_view import ListView, ListView
from kivy_mpbe_widgets.wg_lists.items import TextItem
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
        # LIST VIEW ------------------------------------------------------------------
        it_list = list()
        for it in range(1, 15, 1):
            text = 'Item de List nro {}'.format(it)
            tit = TextItem(text)
            it_list.append(tit)
        self.lv = ListView(items_list=it_list,
                           multi_select=False)
        self.lv.transparent = True
        pply.add_widget(self.lv)
        self.lv.bind(on_select_list_item=self.on_select)

        # BOTONES DE PRUEBAS -------------------------------------------------------
        blv = GridLayout(cols=3, size_hint=(1, 1), spacing=4, padding=4)
        pply.add_widget(blv)
        # Boton Add
        btn = ClickButton(name="Add Item", text_label="Add Item", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_add_item)
        blv.add_widget(btn)
        # Boton Insert
        btn = ClickButton(name="Insert Item", text_label="Insert Item 1 (id=1)", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_insert_item)
        blv.add_widget(btn)
        # Boton Remove
        btn = ClickButton(name="Remove Item", text_label="Remove Item 3, 4", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_remove_item)
        blv.add_widget(btn)
        # Boton GetItem
        btn = ClickButton(name="Get Item", text_label="Get Item id=02", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_get_item)
        blv.add_widget(btn)
        # Boton IsItem
        btn = ClickButton(name="Is Item", text_label="Is Item id=02", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_is_item)
        blv.add_widget(btn)
        # Boton Modify Item
        btn = ClickButton(name="Modify Item", text_label="Modify Item id=02", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_modify_item)
        blv.add_widget(btn)
        # Boton Clear Items
        btn = ClickButton(name="Clear Item", text_label="Clear Items", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_clear_item)
        blv.add_widget(btn)
        # Boton Add List Items
        btn = ClickButton(name="Add List Item", text_label="Add List Items", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_add_list_item)
        blv.add_widget(btn)
        # Boton Insert List Items
        btn = ClickButton(name="Insert List Item", text_label="Insert List Items", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_insert_list_item)
        blv.add_widget(btn)
        # Boton Get List Items
        btn = ClickButton(name="Get List Item", text_label="Get List Items", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_get_list_item)
        blv.add_widget(btn)
        # Boton Get List imgs
        btn = ClickButton(name="Get List Images", text_label="Get List Images", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_get_list_imgs)
        blv.add_widget(btn)
        # Boton Get List Icons
        btn = ClickButton(name="Get List Icons", text_label="Get List Icons", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self.on_get_list_icons)
        blv.add_widget(btn)
        # Boton Selct
        btn = ClickButton(name="Select item 2", text_label="Select item 2", size_hint=(1, None))
        btn.height = 50
        btn.bind(on_click=self._on_selection)
        blv.add_widget(btn)

        return pply

    def on_select(self, instance, id, item):
        print("Selected id "+str(id)+", "+item.text)

    def on_add_item(self, instance, touch, keycode):
        print("Insert Add")
        self.lv.add_item("Nuevo Add Item")

    def on_insert_item(self, instance, touch, keycode):
        print("Insert Item")
        self.lv.insert_item(1, "Nuevo Item")

    def on_remove_item(self, instance, touch, keycode):
        self.lv.remove_item(3, 4)

    def on_get_item(self, instance, touch, keycode):
        txt = self.lv.get_item(2)  # "text_item 02"
        print(txt)

    def on_is_item(self, instance, touchm, keycode):
        id = self.lv.is_item("text_item 02")
        print(id)

    def on_modify_item(self, instance, touchm, keycode):
        self.lv.modify_item(2, new_text="New Text", new_img=kivy_dkw.IMAGES + "type-task-1-i30.png")

    def on_clear_item(self, instance, touchm, keycode):
        self.lv.clear_items()

    def on_add_list_item(self, instance, touchm, keycode):
        self.lv.add_list_items(["New 01", "New 02", "New 03"])

    def on_insert_list_item(self, instance, touchm, keycode):
        self.lv.insert_list_items(1, ["New 01", "New 02", "New 03"])

    def on_get_list_item(self, instance, touchm, keycode):
        print(self.lv.get_txt_list_items())

    def on_get_list_imgs(self, instance, touchm, keycode):
        print(self.lv.get_img_src_list_items())

    def on_get_list_icons(self, instance, touchm, keycode):
        print(self.lv.get_icon_name_list_items())

    def app_finish_init(self, *dt):
        win = self._app_window
        win.bind(on_request_close=self._on_close_app)

    def _on_close_app(self, *largs, **kwargs):
        if 'source' in kwargs and kwargs['source'] == 'keyboard':
            return True
        else:
            return False

    def _on_selection(self, instance, touchm, keycode):
        self.lv.select(2)



if __name__ == '__main__':
    TestApp().run()
