# -*- coding: utf-8 -*-
#
#  rsrc_themes
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


# Load Styles ---------------------------------------------------------------
def _load_styles():
    print("Load Styles: --------------------------------------------")
    THEMES_PATH = mpw.THEMES_PATH
    STYLES = dict()
    for ff in os.listdir(THEMES_PATH):
        ext = ff.split('.')[-1]
        name = ff.split('.')[0]
        if ext == 'style':
            try:
                flname = THEMES_PATH + ff
                # Load and decoding config file
                fl = codecs.open(flname, 'r', 'utf-8')
                txt_style = fl.read()
                fl.close()
                style = json.loads(txt_style)
                STYLES[name] = style
                print(name+": " + str(style))
            except:
                print('Error: load style ' + name)
    return STYLES
STYLES = _load_styles()


# Load Themes ---------------------------------------------------------------
def _load_themes():
    print("Load Themes: --------------------------------------------")
    THEMES_PATH = mpw.THEMES_PATH
    THEMES = dict()
    for ff in os.listdir(THEMES_PATH):
        ext = ff.split('.')[-1]
        name = ff.split('.')[0]
        if ext == 'theme':
            try:
                flname = THEMES_PATH + ff
                # Load and decoding config file
                fl = codecs.open(flname, 'r', 'utf-8')
                txt_theme = fl.read()
                fl.close()
                theme = json.loads(txt_theme)
                THEMES[name] = theme
                print(name+": " + str(theme))
            except:
                print('Error: load theme ' + name)
    return THEMES
THEMES = _load_themes()

# # Fonts Register ------------------------------------------------------------
# # usar funciones internas
# def _register_fonts():
#     print("Load Fonts: ---------------------------------------------")
#     FONTS_PATH = mpw.FONTS_PATH
#     FONTS = [
#         {
#             "name": "Roboto",
#             "fn_regular": FONTS_PATH + 'Roboto-Regular.ttf',
#             "fn_bold": FONTS_PATH + 'Roboto-Medium.ttf',
#             "fn_italic": FONTS_PATH + 'Roboto-Italic.ttf',
#             "fn_bolditalic": FONTS_PATH + 'Roboto-MediumItalic.ttf'
#         },
#         {
#             "name": "RobotoLight",
#             "fn_regular": FONTS_PATH + 'Roboto-Thin.ttf',
#             "fn_bold": FONTS_PATH + 'Roboto-Light.ttf',
#             "fn_italic": FONTS_PATH + 'Roboto-ThinItalic.ttf',
#             "fn_bolditalic": FONTS_PATH + 'Roboto-LightItalic.ttf'
#         },
#     #     {
#     #         "name": "Icons",
#     #         "fn_regular": FONTS_PATH + 'materialdesignicons-webfont.ttf'
#     #     }
#     ]
#     for font in FONTS:
#         LabelBase.register(**font)

# # Icons Register ------------------------------------------------------------
# def _register_icons():
#     print("Load Icons: ---------------------------------------------")
#     FONTS_ICONS_PATH = mpw.FONTS_ICONS_PATH
#     ICONS = dict()
#     for ff in os.listdir(FONTS_ICONS_PATH):
#         ext = ff.split('.')[-1]
#         name = ff.split('.')[0]
#         if ext == 'ttf':
#             try:
#                 flname = FONTS_ICONS_PATH + name + '.def'
#                 # Load and decoding config file
#                 fl = codecs.open(flname, 'r', 'utf-8')
#                 txt_icon_def = fl.read()
#                 fl.close()
#                 icon = json.loads(txt_icon_def)
#                 ICONS[name] = icon
#                 font = {"name": name,
#                         "fn_regular": FONTS_ICONS_PATH + ff
#                        }
#                 LabelBase.register(**font)
#                 print(ff)
#             except:
#                 print('Error: load icon ' + name)
#     return ICONS
# ICONS = _register_icons()

