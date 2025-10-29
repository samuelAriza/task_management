"""
Módulo de pruebas unitarias para la entidad Task del dominio.

Este módulo valida el comportamiento de la clase Task, incluyendo la creación,
actualización y serialización de tareas. Las pruebas cubren casos válidos y de error
para asegurar la consistencia de las reglas de negocio definidas en la entidad.

Utiliza pytest para la ejecución de pruebas unitarias y la verificación de excepciones.
"""

import pytest
from datetime import datetime
from app.domain.task import Task, TaskStatus


class TestTaskEntity:
    
    def test_create_task_with_valid_data(self):
        task = Task.create(title="Test Task", status="pending")
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.status == TaskStatus.PENDING
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
    
    def test_create_task_with_default_status(self):
        task = Task.create(title="Test Task")
        
        assert task.status == TaskStatus.PENDING
    
    def test_create_task_with_empty_title_raises_error(self):
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task.create(title="")
    
    def test_create_task_with_whitespace_title_raises_error(self):
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task.create(title="   ")
    
    def test_create_task_with_invalid_status_raises_error(self):
        with pytest.raises(ValueError, match="Invalid status"):
            Task.create(title="Test", status="invalid")
    
    def test_update_status(self):
        task = Task.create(title="Test", status="pending")
        old_updated_at = task.updated_at
        
        task.update_status("done")
        
        assert task.status == TaskStatus.DONE
        assert task.updated_at > old_updated_at
    
    def test_update_status_with_invalid_status_raises_error(self):
        task = Task.create(title="Test")
        
        with pytest.raises(ValueError, match="Invalid status"):
            task.update_status("invalid")
    
    def test_update_title(self):
        task = Task.create(title="Original Title")
        old_updated_at = task.updated_at
        
        task.update_title("New Title")
        
        assert task.title == "New Title"
        assert task.updated_at > old_updated_at
    
    def test_update_title_with_empty_title_raises_error(self):
        task = Task.create(title="Test")
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            task.update_title("")
    
    def test_to_dict(self):
        task = Task.create(title="Test Task", status="done")
        task_dict = task.to_dict()
        
        assert task_dict["id"] == task.id
        assert task_dict["title"] == "Test Task"
        assert task_dict["status"] == "done"
        assert "created_at" in task_dict
        assert "updated_at" in task_dict
    
    def test_title_trimmed_on_creation(self):
        task = Task.create(title="  Test Task  ")
        
        assert task.title == "Test Task"