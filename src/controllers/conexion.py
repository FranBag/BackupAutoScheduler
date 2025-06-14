import os
import sys
import paramiko
from ftplib import FTP
import re
from datetime import datetime, timedelta

#comando para que el router tome automaticamente fecha y hora
#/system ntp client set enabled=yes primary-ntp=8.8.8.8 secondary-ntp=8.8.4.4

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verificar_conexion_ssh(host, usuario, contrasena, puerto=22):
    """
    Verifica si una conexión SSH puede establecerse correctamente.
    
    Args:
        host (str): Dirección del servidor.
        usuario (str): Nombre de usuario.
        contrasena (str): Contraseña del usuario.
        puerto (int): Puerto SSH (por defecto 22).

    Returns:
        tuple: (bool: True si la conexión es exitosa, False en caso contrario,
                str: Mensaje de resultado.)
    """
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=5)
        return True, "Conexión SSH exitosa."
    except paramiko.AuthenticationException:
        return False, "Error de autenticación: Verifica el usuario y la contraseña."
    except paramiko.SSHException as e:
        return False, f"Error SSH: {e}. Asegúrate de que el puerto SSH es correcto y el servicio SSH está activo."
    except TimeoutError:
        return False, "Tiempo de espera agotado: No se pudo conectar al host. Verifica la IP y la conectividad de red."
    except Exception as e:
        return False, f"Error inesperado al intentar conectar: {e}"
    finally:
        cliente.close()

def ssh_ejecutar_comando(host, usuario, contrasena, puerto, comando):
    """
    Establece una conexión SSH, ejecuta un comando y devuelve la salida.
    
    Args:
        host (str): Dirección del servidor.
        usuario (str): Nombre de usuario.
        contrasena (str): Contraseña del usuario.
        puerto (int): Puerto SSH.
        comando (str): Comando a ejecutar.

    Returns:
        tuple: (bool: True si el comando se ejecutó sin errores, False en caso contrario,
                str: Salida del comando o mensaje de error.)
    """
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=5)
        stdin, stdout, stderr = cliente.exec_command(comando)
        salida = stdout.read().decode().strip()
        errores = stderr.read().decode().strip()

        if errores:
            return False, f"Error al ejecutar el comando '{comando}': {errores}"
        return True, salida

    except paramiko.AuthenticationException:
        return False, "Error de autenticación al ejecutar comando: Verifica usuario y contraseña."
    except paramiko.SSHException as e:
        return False, f"Error SSH al ejecutar comando: {e}"
    except TimeoutError:
        return False, "Tiempo de espera agotado al ejecutar comando."
    except Exception as e:
        return False, f"Error inesperado al ejecutar comando: {e}"
    finally:
        cliente.close()


def genera_backup(host, usuario, contrasena, puerto):
    """
    Envía el comando al Mikrotik para generar un archivo de backup.
    """
    success, message = ssh_ejecutar_comando(host, usuario, contrasena, puerto, "system backup save")
    if not success:
        return False, f"Fallo al generar backup en Mikrotik: {message}"
    return True, "Comando de backup enviado al Mikrotik. Esperando unos segundos para su creación..."


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


def obtener_y_descargar_backup_mas_reciente(host, usuario, contrasena, puerto):
    """
    Busca el archivo .backup más reciente en el Mikrotik (basándose en el timestamp en el nombre)
    y descarga su contenido binario vía SFTP.
    
    Returns:
        tuple: (bool: True si se descarga el backup, False en caso contrario,
                bytes: Contenido binario del backup si es exitoso, None en caso de error,
                str: Nombre del archivo de backup, None en caso de error/fallo.)
    """
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sftp = None # Inicializar sftp a None

    try:
        cliente.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=10)

        # Usamos /file print detail para obtener los nombres de archivo y sus propiedades
        _stdin, stdout, _stderr = cliente.exec_command('/file print detail')
        salida_files = stdout.read().decode()

        backups = []
        
        # Expresión regular para capturar el nombre del archivo '.backup'
        patron_nombre_backup = re.compile(r'name="([^"]+\.backup)"')
        
        # Expresión regular para extraer la fecha/hora de un nombre de archivo
        patron_fecha_en_nombre = re.compile(r'(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})')

        for linea in salida_files.splitlines():
            nombre_match = patron_nombre_backup.search(linea)
            if nombre_match:
                nombre_archivo_completo = nombre_match.group(1)
                fecha_dt = None
                
                # Intentar extraer la fecha/hora del nombre del archivo
                fecha_en_nombre_match = patron_fecha_en_nombre.search(nombre_archivo_completo)
                if fecha_en_nombre_match:
                    try:
                        año, mes, dia, hora, minuto = map(int, fecha_en_nombre_match.groups())
                        fecha_dt = datetime(año, mes, dia, hora, minuto)
                    except ValueError:
                        pass
                
                if fecha_dt: 
                    backups.append((nombre_archivo_completo, fecha_dt))

        if not backups:
            return False, None, "No se encontraron archivos .backup con un formato de fecha reconocido en el nombre."

        # Ordenar por fecha descendente para obtener el más reciente
        backups.sort(key=lambda x: x[1], reverse=True)
        nombre_backup_mas_reciente = backups[0][0]

        # Descargar el archivo de backup usando SFTP
        sftp = cliente.open_sftp()
        
        # Leer el contenido del archivo en memoria
        with sftp.open(nombre_backup_mas_reciente, 'rb') as f:
            contenido_backup = f.read()
        
        return True, contenido_backup, nombre_backup_mas_reciente

    except paramiko.AuthenticationException:
        return False, None, "Error de autenticación SFTP: Verifica usuario y contraseña."
    except paramiko.SSHException as e:
        return False, None, f"Error SSH/SFTP: {e}. Asegúrate de que el servicio SFTP está habilitado en el Mikrotik y el puerto SSH es correcto."
    except TimeoutError:
        return False, None, "Tiempo de espera agotado al descargar backup (Mikrotik no responde o muy lento)."
    except Exception as e:
        return False, None, f"Error inesperado al descargar backup: {e}"
    finally:
        if sftp:
            sftp.close()
        cliente.close()
        


