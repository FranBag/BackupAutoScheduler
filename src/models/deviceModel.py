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

def iniciardevice():
    createDevice("rou1", "192.168.56.120", "22", "admin", "admin", "Diaria", "20:30")
    createDevice("rou2", "10.10.50.20", "2222", "user", "pass", "Anual", "12:00")
    createDevice("rou3", "121.166.0.15", "22", "test", "test", "Anual", "01:00")
    createDevice("rou4", "172.16.0.2", "2200", "user", "12345", "Semanal", "5:30")
    createDevice("rou5", "10.0.2.18", "8022", "admin", "root", "Mensual", "23:59")

if __name__ == "__main__":
    pass