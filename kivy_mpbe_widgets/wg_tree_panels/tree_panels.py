#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tree_panels.py
#
#  Copyright 2020 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License fo
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


'''
Tree Base widget for kivy_dkw \n
Created on 06/10/2024

@author: mpbe
@note:
'''


# imports del sistema -------------------------------------------------------
import os
import sys
import re
import shutil

from kivy import level
from kivy.uix.widget import Widget

from helpers_mpbe.python import compose, compose_dict, FolderWrapper
# Kivy imports --------------------------------------------------------------
import kivy
kivy.require('1.10.1')
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty, ColorProperty
from kivy.uix.label import Label
from kivy.uix.image import Image
# kivy_mpbe_widgets ------------------------------------------------------------------
from kivy_mpbe_widgets.theming import ThemableBehavior
from kivy_mpbe_widgets.graphics.widget_graphics import GFocus
from kivy_mpbe_widgets.base_widgets import FrameFocused
from kivy_mpbe_widgets.wg_panels.panels import BoxPanel
from kivy_mpbe_widgets.wg_dialogs.basic_dialogs import TwoButtonsDialog
from kivy_mpbe_widgets.wg_buttons.click_buttons import ClickIcon
from kivy_mpbe_widgets.wg_tree_panels.nodes import FontIconNode, FileNode
from kivy_mpbe_widgets.wg_buttons.toggle_buttons import ToggleButton
from kivy_mpbe_widgets.events.tree_events import TreeNodeSelectedEventDispatcher
from kivy_mpbe_widgets.events.file_events import DeleteFileEventDispatcher, RenameFileEventDispatcher, DuplicateFileEventDispatcher
from kivy_mpbe_widgets.events.file_events import NewFileEventDispatcher, NewFolderEventDispatcher


# Builder.load_string('''
# <TreePanel_KV>
#     tree_view: tree_view
#     ScrollView:
#         size_hint: 1, 1
#         do_scroll_x: False
#         do_scroll_y: True
#         scroll_type: ['bars', 'content']
#         scroll_wheel_distance: dp(50)
#         bar_width: dp(10)
#         bar_color: root.theme.colors['accent_face']
#         TreeView:
#             id: tree_view
#             size_hint_y: None
#             height: self.minimum_height
#             hide_root: False
#             root_options: {'text': '[b][color=#000000]Root Directory[/color][/b]', 'markup': True}
#             indent_level: 15
#
# ''')
#
#
# class TreePanel_KV(BoxPanel):  # VER z_panel_kvlenguaje.py
#     """
#     Widget Kivy_KDW
#     Events:
#
#     """
#     tree_view = ObjectProperty(None)  # Propiedad para referenciar el tree
#


#     def __init__(self, name='string list view', **kwargs):
#         """Constructor class
#         Args:
#
#         """
#         # base init ------------------------------------------
#         super().__init__(name=name, **kwargs)
#         # themes config --------------------------------------
#         # self.spacing = bb
#         # self.padding = bb
#         # UI widgets -----------------------------------------
#         # self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True,
#         #                               scroll_type=['bars', 'content'], scroll_wheel_distance=dp(50), bar_width=dp(10))
#         self.scroll_view.bar_color = self.theme.colors['accent_face']
#         self.add_widget(self.scroll_view)
#         self.tree_view = TreeView(root_options={'text': '[b][color=#000000]Root Directory[/color][/b]', 'markup': True},
#                                  hide_root=False, indent_level=15, size_hint_y=None)
#         self.scroll_view.add_widget(self.tree_view)
#         self.tree_view.bind(minimum_height=self.tree_view.setter('height'))  # Permitir el autoajuste de altura
#
#         # schedule -------------------------------------------
#         Clock.schedule_once(lambda dt: self._finish_init(dt))
#
#     def _finish_init(self, dt):
#         self.update_geometry()
#
#
#     """ UI Functions ------------------------------------------------"""
#     def update_geometry(self):
#         '''Update button position value'''
#         # w, h = self.size
#         # x, y = self.pos
#         self.scroll_view.pos = self.pos  # (x + bb, y +bb)
#         self.scroll_view.size = self.size  # (w-bb*2, h-bb*2)
#         super().update_geometry()
#
#     def redraw(self, instance, args):
#         super().redraw(instance, args)
#         self.update_geometry()
#
#     """ Tree functions ----------------------------------------------"""
#
#
#
#     """ UI Events ---------------------------------------------------"""




