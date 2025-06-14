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
            print(f"❌ Error al configurar fecha/hora: {error}")
        else:
            print(f"✅ Fecha y hora configuradas a {fecha_str} {hora_str} en el router.")
    except Exception as e:
        print(f"❌ Error de conexión o ejecución: {e}")
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
    """
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=10)
        _, stdout, _ = cliente.exec_command('/file print detail')
        salida = stdout.read().decode()

        # Dividir la salida en bloques de archivos
        bloques = salida.strip().split("\n\n")
        backups = []

        for bloque in bloques:
            nombre_match = re.search(r'name="(.+?\.backup)"', bloque)
            fecha_match = re.search(r'creation-time=(\w+/\d+/\d+\s+\d+:\d+:\d+)', bloque)

            if nombre_match and fecha_match:
                nombre = nombre_match.group(1)
                fecha_str = fecha_match.group(1)

                try:
                    fecha_dt = datetime.strptime(fecha_str, "%b/%d/%Y %H:%M:%S")
                    backups.append((nombre, fecha_dt))
                except ValueError:
                    continue

        if not backups:
            print("❌ No se encontraron archivos .backup.")
            return

        # Ordenar por fecha descendente
        backups.sort(key=lambda x: x[1], reverse=True)
        nombre_backup = backups[0][0]
        print(f"📦 Backup más reciente: {nombre_backup}")

    except Exception as e:
        print(f"❌ Error SSH: {e}")
        return
    finally:
        cliente.close()

    # Descargar por FTP
    try:
        with FTP() as ftp:
            ftp.connect(host, puerto_ftp)
            ftp.login(usuario, contrasena)

            with open(ruta_local, 'wb') as f:
                ftp.retrbinary(f"RETR {nombre_backup}", f.write)

        print(f"✅ Backup '{nombre_backup}' descargado como '{ruta_local}'.")

    except Exception as e:
        print(f"❌ Error FTP al descargar el archivo: {e}")


def genera_y_descarga_backup(host, usuario, contrasena, puerto, ruta_local, puerto_ftp=21):
    genera_backup(host, usuario, contrasena, puerto)
    descargar_backup_mas_reciente(host, usuario, contrasena, puerto,ruta_local, puerto_ftp=21)


def borrar_archivos_viejos(host, usuario, contrasena,puerto,  meses=6):
    """
    Borra archivos en Mikrotik con antigüedad mayor a 'meses' vía SSH.
    
    Args:
        host (str): IP o hostname del Mikrotik.
        usuario (str): Usuario SSH.
        contrasena (str): Contraseña.
        meses (int): Edad mínima en meses para borrar (por defecto 6).
    """
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=10)
        _, stdout, _ = cliente.exec_command('/file print detail')
        salida = stdout.read().decode()

        patron = r'name="(.+?)".*?creation-time=(\S+ \S+)'
        fecha_corte = datetime.now() - timedelta(days=meses*30)  # Aproximado 30 días/mes

        archivos_viejos = []
        for match in re.finditer(patron, salida):
            nombre, fecha = match.groups()
            try:
                fecha_dt = datetime.strptime(fecha, "%b/%d/%Y %H:%M:%S")
                if fecha_dt < fecha_corte:
                    archivos_viejos.append(nombre)
            except ValueError:
                continue

        if not archivos_viejos:
            print("No hay archivos con más de", meses, "meses para borrar.")
            return

        print(f"Archivos a borrar ({len(archivos_viejos)}):", archivos_viejos)

        for archivo in archivos_viejos:
            comando_borrar = f'/file remove [find name="{archivo}"]'
            cliente.exec_command(comando_borrar)
            print(f"Archivo borrado: {archivo}")

        print("✅ Proceso de borrado finalizado.")

    except Exception as e:
        print(f"Error SSH: {e}")
    finally:
        cliente.close()
        



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
            print(f"❌ Error al configurar fecha/hora: {error}")
        else:
            print(f"✅ Fecha y hora configuradas a {fecha_str} {hora_str} en el router.")
    except Exception as e:
        print(f"❌ Error de conexión o ejecución: {e}")
    finally:
        cliente.close()
    
    if not verificar_fecha_router(host, usuario, contrasena, puerto):
        return Exception("error en la hora y fecha")
    
if __name__ == "__main__":
    print(verificar_conexion_ssh(host="192.168.56.120", usuario="usuario", contrasena= "pass"))
    
    
    # genera_y_descarga_backup(host="192.168.56.120", usuario="usuario", contrasena= "pass", puerto=22,ruta_local="E:/Francisco/Ing. en Sistemas de la Información/3.Tercer año/Primer cuatri/Comunicaciones/Integrador/codigo/src/controllers/hola.backup")