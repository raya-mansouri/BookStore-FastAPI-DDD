from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from functools import wraps
from jose import jwt
from jose.exceptions import JWTError
from app.settings import settings
from app.user.domain.entities import TokenData


SECRET_KEY =  settings.SECRET_KEY
ALGORITHM =  settings.ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(id=payload.get("id"), username=payload.get("sub"), role=payload.get("role"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

def permission_required(allowed_roles=None, allow_current_user=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            token = token.split(" ")[1]
            token_data = decode_token(token)

            if not token_data:
                raise HTTPException(status_code=401, detail="Invalid token")

            if allow_current_user:
                request.state.user_id = token_data.id

            if allowed_roles and token_data.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

