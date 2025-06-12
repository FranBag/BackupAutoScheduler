import sqlite3 as sqlite

def storeBackup(date, device_id, backup_file):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "INSERT INTO backup(`date`, device_id, backup_file) VALUES(?, ?, ?)"
    cursor.execute(query, (date, device_id, backup_file))
    
    connection.commit()
    connection.close()
    
def getAllBackupByDevice(device_id):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "SELECT * FROM backup WHERE device_id = ?"
    cursor.execute(query, (device_id,))
    result = cursor.fetchall()
    
    connection.commit()
    connection.close()

    return result
    
def getBackupByDevice(device_id, date):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "SELECT * FROM backup WHERE device_id = ? AND date = ?"
    cursor.execute(query, (device_id, date))
    result = cursor.fetchall()
    
    connection.commit()
    connection.close()

    return result

def deleteBackupById(backup_id):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "DELETE FROM backup WHERE id = ?"
    cursor.execute(query, (backup_id,))
    
    connection.commit()
    connection.close()

def iniciarbackup():
    storeBackup("20-06-2024", 2, "BACKUP1")
    storeBackup("15-05-2025", 1, "BACKUP2")

if __name__ == "__main__":
    pass
    # with open("test_media/Mina.webp", "rb") as backup_file:
    #     backup_file_binary = backup_file.read()
    

    
    # getBackupByDevice(1, "15-05-2025")
    
    
    
    # foto = getAllBackupByDevice(2)[0][2]
    # with open("test_media/recuperado.webp", 'wb') as recuperado:
    #     recuperado.write(foto)