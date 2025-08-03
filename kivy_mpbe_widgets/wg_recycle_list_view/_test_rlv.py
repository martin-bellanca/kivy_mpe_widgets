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
from kivy_mpbe_widgets.wg_recycle_list_view.recycle_list_view import FileListView
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

        # bpanel = BoxPanel(padding=(0, 0))
        # bpanel.transparent = True
        # boxh.add_widget(bpanel)


        # # ListView - BaseItem ----------------------------------------------------------------------
        # bpanel = BoxPanel(padding=(0, 0))
        # bpanel.transparent = True
        # boxh.add_widget(bpanel)
        # self.rlv = RecycleListView(size_hint=(1,1))
        # self.rlv.viewclass = 'BaseItem'
        # self.rlv.bind(on_select_item=self._on_select_item, on_unselect_item=self._on_unselect_item)
        # # self.rlv.data = [{'text': f'Data Item {x}', 'activate_background':False} for x in range(100)]
        # for ii in range(100):
        #     id = f'Data Item {ii}'
        #     ss = True if ii == 1 else False
        #     item = BaseDataDic(id=id, selected=ss)
        #     self.rlv.data.append(item.to_dict())
        # # self.rlv.refresh_from_data()
        # bpanel.container.add_widget(self.rlv)
        # # boxh.add_widget(self.rlv)

        # # ListView - TextItem ----------------------------------------------------------------------
        # bpanel = BoxPanel(padding=(0, 0))
        # bpanel.transparent = True
        # boxh.add_widget(bpanel)
        # self.rlv_ti = RecycleListView(size_hint=(1, 1))
        # self.rlv_ti.viewclass = 'TextItem'
        # self.rlv_ti.bind(on_select_item=self._on_select_item, on_unselect_item=self._on_unselect_item)
        # for ii in range(100):
        #     id = f'Data Item {ii}'
        #     ss = True if ii == 2 else False
        #     item = TextDataDic(id=id, text=f'Texto del Item {ii}', state_select=ss)
        #     self.rlv_ti.data.append(item.to_dict())
        # bpanel.container.add_widget(self.rlv_ti)

        # ListView - EditableItem ----------------------------------------------------------------------
        # bpanel = BoxPanel(padding=(0, 0))
        # bpanel.transparent = True
        # boxh.add_widget(bpanel)
        # self.rlv_ei = RecycleListView(size_hint=(1, 1))
        # self.rlv_ei.viewclass = 'EditableItem'
        # self.rlv_ei.bind(on_select_item=self._on_select_item, on_unselect_item=self._on_unselect_item)
        # for ii in range(100):
        #     id = f'Data Item {ii}'
        #     ss = True if ii == 8 else False
        #     item = EditableDataDic(id=id, text=f'Texto del Item {ii}', state_select=ss)
        #     self.rlv_ei.data.append(item.to_dict())
        # bpanel.container.add_widget(self.rlv_ei)

        # ListView - EditableItem with Icon----------------------------------------------------------------------
        bpanel = BoxPanel(padding=(0, 0))
        bpanel.transparent = True
        boxh.add_widget(bpanel)
        self.rlv_eii = RecycleListViewUnfocused(size_hint=(1, 1))
        self.rlv_eii.viewclass = 'IconEditableItem'
        self.rlv_eii.bind(on_select_item=self._on_select_item, on_unselect_item=self._on_unselect_item)
        for ii in range(100):
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
        bpanel.container.add_widget(self.rlv_eii)

        # ListView - File Item -------------------------------------------------------------------------
        bpanel = BoxPanel(padding=(0, 0))
        bpanel.transparent = True
        boxh.add_widget(bpanel)
        self.rlv_fi = FileListView(folder='/home/mpbe/Basura/PRUEBA', size_hint=(1, 1))
        # self.rlv_fi.viewclass = 'FileItem'
        self.rlv_fi.bind(on_select_item=self._on_select_item, on_unselect_item=self._on_unselect_item)
        self.rlv_fi.bind(on_duplicate_file=self._on_duplicate_file, on_delete_file=self._on_delete_file)
        bpanel.container.add_widget(self.rlv_fi)

        # Botones --------------------------------------------------------
        boxv = BoxLayout(orientation='vertical')
        boxh.add_widget(boxv)
        boxv.add_widget(ClickButton("boton 1"))
        boxv.add_widget(ClickButton("boton 2"))
        boxv.add_widget(ClickButton("boton 3"))


        return pply

    # Eventos ----------------------------------------------------------------------------
    def _on_select_item(self, instance, data, index):
        print(f'App._select_item -> {index} - name {data["file_name"]}')

    def _on_unselect_item(self, instance, data, index):
        print(f'App._unselect_item -> {index} - name {data["file_name"]}')

    def _on_duplicate_file(self, instance, new_file_name, source_file_name):
        print('App.Archivo Duplicado ---------------------')
        print(f'  New name: {new_file_name} - Source name: {source_file_name}')

    def _on_delete_file(self, instance, file_name):
        print('Archivo Borrado ---------------------')
        print(f'  File name: {file_name}')


if __name__ == '__main__':
    TestApp().run()
