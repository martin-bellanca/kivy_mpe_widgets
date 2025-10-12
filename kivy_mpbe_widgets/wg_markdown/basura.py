# PARA COMPARAR CLASES Y VER CUAL USAR
# ------------------------------------------------

class MDDocumentLineEditorBACK(BaseItem):
    line = ObjectProperty(baseclass=MDLine, defaultvalue=MDLine(md_text='', prev_line=None, next_line=None))
    num_line = NumericProperty(defaultvalue=0)  # Numero de la linea en la lista
    hidden_line = BooleanProperty(defaultvalue=False)  # Indica si el renglon no es visible en el arbol (nodo padre cerrado)
    hotlight = BooleanProperty(defaultvalue=False)  # indica la linea que tiene el cursor ensima
    focused = BooleanProperty(defaultvalue=False)  # indica si la linea en modo render es linea actual para edición

    def __init__(self):
        """
        Keyword arguments:
            show_number_line (bool): muestra el numero de linea
            show_tree_hook (bool): muestra el arbol del documento
            show_info_bar (bool): muestra la barra de informacion
        """
        super().__init__()

        # BoxLayout.__init__(self, orientation='horizontal')
        # ThemableBehavior.__init__(self)
        # colors -----------------------------------------
        self._hotlight_color = self.theme.colors['hotlight_border']
        self._focused_color = self.theme.colors['focus_border']
        # Layout principal -------------------------------
        self._layout = BoxLayout(orientation="horizontal")
        self.add_widget(self._layout)
        # line -------------------------------------------
        self.md_line = MDLine(md_text="", prev_line=None, next_line=None)
        # Espacio ----------------------------------------
        self.wg_space = MDDLSpace()
        self._layout.add_widget(self.wg_space)
        # Drag Hook --------------------------------------
        self.wg_drag_hook = MDDLDrag()
        self._layout.add_widget(self.wg_drag_hook)
        # Number Line ------------------------------------
        self.wg_number_line = None
        # Tree Hook --------------------------------------
        self.wg_tree_hook = None
        # Info Bar ---------------------------------------
        self.wg_info_bar = None
        # # Espacio ----------------------------------------
        # self.wg_space = MDDLSpace()
        # self._layout.add_widget(self.wg_space)
        # Line Editor ------------------------------------
        self.wg_line_editor = MDLineEditor(line=self.md_line, non_focus=True)
        self._layout.add_widget(self.wg_line_editor)
        self.wg_line_editor.bind(size=self.on_resize_self)
        # Actualiza la Altura ----------------------------
        self._update_height()
        # Eventos ----------------------------------------
        self.wg_line_editor.bind(mode_editor=self.on_mode_editor)
        if kivy_mpbe_widgets.DEVICE_TYPE == 'desktop':
            Window.bind(mouse_pos=self.on_mouse_move)
        self.bind(pos=self._on_update_geometry, size=self._on_update_geometry)

    # # Properties -----------------------------------------------

    # def _set_md_text(self, md_text):
    #     '''
    #     Notas:
    #         -self.line y self.active_label se actualizan de on_txt_change de self.md_editor
    #     '''
    #     # print('MDDocumentLineEditor->on_line')
    #     self.md_line.md_text = md_text
    #     # self.md_editor.text = md_text
    #     # self.active_label.md_text = md_text
    #     # self.line.md_text = md_text
    # def _get_md_text(self):
    #     return self.md_line.md_text
    # md_text = property(_get_md_text, _set_md_text)

    # def _set_type(self, type):
    #     self.md_line.type = type
    # def _get_type(self):
    #     return self.md_line.type
    # type = property(_get_type, _set_type)

    # def _set_mode_editor(self, value:bool):
    #     self.wg_line_editor.mode_editor = value
    # def _get_mode_editor(self)-> bool:
    #     return self.wg_line_editor.mode_editor
    # mode_editor = property(_get_mode_editor, _set_mode_editor)

    # # Private Functions ----------------------------------------
    # def _on_update_geometry(self, instance, value):
    #     self._layout.pos = self.pos
    #     self._layout.size = self.size

    # def _update_height(self):
    #     if self.wg_line_editor:
    #         self.height = self.wg_line_editor.height
    #         self.wg_drag_hook.height = self.wg_line_editor.height
    #         if self.wg_number_line:
    #             self.wg_number_line.height = self.wg_line_editor.height
    #         if self.wg_tree_hook:
    #             self.wg_tree_hook.height = self.wg_line_editor.height
    #         if self.wg_info_bar:
    #             self.wg_info_bar.height = self.wg_line_editor.height
    #         self.wg_space.height = self.wg_line_editor.height
    #     else:
    #         self.height = 16

    # Public Funtions ------------------------------------------
    # def collide_point(self, x, y):  # on windows coordinates
    #     try:
    #         # Check the position of the point
    #         # bpx, bpy = self.to_window(self.pos[0], self.pos[1], True)
    #         bpx, bpy = self.to_window(self.pos[0], self.pos[1], True)
    #         bwidth, bheight = self.size
    #         # Direction X
    #         bpw = bpx + bwidth
    #         inx = True if bpx <= x <= bpw else False
    #         # Direction Y
    #         bph = bpy + bheight
    #         iny = True if bpy <= y <= bph else False
    #         # Collide
    #         return inx and iny
    #     except:
    #         return False

    # def show_number_line(self, value: bool, num_line: int):
    #     if value: # Asigna
    #         if not self.wg_number_line: # Muestra
    #             # Numero de Linea -------------------
    #             self.wg_number_line = MDDLNumberLine()  # text=f"{self.num_line:04d}"
    #             self._layout.add_widget(self.wg_number_line, index=1)
    #             # Espacio ---------------------------
    #             self.wg_space_number_line = MDDLSpace()
    #             self._layout.add_widget(self.wg_space_number_line, index=1)
    #         self.num_line = num_line
    #     else:
    #         self._layout.remove_widget(self.wg_number_line)
    #         self._layout.remove_widget(self.wg_space_number_line)
    #         self.wg_number_line = None

    #     # if value and not self.wg_number_line:  # muestra
    #     #     self.num_line = num_line
    #     #     print(f"MDDocumentLineEditor.show_number_line({value}, {num_line})-> {self.md_line.num_line}: {self.md_line.md_text}")
    #     #     self.wg_number_line = MDDLNumberLine(text=f"{self.num_line:04d}")
    #     #     self._layout.add_widget(self.wg_number_line, index=1)
    #     # elif not value and self.wg_number_line:  # oculta
    #     #     self._layout.remove_widget(self.wg_number_line)
    #     #     self.wg_number_line = None

    # def show_tree_hook(self, value: bool):
    #     if value and not self.wg_tree_hook:  # muestra
    #         self.wg_tree_hook = MDDLTree_hook()
    #         self._layout.add_widget(self.wg_tree_hook, index=2)
    #     elif not value and self.wg_tree_hook:  # oculta
    #         self._layout.remove_widget(self.wg_tree_hook)
    #         self.wg_tree_hook = None

    # def show_info_bar(self, value: bool):
    #     if value and not self.wg_info_bar:  # muestra
    #         self.wg_info_bar = MDDLInfoBar()
    #         self._layout.add_widget(self.wg_info_bar, index=2)
    #     elif not value and self.wg_info_bar:  # oculta
    #         self._layout.remove_widget(self.wg_info_bar)
            self.wg_info_bar = None

    # Funtions events ---------------------------------------------------
    # def on_resize_self(self, instance, value):
    #     self._update_height()

    def on_num_line(self, instance, value):
        self.num_line = value
        if self.wg_number_line:
            self.wg_number_line.text = f"{value:04d}"

    # def on_line(self, instance, value):
    #     # print('MDDocumentLineEditor->on_line')
    #     pass

    # def on_line_type(self, instance, value):
    #     # print('MDDocumentLineEditor->on_line_type')
    #     pass

    # def on_line_md_text(self, instance, value):
    #     # print('MDDocumentLineEditor->on_line_md_text')
    #     pass

    # def on_mouse_move(self, instance, mp):
    #     # print("MDDocumentLineEditor->on_mouse_move")
    #     if self.collide_point(mp[0], mp[1]):
    #         self.hotlight = True
    #     else:
    #         self.hotlight = False

    # def on_mode_editor(self, instance, value):
    #     # print("MDDocumentLineEditor->on_mode_editor")
    #     if value:
    #         self.focused = value

    # Funciones de RecycleDataViewBehavior -------------------------------------
    def refresh_view_attrs(self, rv, index, data):
        '''
        Catch and handle the view changes - se ejecuta cuando hay un cambio en data
        **Parameters:**
            rv (RecycleView): Clase derivada de RecycleView
            index (int): Indice del item
            data (dictionary): Diccionario con la informacion del item
                **Keys:**
                'selected' (bool): Define si el item esta seleccionado
                'start_anim' (bool): Indica si debe animar la seleccion a des-seleccion del item
                'active' (bool): Indica si el item esta activo.
                'mode_editor': Indica si esta en modo edicion.
                'md_line' (MDLine): Clase que guarda la linea a mostrar
                'cursor_col' (int): Ubicación del cursor
                'show_number_line' (bool): Indica si se muestra el numero de linea
                'show_tree' (bool): Indica si se muestran los botones de arbol
                'show_infobar' (bool): Indica si se muestra la barra de información

        '''
        # print(f"MDDocumentLineEditor.refresh_view_attrs()-> {self.md_line.num_line}: {self.md_line.md_text}")
        # Asigna el md_line ---------------------------------
        if 'md_line' in data:
            self.md_line = data['md_line']
            self.md_line.bind(md_text=self.on_line_md_text, type=self.on_line_type)
            self.wg_line_editor.line = self.md_line
            # if 'show_number_line' in data:
            self.show_number_line(data['show_number_line'], self.md_line.num_line)

        if 'active' in data:
            self.mode_editor = data['mode_editor']
            # print (f"   Cursor= {data['cursor']}")
            self.wg_line_editor.md_editor.cursor = data['cursor']
        else:
            self.mode_editor = False
        if 'show_tree' in data:
            self.show_tree_hook(data['show_tree'])
        if 'show_infobar' in data:
            self.show_info_bar(data['show_infobar'])
        # if 'start_anim' in data and data['start_anim']:  # ejecuta la animacion
        #     touch_pos = (self.x+10, self.y+self.height/2)
        #     if data['selected']:
        #         print('    Anima seleccion')
        #         self.graphic_select.animate_select(True, touch_pos)
        #     else:
        #         print('    Anima des-seleccion')
        #         self.graphic_select.animate_select(False, touch_pos)


        return super(MDDocumentLineEditor, self).refresh_view_attrs(rv, index, data)

