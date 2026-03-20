from fastapi.responses import RedirectResponse


def redirect(url: str, status_code: int, cookie_to_delete: str | None = None):
    response = RedirectResponse(url=url, status_code=status_code)
    if cookie_to_delete:
        response.delete_cookie(cookie_to_delete)
    return response
