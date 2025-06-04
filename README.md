# Sistema-de-gestion-de-envios-con-FastAPI

# Gestor de Envíos 📦

Este proyecto es una API REST desarrollada con **FastAPI**, que permite gestionar envíos postales de forma segura y estructurada. Utiliza **SQL Server** como base de datos y **JWT** para autenticación de usuarios.

## Características principales 🚀

- Creación de envíos con número de seguimiento único
- Consulta individual y listado de envíos registrados
- Seguridad mediante autenticación con JWT
- Interacción con base de datos usando SQLAlchemy
- Validación de datos con Pydantic

## Tecnologías utilizadas 🛠️

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PyODBC](https://github.com/mkleehammer/pyodbc)
- [JWT (jose)](https://python-jose.readthedocs.io/)
- [Passlib](https://passlib.readthedocs.io/)
- Base de datos: SQL Server

## Estructura del proyecto 📂

- `Envio`: Modelo SQLAlchemy que representa un envío.
- `EnvioCreate` y `EnvioResponse`: Esquemas Pydantic para entrada y salida de datos.
- Rutas protegidas con autenticación (`Bearer Token`).
- Conexión a SQL Server con autenticación integrada de Windows.

## Endpoints disponibles 📡

| Método | Ruta                  | Descripción                                  | Autenticación |
|--------|-----------------------|----------------------------------------------|----------------|
| POST   | `/token`              | Obtener token de acceso JWT                  | ❌              |
| POST   | `/envios/`            | Crear un nuevo envío                         | ✅              |
| GET    | `/envios/{tracking}`  | Obtener información de un envío específico   | ❌              |
| GET    | `/envios/`            | Listar todos los envíos (con paginación)     | ❌              |

## Cómo ejecutar el proyecto ⚙️

1. Asegurate de tener una base de datos SQL Server activa con una tabla `envios`.
2. Instalá las dependencias:
   ```bash
   pip install fastapi uvicorn sqlalchemy pyodbc python-jose passlib[bcrypt] pydantic
3. Ejecutá el servidor:
   ¨  bash
   uvicorn gestor_de_envios:app --reload

   
