import sqlite3 as sqlite

def createDB():
    connection = sqlite.connect("backups.db")
    connection.commit()
    connection.close()
    
    createTableDevice()
    createTableBackup()

def createTableDevice():
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE device(
            id integer primary key,
            `name` text,
            `user` text,
            pass text
        )
        """)
    connection.commit()
    connection.close()

def createTableBackup():
    connection = sqlite.connect("backups.db")
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE backup(
            id integer primary key,
            `date` text,
            backup_file blob,
            device_id integer,
            foreign key(device_id) references device(id)
        )
        """)
    
    connection.commit()
    connection.close()
    
if __name__ == "__main__":
    createDB()