class TreePanelUnFocused(BoxPanel, TreeNodeSelectedEventDispatcher):
    """
    Widget Kivy_KDW
    Events:

    """

    def __init__(self, **kwargs):
        """
        Panel con abrol
        Attributes:

        """
        # base init ------------------------------------------
        super().__init__(**kwargs)
        # themes config --------------------------------------
        # self.spacing = bb
        # self.padding = bb
        # UI widgets -----------------------------------------
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True,
                                      scroll_type=['bars', 'content'], scroll_wheel_distance=dp(50), bar_width=dp(10))
        self.scroll_view.bar_color = self.theme.colors['accent_face']
        self.container.padding = 1
        self.container.add_widget(self.scroll_view)
        self.tree_view = TreeView(root_options={'text': '[b][color=#000000]Root Directory[/color][/b]', 'markup': True},
                                 hide_root=False, indent_level=15, size_hint_y=None)
        self.scroll_view.add_widget(self.tree_view)
        self.tree_view.bind(minimum_height=self.tree_view.setter('height'))  # Permitir el autoajuste de altura

        # AGREGAR FOCUS GRAPHIC

        # schedule -------------------------------------------
    #     Clock.schedule_once(lambda dt: self._finish_init(dt))
    #
    # def _finish_init(self, dt):
    #     self.update_geometry()


    """ UI Functions ------------------------------------------------"""


    """ Tree functions ----------------------------------------------"""


    """ UI Events ---------------------------------------------------"""


class TreePanel(FrameFocused, TreeNodeSelectedEventDispatcher):
    """
    Widget Kivy_KDW
    Events:

    """

    def __init__(self, **kwargs):
        """
        Panel con abrol
        Attributes:

        """
        # base init ------------------------------------------
        FrameFocused.__init__(self, hotlight=False)
        TreeNodeSelectedEventDispatcher.__init__(self)
        # themes config --------------------------------------
        # self.spacing = bb
        # self.padding = bb

        # UI widgets -----------------------------------------
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True,
                                      scroll_type=['bars', 'content'], scroll_wheel_distance=dp(50), bar_width=dp(10))
        self.scroll_view.bar_color = self.theme.colors['accent_face']
        self.container.padding = 1
        self.container.add_widget(self.scroll_view)
        self.tree_view = TreeView(root_options={'text': '[b][color=#000000]Root Directory[/color][/b]', 'markup': True},
                                 hide_root=False, indent_level=15, size_hint_y=None)
        self.scroll_view.add_widget(self.tree_view)
        self.tree_view.bind(minimum_height=self.tree_view.setter('height'))  # Permitir el autoajuste de altura

        # AGREGAR FOCUS GRAPHIC

        # schedule -------------------------------------------
    #     Clock.schedule_once(lambda dt: self._finish_init(dt))
    #
    # def _finish_init(self, dt):
    #     self.update_geometry()


    """ UI Functions ------------------------------------------------"""
    def on_hotlight_item(self, item, state):
        pass

    """ Tree functions ----------------------------------------------"""


    """ UI Events ---------------------------------------------------"""


