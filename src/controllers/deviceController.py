
import sqlite3 as sqlite
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root) 
from src.models.deviceModel import getAllDevices


def obtener_dispositivos():
    dispositivos = []

    try:
        rows = getAllDevices()
        for row in rows:
            dispositivo = {
                "Nombre": row[0],
                "IP": row[1],
                "Usuario": row[2],
                "Contraseña": row[3],
                "Puerto SSH": row[4],
                "Hora": row[5],
                "Periodicidad": row[6],
            }
            dispositivos.append(dispositivo)
        return dispositivos

    except sqlite.Error as e:
        print("Error al acceder a la base de datos:", e)
        return []
    
print(obtener_dispositivos())