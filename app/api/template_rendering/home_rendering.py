from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.api.dependencies import templates, CookieCurrentUserDep
from app.api.template_rendering.utils import redirect

router = APIRouter()


@router.get("/", response_class=HTMLResponse, status_code=200)
async def render_home_page(request: Request, user: CookieCurrentUserDep):
    if user:
        return redirect("/todos/todos-page", 307)
    return templates.TemplateResponse(request=request, name="home.html")
