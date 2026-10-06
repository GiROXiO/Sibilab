# Sibilab - Sistema de Gestión de Biblioteca

Sibilab es una plataforma web transaccional diseñada para digitalizar y automatizar el proceso de préstamo, devolución y administración del inventario físico de libros de la biblioteca universitaria.

Este proyecto fue desarrollado para el Laboratorio 01 de Bases de Datos.

## Stack Tecnológico

- **Backend:** Python 3.13.15 / Django
- **Base de Datos:** PostgreSQL
- **Frontend:** HTML5 / Bootstrap (Django Templates)

## Equipo de Desarrollo

- **Jerónimo Castro:** Arquitecto de BD e Integrador (Líder del repositorio).
- **Juan Cáceres:** Desarrollador Backend Core (Modelos ORM y operaciones CRUD).
- **Juan Arrieta:** Especialista en Lógica de Negocio (Flujos de validación, préstamos y multas).
- **Miguel Carrizosa:** Analista de Datos (Consultas SQL, métricas y reportes).

## Estructura del Repositorio

- `/docs/`: Documentación técnica (Diagrama Entidad-Relación y Modelo Relacional).
- `/sql/`: Scripts de inicialización (`init.sql`, `insert.sql`) y consultas analíticas para reportes.
- `/src/`: Código fuente de la aplicación en Django.

---

## Guía de Instalación Local

Para ejecutar este proyecto en un entorno local, es necesario configurar el motor de base de datos y el entorno de desarrollo de Django siguiendo este orden estricto:

### 1. Requisitos Previos

- Python 3.13.15.
- PostgreSQL y pgAdmin.
- Git.

### 2. Clonación y Entorno Virtual

Primero debes ubicarte en el directorio de tu computador donde deseas guardar el proyecto, luego descargar el repositorio y aislar las dependencias:

```bash
# 1. Navegar a la carpeta local donde deseas trabajar
cd ruta/a/tu/carpeta/preferida

# 2. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>

# 3. Entrar a la carpeta generada por el repositorio
cd sibilab

# Cambiar a la rama de integración
git checkout develop

# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# Opción A: Si usas Git Bash (Recomendado)
source venv/Scripts/activate

# Opción B: Si usas CMD o PowerShell
venv\Scripts\activate

# Instalar dependencias del proyecto (incluye dotenv para variables de entorno)
pip install django psycopg2-binary python-dotenv
```

### 3. Preparación de la Base de Datos

Con el repositorio ya clonado en el equipo, se deben ejecutar los scripts locales para estructurar la base de datos:

1. Abrir pgAdmin y crear una base de datos vacía con el nombre exacto: `sibilab`.
2. Abrir la herramienta de consultas (Query Tool) sobre esta base de datos.
3. Copiar el contenido del script `/sql/init.sql` (ubicado en la carpeta del repositorio) y ejecutarlo para generar el esquema `core` y las tablas correspondientes.
4. Copiar el contenido del script `/sql/insert.sql` y ejecutarlo para cargar los datos de prueba.

### 4. Configuración de la Conexión a Base de Datos

El proyecto requiere apuntar a la base de datos PostgreSQL local y utiliza variables de entorno para proteger las credenciales.

1. En la raíz del proyecto (al mismo nivel que `manage.py`), crear un archivo llamado exactamente `.env`.
2. Dentro de ese archivo, colocar la contraseña local de PostgreSQL de la siguiente forma:
   ```text
   DB_PASSWORD=tu_contraseña_local
   ```
3. Asegurarse de que el archivo `settings.py` tenga configurado el bloque `DATABASES` para leer esta variable de entorno de la siguiente manera:

```python
from dotenv import load_dotenv
import os

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sibilab',
        'USER': 'postgres',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'options': '-c search_path=core'
        }
    }
}
```

_(Nota: El archivo `.env` está declarado en el `.gitignore`, por lo que las credenciales locales nunca se subirán al repositorio de GitHub)._

### 5. Ejecución del Servidor

Con la base de datos configurada, aplica las migraciones base de Django e inicia el servidor:

```bash
# Entrar a la carpeta del código fuente
cd src

# Generar las tablas automáticas de Django
python manage.py migrate

# Iniciar el servidor
python manage.py runserver
```

El sistema estará disponible en el navegador a través de la ruta `http://127.0.0.1:8000/`.

## Flujo de Trabajo (Git Workflow)

El equipo utilizará un modelo de ramificación basado en características (Feature Branches) para aislar el desarrollo y prevenir conflictos en el código base:

1. Sincronizar el entorno local con los últimos cambios: `git pull origin develop`.
2. Crear una nueva rama para la tarea asignada: `git checkout -b feature/nombre-de-tu-tarea`.
3. Desarrollar la funcionalidad requerida.
4. Registrar los cambios localmente: `git add .` seguido de `git commit -m "feat: descripción técnica del cambio"`.
5. Subir la rama al repositorio remoto: `git push origin feature/nombre-de-tu-tarea`.
6. Generar un Pull Request en GitHub apuntando hacia la rama `develop` para su respectiva revisión y aprobación por parte del Integrador.
