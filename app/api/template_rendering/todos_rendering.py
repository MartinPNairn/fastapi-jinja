from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.api.dependencies import templates, CookieCurrentUserDep, TodoReadServiceDep

from app.api.template_rendering.utils import redirect

router = APIRouter()


@router.get("/todos-page", response_class=HTMLResponse)
async def render_todo_page(
    request: Request,
    user: CookieCurrentUserDep,
    todo_service: TodoReadServiceDep,
):
    if not user:
        return redirect("/auth/login-page", 307)

    todos = todo_service.get_all_for_owner(user)
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
    todo_id: int,
    user: CookieCurrentUserDep,
    todo_service: TodoReadServiceDep,
):
    if not user:
        return redirect("/auth/login-page", 307)

    todo = todo_service.get_by_id(todo_id, user)
    return templates.TemplateResponse(
        request=request,
        name="edit-todo.html",
        context={"todo": todo},
    )
