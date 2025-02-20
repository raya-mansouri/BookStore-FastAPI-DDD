from typing import List
from jose import jwt
from fastapi import HTTPException
from redis import Redis
from app.db.unit_of_work import UnitOfWork
from app.infrastructure.otp_limiter import RateLimiter
from app.adapters.repositories.user_repo import AuthRepository
from app.adapters.repositories.user_repo_redis import AuthRepositoryRedis
from app.settings import settings
from app.user.domain.entities import (
    LoginStep1Request,
    LoginStep2Request,
    User,
    UserCreate,
    UserUpdate,
)
from app.user.service_layer.utils import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.utils.message_interface.sms_service import KaveNegar, Signal, SmsIR, SmsService

SECRET_KEY = settings.SECRET_KEY  # Secret key for JWT encoding and decoding
ALGORITHM = settings.ALGORITHM  # Algorithm used for JWT encoding and decoding
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # Token expiry time

# Redis client setup for managing OTP rate limits
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB0,
    decode_responses=True,
)

# RateLimiter instance to manage OTP requests per user
rate_limiter = RateLimiter(redis_client, "otp_requests")

# SMS service instance using multiple SMS providers for OTP delivery
sms_service = SmsService([SmsIR(), KaveNegar(), Signal()])


class AuthService:
    # Method for creating a new user
    async def create_item(self, user_data: UserCreate, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(
                AuthRepository
            )  # Get the repository for user management
            existing_user = await repo.get_by_username_or_email(
                user_data.username, user_data.email
            )

            # Check if the user already exists
            if existing_user:
                if existing_user.username == user_data.username:
                    raise HTTPException(
                        status_code=400, detail="Username already registered"
                    )
                if existing_user.email == user_data.email:
                    raise HTTPException(
                        status_code=400, detail="Email already registered"
                    )

            # Hash the user's password before storing it
            hashed_password = get_password_hash(user_data.password)
            new_user = await repo.create_item(
                user_data, hashed_password
            )  # Create the user

            # Commit the transaction and return the response
            await uow.commit()
            await uow.refresh(new_user)
            return {"message": "User created successfully"}

    # Method for authenticating a user using username and password
    async def authenticate_user(self, username: str, password: str, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(
                AuthRepository
            )  # Get the repository for user management
            user = await repo.get_by_username(username)  # Fetch the user by username

            # Validate the user and password
            if not user or not verify_password(password, user.password):
                raise HTTPException(status_code=404, detail="User not found")
            return user

    # Method for handling the first step of login (username/password and OTP generation)
    async def login_step1(self, credentials: LoginStep1Request, uow: UnitOfWork):
        async with uow:
            user = await self.authenticate_user(
                credentials.username, credentials.password, uow
            )
            if not user:
                raise HTTPException(
                    status_code=401, detail="Incorrect username or password"
                )

            # Check if OTP requests are allowed based on rate limiting
            await rate_limiter.is_allowed(user.id)
            otp_repo = AuthRepositoryRedis()  # Redis repository for OTP management
            otp = await otp_repo.generate_otp(user.id)  # Generate a new OTP

            phone_number = "09123567891"  # Placeholder phone number, can be dynamic
            try:
                # Send the OTP via SMS
                sent_otp = await sms_service.send_otp(phone_number, otp)
                return {"message": "OTP sent successfully", "otp": sent_otp}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    # Method for handling the second step of login (OTP verification)
    async def login_step2(self, otp_data: LoginStep2Request, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(AuthRepository)
            otp_repo = AuthRepositoryRedis()  # Redis repository for OTP management

            # Verify the OTP
            user_id = await otp_repo.verify_otp(otp_data.otp)
            if not user_id:
                raise HTTPException(status_code=400, detail="Invalid OTP")

            user = await repo.get_by_id(int(user_id))  # Fetch the user by ID

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Create a JWT token for the authenticated user
            access_token = create_access_token(
                {"id": user.id, "sub": user.username, "role": user.role}
            )

            # Reset the rate limiter for the user after successful login
            await rate_limiter.reset(user_id)
            return {"access_token": access_token, "token_type": "bearer"}

    # Method to get the current authenticated user based on the token
    async def get_current_user(self, token: str, uow: UnitOfWork):
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )  # Decode the JWT token
        id = payload.get("id")
        username = payload.get("sub")

        if not id or not username:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )

        async with uow:
            repo = uow.get_repository(AuthRepository)
            user = await repo.get_by_id(id)
            if not user:
                raise HTTPException(
                    status_code=401, detail="Could not validate credentials"
                )
            return user

    # Method to fetch a user by their ID
    async def get_by_id(self, id: int, uow: UnitOfWork) -> User | dict:
        async with uow:
            repo = uow.get_repository(AuthRepository)
            result = await repo.get(id)
            if not result:
                raise HTTPException(
                    status_code=404, detail="User not found"
                )
            return result

    # Method to fetch all users
    async def get_items(self, uow: UnitOfWork) -> List[User]:
        async with uow:
            repo = uow.get_repository(AuthRepository)
            return await repo.get_all()

    # Method to update user data
    async def update_item(self, id: int, user_data: UserUpdate, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(AuthRepository)
            updated_user = await repo.update_item(id, user_data)  # Update user
            await uow.commit()
            await uow.refresh(updated_user)
            return updated_user

    # Method to delete a user by their ID
    async def delete_item(self, id: int, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(AuthRepository)
            deleted_user = await repo.delete_item(id)  # Delete user
            if deleted_user:
                await uow.commit()
                return {"User delete successfully"}
            else:
                raise HTTPException(
                    status_code=404, detail="User not found"
                )


# Dependency function to provide an instance of AuthService
async def get_auth_service() -> AuthService:
    return AuthService()
