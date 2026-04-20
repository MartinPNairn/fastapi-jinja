from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.api.dependencies import templates, CookieCurrentUserDep, SessionDep
from app.crud import get_all_entries, get_entry
from app.models import Todo
from app.api.template_rendering.utils import redirect

router = APIRouter()


@router.get("/todos-page", response_class=HTMLResponse)
async def render_todo_page(
    request: Request,
    db: SessionDep,
    user: CookieCurrentUserDep,
):
    if not user:
        return redirect("/auth/login-page", 307)

    todos = get_all_entries(Todo, db, Todo.owner_id == user.id)
    return templates.TemplateResponse(
        request=request,
        name="todo.html",
        context={"user": user, "todos": todos},
    )


@router.get("/add-todo-page", response_class=HTMLResponse)
async def render_add_todo_page(
    request: Request,
    user: CookieCurrentUserDep,
):
    if not user:
        return redirect("/auth/login-page", 307)

    return templates.TemplateResponse(
        request=request,
        name="add-todo.html",
        context={"user": user},
    )


@router.get("/edit-todo-page/{todo_id}", response_class=HTMLResponse)
async def render_edit_todo_page(
    request: Request,
    db: SessionDep,
    todo_id: int,
    user: CookieCurrentUserDep,
):
    if not user:
        return redirect("/auth/login-page", 307)

    todo = get_entry(Todo, db, id=todo_id)
    return templates.TemplateResponse(
        request=request,
        name="edit-todo.html",
        context={"todo": todo},
    )
