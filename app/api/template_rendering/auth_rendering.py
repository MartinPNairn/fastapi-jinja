from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.api.dependencies import templates, CookieCurrentUserDep
from app.api.template_rendering.utils import redirect


router = APIRouter()


# Get login page
@router.get("/login-page", response_class=HTMLResponse)
async def render_login_page(request: Request, user: CookieCurrentUserDep):
    if user:
        return redirect("/todos/todos-page", 307)
    return templates.TemplateResponse(request=request, name="login.html")


# Get Register page
@router.get("/register-page", response_class=HTMLResponse)
async def render_register_page(request: Request, user: CookieCurrentUserDep):
    if user:
        return redirect("/todos/todos-page", 307)
    return templates.TemplateResponse(request=request, name="register.html")
