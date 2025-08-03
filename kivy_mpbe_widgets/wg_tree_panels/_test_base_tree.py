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
from kivy.uix.treeview import TreeViewLabel, TreeViewNode

# kivy_dkw ------------------------------------------------------------------
import kivy_mpbe_widgets
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_tree_panels.tree_panels import TreePanel, FileTreePanel
from kivy_mpbe_widgets.wg_tree_panels.nodes import IconNode, FontIconNode
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickButton


print(sys.path)


class TestApp(App):
    theme = Theme(name='flat_light', style='light')
    title = "Tree Base Test"

    def build(self):
        Clock.schedule_once(self.app_finish_init, 0)
        Window.size = (476, 800)
        Window.clearcolor = self.theme.style['background_app']
        return self.test01()


    def test01(self):
        # Base Layout
        pply = BoxLayout(orientation="vertical", size_hint=(1,1), spacing=4, padding=4)

        # TreeView ---------------------------------------------------------------
        tree_panel = TreePanel()
        tree_panel.transparent = True
        pply.add_widget(tree_panel)
        self._populate_tree_prj(tree_panel.tree_view)
        # self.bt.bind(on_select_list_item=self.on_select)

        # FileTreePanel --------------------------------------------------------------
        file_tree_panel = FileTreePanel(root_path="/home/mpbe/Basura/PRUEBA", show_files=True)
        # tree_panel.transparent = True
        pply.add_widget(file_tree_panel)

        # # BOTONES DE PRUEBAS -------------------------------------------------------
        # blv = GridLayout(cols=3, size_hint=(1, 1), spacing=4, padding=4)
        # pply.add_widget(blv)


        return pply

    # UI ---------------------------------------------------
    def _populate_tree_prj(self, tree):
        for item in range(1, 8, 1):
            icon_text = '[b][color=#3498db] Item de Tree nro {}[/color][/b]'.format(item)
            # icon_node = IconNode(text=icon_text, icon_source="icon-archive-i24.png", markup=True)
            icon_node = FontIconNode(text=icon_text, icon_name='account', markup=True, icon_color = (1, 0, 0, 1))
            # node = tree.add_node(TreeViewLabel(text=icon_text, markup=True))
            node = tree.add_node(icon_node)
            self._add_subdirectories(tree, node)



        # for item in os.listdir(path):
        #     full_path = os.path.join(path, item)
        #     if os.path.isdir(full_path):
        #         # Nodo de carpeta con ícono en markup
        #         icon_text = '[b][color=#3498db]📁 {}[/color][/b]'.format(item)
        #         node = tree.add_node(TreeViewLabel(text=icon_text, markup=True))
        #         self._add_subdirectories(tree, node, full_path)
        #     # else:
        #     #     # Nodo de archivo con ícono en markup
        #     #     icon_text = '[b][color=#2ecc71]📄 {}[/color][/b]'.format(item)
        #     #     tree.add_node(TreeViewLabel(text=icon_text, markup=True))

    def _add_subdirectories(self, tree, node):
        for item in range(1, 4, 1):
            icon_text = '[b][color=#3400db]Sub-Item de Tree nro {}[/color][/b]'.format(item)
            # icon_node = FontIconNode(text=icon_text, icon_name='account', markup=True)
            icon_node = IconNode(text=icon_text, icon_source="icon-archive-i24.png", markup=True)
            sub_node = tree.add_node(icon_node, node)


        # for item in os.listdir(path):
        #     full_path = os.path.join(path, item)
        #     if os.path.isdir(full_path):
        #         # Subcarpeta con ícono en markup
        #         icon_text = '[b][color=#3498db]📁 {}[/color][/b]'.format(item)
        #         sub_node = tree.add_node(TreeViewLabel(text=icon_text, markup=True), node)
        #         self._add_subdirectories(tree, sub_node, full_path)
        #     # else:
        #     #     # Archivo dentro de subcarpeta con ícono en markup
        #     #     icon_text = '[b][color=#2ecc71]📄 {}[/color][/b]'.format(item)
        #     #     tree.add_node(TreeViewLabel(text=icon_text, markup=True), node)


    # Events -------------------------------

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