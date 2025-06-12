from src.models.dbInicializer import createDB
from src.models.deviceModel import iniciardevice
from src.models.backupModel import iniciarbackup

if __name__ == "__main__":
    createDB()
    iniciardevice()
    iniciarbackup()