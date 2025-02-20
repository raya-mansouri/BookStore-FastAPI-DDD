from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from functools import wraps
from jose import jwt
from jose.exceptions import JWTError
from app.settings import settings
from app.user.domain.entities import TokenData

# Get the secret key and algorithm from the settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# OAuth2PasswordBearer is used to extract the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Function to decode the JWT token and return the associated data
def decode_token(token: str):
    try:
        # Decode the token using the SECRET_KEY and ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Return the TokenData object with the necessary information
        return TokenData(
            id=payload.get("id"), username=payload.get("sub"), role=payload.get("role")
        )
    except JWTError:
        # If decoding fails, raise an unauthorized exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


# Permission check decorator that verifies the user's role or if they are the current user
def permission_required(allowed_roles=None, allow_current_user=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Retrieve the token from the Authorization header
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                # If the token is missing or not in the correct format, raise an authentication error
                raise HTTPException(status_code=401, detail="Not authenticated")

            # Extract the actual token from the header
            token = token.split(" ")[1]
            # Decode the token to get user information
            token_data = decode_token(token)

            if not token_data:
                # If the token data is invalid, raise an error
                raise HTTPException(status_code=401, detail="Invalid token")

            # If the `allow_current_user` flag is set, assign the user ID to the request state
            if allow_current_user:
                request.state.user_id = token_data.id

            # If `allowed_roles` is provided, ensure that the user's role matches one of the allowed roles
            if allowed_roles and token_data.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )

            # Proceed with the original function after checking permissions
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
