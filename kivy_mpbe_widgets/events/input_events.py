#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  input_events.py
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
Created on 20/11/2024

@author: mpbe
'''


# imports del sistema -------------------------------------------------------

# Kivy imports --------------------------------------------------------------
from kivy.event import EventDispatcher



class StartEditingEventDispatcher(EventDispatcher):    # ESTO NO ESTA FUNCIONANDO
    def __init__(self, **kwargs):
        self.register_event_type('on_start_editing')
        EventDispatcher.__init__(self, **kwargs)

    def do_something(self, text):
        self.dispatch('on_start_editing', text)

    def on_start_editing(self, text, *args):
        pass


class FinishEditingEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_finish_editing')
        super().__init__(**kwargs)

    def do_something(self, new_text):
        self.dispatch('on_finish_editing', new_text)

    def on_finish_editing(self, new_text, *args):
        pass

