"""
Módulo principal de la API REST para gestión de tareas.

Este módulo implementa una API REST usando FastAPI con arquitectura hexagonal,
proporcionando endpoints para la gestión completa de tareas (CRUD).
Soporta almacenamiento en memoria y SQLite mediante inyección de dependencias.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import os

from app.application.services.task_service import TaskService
from app.adapters.persistence.memory_task_repository import MemoryTaskRepository
from app.adapters.persistence.sqlite_task_repository import SQLiteTaskRepository


# DTOs (Data Transfer Objects) - Patrón DTO para la capa HTTP
class TaskCreateRequest(BaseModel):
    """
    DTO para la creación de una nueva tarea.
    
    Este modelo define la estructura de datos necesaria para crear una tarea
    a través de la API REST, incluyendo validaciones de negocio.
    
    Attributes:
        title: Título de la tarea, no puede estar vacío.
        status: Estado de la tarea, valores permitidos: 'pending' o 'done'.
    """
    title: str = Field(..., min_length=1, description="Task title")
    status: str = Field(default="pending", description="Task status")
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        """
        Valida que el título no esté vacío.
        
        Args:
            v: Valor del título a validar.
            
        Returns:
            str: Título limpio sin espacios al inicio y final.
            
        Raises:
            ValueError: Si el título está vacío después de eliminar espacios.
        """
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('status')
    @classmethod
    def status_valid(cls, v):
        """
        Valida que el estado sea uno de los valores permitidos.
        
        Args:
            v: Valor del estado a validar.
            
        Returns:
            str: Estado validado.
            
        Raises:
            ValueError: Si el estado no es 'pending' o 'done'.
        """
        if v not in ['pending', 'done']:
            raise ValueError('Status must be either "pending" or "done"')
        return v


class TaskUpdateRequest(BaseModel):
    """
    DTO para la actualización de una tarea existente.
    
    Este modelo permite actualizar parcialmente los campos de una tarea.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    
    Attributes:
        title: Nuevo título de la tarea (opcional).
        status: Nuevo estado de la tarea (opcional).
    """
    title: Optional[str] = Field(None, min_length=1, description="Task title")
    status: Optional[str] = Field(None, description="Task status")
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        """
        Valida que el título no esté vacío si se proporciona.
        
        Args:
            v: Valor del título a validar (puede ser None).
            
        Returns:
            Optional[str]: Título limpio o None si no se proporcionó.
            
        Raises:
            ValueError: Si el título está vacío después de eliminar espacios.
        """
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else None

    @field_validator('status')
    @classmethod
    def status_valid(cls, v):
        """
        Valida que el estado sea uno de los valores permitidos si se proporciona.
        
        Args:
            v: Valor del estado a validar (puede ser None).
            
        Returns:
            Optional[str]: Estado validado o None si no se proporcionó.
            
        Raises:
            ValueError: Si el estado no es 'pending' o 'done'.
        """
        if v is not None and v not in ['pending', 'done']:
            raise ValueError('Status must be either "pending" or "done"')
        return v


class TaskResponse(BaseModel):
    """
    DTO para la respuesta de una tarea.
    
    Este modelo define la estructura de datos que se retorna al cliente
    cuando se consulta o modifica una tarea.
    
    Attributes:
        id: Identificador único de la tarea.
        title: Título de la tarea.
        status: Estado actual de la tarea.
        created_at: Fecha y hora de creación en formato ISO 8601.
        updated_at: Fecha y hora de última actualización en formato ISO 8601.
    """
    id: str
    title: str
    status: str
    created_at: str
    updated_at: str


class HealthResponse(BaseModel):
    """
    DTO para la respuesta del health check.
    
    Proporciona información sobre el estado del servicio y el tipo
    de almacenamiento utilizado.
    
    Attributes:
        status: Estado del servicio (ej: 'healthy').
        service: Nombre del servicio.
        storage: Tipo de almacenamiento utilizado ('Memory' o 'SQLite').
    """
    status: str
    service: str
    storage: str


# Configuración de la aplicación FastAPI
app = FastAPI(
    title="Task Management API",
    description="API REST para gestión de tareas con arquitectura hexagonal",
    version="1.0.0"
)

# Dependency Injection - Patrón Factory
# Permite cambiar entre memoria y SQLite con variable de entorno
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

if USE_SQLITE:
    task_repository = SQLiteTaskRepository("tasks.db")
    storage_type = "SQLite"
else:
    task_repository = MemoryTaskRepository()
    storage_type = "Memory"

task_service = TaskService(task_repository)

# Endpoints de la API REST
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Endpoint de verificación de estado del servicio.
    
    Permite comprobar que el servicio está activo y funcionando correctamente.
    Útil para monitoreo y balanceadores de carga.
    
    Returns:
        HealthResponse: Objeto con el estado del servicio, nombre y tipo de almacenamiento.
        
    Example:
        GET /health
        Response: {
            "status": "healthy",
            "service": "Task Management API",
            "storage": "Memory"
        }
    """
    return HealthResponse(
        status="healthy",
        service="Task Management API",
        storage=storage_type
    )

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"]
)
def create_task(request: TaskCreateRequest):
    """
    Endpoint para crear una nueva tarea.
    
    Crea una nueva tarea en el sistema con el título y estado proporcionados.
    El ID y las fechas de creación/actualización se generan automáticamente.
    
    Args:
        request: Datos de la tarea a crear (título y estado).
        
    Returns:
        TaskResponse: La tarea creada con todos sus campos.
        
    Raises:
        HTTPException 400: Si los datos proporcionados no son válidos.
        
    Example:
        POST /tasks
        Body: {
            "title": "Completar documentación",
            "status": "pending"
        }
        Response (201): {
            "id": "uuid-generado",
            "title": "Completar documentación",
            "status": "pending",
            "created_at": "2025-10-29T10:30:00",
            "updated_at": "2025-10-29T10:30:00"
        }
    """
    try:
        task = task_service.create_task(
            title=request.title,
            status=request.status
        )
        return TaskResponse(**task.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
def get_all_tasks():
    """
    Endpoint para obtener todas las tareas.
    
    Retorna una lista completa de todas las tareas almacenadas en el sistema,
    sin paginación.
    
    Returns:
        List[TaskResponse]: Lista de todas las tareas existentes.
        
    Example:
        GET /tasks
        Response (200): [
            {
                "id": "uuid-1",
                "title": "Tarea 1",
                "status": "pending",
                "created_at": "2025-10-29T10:30:00",
                "updated_at": "2025-10-29T10:30:00"
            },
            {
                "id": "uuid-2",
                "title": "Tarea 2",
                "status": "done",
                "created_at": "2025-10-29T11:00:00",
                "updated_at": "2025-10-29T11:15:00"
            }
        ]
    """
    tasks = task_service.get_all_tasks()
    return [TaskResponse(**task.to_dict()) for task in tasks]


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def get_task(task_id: str):
    """
    Endpoint para obtener una tarea específica por su ID.
    
    Busca y retorna los detalles de una tarea identificada por su ID único.
    
    Args:
        task_id: Identificador único de la tarea a buscar.
        
    Returns:
        TaskResponse: Los datos completos de la tarea encontrada.
        
    Raises:
        HTTPException 404: Si no existe una tarea con el ID especificado.
        
    Example:
        GET /tasks/uuid-123
        Response (200): {
            "id": "uuid-123",
            "title": "Mi tarea",
            "status": "pending",
            "created_at": "2025-10-29T10:30:00",
            "updated_at": "2025-10-29T10:30:00"
        }
    """
    task = task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    return TaskResponse(**task.to_dict())


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def update_task(task_id: str, request: TaskUpdateRequest):
    """
    Endpoint para actualizar una tarea existente.
    
    Permite actualizar el título y/o estado de una tarea existente.
    Solo se actualizan los campos proporcionados (actualización parcial).
    
    Args:
        task_id: Identificador único de la tarea a actualizar.
        request: Datos a actualizar (título y/o estado). Ambos campos son opcionales.
        
    Returns:
        TaskResponse: La tarea actualizada con todos sus campos.
        
    Raises:
        HTTPException 404: Si no existe una tarea con el ID especificado.
        HTTPException 400: Si los datos proporcionados no son válidos.
        
    Example:
        PUT /tasks/uuid-123
        Body: {
            "status": "done"
        }
        Response (200): {
            "id": "uuid-123",
            "title": "Mi tarea",
            "status": "done",
            "created_at": "2025-10-29T10:30:00",
            "updated_at": "2025-10-29T14:00:00"
        }
    """
    try:
        task = task_service.update_task(
            task_id=task_id,
            title=request.title,
            status=request.status
        )
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        
        return TaskResponse(**task.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(task_id: str):
    """
    Endpoint para eliminar una tarea.
    
    Elimina permanentemente una tarea del sistema identificada por su ID.
    No retorna contenido en caso de éxito (204 No Content).
    
    Args:
        task_id: Identificador único de la tarea a eliminar.
        
    Returns:
        None: No retorna contenido si la eliminación es exitosa.
        
    Raises:
        HTTPException 404: Si no existe una tarea con el ID especificado.
        
    Example:
        DELETE /tasks/uuid-123
        Response (204): Sin contenido
    """
    deleted = task_service.delete_task(task_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )