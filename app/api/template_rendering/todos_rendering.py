from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.api.dependencies import templates, get_current_user, SessionDep
from app.crud import get_all_entries, get_entry
from app.models import Todo
from app.api.template_rendering.utils import redirect

router = APIRouter()


@router.get("/todos-page", response_class=HTMLResponse)
async def render_todo_page(request: Request, db: SessionDep):
    try:
        user = await get_current_user(token=request.cookies.get("access_token"), db=db)
        if not user:
            return redirect("/auth/login-page", 307, "access_token")
        todos = get_all_entries(Todo, db, Todo.owner_id == user.id)
        return templates.TemplateResponse(
            request=request,
            name="todo.html",
            context={"user": user, "todos": todos})
    except HTTPException:
        return redirect("/auth/login-page", 307, "access_token")


@router.get("/add-todo-page", response_class=HTMLResponse)
async def render_add_todo_page(request: Request, db: SessionDep):
    try:
        user = await get_current_user(token=request.cookies.get("access_token"), db=db)
        if not user:
            return redirect("/auth/login-page", 307, "access_token")

        return templates.TemplateResponse(request=request, name="add-todo.html", context={"user": user})

    except HTTPException:
        return redirect("/auth/login-page", 307, "access_token")


@router.get("/edit-todo-page/{todo_id}", response_class=HTMLResponse)
async def render_edit_todo_page(request: Request, db: SessionDep, todo_id: int):
    try:
        user = await get_current_user(token=request.cookies.get("access_token"), db=db)
        if not user:
            return redirect("/auth/login-page", 307, "access_token")

        todo = get_entry(Todo, db, id=todo_id)
        return templates.TemplateResponse(request=request, name="edit-todo.html", context={"todo": todo})

    except HTTPException:
        return redirect("/auth/login-page", 307, "access_token")

