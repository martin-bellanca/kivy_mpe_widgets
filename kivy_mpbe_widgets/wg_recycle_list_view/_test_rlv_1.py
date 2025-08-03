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
from kivy.uix.label import Label

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_recycle_list_view.recycle_list_view import RecycleListView, FileListView
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import BaseItem, BaseDataDic
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import TextDataDic, TextItem
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import EditableDataDic, EditableItem
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import IconEditableDataDic, IconEditableItem
from kivy_mpbe_widgets.wg_recycle_list_view.data_items import FileDataDic, FileItem
from kivy_mpbe_widgets.wg_panels.panels import BoxPanel
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButton


print(sys.path)


class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "List View Test"

    def build(self):
        # Clock.schedule_once(self.app_finish_init, 0)
        Window.size = (800, 800)
        Window.clearcolor = self.theme.style['background_app']
        return self.test01()


    def test01(self):
        # Base Layout
        pply = BoxLayout(orientation="vertical", size_hint=(1,1), spacing=4, padding=4)
        boxh = BoxLayout(orientation='horizontal')
        pply.add_widget(boxh)



        # ListView - EditableItem with Icon----------------------------------------------------------------------
        # bpanel = BoxPanel(padding=(0, 0))
        # bpanel.transparent = True
        # boxh.add_widget(bpanel)
        self.rlv_eii = RecycleListView(size_hint=(1, 1))
        self.rlv_eii.viewclass = 'IconEditableItem'
        self.rlv_eii.bind(on_select_item=self._on_select_item, on_unselect_item=self._on_unselect_item)
        for ii in range(10):
            id = f'Data Item {ii}'
            # ss = True if ii == 5 else False
            ss = False
            icn = 'alarm'
            if ii == 5:
                ss = True
                icn = 'account'
            item = IconEditableDataDic(id=id, text=f'Texto del Item {ii}', icon_name=icn, selected=ss)
            it_dict = item.to_dict()
            self.rlv_eii.data.append(it_dict)
        boxh.add_widget(self.rlv_eii)
        # bpanel.container.add_widget(self.rlv_eii)

        # # ListView - File Item -------------------------------------------------------------------------
        # bpanel = BoxPanel(padding=(0, 0))
        # bpanel.transparent = True
        # boxh.add_widget(bpanel)
        # self.rlv_fi = FileListView(folder='/home/mpbe/Basura/PRUEBA', size_hint=(1, 1))
        # # self.rlv_fi.viewclass = 'FileItem'
        # self.rlv_fi.bind(on_select_item=self._on_select_item, on_unselect_item=self._on_unselect_item)
        # self.rlv_fi.bind(on_duplicate_file=self._on_duplicate_file, on_delete_file=self._on_delete_file)
        # bpanel.container.add_widget(self.rlv_fi)

        # Botones --------------------------------------------------------
        boxv = BoxLayout(orientation='vertical')
        boxh.add_widget(boxv)
        boxv.add_widget(ClickButton("boton 1"))
        boxv.add_widget(ClickButton("boton 2"))
        boxv.add_widget(ClickButton("boton 3"))


        return pply

    # Eventos ----------------------------------------------------------------------------
    def _on_select_item(self, instance, data, index):
        # print(f'App._select_item -> {index} - name {data["file_name"]}')
        pass

    def _on_unselect_item(self, instance, data, index):
        # print(f'App._unselect_item -> {index} - name {data["file_name"]}')
        pass

    def _on_duplicate_file(self, instance, new_file_name, source_file_name):
        # print('App.Archivo Duplicado ---------------------')
        # print(f'  New name: {new_file_name} - Source name: {source_file_name}')
        pass

    def _on_delete_file(self, instance, file_name):
        # print('Archivo Borrado ---------------------')
        # print(f'  File name: {file_name}')
        pass


if __name__ == '__main__':
    TestApp().run()
