import os

from src.models.dbInicializer import createDB
from src.models.deviceModel import iniciardevice
from src.models.backupModel import iniciarbackup
from src.view import GUI

def backup_exist():
    route = os.path.join(".", "backups.db")
    return os.path.isfile(route)

if __name__ == "__main__":
    if not backup_exist():
        createDB()
        iniciardevice()
        iniciarbackup()
        print("Se ha creado la base de datos")
    
    root = GUI.tk.Tk()
    app = GUI.BackupGUI(root)
    root.mainloop()
