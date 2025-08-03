# -*- coding: utf-8 -*-
#
#  rsrc_font_icons
#
#  Copyright 2018 Martin Pablo Bellanca <mbellanca@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
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
Base Package of themes of kivy_dkw \n
Created on 09/09/2019

@author: mpbe
@note:
'''


# imports -------------------------------------------------------------------
import os
import sys
# python imports ------------------------------------------------------------
import codecs
import json
# kivy imports --------------------------------------------------------------
from kivy import platform
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy import Logger

# kivy_mpw ------------------------------------------------------------------
import kivy_mpbe_widgets as mpw


"""

"""


# Work Dir config -----------------------------------------------------------
# try:
#     THEMES_PATH = os.path.dirname(os.path.abspath(__file__))
# except:
#     THEMES_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
# THEMES_PATH += '/'


# Icons Register ------------------------------------------------------------
def _register_icons():
    print("Load Icons: ---------------------------------------------")
    FONTS_ICONS_PATH = mpw.FONTS_ICONS_PATH
    ICONS = dict()
    for ff in os.listdir(FONTS_ICONS_PATH):
        ext = ff.split('.')[-1]
        name = ff.split('.')[0]
        if ext == 'ttf':
            try:
                flname = FONTS_ICONS_PATH + name + '.def'
                # Load and decoding config file
                fl = codecs.open(flname, 'r', 'utf-8')
                txt_icon_def = fl.read()
                fl.close()
                icon = json.loads(txt_icon_def)
                ICONS[name] = icon
                font = {"name": name,
                        "fn_regular": FONTS_ICONS_PATH + ff
                       }
                LabelBase.register(**font)
                print(ff)
            except:
                print('Error: load icon ' + name)
    return ICONS
ICONS = _register_icons()