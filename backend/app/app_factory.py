import sentry_sdk
from fastapi import FastAPI, Request
from scalar_fastapi import get_scalar_api_reference
from fastapi.responses import ORJSONResponse
from apps.info.router import router as info_router
from apps.auth.router import router as auth_router
from apps.users.router import router as users_router
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from apps.services.redis_service import redis_service
from settings import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    send_default_pii=True,
)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = redis_service.redis
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await redis.close()
    await redis.connection_pool.disconnect()


def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        root_path="/api",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    app.include_router(auth_router)
    app.include_router(users_router)

    if settings.DEBUG:
        app.include_router(info_router)

    @app.get("/scalar", include_in_schema=False)
    async def scalar_html(request: Request):
        return get_scalar_api_reference(
            openapi_url=request.scope.get("root_path", "") + app.openapi_url,
            title=app.title,
        )

    return app
