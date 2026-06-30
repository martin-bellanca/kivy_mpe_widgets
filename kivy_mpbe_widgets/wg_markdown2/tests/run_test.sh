#!/bin/bash
# Script launcher para test_app.py

# Agregar el directorio padre al PYTHONPATH
export PYTHONPATH="/home/mpbe/Documentos/Programacion/Programacion_lin/Visual_Studio_Code/kivy_mpe_widgets_prj:$PYTHONPATH"
export PYTHONPATH="/home/mpbe/Documentos/Programacion/Programacion_lin/Visual_Studio_Code/helpers_mpbe_prj:$PYTHONPATH"

# Ejecutar la app
python test_app.py
