# backend-diocesis

## 🧪 Instrucciones para desarrollo

1. Ejecutar `git fetch` para revisar cambios pendientes  
2. Ejecutar `git pull` para actualizar el proyecto
3. Crear el entorno virtual con el comnando:
    ```
    python -m venv venv
    ```
4. Activar el entorno virtual:

   ```
   venv\Scripts\activate
   ```

5. Instalar dependencias:

   ```
   pip install -r requirements.txt
   ```

6. Crear el archivo `.env.dev` dentro de la carpeta `config`, basado en `.env.template`  
7. Ejecutar el servidor:

   ```
   python manage.py runserver
   ```

8. Ingresar a la aplicación:

   ```
   http://127.0.0.1:8000/
   ```

---

## 💾 Instrucciones para guardar cambios en Git

1. Añadir los archivos modificados:

   ```
   git add .
   ```

2. Confirmar los cambios:

   ```
   git commit -m "Mensaje"
   ```

### 🏷️ Nomenclatura recomendada

- `fix:` para arreglar errores
- `update:` para actualizar funcionalidades
- `create:` para nuevos archivos o funciones
- `delete:` para eliminar archivos

**Ejemplo:** `fix - carga de archivos desde csv`

📌 Si se instala una nueva librería, recuerda actualizar:

```
requirements.txt
```
---

## 🚀 Instrucciones para producción

1. Activar el entorno virtual:

   ```
   venv\Scripts\activate
   ```

2. Crear archivo de configuración:

   ```
   config/.env.prod
   ```

   Basado en `.env.template` con ajustes como:

   - `DEBUG=False`
   - Dominio válido en `ALLOWED_HOSTS`
   - Claves reales de producción

3. Establecer variable de entorno `DJANGO_ENV`:

   - En **PowerShell**:

     ```
     $env:DJANGO_ENV = "prod"
     ```

   - En **CMD**:

     ```
     set DJANGO_ENV=prod
     ```

4. Aplicar migraciones y colectar archivos estáticos:

   ```
   python manage.py migrate
   python manage.py collectstatic
   ```

5. Ejecutar el servidor:

   ```
   python manage.py runserver
   ```

   O configurar WSGI en producción según el hosting (por ejemplo, Hostinger).

---

✅ ¡Listo! Tu proyecto estará funcionando en modo desarrollo o producción según la variable `DJANGO_ENV`.