# Funciones no utilizadas

def verificar_fecha_router(host, usuario, contrasena, max_diferencia_dias=1):
    """
    Verifica que la fecha/hora del router Mikrotik no difiera más de max_diferencia_dias de la fecha local.
    
    Args:
        host (str): IP o hostname del Mikrotik.
        usuario (str): Usuario SSH.
        contrasena (str): Contraseña.
        max_diferencia_dias (int): Días máximo de diferencia permitida (default 1).
        
    Returns:
        bool, str: (True, mensaje) si está OK, (False, mensaje_error) si hay demasiada diferencia.
    """
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(hostname=host, username=usuario, password=contrasena, timeout=10)
        _, stdout, _ = cliente.exec_command('/system clock print')
        salida = stdout.read().decode()

        # Salida típica:
        # time: 14:23:10
        # date: jun/13/2025

        # Extraer time y date usando regex
        time_match = re.search(r'time:\s*(\d{2}:\d{2}:\d{2})', salida)
        date_match = re.search(r'date:\s*([a-z]{3}/\d{1,2}/\d{4})', salida, re.IGNORECASE)

        if not time_match or not date_match:
            return False, "No se pudo extraer fecha/hora del router."

        hora_str = time_match.group(1)
        fecha_str = date_match.group(1).lower()

        # Parsear fecha y hora Mikrotik
        fecha_hora_str = f"{fecha_str} {hora_str}"  # ej: jun/13/2025 14:23:10
        fecha_hora = datetime.strptime(fecha_hora_str, "%b/%d/%Y %H:%M:%S")

        # Obtener fecha/hora local
        ahora_local = datetime.now()

        diferencia = abs(ahora_local - fecha_hora)

        if diferencia > timedelta(days=max_diferencia_dias):
            return False, f"Diferencia de fecha/hora demasiado grande: {diferencia}."

        return True, "Fecha/hora del router está dentro del rango aceptable."

    except Exception as e:
        return False, f"Error al verificar fecha/hora: {e}"
    finally:
        cliente.close()
        
def sincronizar_fecha_hora_router(host, usuario, contrasena, puerto):
    """
    Configura la fecha y hora del router MikroTik igual que la fecha/hora local de la PC.
    """
    # Obtener fecha y hora local en el formato esperado por MikroTik (MMM/DD/YYYY HH:MM:SS)
    ahora = datetime.now()
    fecha_str = ahora.strftime("%b/%d/%Y").lower()  # ej: jun/13/2025 (en minúsculas)
    hora_str = ahora.strftime("%H:%M:%S")          # ej: 14:35:20

    comando = f'/system clock set date={fecha_str} time={hora_str}'

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(hostname=host,port=puerto, username=usuario, password=contrasena, timeout=10)
        stdin, stdout, stderr = cliente.exec_command(comando)
        error = stderr.read().decode()
        if error:
            print(f"Error al configurar fecha/hora: {error}")
        else:
            print(f"Fecha y hora configuradas a {fecha_str} {hora_str} en el router.")
    except Exception as e:
        print(f"Error de conexión o ejecución: {e}")
    finally:
        cliente.close()
    
    if not verificar_fecha_router(host, usuario, contrasena, puerto):
        return Exception("error en la hora y fecha")
    
def sincronizar_fecha_hora_router(host, usuario, contrasena, puerto):
    """
    Configura la fecha y hora del router MikroTik igual que la fecha/hora local de la PC.
    """
    # Obtener fecha y hora local en el formato esperado por MikroTik (MMM/DD/YYYY HH:MM:SS)
    ahora = datetime.now()
    fecha_str = ahora.strftime("%b/%d/%Y").lower()  # ej: jun/13/2025 (en minúsculas)
    hora_str = ahora.strftime("%H:%M:%S")          # ej: 14:35:20

    comando = f'/system clock set date={fecha_str} time={hora_str}'

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=10)
        stdin, stdout, stderr = cliente.exec_command(comando)
        error = stderr.read().decode()
        if error:
            print(f"Error al configurar fecha/hora: {error}")
        else:
            print(f"Fecha y hora configuradas a {fecha_str} {hora_str} en el router.")
    except Exception as e:
        print(f"Error de conexión o ejecución: {e}")
    finally:
        cliente.close()

if __name__ == "__main__":
    print(verificar_conexion_ssh(host="192.168.56.120", usuario="usuario", contrasena= "pass"))
    
    