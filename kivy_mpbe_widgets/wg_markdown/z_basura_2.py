from kivy.app import App
from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty

# Cargar el archivo KV
Builder.load_string('''
<IconTextTreeViewNode>:
    orientation: 'horizontal'
    spacing: 5
    size_hint_y: None
    height: 30  # Ajusta la altura del nodo

    Image:
        id: icon
        source: root.icon_source
        size_hint: None, None
        size: 24, 24
        allow_stretch: True
        pos_hint: {'center_y': 0.5}  # Centrar la imagen verticalmente

    Label:
        id: label
        text: root.text
        valign: 'middle'
        halign: 'left'
        size_hint_y: None
        height: root.height
        text_size: self.size  # Ajustar el tamaño del texto para alinearlo
''')




class IconTextTreeViewNode(BoxLayout, TreeViewNode):
    icon_source = StringProperty('')  # Propiedad para la ruta del ícono
    text = StringProperty('')  # Propiedad para el texto del nodo

class TreeViewWithIconsApp(App):
    def build(self):
        # Crear un ScrollView para contener el TreeView
        scroll_view = ScrollView(size_hint=(1, None), size=(400, 400))

        # Crear un TreeView
        tree = TreeView(size_hint_y=None)
        tree.bind(minimum_height=tree.setter('height'))

        # Añadir nodos personalizados con ícono y texto
        for i in range(5):
            root_node = tree.add_node(
                IconTextTreeViewNode(
                    icon_source='folder_icon.png',
                    text=f'Folder {i}'
                )
            )
            for j in range(3):
                tree.add_node(
                    IconTextTreeViewNode(
                        icon_source='file_icon.png',
                        text=f'File {i}.{j}'
                    ),
                    root_node
                )

        # Añadir el TreeView al ScrollView
        scroll_view.add_widget(tree)

        return scroll_view

if __name__ == '__main__':
    TreeViewWithIconsApp().run()
