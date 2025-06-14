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
    storeBackup("2024-06-20", 2, "BACKUP1")
    storeBackup("2025-05-15", 1, "BACKUP2")
    storeBackup("2024-10-28", 3, "BACKUP3")
    storeBackup("2025-04-11", 2, "BACKUP4")
    storeBackup("1992-05-09", 2, "BACKUP5")
    storeBackup("2025-03-22", 1, "BACKUP6")
    storeBackup("2024-02-16", 5, "BACKUP7")
    storeBackup("2023-11-13", 4, "BACKUP8")
    storeBackup("2022-10-15", 4, "BACKUP8")
    storeBackup("2025-02-17", 5, "BACKUP9")


if __name__ == "__main__":
    pass