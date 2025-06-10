import sqlite3 as sqlite

def createDevice(name, user, password):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "INSERT INTO device(`name`, `user`, pass) VALUES (?, ?, ?)"
    cursor.execute(query, [name, user, password]) # Los arrays deberían de reemplazarse por tuplas (x,x,x)
    
    connection.commit()
    connection.close()

def getDevicebyName(name):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "SELECT * FROM device WHERE name = ?"
    cursor.execute(query, [name]) # (x,)
    result = cursor.fetchall()
    
    connection.commit()
    connection.close()
    return result
    
def getDevicebyId(device_id):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "SELECT * FROM device WHERE id = ?"
    cursor.execute(query, [device_id])
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
    cursor.execute(query, [new_value, device_id])
    
    connection.commit()
    connection.close()

def deleteDevice(device_id):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "DELETE FROM device WHERE id = ?"
    cursor.execute(query,[device_id])
    
    connection.commit()
    connection.close()
    
# def getAllDevices():
#     connection = None
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


if __name__ == "__main__":
    createDevice("rouA", "admin", "admin")
    createDevice("rouB", "user", "pass")
    createDevice("rouC", "test", "12345")
    
    print(getAllDevices())
    
    deleteDevice(3)
    
    print(getDevicebyName("rouC"))
    
    print(getDevicebyId(2))