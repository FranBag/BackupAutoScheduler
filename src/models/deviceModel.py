import sqlite3 as sqlite

def createDevice(name, user, password):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    query = "INSERT INTO device(`name`, `user`, pass) VALUES (?, ?, ?)"
    cursor.execute(query, [name, user, password])
    connection.commit()
    connection.close()

def getDevicebyName(name):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    query = "SELECT * FROM device WHERE name = ?"
    cursor.execute(query, [name])
    device = cursor.fetchall()
    connection.commit()
    connection.close()
    print(device)
    
if __name__ == "__main__":
    createDevice("romero", "romaro", "romare")
    getDevicebyName("romero")