#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  file_events.py
#
#  Copyright 2012 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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


'''
Created on 22/12/2024

@author: mpbe
'''


# imports del sistema -------------------------------------------------------

# Kivy imports --------------------------------------------------------------
from kivy.event import EventDispatcher

class RenameFileEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_rename_file')
        EventDispatcher.__init__(self, **kwargs)
#         super(TouchEventDispatcher, self).__init__(**kwargs)

    def do_something(self, new_file_name, old_file_name, path):
        self.dispatch('on_rename_file', new_file_name, old_file_name, path)

    def on_rename_file(self, *args):
        pass


class DuplicateFileEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_duplicate_file')
        EventDispatcher.__init__(self, **kwargs)
#         super(TouchEventDispatcher, self).__init__(**kwargs)

    def do_something(self, new_file_name, source_file_name):
        self.dispatch('on_duplicate_file', new_file_name, source_file_name)

    def on_duplicate_file(self, *args):
        pass


class DeleteFileEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_delete_file')
        EventDispatcher.__init__(self, **kwargs)
#         super(TouchEventDispatcher, self).__init__(**kwargs)

    def do_something(self, file_name):
        self.dispatch('on_delete_file', file_name)

    def on_delete_file(self, file_name, *args):
        pass


class SaveFileEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_save_file')
        EventDispatcher.__init__(self, **kwargs)
#         super(TouchEventDispatcher, self).__init__(**kwargs)

    def do_something(self, file_name):
        self.dispatch('on_save_file', file_name)

    def on_save_file(self, *args):
        pass


class NewFileEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_new_file')
        EventDispatcher.__init__(self, **kwargs)

    def do_something(self, parent_folder):
        self.dispatch('on_new_file', parent_folder)

    def on_new_file(self, *args):
        pass


class NewFolderEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_new_folder')
        EventDispatcher.__init__(self, **kwargs)

    def do_something(self, parent_folder):
        self.dispatch('on_new_folder', parent_folder)

    def on_new_folder(self, *args):
        pass
