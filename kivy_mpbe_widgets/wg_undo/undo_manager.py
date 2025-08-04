#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  undo_manager.py
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
Created on 03/08/2025

@author: mpbe
@note:
'''


class Command:
    """Clase base abstracta para todos los comandos."""
    def execute(self):
        raise NotImplementedError
    
    def undo(self):
        raise NotImplementedError


class UndoManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def execute(self, command):
        """Ejecuta un nuevo comando y lo guarda en el historial."""
        command.execute()
        self.undo_stack.append(command)
        # Una nueva acción borra el historial de "redo"
        self.redo_stack.clear()

    def undo(self):
        """Deshace el último comando."""
        if not self.undo_stack:
            return
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)

    def redo(self):
        """Rehace el último comando deshecho."""
        if not self.redo_stack:
            return
        command = self.redo_stack.pop()
        # Volvemos a ejecutar la acción original
        command.execute()
        self.undo_stack.append(command)

