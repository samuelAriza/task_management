"""
Módulo de implementación del repositorio de tareas con SQLite.

Este módulo proporciona una implementación concreta del repositorio de tareas
utilizando SQLite como mecanismo de almacenamiento persistente.
Implementa el patrón Repository y cumple con el principio Open/Closed (OCP).
"""

import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from app.domain.task import Task, TaskStatus
from app.application.ports.task_repository import ITaskRepository

# SQLite implementation of the Task Repository (OCP)
class SQLiteTaskRepository(ITaskRepository):
    """
    Repositorio de tareas con almacenamiento persistente en SQLite.
    
    Esta clase implementa la interfaz ITaskRepository usando una base de datos
    SQLite como mecanismo de almacenamiento persistente. Los datos se mantienen
    entre reinicios de la aplicación.
    
    Cumple con el principio Open/Closed (OCP) al implementar la interfaz
    del puerto sin modificar el código del dominio.
    
    Attributes:
        db_path: Ruta del archivo de base de datos SQLite.
    """
    
    def __init__(self, db_path: str = "/app/data/tasks.db"):
        """
        Inicializa el repositorio SQLite.
        
        Crea el directorio necesario para la base de datos si no existe
        e inicializa la estructura de tablas.
        
        Args:
            db_path: Ruta completa del archivo de base de datos SQLite.
                    Por defecto: "/app/data/tasks.db".
        """
        dir_path = os.path.dirname(db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """
        Inicializa la estructura de la base de datos.
        
        Crea la tabla 'tasks' si no existe, con todos los campos necesarios
        para almacenar las tareas de manera persistente.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def _get_connection(self):
        """
        Crea una nueva conexión a la base de datos SQLite.
        
        Configura la conexión para retornar filas como objetos Row de SQLite,
        permitiendo acceso a las columnas por nombre.
        
        Returns:
            sqlite3.Connection: Conexión configurada a la base de datos.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save(self, task: Task) -> Task:
        """
        Guarda una nueva tarea en la base de datos.
        
        Inserta una tarea en la tabla 'tasks'. Si ya existe una tarea con
        el mismo ID, se lanzará una excepción de constraint.
        
        Args:
            task: La instancia de Task a guardar.
            
        Returns:
            Task: La misma tarea que fue guardada.
            
        Raises:
            sqlite3.IntegrityError: Si ya existe una tarea con el mismo ID.
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (id, title, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.title,
                    task.status.value,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat()
                )
            )
            conn.commit()
        return task
    
    def find_all(self) -> List[Task]:
        """
        Obtiene todas las tareas de la base de datos.
        
        Retorna una lista de todas las tareas almacenadas, ordenadas
        por fecha de creación en orden descendente (más recientes primero).
        
        Returns:
            List[Task]: Lista de todas las tareas ordenadas por fecha de creación
                       (de más reciente a más antigua).
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]
    
    def find_by_id(self, task_id: str) -> Optional[Task]:
        """
        Busca una tarea por su identificador único.
        
        Args:
            task_id: El identificador único de la tarea a buscar.
            
        Returns:
            Optional[Task]: La tarea encontrada o None si no existe una tarea
                           con el ID especificado en la base de datos.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task_id,)
            )
            row = cursor.fetchone()
            return self._row_to_task(row) if row else None
    
    def update(self, task: Task) -> Optional[Task]:
        """
        Actualiza una tarea existente en la base de datos.
        
        Actualiza los campos de título, estado y fecha de actualización
        de una tarea existente. Si la tarea no existe, no se realiza
        ninguna acción.
        
        Args:
            task: La instancia de Task con los datos actualizados.
                 Debe tener un ID que corresponda a una tarea existente.
            
        Returns:
            Optional[Task]: La tarea actualizada si existía previamente,
                           None si no se encontró la tarea en la base de datos.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE tasks
                SET title = ?, status = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    task.title,
                    task.status.value,
                    task.updated_at.isoformat(),
                    task.id
                )
            )
            conn.commit()
            if cursor.rowcount == 0:
                return None
            return task
    
    def delete(self, task_id: str) -> bool:
        """
        Elimina una tarea de la base de datos.
        
        Elimina permanentemente una tarea de la tabla 'tasks' si existe.
        
        Args:
            task_id: El identificador único de la tarea a eliminar.
            
        Returns:
            bool: True si la tarea fue encontrada y eliminada exitosamente,
                 False si no existía una tarea con el ID especificado.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """
        Convierte una fila de SQLite en una instancia de Task.
        
        Transforma los datos de una fila de la base de datos en un objeto
        del dominio Task, convirtiendo los tipos de datos apropiadamente.
        
        Args:
            row: Fila de SQLite con los datos de la tarea.
            
        Returns:
            Task: Instancia de Task con los datos de la fila.
        """
        return Task(
            id=row["id"],
            title=row["title"],
            status=TaskStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )