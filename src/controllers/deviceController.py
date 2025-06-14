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
    valid_freq = ["Diaria", "Semanal", "Mensual", "Anual"]
    
    if freq not in valid_freq:
        print(f"Frecuencia inválida: '{freq}'. Debe ser una de {valid_freq}.")
        return False
    try:
        deviceModel.createDevice(name, ip, ssh_port, user, password, freq, time)
        return True
    except Exception as e:
        print(f"Error al agregar dispositivo: {e}")
        return False

def update_device(device_id, data):
    try:
        valid_freq = ["Diaria", "Semanal", "Mensual", "Anual"]
        db_column_map = {
            "Nombre": "name",
            "IP": "ip",
            "Puerto SSH": "ssh_port",
            "Usuario": "user",
            "Contraseña": "pass",
            "Periodicidad": "frequency",
            "Hora": "scheduled_date"
        }

        for column, new_value in data.items():
            if column == "Periodicidad" and new_value not in valid_freq:
                print(f"Frecuencia inválida: '{new_value}'. Debe ser una de {valid_freq}.")
                return False

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