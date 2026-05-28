from tests.utils import get_fresh_entry_by_primary_key
from app.schemas import UserResponse, TodoResponse
from app.models import Todo


def test_get_all_users(client, test_admin):
    test_client = client(test_admin)
    response = test_client.get("/admin/users")
    assert response.status_code == 200
    assert response.json() == [UserResponse.model_validate(test_admin).model_dump()]


def test_get_all_users_not_admin(client, test_user):
    test_client = client(test_user)
    response = test_client.get("/admin/users")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}


def test_get_all_users_not_authenticated(client):
    test_client = client()
    response = test_client.get("/admin/users")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Authentication failed.'}


def test_get_all_todos(client, test_admin, test_todo):
    test_client = client(test_admin)
    response = test_client.get("/admin/todos")
    assert response.status_code == 200
    assert response.json() == [TodoResponse.model_validate(test_todo).model_dump()]


def test_get_all_todos_not_admin(client, test_user):
    test_client = client(test_user)
    response = test_client.get("/admin/todos")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}


def test_get_all_todos_not_authenticated(client):
    test_client = client()
    response = test_client.get("/admin/todos")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}


def test_delete_todo(client, test_admin, test_todo, db):
    test_client = client(test_admin)
    response = test_client.delete(f"/admin/todos/delete/{test_todo.id}")
    todo_deleted = get_fresh_entry_by_primary_key(db, Todo, test_todo.id)
    assert todo_deleted is None
    assert response.status_code == 204
    assert response.text == ""


def test_delete_todo_not_admin(client, test_user, test_todo):
    test_client = client(test_user)
    response = test_client.delete(f"/admin/todos/delete/{test_todo.id}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}


def test_delete_todo_not_authenticated(client, test_todo):
    test_client = client()
    response = test_client.delete(f"/admin/todos/delete/{test_todo.id}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}


def test_delete_todo_not_found(client, test_admin, test_todo):
    test_client = client(test_admin)
    response = test_client.delete(f"/admin/todos/delete/{test_todo.id + 999}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found."}
