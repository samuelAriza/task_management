"""
Módulo del dominio de tareas.

Este módulo contiene las entidades y objetos de valor del dominio de tareas,
implementando la lógica de negocio central de la aplicación. Es el núcleo
de la arquitectura hexagonal, independiente de frameworks y tecnologías.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class TaskStatus(str, Enum):
    """
    Enumeración de los estados posibles de una tarea.
    
    Define los valores permitidos para el estado de una tarea,
    garantizando type-safety y evitando valores inválidos.
    
    Attributes:
        PENDING: Estado de tarea pendiente por completar.
        DONE: Estado de tarea completada.
    """
    PENDING = "pending"
    DONE = "done"

@dataclass
class Task:
    """
    Entidad del dominio que representa una tarea.
    
    Esta clase es la entidad principal del dominio, conteniendo la lógica
    de negocio relacionada con tareas. Encapsula las reglas de validación
    y comportamiento de las tareas siguiendo principios de Domain-Driven Design.
    
    Las tareas son entidades identificadas por su ID único y tienen
    invariantes que deben mantenerse (título no vacío, estado válido).
    
    Attributes:
        id: Identificador único de la tarea (UUID).
        title: Título descriptivo de la tarea (no puede estar vacío).
        status: Estado actual de la tarea (pending o done).
        created_at: Fecha y hora de creación de la tarea (UTC).
        updated_at: Fecha y hora de última actualización (UTC).
    """
    id: str
    title: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(title: str, status: str = "pending") -> "Task":
        """
        Factory method para crear una nueva tarea.
        
        Crea una instancia de Task con valores por defecto apropiados,
        generando automáticamente el ID único y las fechas de creación.
        Aplica validaciones de negocio antes de crear la instancia.
        
        Args:
            title: Título de la nueva tarea.
            status: Estado inicial de la tarea. Por defecto "pending".
            
        Returns:
            Task: Nueva instancia de Task con ID y fechas generadas.
            
        Raises:
            ValueError: Si el título está vacío o el status no es válido.
            
        Example:
            >>> task = Task.create("Completar documentación")
            >>> task.status
            <TaskStatus.PENDING: 'pending'>
        """
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        
        if status not in [s.value for s in TaskStatus]:
            raise ValueError(f"Invalid status, must be one of: {', '.join([s.value for s in TaskStatus])}")
        
        now = datetime.now(timezone.utc)
        
        return Task(
            id=str(uuid.uuid4()),
            title=title.strip(),
            status=TaskStatus(status),
            created_at=now,
            updated_at=now
        )
    
    def update_status(self, new_status: str) -> None:
        """
        Actualiza el estado de la tarea.
        
        Cambia el estado de la tarea a un nuevo valor válido y actualiza
        automáticamente la fecha de última modificación.
        
        Args:
            new_status: Nuevo estado de la tarea ("pending" o "done").
            
        Raises:
            ValueError: Si el nuevo estado no es uno de los valores permitidos.
            
        Example:
            >>> task.update_status("done")
            >>> task.status
            <TaskStatus.DONE: 'done'>
        """
        if new_status not in [s.value for s in TaskStatus]:
            raise ValueError(f"Invalid status. Must be one of: {', '.join([s.value for s in TaskStatus])}")
        
        self.status = TaskStatus(new_status)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_title(self, new_title: str) -> None:
        """
        Actualiza el título de la tarea.
        
        Cambia el título de la tarea validando que no esté vacío y
        actualiza automáticamente la fecha de última modificación.
        
        Args:
            new_title: Nuevo título para la tarea.
            
        Raises:
            ValueError: Si el nuevo título está vacío o contiene solo espacios.
            
        Example:
            >>> task.update_title("Documentación actualizada")
            >>> task.title
            'Documentación actualizada'
        """
        if not new_title or not new_title.strip():
            raise ValueError("Title cannot be empty")

        self.title = new_title.strip()
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        """
        Convierte la tarea a un diccionario serializable.
        
        Transforma la entidad Task en un diccionario Python con todos
        sus campos en formato serializable (strings), útil para persistencia
        y serialización JSON.
        
        Returns:
            dict: Diccionario con todos los campos de la tarea.
                 Las fechas están en formato ISO 8601 y el status como string.
            
        Example:
            >>> task.to_dict()
            {
                'id': 'uuid-123',
                'title': 'Mi tarea',
                'status': 'pending',
                'created_at': '2025-10-29T10:30:00+00:00',
                'updated_at': '2025-10-29T10:30:00+00:00'
            }
        """
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }