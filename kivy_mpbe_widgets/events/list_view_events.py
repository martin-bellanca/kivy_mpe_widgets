#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  list_view_events.py
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
Created on 16/02/2020

@author: mpbe
'''


# imports del sistema -------------------------------------------------------

# Kivy imports --------------------------------------------------------------
from kivy.event import EventDispatcher


class SelectListItemEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_select_list_item')
        super().__init__(**kwargs)

    def do_something(self, selected_id, item):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        self.dispatch('on_select_list_item', selected_id, item)

    def on_select_list_item(self, *args):
        pass


class SelectItemEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_select_item')
        EventDispatcher.__init__(self, **kwargs)
#         super(TouchEventDispatcher, self).__init__(**kwargs)

    def do_something(self):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        self.dispatch('on_select_item')

    def on_select_item(self, *args):
        pass


class UnSelectItemEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_unselect_item')
        EventDispatcher.__init__(self, **kwargs)
#         super(TouchEventDispatcher, self).__init__(**kwargs)

    def do_something(self):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        self.dispatch('on_unselect_item')

    def on_unselect_item(self, *args):
        pass


class ChangePriorityEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_change')
        super(ChangePriorityEventDispatcher, self).__init__(**kwargs)

    def do_something(self, priorities, new_id, old_id):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        self.dispatch('on_change', priorities, new_id, old_id)

    def on_change(self, priorities, new_id, old_id, *args):
#         print (f"Change priority event dispatch. Old Id {old_id}, New Id {new_id}")
        pass
