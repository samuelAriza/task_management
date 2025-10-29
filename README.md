# Parcial 2 - Examen Técnico 70%
###  Samuel Andrés Ariza Gómez
---

## Resumen del proyecto 

Este repositorio contiene una implementación mínima y profesional de una API REST para la gestión de tareas escrita en **Python 3.11+** con **FastAPI**, preparada para ejecutarse dentro de un contenedor **Docker**. El propósito del proyecto es demostrar buenas prácticas de diseño (patrones, principios SOLID) de software.

---

## Estructura del proyecto

```bash
.
├── Dockerfile
├── README.md
├── app
│   ├── __init__.py
│   ├── adapters
│   │   ├── __init__.py
│   │   ├── http
│   │   │   ├── __init__.py
│   │   │   └── fastapi_app.py
│   │   └── persistence
│   │       ├── __init__.py
│   │       ├── memory_task_repository.py
│   │       └── sqlite_task_repository.py
│   ├── application
│   │   ├── __init__.py
│   │   ├── ports
│   │   │   ├── __init__.py
│   │   │   └── task_repository.py
│   │   └── services
│   │       ├── __init__.py
│   │       └── task_service.py
│   └── domain
│       ├── __init__.py
│       └── task.py
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_domain.py
│   └── test_service.py
└── venv
```


Descripción breve de módulos clave:

- Domain
  - [`app.domain.task.Task`](app/domain/task.py): Entidad con validaciones (título obligatorio, status válido), fábrica `create`, métodos `update_title`, `update_status` y `to_dict`.
  - [`app.domain.task.TaskStatus`](app/domain/task.py): Enumeración (`pending`, `done`).
- Application
  - [`app.application.services.task_service.TaskService`](app/application/services/task_service.py): Orquesta casos de uso; depende de la interfaz de repositorio (`ITaskRepository`).
  - [`app.application.ports.task_repository.ITaskRepository`](app/application/ports/task_repository.py): Contrato de persistencia (save, find_all, find_by_id, update, delete).
- Adapters
  - HTTP: [`app.adapters.http.fastapi_app`](app/adapters/http/fastapi_app.py) expone los endpoints y define DTOs (Pydantic).
  - Persistence: `MemoryTaskRepository` y `SQLiteTaskRepository` implementan `ITaskRepository`.

---

## Ejecución del proyecto de manera local

Requisitos previos:
- Python 3.10+ (recomendado 3.11)
- pip
- (opcional) Docker y docker-compose

1. Clonar el repositorio (si no está ya en su máquina):
   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```

2. Crear y activar un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Ejecutar la API con uvicorn (modo local, *in-process*):
   - Punto de entrada ASGI: [`app.adapters.http.fastapi_app:app`](app/adapters/http/fastapi_app.py)
   ```bash
   # desde la raíz del proyecto
   python -m uvicorn app.adapters.http.fastapi_app:app --host 0.0.0.0 --port 8000
   ```
   - Alternativamente, usar el comando definido en el Dockerfile:
   ```bash
   python -m "uvicorn" app.adapters.http.fastapi_app:app --host 0.0.0.0 --port 8000
   ```

5. Verificar:
   - Health: http://localhost:8000/health
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## Ejecutar usando Docker

El proyecto está listo para correr en Docker. El contenedor expone el puerto `8000` y, si se usa SQLite, la base de datos se almacena en `/app/data/tasks.db` (montada desde host si se usa docker-compose).

Archivos relevantes:
- [Dockerfile](Dockerfile)
- [docker-compose.yml](docker-compose.yml)

Construir imagen Docker:
```bash
docker build -t task-management-api:latest .
```

Ejecutar con Docker (sin docker-compose):
```bash
# Ejecuta la imagen y mapea el puerto 8000 local->contenedor
docker run --rm -p 8000:8000 \
  -e USE_SQLITE=true \
  -v "$(pwd)/data:/app/data" \
  task-management-api:latest
