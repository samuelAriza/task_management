"""
Módulo de tests de integración para la API REST de tareas.

Este módulo contiene pruebas end-to-end que verifican el funcionamiento
completo de los endpoints de la API, incluyendo casos de éxito y error.
Utiliza pytest y FastAPI TestClient para simular peticiones HTTP.
"""

import os
import sqlite3
import pytest
from fastapi.testclient import TestClient
from app.adapters.http.fastapi_app import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    """
    Limpia la base de datos SQLite antes de cada test.
    """
    db_path = "/app/data/tasks.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()

class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "storage" in data


class TestTasksEndpoints:
    
    def test_get_tasks_empty(self, client):
        response = client.get("/tasks")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_task(self, client):
        response = client.post(
            "/tasks",
            json={"title": "Test Task", "status": "pending"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_task_with_default_status(self, client):
        response = client.post(
            "/tasks",
            json={"title": "Test Task"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
    
    def test_create_task_with_empty_title(self, client):
        response = client.post(
            "/tasks",
            json={"title": ""}
        )
        
        assert response.status_code == 422
    
    def test_create_task_with_invalid_status(self, client):
        response = client.post(
            "/tasks",
            json={"title": "Test", "status": "invalid"}
        )
        
        assert response.status_code == 422
    
    def test_create_task_without_title(self, client):
        response = client.post(
            "/tasks",
            json={"status": "pending"}
        )
        
        assert response.status_code == 422
    
    def test_get_task_by_id(self, client):
        create_response = client.post(
            "/tasks",
            json={"title": "Test Task"}
        )
        task_id = create_response.json()["id"]
        
        response = client.get(f"/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
    
    def test_get_task_by_id_not_found(self, client):
        response = client.get("/tasks/non-existent-id")
        
        assert response.status_code == 404
    
    def test_update_task(self, client):
        create_response = client.post(
            "/tasks",
            json={"title": "Original", "status": "pending"}
        )
        task_id = create_response.json()["id"]
        
        response = client.put(
            f"/tasks/{task_id}",
            json={"title": "Updated", "status": "done"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["status"] == "done"
    
    def test_update_task_partial(self, client):
        create_response = client.post(
            "/tasks",
            json={"title": "Test", "status": "pending"}
        )
        task_id = create_response.json()["id"]
        
        response = client.put(
            f"/tasks/{task_id}",
            json={"status": "done"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test"
        assert data["status"] == "done"
    
    def test_update_task_not_found(self, client):
        response = client.put(
            "/tasks/non-existent-id",
            json={"title": "Updated"}
        )
        
        assert response.status_code == 404
    
    def test_update_task_with_invalid_status(self, client):
        create_response = client.post(
            "/tasks",
            json={"title": "Test"}
        )
        task_id = create_response.json()["id"]
        
        response = client.put(
            f"/tasks/{task_id}",
            json={"status": "invalid"}
        )
        
        assert response.status_code == 422
    
    def test_delete_task(self, client):
        create_response = client.post(
            "/tasks",
            json={"title": "Test"}
        )
        task_id = create_response.json()["id"]
        
        response = client.delete(f"/tasks/{task_id}")
        
        assert response.status_code == 204
        
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404
    
    def test_delete_task_not_found(self, client):
        response = client.delete("/tasks/non-existent-id")
        
        assert response.status_code == 404
    
    def test_complete_workflow(self, client):
        create_response = client.post(
            "/tasks",
            json={"title": "Workflow Test", "status": "pending"}
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        
        update_response = client.put(
            f"/tasks/{task_id}",
            json={"status": "done"}
        )
        assert update_response.status_code == 200
        
        list_response = client.get("/tasks")
        assert list_response.status_code == 200
        assert len(list_response.json()) >= 1
        
        delete_response = client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == 204
        
        final_get = client.get(f"/tasks/{task_id}")
        assert final_get.status_code == 404