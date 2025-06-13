import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import deviceModel

def get_all_devices_data():
    devices = deviceModel.getAllDevices()
    formatted_devices = []
    for device in devices:
        formatted_devices.append({
            "ID": device[0],
            "Nombre": device[1],
            "IP": device[2],
            "Puerto SSH": device[3],
            "Usuario": device[4],
            "Contraseña": device[5],
            "Periodicidad": device[6],
            "Hora": device[7]
        })
    return formatted_devices

def add_device(name, ip, ssh_port, user, password, freq, time):
    try:
        deviceModel.createDevice(name, ip, ssh_port, user, password, freq, time)
        return True
    except Exception as e:
        print(f"Error al agregar dispositivo: {e}")
        return False

def update_device(device_id, data):
    try:
        for column, new_value in data.items():
            db_column_map = {
                "Nombre": "name",
                "IP": "ip",
                "Puerto SSH": "ssh_port",
                "Usuario": "user",
                "Contraseña": "pass",
                "Periodicidad": "frequency",
                "Hora": "scheduled_date"
            }
            if column in db_column_map:
                deviceModel.updateDevice(device_id, db_column_map[column], new_value)
        return True
    except Exception as e:
        print(f"Error al actualizar dispositivo: {e}")
        return False

def delete_device(device_id):
    try:
        deviceModel.deleteDevice(device_id)
        return True
    except Exception as e:
        print(f"Error al eliminar dispositivo: {e}")
        return False
    
def get_device_by_id(device_id):
    device = deviceModel.getDevicebyId(device_id)
    if device:
        device_data = device[0]
        return {
            "ID": device_data[0],
            "Nombre": device_data[1],
            "IP": device_data[2],
            "Puerto SSH": str(device_data[3]),
            "Usuario": device_data[4],
            "Contraseña": device_data[5],
            "Periodicidad": device_data[6],
            "Hora": device_data[7]
        }
    return None

# def obtener_dispositivos():
#     dispositivos = []

#     try:
#         rows = deviceModel.getAllDevices()
#         for row in rows:
#             dispositivo = {
#                 "Nombre": row[0],
#                 "IP": row[1],
#                 "Usuario": row[2],
#                 "Contraseña": row[3],
#                 "Puerto SSH": row[4],
#                 "Hora": row[5],
#                 "Periodicidad": row[6],
#             }
#             dispositivos.append(dispositivo)
#         return dispositivos

#     except sqlite.Error as e:
#         print("Error al acceder a la base de datos:", e)
#         return []
    
# print(obtener_dispositivos())