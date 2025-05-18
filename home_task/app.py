from fastapi import FastAPI
from home_task.api.endpoint import router as stats_router

app = FastAPI(
    title="Home task API",
    version="1.0.0",
)

app.include_router(stats_router)
