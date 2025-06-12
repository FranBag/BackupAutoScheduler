import sqlite3 as sqlite

def createDevice(name, ip, ssh_port, user, password, freq, time):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "INSERT INTO device(`name`, ip, ssh_port, `user`, pass, frequency, scheduled_date) VALUES (?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(query, (name, ip, ssh_port, user, password, freq, time))
    
    connection.commit()
    connection.close()
    
def getDevicebyName(name):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "SELECT * FROM device WHERE name = ?"
    cursor.execute(query, (name,))
    result = cursor.fetchall()
    
    connection.commit()
    connection.close()
    return result
    
def getDevicebyId(device_id):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "SELECT * FROM device WHERE id = ?"
    cursor.execute(query, (device_id,))
    result = cursor.fetchall()
    
    connection.commit()
    connection.close()
    return result
    
def getAllDevices():
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "SELECT * FROM device"
    cursor.execute(query)
    result = cursor.fetchall()
    
    connection.commit()
    connection.close()
    return result
    
def updateDevice(device_id, column, new_value):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = f"UPDATE device SET {column} = ? WHERE id = ?"
    cursor.execute(query, (new_value, device_id))
    
    connection.commit()
    connection.close()

def deleteDevice(device_id):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "DELETE FROM device WHERE id = ?"
    cursor.execute(query, (device_id,))
    
    connection.commit()
    connection.close()
    

#     try:
#         connection = sqlite3.connect("backups.db")
#         cursor = connection.cursor()
#         query = "SELECT * FROM device"
#         cursor.execute(query)
#         devices = cursor.fetchall()
#         print("All Devices:")
#         for device in devices:
#             print(device)
#         return devices # Return devices for potential further use
#     except sqlite3.Error as e:
#         print(f"Error retrieving devices: {e}")
#         return []
#     finally:
#         if connection:
#             connection.close()
def obtener_dispositivos():
    dispositivos = []

    try:
        # Conexión a la base de datos
        conn = sqlite.connect("backups.db")
        cursor = conn.cursor()

        # Consulta para obtener todos los dispositivos
        cursor.execute("""
            SELECT name, ip, user, pass, ssh_port, scheduled_date, frequency
            FROM device
        """)

        # Procesar cada fila
        for row in cursor.fetchall():
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

        conn.close()
        return dispositivos

    except sqlite.Error as e:
        print("Error al acceder a la base de datos:", e)
        return []

def iniciardevice():
    createDevice("rouA", "192.168.50.120", "2222", "admin", "admin", "daily", "20:30")
    createDevice("rouB", "10.10.50.20", "22", "user", "pass", "yearly", "12:00")
    createDevice("rouC", "255.255.255.255", "8888", "weekly", "12345", "", "")

if __name__ == "__main__":

    
    pass