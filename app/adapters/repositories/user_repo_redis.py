from typing import Optional
import secrets, redis
from app.settings import settings


class AuthRepositoryRedis:
    def __init__(self):
        """
        Initializes the Redis connection for OTP storage and retrieval.

        Redis connection details are loaded from the application settings.
        """
        self.redis = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB0
        )

    async def generate_otp(self, user_id: int) -> str:
        """
        Generates a one-time password (OTP) for the given user ID and stores it in Redis.

        :param user_id: The user ID for which to generate the OTP.
        :return: The generated OTP code as a 6-digit string.
        """
        otp = secrets.randbelow(
            999999
        )  # Generates a random integer between 0 and 999999
        otp_code = f"{otp:06d}"  # Formats the OTP as a 6-digit string, e.g. 000123
        self.redis.set(
            otp_code, user_id, ex=300
        )  # Store the OTP in Redis with an expiration time of 300 seconds (5 minutes)
        return otp_code

    async def verify_otp(self, otp: str) -> Optional[str]:
        """
        Verifies if the provided OTP exists in Redis and returns the associated user ID.

        :param otp: The OTP to verify.
        :return: The associated user ID if the OTP is valid, None if invalid or expired.
        """
        user_id = self.redis.get(
            otp
        )  # Get the user ID associated with the OTP from Redis
        if not user_id:
            return None  # Return None if the OTP doesn't exist or has expired
        return user_id  # Return the user ID associated with the OTP
