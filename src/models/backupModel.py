import sqlite3 as sqlite

def storeBackup(date, device_id, backup_file):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "INSERT INTO backup(`date`, device_id, backup_file) VALUES(?, ?, ?)"
    cursor.execute(query, [date, device_id, backup_file])
    
    connection.commit()
    connection.close()
    
def getAllBackupByDevice(device_id):
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    
    query = "SELECT * FROM backup WHERE device_id = ?"
    cursor.execute(query, [device_id])
    result = cursor.fetchall()
    
    connection.commit()
    connection.close()

    return result
    
def getBackupByDevice(device_id, date):
    pass

def deleteBackupById(backup_id):
    pass

if __name__ == "__main__":
    pass
    # with open("test_media/Mina.webp", "rb") as backup_file:
    #     backup_file_binary = backup_file.read()
    
    # storeBackup("hoymismo", 2, backup_file_binary)
    
    
    # foto = getAllBackupByDevice(2)[0][2]
    # with open("test_media/recuperado.webp", 'wb') as recuperado:
    #     recuperado.write(foto)