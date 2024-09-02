# Monitorizacion-Archivos
Este script hace uso de la libreria Watchdog de python para la monitorizacion de ficheros. 
Además de enviar por correo alertas cuando un archivo que se ha creado o modificado cuenta con permisos elevados(777).

###Para la parte del correo es necesario cambiar las variables:
#### CORREO = 'tu_correo'
#### PASS = 'contraseña_aplicacion' -> se consigue al tener activado la doble autentificacion en seguridad en gmail y al buscar 'contraseña de aplicaciones'.
####CORREO_DESTINO = 'correo_destino'

### También se deben cambiar el contenido de las variables:
#### ignorar_archivos = [] -> extensiones de archivos a ignorar, o si contienen algun tipo de carácteres/nombre
#### directorios = [] -> Directorios a monitorizar
para estas variables he añadido algunas cosas que podrian interesar además de archivos que genera el sistema para ignorarlos

Ojo: No se monitorizan los directorios de manera recursiva. 
Ya para ello puedes modificarlo para añadirle esa opción para el directorio que quieras.

Para el fichero log debes añadir la ruta en la que quieres que este en esta variable:
#### fichero_log = f"{directorios[3]}/scripts/log.txt"


## Puedes configurar este script como un servicio, para ello puedes hacer esto:

#### 1.- crear el archivo de servicio en systemd
sudo nano /etc/systemd/system/scriptFicheros.service

#### 2.- colocar lo siguiente:
[Unit]
Description=Script Monitorizacion Archivos
After=network.target

[Service]
ExecStart=/usr/bin/python3 script.py
WorkingDirectory=/ruta_directorio_script
Restart=always
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target

#### 3.- Reiniciar demonio
sudo systemctl daemon-reload

#### 4.- habilitar, iniciar y comprobar servicio
sudo systemctl enable scriptFicheros.service
sudo systemctl start scriptFicheros.service
sudo systemctl status scriptFicheros.service
