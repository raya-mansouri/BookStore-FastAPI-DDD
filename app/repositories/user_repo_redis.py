from typing import Optional
import secrets, redis
from app.settings import settings


class AuthRepositoryRedis:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            db=settings.REDIS_DB
        )

    async def generate_otp(self, user_id: int) -> str:
        otp = secrets.randbelow(999999)
        otp_code = f"{otp:06d}"
        self.redis.set(otp_code, user_id, ex=300)
        return otp_code

    async def verify_otp(self, otp: str) -> Optional[str]:
        user_id = self.redis.get(otp)
        if not user_id:
            return None
        return user_id