class FileTreeView(TreeView, ThemableBehavior, NewFileEventDispatcher, NewFolderEventDispatcher,
                    RenameFileEventDispatcher, DuplicateFileEventDispatcher, DeleteFileEventDispatcher,
                    TreeNodeSelectedEventDispatcher):
    root_path = StringProperty()
    sorted = BooleanProperty(True)
    show_hidden = BooleanProperty(False)
    show_files = BooleanProperty(True)
    filter_ext = ListProperty(['*'])
    icons_color = ColorProperty((0, 0, 0, 1))

    def __init__(self, root_path, sorted=True, show_files=True, filter_ext=['*'], show_hidden=False, **kwargs):
        # super().__init__()
        TreeView.__init__(self)
        ThemableBehavior.__init__(self)
        NewFileEventDispatcher.__init__(self)
        NewFolderEventDispatcher.__init__(self)
        RenameFileEventDispatcher.__init__(self)
        DuplicateFileEventDispatcher.__init__(self)
        DeleteFileEventDispatcher.__init__(self)
        TreeNodeSelectedEventDispatcher.__init__(self)

        self.sorted = sorted
        self.show_files = show_files
        self.filter_etx = filter_ext
        self.show_hidden = show_hidden
        self.color_icons = self.theme.colors['icons']
        self.hide_root = True
        self.root_node = None
        self.root_path = root_path
        self._node_hotlight = None
        self._Rename_old_name = None
        self._rename_path = None

        # Botones IconClick
        # self.btn_new_file = ClickIcon(icon_name='note-plus', icon_size=18, size_hint_x=None)
        # self.btn_new_folder = ClickIcon(icon_name='folder-plus', icon_size=18, size_hint_x=None)
        # self.btn_rename = ClickIcon(icon_name='rename-box', icon_size=18, size_hint_x=None)
        # self.btn_duplicate = ClickIcon(icon_name='file-multiple', icon_size=18, size_hint_x=None)
        # self.btn_delete = ClickIcon(icon_name='delete', icon_size=18, size_hint_x=None)

    '''Manipulacion del Arbol de Directorio -----------------------------------'''
    def _populate_tree_prj(self, path, node=None, sorted=True, show_files=True, filters=['*'], show_hidden=False):
        wrapper = FolderWrapper(path)
        lstfolders, lstfiles = wrapper.getChildsNames(sorted, show_hidden, filters)
        for folder in lstfolders:
            icon_node = FileNode(text=folder, icon_name='folder', markup=True, icon_color=(0.3, 0.3, 0.4, 1), type="folder")
            icon_node.label.bind(on_finish_editing=self._on_finish_editing)
            child_node = self.add_node(icon_node, node)
            # child_node.bind(on_touch_down=self.on_node_touch)
            child_path = path + os.sep + folder
            child_node.path_node = child_path
            self._populate_tree_prj(child_path, child_node, sorted, show_files, filters, show_hidden)
        if show_files:
            for file in lstfiles:
                icon_node = FileNode(text=file, icon_name='file', markup=True, icon_color=(0.4, 0.4, 0.4, 1), type="file")
                icon_node.label.bind(on_finish_editing=self._on_finish_editing)
                file_node = self.add_node(icon_node, node)
                file_node.path_node = path
                # file_node.bind(on_touch_down=self.on_node_touch)

    def matches_filters(self, filename):
        # Convierte cada filtro en una expresión regular
        filters = self.filter_files
        patterns = [
            re.compile(
                filter.replace('.', r'\.').replace('*', r'.*') + '$'
            ) for filter in filters
        ]
        # Verifica si el filename coincide con alguno de los patrones
        return any(pattern.match(filename) for pattern in patterns)

    def clear_tree(self):
        if self.root_node:
            self.remove_node(self.root_node)

    def get_path_to_root(self, node):
        path = []
        level = node.level
        while level > 0:
            path.append(node.text)
            node = node.parent_node
            level = node.level
        path = path[::-1]  # Invertir para mostrar desde el root hasta el nod
        root_path = ""
        for ph in path:
            root_path += os.sep + ph
        return root_path

    def get_file_system_path(self, node):
        path = []
        node = node.parent_node
        level = node.level
        while level > 1:
            path.append(node.text)
            node = node.parent_node
            level = node.level
        path = path[::-1]  # Invertir para mostrar desde el root hasta el nod
        root_path = ""
        for ph in path:
            root_path += os.sep + ph
        return self.root_path + root_path

    '''UI Events --------------------------------------------------------------'''
    def on_root_path(self, instance, root_path):
        # self.folder_wrapper = FolderWrapper(value)
        self.clear_tree()
        self.root_path = root_path
        wrapper = FolderWrapper(root_path)
        icon_node = FileNode(text=wrapper.getFolderName(), icon_name='home', markup=True,
                             icon_color=self.color_icons, type="root_folder")
        root_node = self.add_node(icon_node)
        # root_node.bind(on_touch_down=self.on_node_touch)
        root_node.path_node = root_path
        self.root_node = root_node
        self._populate_tree_prj(path=self.root_path, node=root_node, sorted=self.sorted, show_files=self.show_files,
                                filters=self.filter_ext, show_hidden=self.show_hidden)
        self.toggle_node(root_node)
        self.select_node(root_node)

    def on_touch_down(self, touch):
        # print(f'FileTreeView.on_touch_down')
        # super(RecycleView, self).on_touch_down(touch)
        ltouch = self.to_local(*touch.pos)
        if self.collide_point(*ltouch) and len(
                self.children) > 0 and self.theme.level_render != 'high':
            for node in self.children:  # busca el item sobre el que se hizo el touch
                if node.collide_point(*touch.pos):
                    break
            # print(f'FileTreeView.on_touch_down - presion sobre el nodo {node.text}')
            if touch.button == 'left':  # Seleccion y Des-seleccion de los items (Boton Izquierdo)
                # Chequeo de botones
                if node.btn_new_file and node.btn_new_file.is_hotlight():
                    # print('FileTreeView.on_touch_down->btn new file presionado')
                    # print(f'  name: {node.text} - root path: {self.get_path_to_root(node)}')
                    # print(f'  name: {node.text} - file system path: {self.get_file_system_path(node)}')
                    node.btn_new_file.on_touch_down(touch)
                    self._new_file(node)
                    return True
                elif node.btn_new_folder and node.btn_new_folder.is_hotlight():
                    # print('FileTreeView.on_touch_down->btn new folder presionado')
                    node.btn_new_folder.on_touch_down(touch)
                    self._new_folder(node)

                    # self._duplicate_file(self._item_hotlight)
                    return True
                elif node.btn_rename and node.btn_rename.is_hotlight():
                    # print('FileTreeView.on_touch_down->btn rename presionado')
                    node.btn_rename.on_touch_down(touch)
                    self._rename_old_name = node.text
                    self._rename_path = self.get_file_system_path(node)
                    node.label.start_editing()
                    # RenameFileEventDispatcher.do_something(self, )
                    # self.start_edition()
                    return True
                elif node.btn_duplicate and node.btn_duplicate.is_hotlight():  # Solo en files
                    # print('FileTreeView.on_touch_down->btn duplicate presionado')
                    node.btn_duplicate.on_touch_down(touch)
                    self._duplicate_file(node)
                    # self.start_edition()
                    return True
                elif node.btn_delete and node.btn_delete.is_hotlight():
                    # print('FileTreeView.on_touch_down->btn delete presionado')
                    node.btn_delete.on_touch_down(touch)
                    self._delete_file(node)
                    # self._delete_file(self._item_hotlight)
                    return True
                # print("FileTreeView.on_touch_down - Selecciono una Carpeta --------------")
                TreeNodeSelectedEventDispatcher.do_something(self, node, touch)
            super().on_touch_down(touch)

    # def on_node_touch(self, node, mouse):
    #     TreeNodeSelectedEventDispatcher.do_something(self, node, mouse)

    '''Funciones sobre archivos -----------------------------------------------'''
    def _on_finish_editing(self, instance, new_name):
        print(f"FileTreeView._on_finish_editing({new_name}) - old name: {self._rename_old_name} - path: {self._rename_path}")
        if new_name != self._rename_old_name:
            # Renombra el archivo ----------------
            actual_name = self._rename_path + os.sep + self._rename_old_name
            new_name = self._rename_path + os.sep + new_name
            try:
                os.rename(actual_name, new_name)
            except:
                print("Error creando el directorio:\n")
                print(str(sys.exc_info()[0]) + '\n')
                print(str(sys.exc_info()[1]) + '\n')
                return None
            # Actualiza el valor de path_node (VERIFICAR)
            instance.path_node = self._rename_path
            # Call event --------------------------------------
            RenameFileEventDispatcher.do_something(self, new_name, self._rename_old_name, self._rename_path)
            self._rename_old_name = None
            self._rename_path = None

    def _new_file(self, node):
        if node.level > 1:
            path = self.get_file_system_path(node) + os.sep + node.text
        else:
            path = self.get_file_system_path(node)
        file = "new_file.md"
        # print(f'FileListView._new_file(file={file_name})')
        file_path = path + os.sep + file
        try:
            with open(file_path, 'x', encoding='utf-8') as archivo:
                archivo.write("Este es un archivo de texto nuevo.\n")
        except FileExistsError:
            print(f"The folder '{file_path}' already exists.")
            return False
        except Exception as e:
            print(f"Creating file error: {e}")
            return False
        # Crear el Nodo -----------------------
        if self.show_files:
            icon_node = FileNode(text=file, icon_name='file', markup=True, icon_color=(0.4, 0.4, 0.4, 1), type="file")
            icon_node.label.bind(on_finish_editing=self._on_finish_editing)
            file_node = self.add_node(icon_node, node)
            file_node.path_node = path
        # Call event --------------------------
        NewFileEventDispatcher.do_something(self, path)
        return True

    def _new_folder(self, node):
        if node.level > 1:
            path = self.get_file_system_path(node) + os.sep + node.text
        else:
            path = self.get_file_system_path(node)
        # print(f'FileListView._new_folder(file={file_name})')
        file_path = path + os.sep + "new_folder"
        try:
            os.mkdir(file_path)
        except FileExistsError:
            print(f"The folder '{file_path}' already exists.")
            return False
        except Exception as e:
            print(f"Creating file error: {e}")
            return False
        # Crear el Nodo -----------------------
        icon_node = FileNode(text="new_folder", icon_name='folder', markup=True, icon_color=(0.3, 0.3, 0.4, 1), type="folder")
        icon_node.label.bind(on_finish_editing=self._on_finish_editing)
        child_node = self.add_node(icon_node, node)
        child_node.path_node = file_path
        # Call event --------------------------
        NewFolderEventDispatcher.do_something(self, path)
        return True

    def _duplicate_file(self, node):  # Solo en files
        # Duplica el archivo ---------------------------------
        print(f"FileTreeView._duplicate_file")
        path = self.get_file_system_path(node) + os.sep
        file = node.text
        print(f"  path: {path} - name: {file}")
        # print(f'FileListView._duplicate_file(file={file_name})')
        actual_name = path + file
        name, ext = os.path.splitext(file)
        new_name = path + name + '-copy' + ext
        try:
            shutil.copy(actual_name, new_name)
        except:
            print("Error copiando FileWrapper:\n")
            print(str(sys.exc_info()[0]) + '\n')
            print(str(sys.exc_info()[1]) + '\n')
            return False
        # Actualiza la lista ----------------------------
        icon_node = FileNode(text=new_name, icon_name='file', markup=True, icon_color=(0.4, 0.4, 0.4, 1), type="file")
        icon_node.label.bind(on_finish_editing=self._on_finish_editing)
        file_node = self.add_node(icon_node, path)
        file_node.path_node = path
        # self.populate(folder=self.root_path, select_file=sel_file)
        # self.select_node(root_node)
        # Call event --------------------------
        DuplicateFileEventDispatcher.do_something(self, new_name, actual_name)
        # df = FileDataDic(file_name=name + '-copy' + ext, folder=self.folder).to_dict()
        # self.data.append(df)
        # self.refresh_from_data()

    def _delete_file(self, node):
        """
        Elimina un archivo dado su nombre.
        args:
            item (FileItem): Item del archivo a eliminar
        """
        # Borra el archivo ---------------------------------
        # print(f"FileTreeView._delete_file")

        def on_yes(instance, touch, keycode):
            # Obtiene el nombre del archivo
            popup.dismiss()
            path = self.get_file_system_path(node)
            file = node.text
            # print(f"  path: {path} - name: {file}")
            # print(f'FileListView._delete_file(file={file_name})')
            file_path = path + os.sep + file
            try:
                if os.path.exists(file_path):
                    if node.type == "folder":
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                else:
                    print(f"El archivo '{file}' no existe.")
            except Exception as e:
                print(f"Error al intentar eliminar el archivo: {e}")
                return False
            # Actualiza la lista ----------------------------
            self.remove_node(node)
            # Call event --------------------------
            DeleteFileEventDispatcher().do_something(file_path)

        # Cuadro de Dialogo de Confirmacion
        popup = TwoButtonsDialog(title="File System", question_text=f"Are you sure you want to delete {node.text}?",
                                 btn1_text="Yes", btn2_text="Cancel")
        popup.button_1.bind(on_click=on_yes)
        popup.button_2.bind(on_click=popup.dismiss)
        popup.open()



'''Relacionado con FileTreeView--------------'''
class FileTreePanel(FrameFocused):
    def __init__(self, root_path, sorted=True, show_files=True, filter_ext=['*'], show_hidden=False, **kwargs):
        """
            Panel con arbol
            Attributes:
        """
        # base init ------------------------------------------
        FrameFocused.__init__(self, hotlight=False)
        # TreeNodeSelectedEventDispatcher.__init__(self)
        # themes config --------------------------------------
        # self.spacing = bb
        # self.padding = bb

        # UI widgets -----------------------------------------
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True,
                                      scroll_type=['bars', 'content'], scroll_wheel_distance=dp(50), bar_width=dp(10))
        self.scroll_view.bar_color = self.theme.colors['accent_face']
        self.container.padding = 1
        self.container.add_widget(self.scroll_view)
        self.tree_view = FileTreeView(root_path=root_path, sorted=sorted, show_files=show_files, filter_ext=filter_ext,
                                      show_hidden=show_hidden, size_hint_y=None)
        self.scroll_view.add_widget(self.tree_view)
        self.tree_view.bind(minimum_height=self.tree_view.setter('height'))  # Permitir el autoajuste de altura

# AGREGAR ACA property ROOT_PATH QUE LLAME A tree_view.root_path
