"""
Módulo de servicio de aplicación para gestión de tareas.

Este módulo implementa la capa de aplicación que orquesta la lógica de negocio
de las tareas. Actúa como intermediario entre la capa de presentación (API)
y la capa de dominio/persistencia, aplicando casos de uso de la aplicación.
"""

from typing import List, Optional
from app.domain.task import Task
from app.application.ports.task_repository import ITaskRepository

class TaskService:
    """
    Servicio de aplicación para la gestión de tareas.
    
    Esta clase implementa los casos de uso de la aplicación relacionados
    con tareas, coordinando las operaciones entre el dominio y el repositorio.
    Sigue el patrón de Servicios de Aplicación en arquitectura hexagonal.
    
    El servicio depende de la abstracción ITaskRepository (inyección de
    dependencias) lo que permite desacoplar la lógica de negocio del
    mecanismo de persistencia específico.
    
    Attributes:
        _repository: Implementación del repositorio de tareas inyectada.
    """
    
    def __init__(self, repository: ITaskRepository):
        """
        Inicializa el servicio de tareas.
        
        Args:
            repository: Implementación concreta de ITaskRepository que se
                       utilizará para las operaciones de persistencia.
        """
        self._repository = repository
    
    def create_task(self, title: str, status: str = "pending") -> Task:
        """
        Crea una nueva tarea en el sistema.
        
        Utiliza el método factory del dominio para crear la tarea con
        valores por defecto apropiados y la persiste en el repositorio.
        
        Args:
            title: Título de la nueva tarea.
            status: Estado inicial de la tarea. Por defecto "pending".
            
        Returns:
            Task: La tarea creada y guardada con su ID generado.
            
        Raises:
            ValueError: Si el título está vacío o el status no es válido.
        """
        task = Task.create(title=title, status=status)
        return self._repository.save(task)
    
    def get_all_tasks(self) -> List[Task]:
        """
        Obtiene todas las tareas del sistema.
        
        Returns:
            List[Task]: Lista de todas las tareas existentes.
        """
        return self._repository.find_all()
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Busca una tarea específica por su identificador.
        
        Args:
            task_id: Identificador único de la tarea a buscar.
            
        Returns:
            Optional[Task]: La tarea encontrada o None si no existe.
        """
        return self._repository.find_by_id(task_id)
    
    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[Task]:
        """
        Actualiza una tarea existente.
        
        Permite actualizar el título y/o estado de una tarea de forma parcial.
        Solo se modifican los campos que se proporcionan (no None).
        Las reglas de negocio del dominio se aplican automáticamente.
        
        Args:
            task_id: Identificador único de la tarea a actualizar.
            title: Nuevo título de la tarea (opcional).
            status: Nuevo estado de la tarea (opcional).
            
        Returns:
            Optional[Task]: La tarea actualizada si existía, None si no se encontró.
            
        Raises:
            ValueError: Si los valores proporcionados no cumplen las reglas del dominio.
        """
        
        task = self._repository.find_by_id(task_id)
        
        if not task:
            return None
        
        if title is not None:
            task.update_title(title)
        
        if status is not None:
            task.update_status(status)
        
        return self._repository.update(task)
    
    def delete_task(self, task_id: str) -> bool:
        """
        Elimina una tarea del sistema.
        
        Args:
            task_id: Identificador único de la tarea a eliminar.
            
        Returns:
            bool: True si la tarea fue eliminada exitosamente,
                 False si no existía una tarea con el ID especificado.
        """
        return self._repository.delete(task_id)