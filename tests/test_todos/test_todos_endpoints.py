from app.models import Todo
from tests.utils import (
    get_fresh_entry_by_primary_key,
    get_fresh_entry_with_conditions,
    entry_is_in_db,
)
from app.schemas import TodoResponse


def test_read_all_authenticated(client, test_user, test_todo):
    test_client = client(test_user)
    response = test_client.get("/todos/all")
    assert response.status_code == 200
    assert response.json() == [
        TodoResponse.model_validate(test_todo).model_dump(mode="json")
    ]


def test_read_one_authenticated(client, test_user, test_todo):
    test_client = client(test_user)
    response = test_client.get(f"/todos/todo/{test_todo.id}")
    assert response.status_code == 200
    assert response.json() == TodoResponse.model_validate(test_todo).model_dump(
        mode="json"
    )


def test_read_one_authenticated_not_found(client, test_user, test_todo):
    test_client = client(test_user)
    response = test_client.get(f"/todos/todo/{test_todo.id + 999}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_todo(client, test_user, db, valid_todo_payload):
    test_client = client(test_user)
    response = test_client.post("/todos/create", json=valid_todo_payload)
    assert response.status_code == 201
    todo = get_fresh_entry_with_conditions(
        db,
        Todo,
        Todo.title == valid_todo_payload["title"],
        Todo.owner_id == test_user.id,
    )
    assert todo is not None
    for key in valid_todo_payload.keys():
        assert getattr(todo, key) == valid_todo_payload[key]


def test_create_todo_incomplete_request(client, test_user):
    bad_request_data = {
        "priority": 1,
    }
    test_client = client(test_user)
    response = test_client.post("/todos/create", json=bad_request_data)
    assert response.status_code == 422


def test_create_todo_empty_required_values(client, test_user, valid_todo_payload):
    test_client = client(test_user)
    response = test_client.post(
        "/todos/create", json={**valid_todo_payload, "title": ""}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "string_too_short"


def test_update_todo(client, test_user, db, test_todo, valid_todo_payload):
    test_client = client(test_user)
    update_data = {**valid_todo_payload, "title": "An updated title"}
    response = test_client.put(
        f"/todos/update/{test_todo.id}",
        json=update_data,
    )
    updated_todo = get_fresh_entry_by_primary_key(db, Todo, test_todo.id)
    assert response.status_code == 204
    for key in update_data:
        assert getattr(updated_todo, key) == update_data[key]


def test_update_todo_not_found(client, test_user, test_todo, valid_todo_payload):
    test_client = client(test_user)
    response = test_client.put(
        f"/todos/update/{test_todo.id + 999}", json=valid_todo_payload
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_todo_wrong_user(client, test_user, db, test_todo, valid_todo_payload):
    test_todo.owner_id = test_user.id + 999
    db.commit()
    test_client = client(test_user)
    response = test_client.put(f"/todos/update/{test_todo.id}", json=valid_todo_payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_todo(client, test_user, db, test_todo):
    test_client = client(test_user)
    response = test_client.delete(f"/todos/delete/{test_todo.id}")
    assert response.status_code == 204
    assert not entry_is_in_db(db, Todo, test_todo.id)


def test_delete_todo_not_found(client, test_user, test_todo):
    test_client = client(test_user)
    response = test_client.delete(f"/todos/delete/{test_todo.id + 999}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
