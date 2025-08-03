#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_render_def.py
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
Created on 03/08/2024
@author: mpbe
'''

# imports del sistema -------------------------------------------------------
import re
from markdown import markdown
# helpers_mpbe --------------------------------------------------------------
# Kivy imports --------------------------------------------------------------
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.lang import Builder
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets import IMAGES_PATH
from kivy_mpbe_widgets.theming import Theme
from kivy_mpbe_widgets.wg_markdown.md_labels import *
from kivy_mpbe_widgets.wg_markdown.md_editors import MarkdownRowTextInputWLabel_OBSOLETO
from kivy_mpbe_widgets.wg_markdown.markdown_extension import TaskListMDExtension, WhiteLineMDExtension
from kivy_mpbe_widgets.wg_markdown.md_translate import translate_markdown_to_html, translate_markdown_line_to_kvmarkup


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++
# NO SIRVE PARA MarkDownEditor. Con la clase MarkdownDocument ya separa por parrafo o linea

# ----------------------------------------------------
# ToDo: ES PARA CONVERTIR MARK UP A TRAVEZ DE HTML. SACAR
# -----------------------------------------------------

def render_line_markdown_to_widget(markdown_text):
    # Convertir Markdown a HTML
    html = translate_markdown_to_html(markdown_text)

    # Manejar lineas en blanco
    if html.startswith('<br>') or html == '<p><br>' or html == '<p><br></p>':
        return MDTextLabel(text="\r")
    # Manejar imágenes ![alt text](image_url)
    match_img = re.match(r'!\[.*?\]\((.*?)\)', html)
    if match_img:
        img_src = match_img.group(1)
        return Image(source=img_src, size_hint_y=None, height=200)
    # Manejar separadores <hr>
    if '<hr' in html:
        return MDSeparatorLabel()
    # Manejar tablas <table>...</table>
    if '<table>' in html:
        table_html = re.search(r'(<table>.*?</table>)', html, re.DOTALL).group(1)
        return MDTableLabel(table_html)
    # Convertir HTML a texto marcado de Kivy
    kivy_text = translate_markdown_line_to_kvmarkup(html)
    if kivy_text.strip():  # Elimina los espacios en blanco delante y detras. strip('*') elimina asterirscos
        return MDTextLabel(text=kivy_text)
    return MDTextLabel(text="")


# def render_line_markdown_to_widget(markdown_text):
#     # Convertir Markdown a HTML
#     html = markdown(markdown_text, extensions=[TaskListMDExtension(), WhiteLineMDExtension()])
#
#     # Manejar lineas en blanco
#     if html.startswith('<br>') or html == '<p><br>' or html == '<p><br></p>':
#         return MDRowLabel(text="\r")
#     # Manejar imágenes ![alt text](image_url)
#     match_img = re.match(r'!\[.*?\]\((.*?)\)', html)
#     if match_img:
#         img_src = match_img.group(1)
#         return Image(source=img_src, size_hint_y=None, height=200)
#     # Manejar separadores <hr>
#     if '<hr' in html:
#         return MDLineSeparator()
#     # Manejar tablas <table>...</table>
#     if '<table>' in html:
#         table_html = re.search(r'(<table>.*?</table>)', html, re.DOTALL).group(1)
#         return MDTable(table_html)
#     # Convertir HTML a texto marcado de Kivy
#     kivy_text = html
#     kivy_text = re.sub(r'<strong>(.*?)</strong>', r'[b]\1[/b]', kivy_text)
#     kivy_text = re.sub(r'<em>(.*?)</em>', r'[i]\1[/i]', kivy_text)
#     kivy_text = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[ref=\1]\2[/ref]', kivy_text)
#     kivy_text = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'[size=30][b]\1[/b][/size]', kivy_text)
#     kivy_text = re.sub(r'<li>(.*?)</li>', r'• \1', kivy_text)
#     kivy_text = re.sub(r'<ul>|</ul>', '', kivy_text)
#     kivy_text = re.sub(r'<ol>|</ol>', '', kivy_text)
#     kivy_text = re.sub(r'<[^>]+>', '', kivy_text)  # Eliminar otras etiquetas HTML
#     if kivy_text.strip():  # Elimina los espacios en blanco delante y detras. strip('*') elimina asterirscos
#         return MDRowLabel(text=kivy_text)
#     return MDRowLabel(text="")


def render_markdown_to_widgets(markdown_text):
    # Lista de widgets para añadir al layout
    widgets = []
    # Dividir el HTML por líneas para procesar
    lines = markdown_text.split('\n')
    for line in lines:
        widget = render_line_markdown_to_widget(markdown_text=line)
        widgets.append(widget)
    return widgets

