"""
Módulo de pruebas unitarias para el servicio de tareas (TaskService).

Este módulo verifica el correcto funcionamiento de la capa de aplicación encargada
de gestionar las operaciones CRUD sobre las tareas, utilizando un repositorio en memoria
para simular la persistencia de datos.

Las pruebas cubren la creación, obtención, actualización y eliminación de tareas,
así como el manejo de errores en casos inválidos. Se utiliza pytest para la
ejecución de las pruebas y la validación de excepciones esperadas.
"""

import pytest
from app.application.services.task_service import TaskService
from app.adapters.persistence.memory_task_repository import MemoryTaskRepository

class TestTaskService:

    @pytest.fixture
    def service(self):
        repository = MemoryTaskRepository()
        return TaskService(repository)
    
    def test_create_task(self, service):
        task = service.create_task(title="Test Task", status="pending")
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.status.value == "pending"
    
    def test_get_all_tasks_empty(self, service):
        tasks = service.get_all_tasks()
        
        assert len(tasks) == 0
    
    def test_get_all_tasks(self, service):
        service.create_task(title="Task 1")
        service.create_task(title="Task 2")
        
        tasks = service.get_all_tasks()
        
        assert len(tasks) == 2

    def test_get_task_by_id(self, service):
        created_task = service.create_task(title="Test Task")

        found_task = service.get_task_by_id(created_task.id)
        
        assert found_task is not None
        assert found_task.id == created_task.id
        assert found_task.title == "Test Task"
    
    def test_get_task_by_id_not_found(self, service):
        task = service.get_task_by_id("non-existent-id")
        
        assert task is None
    
    def test_update_task(self, service):
        created_task = service.create_task(title="Original")
        
        updated_task = service.update_task(
            task_id=created_task.id,
            title="Updated",
            status="done"
        )
        
        assert updated_task is not None
        assert updated_task.title == "Updated"
        assert updated_task.status.value == "done"
    
    def test_update_task_only_title(self, service):
        created_task = service.create_task(title="Original", status="pending")
        
        updated_task = service.update_task(
            task_id=created_task.id,
            title="Updated"
        )
        
        assert updated_task.title == "Updated"
        assert updated_task.status.value == "pending"
    
    def test_update_task_only_status(self, service):
        created_task = service.create_task(title="Test", status="pending")
        
        updated_task = service.update_task(
            task_id=created_task.id,
            status="done"
        )
        
        assert updated_task.title == "Test"
        assert updated_task.status.value == "done"
    
    def test_update_task_not_found(self, service):
        updated_task = service.update_task(
            task_id="non-existent-id",
            title="Updated"
        )
        
        assert updated_task is None
    
    def test_delete_task(self, service):
        created_task = service.create_task(title="Test")
        
        deleted = service.delete_task(created_task.id)
        
        assert deleted is True
        assert service.get_task_by_id(created_task.id) is None
    
    def test_delete_task_not_found(self, service):
        deleted = service.delete_task("non-existent-id")
        
        assert deleted is False
    
    def test_create_task_with_invalid_data_raises_error(self, service):
        with pytest.raises(ValueError):
            service.create_task(title="")
    
    def test_update_task_with_invalid_status_raises_error(self, service):
        task = service.create_task(title="Test")
        
        with pytest.raises(ValueError):
            service.update_task(task_id=task.id, status="invalid")