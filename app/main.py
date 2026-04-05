from fastapi import FastAPI

from app.routes.calendar import router as calendar_router
from app.routes.health import router as health_router
from app.routes.jobs import router as jobs_router
from app.routes.tasks import router as tasks_router


def create_app() -> FastAPI:
    app = FastAPI(title="Personal Operating System", version="0.1.0")
    app.include_router(health_router)
    app.include_router(jobs_router)
    app.include_router(tasks_router)
    app.include_router(calendar_router)
    return app


app = create_app()

