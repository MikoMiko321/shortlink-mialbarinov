from fastapi import APIRouter

from app.cache.redis import redis_client

admin_router = APIRouter(prefix="/admin")


@admin_router.post("/redis/flush")
def flush_redis():
    redis_client.flushall()
    return {"status": "redis cleared"}
