import time
import redis.asyncio as redis
from fastapi import HTTPException


class RateLimiter:
    def __init__(self, redis_client: redis.Redis, key_prefix: str):
        self.redis = redis_client
        self.key_prefix = key_prefix

    async def is_allowed(self, user_id: int):
        now = int(time.time())

        two_minute_key = f"{self.key_prefix}:{user_id}:2min"
        one_hour_key = f"{self.key_prefix}:{user_id}:1hour"

        # get number of previous requests
        two_minute_count = self.redis.get(two_minute_key) or 0
        one_hour_count = self.redis.get(one_hour_key) or 0

        if int(two_minute_count) >= 5:
            raise HTTPException(
                status_code=429,
                detail="Too many OTP requests. Try again after 2 minutes.",
            )

        if int(one_hour_count) >= 10:
            raise HTTPException(
                status_code=429, detail="Too many OTP requests. Try again after 1 hour."
            )

        # increase counter
        self.redis.incr(two_minute_key)
        self.redis.incr(one_hour_key)

        # set TTL for limits
        self.redis.expire(two_minute_key, 120)  # 2 min
        self.redis.expire(one_hour_key, 3600)  # 1 hour

    async def reset(self, user_id: int):
        """reset in case of successful login"""
        self.redis.delete(f"{self.key_prefix}:{user_id}:2min")
        self.redis.delete(f"{self.key_prefix}:{user_id}:1hour")
