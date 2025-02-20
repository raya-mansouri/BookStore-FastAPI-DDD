import time
import redis.asyncio as redis
from fastapi import HTTPException


class RateLimiter:
    def __init__(self, redis_client: redis.Redis, key_prefix: str):
        """
        Initialize the rate limiter with a Redis client and a key prefix.

        :param redis_client: Redis client instance.
        :param key_prefix: Prefix to use for Redis keys to uniquely identify rate limits for each user.
        """
        self.redis = redis_client
        self.key_prefix = key_prefix

    async def is_allowed(self, user_id: int):
        """
        Check if the user has exceeded the rate limit for OTP requests.

        It checks two different time windows:
        - 2 minutes for a limit of 5 requests.
        - 1 hour for a limit of 10 requests.

        :param user_id: Unique identifier for the user whose rate limit is being checked.
        :raises HTTPException: If the user has exceeded the rate limit.
        """
        now = int(time.time())

        # Redis keys to track request counts in the last 2 minutes and 1 hour
        two_minute_key = f"{self.key_prefix}:{user_id}:2min"
        one_hour_key = f"{self.key_prefix}:{user_id}:1hour"

        # Get the number of OTP requests made by the user in the last 2 minutes and 1 hour
        two_minute_count = self.redis.get(two_minute_key) or 0
        one_hour_count = self.redis.get(one_hour_key) or 0

        # Check if the user has exceeded the 2-minute limit (5 requests)
        if int(two_minute_count) >= 5:
            raise HTTPException(
                status_code=429,
                detail="Too many OTP requests. Try again after 2 minutes.",
            )

        # Check if the user has exceeded the 1-hour limit (10 requests)
        if int(one_hour_count) >= 10:
            raise HTTPException(
                status_code=429, detail="Too many OTP requests. Try again after 1 hour."
            )

        # Increment the request count for the user in both time windows
        self.redis.incr(two_minute_key)
        self.redis.incr(one_hour_key)

        # Set time-to-live (TTL) for the keys so they expire after the specified time windows
        self.redis.expire(two_minute_key, 120)  # 2 minutes
        self.redis.expire(one_hour_key, 3600)  # 1 hour

    async def reset(self, user_id: int):
        """
        Reset the rate limit counters for the user in case of successful OTP verification.

        This is called when the user successfully logs in or verifies the OTP.

        :param user_id: Unique identifier for the user to reset the rate limit.
        """
        # Delete the keys tracking the request counts in the last 2 minutes and 1 hour
        self.redis.delete(f"{self.key_prefix}:{user_id}:2min")
        self.redis.delete(f"{self.key_prefix}:{user_id}:1hour")
