import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import backupModel

def get_backups_for_device(device_id):
    try:
        backups_raw = backupModel.getAllBackupByDevice(device_id)
        formatted_backups = []
        for backup in backups_raw:
            # El campo backup_file es BLOB, si almacenas texto o ruta, asegúrate de decodificarlo
            # Si es un archivo binario, aquí deberías manejarlo como tal o solo mostrar el nombre.
            # Para la UI, asumiremos que se almacena una ruta o nombre de archivo como string.
            # Si es un BLOB con bytes de un archivo, necesitarías guardarlo en disco para mostrarlo o abrirlo.
            # Para este ejemplo, lo decodificamos si es bytes, o lo usamos directamente si ya es string.
            backup_file_content = backup[2] # backup[2] es backup_file
            if isinstance(backup_file_content, bytes):
                try:
                    backup_file_content = backup_file_content.decode('utf-8')
                except UnicodeDecodeError:
                    backup_file_content = "<Contenido Binario>" # O manejarlo de otra forma
            
            formatted_backups.append({
                "ID": backup[0], # ID del backup
                "Fecha": backup[1],
                "Archivo": backup_file_content,
                "DeviceID": backup[3] # Para referencia interna, aunque no se mostrará directamente
            })
        return formatted_backups
    
    except Exception as e:
        print(f"Error al obtener backups para el dispositivo {device_id}: {e}")
        return []
    

def add_backup(date, device_id, backup_file_data):
    """
    Almacena un nuevo backup en la base de datos.
    backup_file_data debe ser bytes (para BLOB).
    """
    try:
        backupModel.storeBackup(date, device_id, backup_file_data)
        return True
    except Exception as e:
        print(f"Error al agregar backup: {e}")
        return False

def delete_backup(backup_id):
    """
    Elimina un backup de la base de datos por su ID.
    """
    try:
        backupModel.deleteBackupById(backup_id)
        return True
    except Exception as e:
        print(f"Error al eliminar backup: {e}")
        return False