```

Ejecutar con docker-compose:
```bash
# Levanta el servicio definido en docker-compose.yml
docker compose up --build
```

Notas:
- La variable de entorno `USE_SQLITE` (definida en [app/adapters/http/fastapi_app.py](app/adapters/http/fastapi_app.py)) controla si se usa SQLite (`true`) o almacenamiento en memoria (`false`).
- Si `USE_SQLITE=true` y se monta `./data:/app/data`, la base SQLite persistirá en `./data/tasks.db`.
- `docker-compose.yml` por defecto exporta el puerto `8000` y monta `./data:/app/data`.

---

## Ejemplos de uso (curl) — probar endpoints

Health:
```bash
curl -sS http://localhost:8000/health | jq
```

Listar tareas (inicialmente vacía):
```bash
curl -sS http://localhost:8000/tasks | jq
```

Crear tarea:
```bash
curl -sS -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Mi tarea de ejemplo","status":"pending"}' | jq
```

Obtener por id:
```bash
curl -sS http://localhost:8000/tasks/<task_id> | jq
```

Actualizar tarea (parcial o completa):
```bash
curl -sS -X PUT http://localhost:8000/tasks/<task_id> \
  -H "Content-Type: application/json" \
  -d '{"status":"done"}' | jq
```

Eliminar tarea:
```bash
curl -sS -X DELETE http://localhost:8000/tasks/<task_id> -v
```

(En los ejemplos sustituir `<task_id>` por el id devuelto al crear la tarea.)

---

## Diseño y Principios SOLID aplicados

Resumen de cómo se aplican principios y patrones:

- SRP (Single Responsibility Principle):
  - `Task` ([app/domain/task.py](app/domain/task.py)) encapsula la lógica de la entidad (validaciones, estado, timestamps).
  - `TaskService` ([app/application/services/task_service.py](app/application/services/task_service.py)) orquesta casos de uso y no conoce detalles de almacenamiento.
  - Repositorios (`MemoryTaskRepository`, `SQLiteTaskRepository`) gestionan solo la persistencia.

- OCP (Open/Closed Principle):
  - Las implementaciones de persistencia se pueden extender sin modificar el servicio ni el dominio. El servicio depende de la interfaz `ITaskRepository` ([app/application/ports/task_repository.py](app/application/ports/task_repository.py)).

- DIP (Dependency Inversion Principle):
  - `TaskService` depende de la abstracción `ITaskRepository` y no de implementaciones concretas. La inyección de dependencia se realiza en [`app.adapters.http.fastapi_app`](app/adapters/http/fastapi_app.py), que decide en tiempo de inicialización si usar memoria o SQLite.

Patrones principales:
- Repository: [`app.application.ports.task_repository.ITaskRepository`](app/application/ports/task_repository.py) + implementaciones en [`app.adapters.persistence`](app/adapters/persistence).
- Service / Application Service: [`app.application.services.task_service.TaskService`](app/application/services/task_service.py) — coordenador de casos de uso.
- Factory / DI simple: El módulo HTTP crea la instancia del repositorio dependiendo de la variable `USE_SQLITE` y construye el `TaskService`.

---

## Validaciones y respuestas HTTP

Validaciones mínimas aplicadas:
- `title`: obligatorio, no vacío (trim aplicado)
- `status`: debe ser `pending` o `done`
- En caso de datos inválidos el endpoint responde con `400` o `422` dependiendo del punto de validación (Pydantic/servicio).
- Endpoints REST utilizan las respuestas y códigos HTTP adecuados (201 para creación, 204 para eliminación exitosa sin contenido, 404 para no encontrado).

Los DTOs y validaciones están en: [`app.adapters.http.fastapi_app.TaskCreateRequest`](app/adapters/http/fastapi_app.py) y [`TaskUpdateRequest`](app/adapters/http/fastapi_app.py).

---

## Tests — Ejecutar pruebas

Se incluyen pruebas en `tests/`:

- [tests/test_domain.py](tests/test_domain.py) — pruebas unitarias de la entidad `Task`.
- [tests/test_service.py](tests/test_service.py) — pruebas del `TaskService` usando `MemoryTaskRepository`.
- [tests/test_api.py](tests/test_api.py) — pruebas de integración de la API con FastAPI `TestClient`.

Ejecutar las pruebas con pytest:
```bash
pip install -r requirements.txt
pytest -q
# o para salida detallada
pytest -v
```

Archivo de configuración: [pytest.ini](pytest.ini)

---

## Requisitos técnicos

- Python: 3.10+ (probado con 3.11)
- FastAPI: especificado en [requirements.txt](requirements.txt)
- Uvicorn ASGI server
- Puerto por defecto: `8000`
- Docker: para contenedores (opcional pero requerido para evaluación con Dockerfile)
- Entorno y configuración:
  - Variable: `USE_SQLITE` — controla persistencia (`true` usa SQLite, `false` usa memoria)
  - Ruta base SQLite: `/app/data/tasks.db` (si se usa SQLite)

Dependencias principales (ver [requirements.txt](requirements.txt)):
- fastapi
- uvicorn
- pydantic
- pytest

---