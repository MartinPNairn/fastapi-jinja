from app.models import Todo
from app.crud import get_entry
from app.schemas import TodoResponse, TodoRequest


def test_read_all_authenticated(client, test_user, test_todo):
    test_client = client(test_user)
    response = test_client.get("/todos/all")
    assert response.status_code == 200
    assert response.json() == [TodoResponse.model_validate(test_todo).model_dump()]


def test_read_one_authenticated(client, test_user, test_todo):
    test_client = client(test_user)
    response = test_client.get("/todos/todo/1")
    assert response.status_code == 200
    assert response.json() == TodoResponse.model_validate(test_todo).model_dump()


def test_read_one_authenticated_not_found(client, test_user, test_todo):
    test_client = client(test_user)
    response = test_client.get("/todos/todo/111")
    assert response.status_code == 404
    assert response.json() == {'detail': 'To-Do not found.'}


def test_create_todo(client, test_user, db):
    test_client = client(test_user)
    request_data = {
        'title': 'A new todo',
        'description': 'This is a todo',
        'priority': 1,
        'complete': False
    }
    response = test_client.post("/todos/create", json=request_data)
    assert response.status_code == 201

    todo = get_entry(Todo, db, (Todo.title == request_data["title"]))
    assert todo is not None

    assert todo.title == request_data["title"]
    assert todo.description == request_data["description"]
    assert todo.priority == request_data["priority"]
    assert todo.complete == request_data["complete"]


def test_create_todo_incomplete_request(client, test_user, db):
    bad_request_data = {
        "priority": 1,
    }
    test_client = client(test_user)
    response = test_client.post("/todos/create", json=bad_request_data)
    assert response.status_code == 422


def test_create_todo_empy_required_values(client, test_user, db):
    bad_request_data = {
        "title": "",
        "description": "A description",
        "priority": 1,
        "complete": False
    }
    test_client = client(test_user)
    response = test_client.post("/todos/create", json=bad_request_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at least 3 characters"


def test_update_todo(client, test_user, db, test_todo):
    request_data = TodoRequest(
        title="A todo being updated",
        description="This is a todo that has been updated",
        priority=2,
        complete=True,
    )
    test_client = client(test_user)
    response = test_client.put(f"/todos/update/{test_todo.id}", json=request_data.model_dump())
    updated_todo = get_entry(Todo, db, id=1)
    assert response.status_code == 204

    for attr, value in request_data.model_dump().items():
        assert getattr(updated_todo, attr) == getattr(request_data, attr)


def test_update_todo_not_found(client, test_user, db):
    request_data = TodoRequest(
        title="A todo that is not in db",
        description="This is a todo that won't be found",
        priority=2,
        complete=False,
    )
    test_client = client(test_user)
    response = test_client.put("/todos/update/111", json=request_data.model_dump())
    assert response.status_code == 404
    assert response.json() == {'detail': 'To-Do to update not found. Rolling back.'}


def test_update_todo_wrong_user(client, test_user, db, test_todo):
    test_todo.owner_id = 2
    db.commit()

    request_data = TodoRequest(
        title="A todo being updated but failing",
        description="This is a todo that has not been updated",
        priority=2,
        complete=False,
    )
    test_client = client(test_user)
    response = test_client.put(f"/todos/update/{test_todo.id}", json=request_data.model_dump())
    assert response.status_code == 403
    assert response.json() == {'detail': 'To-Do to update not linked to current user.'}
    assert test_todo.owner_id != test_user.id


def test_delete_todo(client, test_user, db, test_todo):
    test_client = client(test_user)
    response = test_client.delete(f"/todos/delete/{test_todo.id}")
    todo_exists = get_entry(Todo, db, id=test_todo.id)
    assert todo_exists is None
    assert response.status_code == 204


def test_delete_todo_not_found(client, test_user, db):
    unreal_id = 111
    test_client = client(test_user)
    response = test_client.delete(f"/todos/delete/{unreal_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "To-Do to delete not found. Rolling back."}
