from fastapi import APIRouter
from .system import health
from .v1 import todos, auth, admin, users
from .template_rendering import home_rendering, auth_rendering, todos_rendering

router_aggregator = APIRouter()

# API
router_aggregator.include_router(health.router, tags=["health_check"])
router_aggregator.include_router(todos.router, prefix="/todos", tags=["todos"])
router_aggregator.include_router(auth.router, prefix="/auth", tags=["auth"])
router_aggregator.include_router(admin.router, prefix="/admin", tags=["admin"])
router_aggregator.include_router(users.router, prefix="/users", tags=["users"])


# TEMPLATE RENDERING
router_aggregator.include_router(home_rendering.router, tags=["templates"])
router_aggregator.include_router(auth_rendering.router, prefix="/auth", tags=["templates"])
router_aggregator.include_router(todos_rendering.router, prefix="/todos", tags=["templates"])
