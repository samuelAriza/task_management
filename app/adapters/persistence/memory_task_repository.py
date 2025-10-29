"""
Módulo de implementación del repositorio de tareas en memoria.

Este módulo proporciona una implementación concreta del repositorio de tareas
utilizando un diccionario en memoria como mecanismo de almacenamiento.
Implementa el patrón Repository y cumple con el principio Open/Closed (OCP).
"""

from typing import Dict, List, Optional
from app.domain.task import Task
from app.application.ports.task_repository import ITaskRepository

# Implementación en memoria del repositorio de tareas (OCP)
class MemoryTaskRepository(ITaskRepository):
    """
    Repositorio de tareas con almacenamiento en memoria.
    
    Esta clase implementa la interfaz ITaskRepository usando un diccionario
    Python como mecanismo de almacenamiento temporal. Los datos se pierden
    cuando la aplicación se reinicia.
    
    Cumple con el principio Open/Closed (OCP) al implementar la interfaz
    del puerto sin modificar el código del dominio.
    
    Attributes:
        _tasks: Diccionario privado que almacena las tareas indexadas por ID.
    """
    
    def __init__(self):
        """
        Inicializa el repositorio con un diccionario vacío.
        
        Crea una nueva instancia del repositorio en memoria sin tareas.
        """
        self._tasks: Dict[str, Task] = {}
    
    def save(self, task: Task) -> Task:
        """
        Guarda una tarea en el repositorio.
        
        Almacena o actualiza una tarea en el diccionario interno usando
        su ID como clave. Si ya existe una tarea con el mismo ID,
        será sobrescrita.
        
        Args:
            task: La instancia de Task a guardar.
            
        Returns:
            Task: La misma tarea que fue guardada.
        """
        self._tasks[task.id] = task
        return task
    
    def find_all(self) -> List[Task]:
        """
        Obtiene todas las tareas del repositorio.
        
        Retorna una lista de todas las tareas almacenadas, ordenadas
        por fecha de creación en orden descendente (más recientes primero).
        
        Returns:
            List[Task]: Lista de todas las tareas ordenadas por fecha de creación
                       (de más reciente a más antigua).
        """
        return sorted(
            list(self._tasks.values()),
            key=lambda t: t.created_at,
            reverse=True
        )
    
    def find_by_id(self, task_id: str) -> Optional[Task]:
        """
        Busca una tarea por su identificador único.
        
        Args:
            task_id: El identificador único de la tarea a buscar.
            
        Returns:
            Optional[Task]: La tarea encontrada o None si no existe una tarea
                           con el ID especificado.
        """
        return self._tasks.get(task_id)
    
    def update(self, task: Task) -> Optional[Task]:
        """
        Actualiza una tarea existente en el repositorio.
        
        Actualiza los datos de una tarea si existe en el repositorio.
        Si la tarea no existe, no se realiza ninguna acción.
        
        Args:
            task: La instancia de Task con los datos actualizados.
                 Debe tener un ID que corresponda a una tarea existente.
            
        Returns:
            Optional[Task]: La tarea actualizada si existía previamente,
                           None si no se encontró la tarea en el repositorio.
        """
        if task.id not in self._tasks:
            return None
        self._tasks[task.id] = task
        return task
    
    def delete(self, task_id: str) -> bool:
        """
        Elimina una tarea del repositorio.
        
        Elimina permanentemente una tarea del diccionario interno si existe.
        
        Args:
            task_id: El identificador único de la tarea a eliminar.
            
        Returns:
            bool: True si la tarea fue encontrada y eliminada exitosamente,
                 False si no existía una tarea con el ID especificado.
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False