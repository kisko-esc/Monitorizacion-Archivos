#!/bin/bash/ env python3

import sys
import os
import subprocess
import pkg_resources
from datetime import datetime

# Obtener IP
import socket
import psutil

def get_ip():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                print(f'Interfaz: {interface} - Dirección IP: {addr.address}')
                return addr.address


def install_package(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
        pkg_resources.require("watchdog")

except pkg_resources.DistributionNotFound:
    print("La biblioteca 'watchdog' no esta instalada. Intentando instalar...")

    try:
        install_package("watchdog")
        print("Instalacion exitosa. Reejecuta el script.")
    except Exception as e:
        print(f"Error durante la instalacion de 'watchdog': {e}")
    sys.exit(1)

except Exception as e:
    print(f"Error inesperado: {e}")
    sys.exit(1)

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import mimetypes

# Enviar por correo las alertas de Permisos elevados
import smtplib

CORREO = 'tu_correo'
PASS = 'contraseña_aplicacion'
CORREO_DESTINO = 'correo_destino'

ignorar_archivos = [
    ".png",
    ".jpg",
    ".gif",
    "jpeg",
    ".tmp",
    "systemd-private",
    "etilqs_",
    ".goutputstream-",
    ".zsh_history."
]

usr_desktop = '/home' + os.getenv("HOME") + "/Desktop"
usr = '/home' + os.getenv('HOME')

directorios = [
    usr_desktop,
    usr,
    '/home/kali',
    '/home/kali/Desktop',
    '/home',
    '/',
    '/var/tmp',
    '/root',
    '/tmp'
]



fichero_log = f"{directorios[3]}/scripts/log.txt"

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.archivo = []

    def enviar_correo(self, msg):
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(CORREO, PASS)

            asunto = "Permisos elevados detectados"
            headers = f'From: {CORREO}\r\nTo: {CORREO_DESTINO}\r\nSubject: {asunto}'
            smtp.sendmail(CORREO, CORREO_DESTINO, f'{headers}\r\n{msg}')

    def ignorar(self, path):
        for ruta in ignorar_archivos:
            if ruta in path:
                return True
        return False

    def permisos(self, path):
        try:
            permisos = oct(os.stat(path).st_mode)[-3:]
            return permisos

        except FileNotFoundError as e:
            print(f"Error. No existe el directorio {path}")
            print(e)

    def acciones(self, path, permisos, tipoArchivo):
        # Quitar permisos si detecta permisos elevados
        for directorio in directorios:
            if directorio != path:
                if '7' in str(permisos):
                    os.chmod(path, 000)
                    msg = f"Permisos Elevados Detectados\nPermisos del archivo: {path} - Modificados a 000\nExtension: {tipoArchivo}\nHora: {now}\nDireccion IP: {get_ip()}"
                    self.enviar_correo(msg)
                    print(' ')
                    print("Correo enviado")
                    break

    def on_modified(self, event):
        if self.ignorar(event.src_path):
            pass
        else:
            for archivo in self.archivo:
                if archivo[0] == event.src_path and archivo[2] != self.permisos(event.src_path):
                    print(' ')
                    print(f"Permisos modificados para: {archivo[0]}")
                    print(f"Permisos originales: {archivo[2]}")
                    print(f'Permisos actuales: {self.permisos(event.src_path)}')

                    # enviar alerta al correo y modificar permisos
                    if '7' in str(self.permisos(event.src_path)):
                        msg = f'Cambios de permisos detectados\nNombre Archivo:{event.src_path} \nPermisos Originales:{archivo[2]} \nPermisos Actuales: {self.permisos(event.src_path)}\nDireccion IP: {get_ip()}\nPermisos actuales modificados a  000'
                        os.chmod(event.src_path, 000)
                        self.enviar_correo(msg)
                        print('Correo enviado')
                    
                    # Sobreescribir permisos en la lista
                    self.archivo[self.archivo.index(archivo)][2] = self.permisos(event.src_path)

    def on_created(self, event):
        if self.ignorar(event.src_path):
            pass
        else:
            print(" ")
            print(f'Archivo Creado: {event.src_path}')
            print(f'Tipo Archivo: {mimetypes.guess_type(event.src_path)[0]}')
            print(f'Hora: {now}')
            print(f'Permisos: {self.permisos(event.src_path)}')

            # Realizar las acciones
            self.acciones(event.src_path, self.permisos(event.src_path), mimetypes.guess_type(event.src_path)[0])

            # Agregar archivos creados a una variable
            self.archivo.append([event.src_path, mimetypes.guess_type(event.src_path)[0], self.permisos(event.src_path)])


    def on_deleted(self, event):
        if self.ignorar(event.src_path):
            pass
        else:
            print(" ")
            print(f'Archivo Eliminado: {event.src_path}')
            print(f'Hora: {now}')

            # Eliminar archivo de la lista con sus demas valores
            for archivo in self.archivo:
                if archivo[0] == event.src_path:
                    self.archivo.remove(archivo)


if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()

    # Programar la observacion para cada directorio en la lista
    for path in directorios:
        if os.path.isdir(path):
            observer.schedule(event_handler, path=path, recursive=False)

    observer.start()

    try:
        while True:
            time.sleep(1)
            now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            sys.stdout = open(fichero_log, 'a+')

    except KeyboardInterrupt:
        observer.stop()

    observer.join()

    sys.stdout = sys.__stdout__