from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from sqladmin import Admin
import sentry_sdk

from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.database.database import engine

from app.admin.auth import authentication_backend
from app.logger import logger
from app.routers.bookings_router import router as router_bookings
from app.routers.hotels_router import router as router_hotels
from app.routers.rooms_router import router_hotels
from app.routers.users_router import router as router_users
from app.routers.pages_router import router as router_pages
from app.routers.images_router import router as router_images

from app.config.config import settings


sentry_sdk.init(
    dsn="https://1e3d2cf14710302f3d7f7931dd27eb09@o4508729773785088.ingest.de.sentry.io/4508729779486800",
    traces_sample_rate=1.0,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}", decode_responses=True, encoding="utf-8"
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)

app.include_router(router_pages)
app.include_router(router_images)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
    ],
)

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        "Request hadling time",
        extra={
            "process_time": round(process_time, 4),
        },
    )
    return response
