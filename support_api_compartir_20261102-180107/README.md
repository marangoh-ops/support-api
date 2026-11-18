# API de Solicitudes de Soporte

API para crear, consultar y actualizar solicitudes de soporte. Requiere Python 3.11 o superior. Sigue los pasos de tu sistema operativo desde la carpeta del proyecto.

## Compartir con un compañero

Comprime y comparte la carpeta del proyecto. No incluyas `.venv`, `support_requests.db` ni `__pycache__`: el entorno y la base de datos se crean localmente, y los usuarios de prueba se agregan al iniciar la API. El archivo `pyproject.toml` instala las dependencias necesarias.

Quien reciba el proyecto solo debe instalar Python 3.11, extraer la carpeta, abrir esa carpeta en VS Code y seguir los pasos de Windows o Linux de abajo. Antes de ejecutar comandos, debe confirmar que la terminal esta ubicada en la carpeta principal del proyecto.

## Windows

Abre la terminal de VS Code con **Terminal > Nueva terminal**. Los comandos deben ejecutarse desde la carpeta del proyecto, no desde `C:\Windows\system32`. Si la terminal muestra `PS C:\Windows\system32>`, primero ejecuta:

```powershell
Set-Location "$HOME\Downloads\Proyecto final programacion avanzada"
```

Confirma que la linea de la terminal ahora termina en `Proyecto final programacion avanzada>`.

La instalacion se hace una sola vez (o cuando cambien las dependencias):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Para iniciar la API, ejecuta:

```powershell
.\.venv\Scripts\python.exe -m uvicorn support_api.main:app --app-dir src --reload
```

Ejecuta las pruebas en otra terminal:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Linux

Abre una terminal en la carpeta del proyecto. Si estas en otra ubicacion, cambia a esa carpeta; reemplaza la ruta de ejemplo por la ubicacion real:

```bash
cd "/ruta/a/Proyecto final programacion avanzada"
```

La instalacion se hace una sola vez (o cuando cambien las dependencias):

```bash
python3.11 -m venv .venv
./.venv/bin/python -m pip install -e ".[dev]"
```

Para iniciar la API, ejecuta:

```bash
./.venv/bin/python -m uvicorn support_api.main:app --app-dir src --reload
```

Ejecuta las pruebas en otra terminal:

```bash
./.venv/bin/python -m pytest
```

## Ver la API

Cuando Uvicorn muestre que el servidor esta corriendo, deja esa terminal abierta y abre http://127.0.0.1:8000/docs en el navegador. Ahi puedes probar los endpoints en Swagger. Para detener el servidor, vuelve a la terminal y presiona `Ctrl+C`. La API crea los usuarios de prueba `USR-01`, `USR-02` y `USR-03` al iniciar.

La consulta individual acepta el ID en la ruta, por ejemplo `/api/v1/solicitudes/SOL-001`, y tambien como parametro con `/api/v1/solicitudes/consulta?id_solicitud=SOL-001`. Si el parametro esta vacio, la API responde con error 422.

## Archivos principales

- `main.py`: crea la aplicacion, prepara la base de datos al iniciar y convierte errores del negocio en respuestas HTTP.
- `routes.py`: define las direcciones HTTP y entrega el trabajo a la capa de servicio.
- `schemas.py`: define enumeraciones y valida los campos que entran y salen de la API.
- `service.py`: contiene las reglas para crear, buscar, listar y cambiar solicitudes; valida antes de guardar.
- `models.py`: describe las tablas y columnas que SQLAlchemy guarda en SQLite.
- `database.py`: crea el motor y las sesiones de base de datos, y agrega los usuarios ficticios iniciales.
- `errors.py`: agrupa errores de negocio con sus codigos HTTP.
- `tests/conftest.py`: configura los datos y el cliente temporales que comparten las pruebas.
- `tests/test_api.py`: contiene los casos de prueba para las operaciones y reglas.
- `pyproject.toml`: declara dependencias y configuracion de pytest.

## Como explicar el recorrido

Cuando llega una peticion, `routes.py` recibe la ruta y el cuerpo HTTP. `schemas.py` comprueba el formato y los valores permitidos. La ruta llama a `service.py`, que aplica las reglas del negocio y consulta o modifica los modelos de `models.py` mediante una sesion creada en `database.py`. Finalmente, FastAPI devuelve el resultado; si hay un error de negocio, `main.py` lo convierte en una respuesta con el codigo HTTP correspondiente.

Ejemplo para crear una solicitud: el cliente envia usuario, categoria, descripcion y prioridad; el esquema valida los datos, el servicio confirma que el usuario exista y guarda la solicitud con estado `NUEVA`, y la API devuelve el registro creado con su ID.

## Como funcionan las pruebas

Las pruebas se ejecutan desde la carpeta principal del proyecto. No es necesario iniciar el servidor: `TestClient` envia peticiones directamente a la aplicacion. `conftest.py` crea una base SQLite temporal en memoria con usuarios de prueba y la elimina al terminar, para que los casos no dependan de la base de datos real.

Para ejecutar las pruebas, abre una segunda terminal. Asegurate de volver a la carpeta del proyecto (en Windows usa el mismo `Set-Location` anterior) y ejecuta:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

En Linux, ejecuta:

```bash
./.venv/bin/python -m pytest
```

Pytest encuentra automaticamente los archivos `test_*.py`. Los casos comprueban creacion y estado inicial, limites de descripcion, rechazos sin persistencia, categorias y prioridades validas, consulta por ID vacio, invalido o inexistente, listado con exactamente dos coincidencias, transiciones permitidas y prohibidas, notas obligatorias e inmutabilidad de solicitudes cerradas. Un resultado como `11 passed` significa que los once casos terminaron correctamente.

El codigo tambien tiene docstrings en espanol. En VS Code puedes dejar el cursor sobre una funcion o clase para ver su explicacion; en las pruebas, las descripciones indican que requisito se esta comprobando.

Los nombres son convenciones comunes de Python y separan responsabilidades; se pueden cambiar, pero habría que actualizar también sus importaciones y pruebas. No es necesario modificarlos para instalar o ejecutar el proyecto.
