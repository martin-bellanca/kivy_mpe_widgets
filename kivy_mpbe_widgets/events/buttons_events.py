#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  events.py
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
Created on 05/02/2025
author: mpbe
'''


# imports del sistema -------------------------------------------------------

# Kivy imports --------------------------------------------------------------
from kivy.event import EventDispatcher


class ClickEventDispatcher(EventDispatcher):
    """
    Event Type: on_click
    """
    def __init__(self, **kwargs):
        self.register_event_type('on_click')
        EventDispatcher.__init__(self, **kwargs)
    #         super(TouchEventDispatcher, self).__init__(**kwargs)

    def do_something(self, touch, keycode):
        # when do_something is called, the 'on_click' event will be
        # dispatched with the value
        self.dispatch('on_click', touch, keycode)

    def on_click(self, touch, keycode, *args):
        pass


class ChangeStateEventDispatcher(EventDispatcher):
    """
    Event Type: on_change_state
    States: 'on', 'off'
    """
    def __init__(self, **kwargs):
        self.register_event_type('on_change_state')
        super().__init__(**kwargs)

    def do_something(self, state):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        if state in ['on', 'off']:
            self.dispatch('on_change_state', state)
        else:
            raise ValueError('Incorrect event Value. Must be "on" or "off"')

    def on_change_state(self, state, *args):
        pass


class ToggleEventDispatcher(EventDispatcher):
    """
    Event Type: on_toggle_state
    States: 'toggled', 'untoggled'
    """
    def __init__(self, **kwargs):
        self.register_event_type('on_toggle_state')
        super().__init__(**kwargs)

    def do_something(self, state):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        if state in ['toggled', 'untoggled']:
            self.dispatch('on_toggle_state', state)
        else:
            raise ValueError('Incorrect event Value. Must be "toggled" or "untoggled"')

    def on_toggle_state(self, state, *args):
        pass


class StateSwitchEventDispatcher(EventDispatcher):
    """
    Event Type: on_switch_state
    States: 'on', 'off'
    """
    def __init__(self, **kwargs):
        self.register_event_type('on_switch_state')
        super().__init__(**kwargs)

    def do_something(self, state):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        if state in ['on', 'off']:
            self.dispatch('on_switch_state', state)
        else:
            raise ValueError('Incorrect event Value. Must be "on" or "off"')

    def on_switch_state(self, state, *args):
        pass


class StateCheckEventDispatcher(EventDispatcher):
    """
    Event Type: on_check_state
    States: 'checked', 'unchecked'
    """
    def __init__(self, **kwargs):
        self.register_event_type('on_check_state')
        super().__init__(**kwargs)

    def do_something(self, state):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        if state in ['checked', 'unchecked']:
            self.dispatch('on_check_state', state)
        else:
            raise ValueError('Incorrect event Value. Must be "checked" or "unchecked"')

    def on_check_state(self, state, *args):
        pass
