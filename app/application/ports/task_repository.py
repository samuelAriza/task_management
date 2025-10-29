"""
Módulo de interfaz del repositorio de tareas.

Este módulo define el puerto (interface) del repositorio de tareas siguiendo
el patrón Ports and Adapters (Arquitectura Hexagonal). Define el contrato
que deben implementar todos los adaptadores de persistencia de tareas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.task import Task

# Repositorio de Tareas
class ITaskRepository(ABC):
    """
    Interfaz abstracta del repositorio de tareas.
    
    Define el contrato que deben cumplir todas las implementaciones concretas
    del repositorio de tareas. Esta interfaz es un puerto en la arquitectura
    hexagonal que permite cambiar la implementación de persistencia sin
    afectar la lógica de negocio.
    
    Las implementaciones concretas pueden usar cualquier mecanismo de
    almacenamiento (memoria, SQLite, PostgreSQL, MongoDB, etc.) siempre
    que cumplan con este contrato.
    """
    
    @abstractmethod
    def save(self, task: Task) -> Task:
        """
        Guarda una nueva tarea en el repositorio.
        
        Args:
            task: La instancia de Task a guardar.
            
        Returns:
            Task: La tarea guardada.
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[Task]:
        """
        Obtiene todas las tareas del repositorio.
        
        Returns:
            List[Task]: Lista de todas las tareas almacenadas.
        """
        pass
    
    @abstractmethod
    def find_by_id(self, task_id: str) -> Optional[Task]:
        """
        Busca una tarea por su identificador único.
        
        Args:
            task_id: El identificador único de la tarea a buscar.
            
        Returns:
            Optional[Task]: La tarea encontrada o None si no existe.
        """
        pass
    
    @abstractmethod
    def update(self, task: Task) -> Optional[Task]:
        """
        Actualiza una tarea existente en el repositorio.
        
        Args:
            task: La instancia de Task con los datos actualizados.
            
        Returns:
            Optional[Task]: La tarea actualizada si existía, None si no se encontró.
        """
        pass
    
    @abstractmethod
    def delete(self, task_id: str) -> bool:
        """
        Elimina una tarea del repositorio.
        
        Args:
            task_id: El identificador único de la tarea a eliminar.
            
        Returns:
            bool: True si la tarea fue eliminada exitosamente, False si no existía.
        """
        pass