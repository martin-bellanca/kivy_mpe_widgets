#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _test_editor_row_01.py
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
Created on 10/09/2023
@author: mpbe
'''

"""------------------------------------------------------------------------"""
"""-- Test Program  -------------------------------------------------------"""
"""------------------------------------------------------------------------"""
from kivy_mpbe_widgets.wg_markdown.md_document import MDDocument

doc_md = """TITULO PRINCIPAL
===
Linea de parrafo.
Otra linea

**Negrita****
"""


path = '''/home/mpbe/Documentos/Programacion_lin/PyCharmProjects/kivy_dkw3_prj'''
dname = 'markdown_example.md'

# doc = MarkdownDocument(md_document=doc_md, doc_name=dname, doc_path=path)
# print(doc.document)

# doc = MarkdownDocument(md_document=None, doc_name=dname, doc_path=path)
# print(doc.document)

doc = MDDocument(md_document=None, doc_name=dname, doc_path=path)
print(doc.document)
print()
print("------------------------------------------------")
# doc.doc_name = "Prueba_write.md"
# doc.save_doc()

# doc.save_as_doc(path=doc.doc_path, doc_name="Prueba_write.md")

lines = doc.separate_lines()
for line in lines:
    print(line)