import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.gateways import auth_router, chat_router, users_router

# Import models so they are registered on Base.metadata before create_all.
from app.repositories import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No Alembic for this MVP: create the schema on startup (SQLite).
    Base.metadata.create_all(bind=engine)
    yield


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("api.perf")

app = FastAPI(title="Comé que Tá API", debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # Allow any localhost/127.0.0.1 port in development (Vite may pick 5173,
    # 5174, 5175, ... when a port is already in use).
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request_performance(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(chat_router.router)
app.include_router(chat_router.ws_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
