from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.api.dependencies import templates, SessionDep, get_current_user
from app.api.template_rendering.utils import redirect

router = APIRouter()


@router.get("/", response_class=HTMLResponse, status_code=200)
async def render_home_page(request: Request, db: SessionDep):
    try:
        user = await get_current_user(token=request.cookies.get("access_token"), db=db)
        if user:
            return redirect("/todos/todos-page", 307)
    except HTTPException:
        return templates.TemplateResponse(request=request, name="home.html")
