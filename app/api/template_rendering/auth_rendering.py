from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.api.dependencies import templates, SessionDep
from app.api.template_rendering.utils import redirect
from app.api.dependencies import get_current_user


router = APIRouter()


# Get login page
@router.get("/login-page", response_class=HTMLResponse)
async def render_login_page(request: Request, db: SessionDep):
    try:
        user = await get_current_user(token=request.cookies.get("access_token"), db=db)
        if user:
            return redirect("/todos/todos-page", 307)
    except HTTPException:
        return templates.TemplateResponse(request=request, name="login.html")


# Get Register page
@router.get("/register-page", response_class=HTMLResponse)
async def render_register_page(request: Request, db:SessionDep):
    try:
        user = await get_current_user(token=request.cookies.get("access_token"), db=db)
        if user:
            return redirect("/todos/todos-page", 307)
    except HTTPException:
        return templates.TemplateResponse(request=request, name="register.html")
