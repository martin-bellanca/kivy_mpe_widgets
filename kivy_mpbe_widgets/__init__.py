# -*- coding: utf-8 -*-
#
#  kivy_mpbe_widgets, Desktop Kivy Widgets
#
#  Copyright 2024 Martin Pablo Bellanca <mbellanca@gmail.com>
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
Base Package of kivy_mpbe_widgets \n
Created on 24/12/2024

@author: mpbe
@note:
'''

# imports -------------------------------------------------------------------
import os
import sys
# python imports ------------------------------------------------------------
# kivy imports --------------------------------------------------------------
from kivy import platform
from kivy.core.window import Window
from kivy.metrics import dp
from kivy import Logger


# constantes del Modulo -----------------------------------------------------
__author__ = 'Martin Pablo Bellanca <mpbellanca@gmail.com>'
__contact__ = 'mpbellanca@gmail.com'
__organization__ = 'mpbe'
__license__ = "GPL3"
__version_info__ = (0, 0, 1)
__version__ = 'alfa_0.0.1-2019-09-03'
INFO_DESCRIPCION = """
  kivy_mpw es un conjunto de widgets multi plataforma.
  Es software libre y se encuentra licenciado bajo los 
términos de la Licencia Pública General de GNU versión 3 
según se encuentra publicada por la Free Software Foundation.
"""
INFO_LICENSE = """
  Este programa es software libre. Puede redistribuirlo y/o modificarlo bajo los términos de la 
Licencia Pública General de GNU según se encuentra publicada por la Free Software Foundation, 
bien de la versión 3 de dicha Licencia o bien (según su elección) de cualquier versión posterior.
  Este programa se distribuye con la esperanza de que sea útil, pero SIN NINGUNA GARANTÍA, 
incluso sin la garantía MERCANTIL implícita o sin garantizar la ADECUACIÓN A UN PROPÓSITO PARTICULAR. 
Véase la Licencia Pública General de GNU para más detalles.
  Debería haber recibido una copia de la Licencia Pública General junto con este programa. 
Si no ha sido así, escriba a la Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

http://www.fsf.org/
http://www.gnu.org/home.es.html
http://es.wikipedia.org/wiki/GNU
"""

# __add__ = ['behaviors', 'const', 'dkw_widget', 'events', 'graphics',
#            'icon_definitions', 'icons', 'theming']
# Work Dir config -----------------------------------------------------------
try:
    DIR_BASE = os.path.dirname(os.path.abspath(__file__))
except:
    DIR_BASE = os.path.dirname(os.path.abspath(sys.argv[0]))
# Agrega los path de la aplicacion
# DIRBASE = str.rsplit(DIR_APP, os.sep, 1)[0]
# sys.path.append(str.rsplit(DIR_BASE, os.sep, 1)[0])  # Define el dir base del codigo fuente

try:
    PATH_HOME = os.environ['HOME']
except KeyError:
    PATH_HOME = os.environ['HOMEPATH']

THEMES_PATH = os.path.join(DIR_BASE, 'rsrc_themes/')
FONTS_PATH = os.path.join(DIR_BASE, 'rsrc_fonts/')
FONTS_ICONS_PATH = os.path.join(DIR_BASE, 'rsrc_fonts_icons/')
IMAGES_PATH = os.path.join(DIR_BASE, 'rsrc_images/')

# Define device type --------------------------------------------------------
if platform != "android" and platform != "ios":
    DEVICE_TYPE = "desktop"
elif Window.width >= dp(600) and Window.height >= dp(600):
    DEVICE_TYPE = "tablet"
else:
    DEVICE_TYPE = "mobile"

# Logger.info("kivy dkw: version: {}".format(__version__))

