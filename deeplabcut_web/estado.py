# estado.py
import os
import tempfile

carpeta_temp = tempfile.gettempdir()
RUTA_ESTADO = os.path.join(carpeta_temp, 'estado_dlc.txt')

def escribir_estado(mensaje):
    with open(RUTA_ESTADO, 'w', encoding='utf-8') as f:
        f.write(mensaje)