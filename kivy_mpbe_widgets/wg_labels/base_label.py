#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  base_lavel.py
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
Created on 11/01/2025
author: mpbe
'''

# imports del sistema -------------------------------------------------------

# Kivy imports --------------------------------------------------------------

# kivy_dkw ------------------------------------------------------------------

class BaseLabel():
    def lbl_disabled(self, value):
        raise NotImplementedError("Should have implemented lbl_disabled()")

    def lbl_hotlight(self, value):
        raise NotImplementedError("Should have implemented lbl_hotlight()")

    def lbl_focus(self, value):
        raise NotImplementedError("Should have implemented lbl_focus()")

    def lbl_activate(self, value):
        raise NotImplementedError("Should have implemented lbl_activate()")
