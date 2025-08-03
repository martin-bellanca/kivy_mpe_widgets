#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_translate.py
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
from helpers_mpbe.python import compose, compose_dict, check_list
# Kivy imports --------------------------------------------------------------
# kivy_dkw ------------------------------------------------------------------
from kivy_mpbe_widgets.wg_markdown.markdown_extension import TaskListMDExtension, WhiteLineMDExtension



'''Traducción con markdown a traves de Html (obsoleto) -------------------------------'''
def translate_markdown_to_html(markdown_text):
    return markdown(markdown_text, extensions=[TaskListMDExtension(), WhiteLineMDExtension()])


def translate_markdown_line_to_kvmarkup(markdown_text):
    # Convertir Markdown a HTML
    html = translate_markdown_to_html(markdown_text)

    # Manejar lineas en blanco
    if html.startswith('<br>') or html == '<p><br>' or html == '<p><br></p>':
        return "\r"
    # Manejar imágenes ![alt text](image_url)
    match_img = re.match(r'!\[.*?\]\((.*?)\)', html)
    if match_img:
        return match_img.group(1)
    # Manejar separadores <hr>
    if '<hr' in html:
        return "---"
    # Manejar tablas <table>...</table>
    if '<table>' in html:
        table_html = re.search(r'(<table>.*?</table>)', html, re.DOTALL).group(1)
        return table_html
    # Convertir HTML a texto marcado de Kivy
    kv_markup = html
    kv_markup = re.sub(r'<strong>(.*?)</strong>', r'[b]\1[/b]', kv_markup)
    kv_markup = re.sub(r'<em>(.*?)</em>', r'[i]\1[/i]', kv_markup)
    kv_markup = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[ref=\1]\2[/ref]', kv_markup)
    kv_markup = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'[size=30][b]\1[/b][/size]', kv_markup)
    kv_markup = re.sub(r'<li>(.*?)</li>', r'• \1', kv_markup)
    kv_markup = re.sub(r'<ul>|</ul>', '', kv_markup)
    kv_markup = re.sub(r'<ol>|</ol>', '', kv_markup)
    kv_markup = re.sub(r'<[^>]+>', '', kv_markup)  # Eliminar otras etiquetas HTML
    if kv_markup.strip():  # Elimina los espacios en blanco delante y detras. strip('*') elimina asterirscos
        return kv_markup
    return ""



    # Titulos

    # Formato del Texto Basico


    # Tabla


'''Traduccion directa Markdown To KVMarkup ----------------------------------------------'''
'''Extensiones para Translate Markdown To KVMarkup --------------------------------------'''
class Extension():
    '''Se aplica en el documento linea a linea'''
    def run(self, md):
        """Debe devolver el md modificado"""
        raise NotImplementedError("Should have implemented run()")


class _ExtTitle(Extension):
    def run(self, md):
        def replace_heading(match):
            # Extrae el nivel de título y el texto
            level = len(match.group(1))
            content = match.group(2).strip()

            # Define el tamaño del texto según el nivel
            size = 40 - (level - 1) * 5  # Disminuye el tamaño según el nivel de título

            # Retorna el texto formateado para Kivy Markup
            return f"[b][size={size}]{content}[/size][/b]"

        # Expresión regular para títulos de Markdown (# Título)
        pattern = r'^(#{1,6})\s(.*)$'  # ^#+\s+(.*)$  '^(#{1,6})\s(.*)$'

        # Usamos `re.sub` para reemplazar todos los títulos
        kivy_text = re.sub(pattern, replace_heading, md, flags=re.MULTILINE)
        return kivy_text

        # sz1 = 40
        # sz2 = 36
        # sz3 = 32
        #
        # md = re.sub(r'# (.*?)', r'[size='+str(sz1)+'][b]\1[/b][/size]', md)
        # md = re.sub(r'## (.*?)', r'[size=' + str(sz2) + '][b]\1[/b][/size]', md)
        # md = re.sub(r'### (.*?)', r'[size=' + str(sz3) + '][b]\1[/b][/size]', md)


class _ExtBasicText(Extension):
    def run(self, md):
        md = compose(md, str, False)
        # Negrita: **texto** o __texto__
        md = re.sub(r'\*\*(.*?)\*\*', r'[b]\1[/b]', md)
        md = re.sub(r'__(.*?)__', r'[b]\1[/b]', md)

        # Cursiva: *texto* o _texto_
        md = re.sub(r'\*(.*?)\*', r'[i]\1[/i]', md)
        md = re.sub(r'_(.*?)_', r'[i]\1[/i]', md)

        # Subrayado: ~texto~ No es Estandar
        md = re.sub(r'~(.*?)~', r'[u]\1[/u]', md)

        # Strikethrough (tachado): ~~texto~~
        md = re.sub(r'~~(.*?)~~', r'[strike]\1[/strike]', md)

        # Código: `texto`
        md = re.sub(r'`(.*?)`', r'[font=RobotoMono]\1[/font]', md)

        # Links: [texto](url)
        md = re.sub(r'\[(.*?)\]\((.*?)\)', r'[ref=\2]\1[/ref]', md)

        return md


class ExtKVTable(Extension):
    """Extension para traducir las tablas a formato GridLayout"""
    def run(self, md):
        md = compose(md, str, False)
        pass  # TODO: Codificar


'''TranslateMarkdown To KVMarkup -------------------------------------------------------'''
class TranslateMarkdownToKVMarkup():
    def __init__(self, **kwargs):
        """
        Constructor class
        Keyword arguments:
            extension (Extension): Clase derivada de Extension
            extensions (list(Extension)): Lista de Extensiones a agregar
        """
        self.extensions = [_ExtTitle(), _ExtBasicText()]
        if extension := compose_dict(kwargs, 'extension', Extension, None, acept_none=True):
            self.extensions.append(extension)
        if extensions := compose_dict(kwargs, 'extensions', list, None, acept_none=True):
            check_list(extensions, Extension, False)
            self.extensions.extend(extensions)


    def translate(self, markdown_text):
        for ext in self.extensions:
            markdown_text = ext.run(markdown_text)
        return markdown_text


    def append_extension(self, extension):
        """Agrega una o varias extensiones para la traduccion
        Parameters:
            extension (Extension): Clase derivada de Extension
        """
        if ext := compose(extension, Extension, False):
            self.extensions.append(ext)
        return True


    def extend_extensions(self, extensions):
        """"
        Extiende la lista de extensiones
        extensions (list(Extension)): Lista de Extensiones a agregar
        """
        check_list(extensions, Extension, False)
        self.extensions.extend(extensions)
        return True


    def insert_extension(self, i, extension):
        self.extensions.insert(i, extension)



""" ETIQUETAS ::ddddd   (USAR FONTICONS)
from kivy.core.text import LabelBase
from kivy.app import App
from kivy.uix.label import Label

# Registrar la fuente con Kivy
LabelBase.register(name="FontAwesome", fn_regular="path/to/fontawesome-webfont.ttf")

class MyApp(App):
    def build(self):
        # Crear un Label usando la fuente registrada
        return Label(
            text="[font=FontAwesome]&#xf007;[/font] This is a user icon",
            markup=True
        )

if __name__ == '__main__':
    MyApp().run()

"""