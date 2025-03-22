# backend-diocesis

Instrucciones para desarrollo:

1. Ejecutar comando `git fetch` para revisar cambios pendinetes
2. Ejecutar comando `git pull` para actualizar el proyecto
3. Ejecutar comando `venv\Scripts\activate` para entrar al entorno virtual
4. Ejecutar comando `pip install -r requirements.txt` para instalar librerias
5. Crear el archivo `.env` en base al archivo `.env.template` 
6. Ejecutar servidor con el comando:
```
python manage.py runserver
```

6. Ingresar a la siguiente dirección:
```
http://127.0.0.1:8000/
```

Instrucciones para guardado de cambios:

1. Ejecutar comando ``git add .`` para seleccionar los archivos modificados
2. Ejecutar comando ``git commmit -m "Mensaje"``

Nomenclatura recomendada:

- fix: para arreglar errores
- update: para actualizar
- create: para nuevos archivos o funcionalidades
- delete: para borrado de archivos

EJEMPLO: fix - carga de archivos desde csv

NOTA:

Si se instala una nuneva librería esta debe ser agregada en el archivo
```
requirements.txt
```


