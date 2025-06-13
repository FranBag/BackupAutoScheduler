import paramiko
from ftplib import FTP
import re
from datetime import datetime

def ssh_ejecutar_comando(host, usuario, contrasena, puerto, comando):
    """
    Establece una conexión SSH, ejecuta un comando y devuelve la salida.
    
    Args:
        host (str): Dirección del servidor.
        usuario (str): Nombre de usuario.
        contrasena (str): Contraseña del usuario.
        comando (str): Comando a ejecutar.

    Returns:
        str: Salida del comando o mensaje de error.
    """
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conexión al servidor
        cliente.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=10)
        # Ejecutar el comando
        stdin, stdout, stderr = cliente.exec_command(comando)
        salida = stdout.read().decode().strip()
        errores = stderr.read().decode().strip()

        if errores:
            return f"Error al ejecutar el comando:\n{errores}"
        return salida

    except paramiko.AuthenticationException:
        return "Error: Falló la autenticación. Verifica usuario y contraseña."
    except paramiko.SSHException as e:
        return f"Error SSH: {e}"
    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        cliente.close()
        

def verificar_conexion_ssh(host, usuario, contrasena, puerto=22):
    """
    Verifica si una conexión SSH puede establecerse correctamente.
    
    Args:
        host (str): Dirección del servidor.
        usuario (str): Nombre de usuario.
        contrasena (str): Contraseña del usuario.
        puerto (int): Puerto SSH (por defecto 22).

    Returns:
        bool: True si la conexión es exitosa, False en caso contrario.
        str: Mensaje de resultado.
    """
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        
        return True, "Conexión SSH exitosa."
    except paramiko.AuthenticationException:
        return False, "Error: Falló la autenticación. Verifica usuario y contraseña."
    except paramiko.SSHException as e:
        return False, f"Error SSH: {e}"
    except Exception as e:
        return False, f"Error inesperado: {e}"
    finally:
        cliente.close()
    


def genera_backup(host, usuario, contrasena, puerto):
    ssh_ejecutar_comando(host, usuario, contrasena, puerto, "system/backup/save")
    


def listado_archivos_con_detalles_ssh(host, usuario, contrasena, puerto):
    """
    Conecta vía SSH al Mikrotik y obtiene la lista de archivos con nombre, tamaño y fecha de creación.
    """
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=10)

        _, stdout, _ = cliente.exec_command('/file print detail')
        salida = stdout.read().decode()

        archivos = []
        # esto define como extraer la informacion
        patron = r'name="(.+?)".*?size=(\S+).*?creation-time=(\S+ \S+)'

        for match in re.finditer(patron, salida):
            nombre, tamaño, fecha = match.groups()
            archivos.append({
                "nombre": nombre,
                "tamaño": tamaño,
                "fecha_creacion": fecha
            })

        return archivos

    except Exception as e:
        print(f"Error al obtener archivos: {e}")
        return []
    finally:
        cliente.close()



def descargar_backup_mas_reciente(host, usuario, contrasena, puerto, ruta_local, puerto_ftp=21):
    """
    Busca el archivo .backup más reciente en el Mikrotik y lo descarga vía FTP.
    
    Args:
        host (str): IP o hostname del Mikrotik.
        usuario (str): Usuario para SSH y FTP.
        contrasena (str): Contraseña.
        ruta_local (str): Ruta donde guardar el archivo descargado.
        puerto_ftp (int): Puerto FTP (por defecto 21).
    """
    # 1. Conectarse por SSH para obtener detalles
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=10)
        _, stdout, _ = cliente.exec_command('/file print detail')
        salida = stdout.read().decode()

        # 2. Parsear archivos .backup
        patron = r'name="(.+?\.backup)".*?creation-time=(\S+ \S+)'
        backups = []

        for match in re.finditer(patron, salida):
            nombre, fecha = match.groups()
            try:
                fecha_dt = datetime.strptime(fecha, "%b/%d/%Y %H:%M:%S")
                backups.append((nombre, fecha_dt))
            except ValueError:
                continue  # Ignorar fechas que no se pueden parsear

        if not backups:
            print("❌ No se encontraron archivos .backup.")
            return

        # 3. Seleccionar el backup más reciente
        backups.sort(key=lambda x: x[1], reverse=True)
        nombre_backup = backups[0][0]
        print(f"📦 Backup más reciente: {nombre_backup}")

    except Exception as e:
        print(f"❌ Error SSH: {e}")
        return
    finally:
        cliente.close()

    # 4. Descargar el archivo por FTP
    try:
        with FTP() as ftp:
            ftp.connect(host, puerto_ftp)
            ftp.login(usuario, contrasena)

            with open(ruta_local, 'wb') as f:
                ftp.retrbinary(f"RETR {nombre_backup}", f.write)

        print(f"✅ Backup '{nombre_backup}' descargado como '{ruta_local}'.")

    except Exception as e:
        print(f"❌ Error FTP al descargar el archivo: {e}")
