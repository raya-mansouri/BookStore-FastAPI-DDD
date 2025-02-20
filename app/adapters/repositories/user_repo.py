from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.exceptions import InvalidFieldError, NotFoundException
from app.user.domain.entities import User, UserCreate, UserUpdate


class AuthRepository:
    def __init__(self, db: AsyncSession):
        """
        Initializes the repository with the provided AsyncSession instance.

        :param db: The database session to interact with.
        """
        self.db = db

    async def get_by_username_or_email(
        self, username: str, email: str
    ) -> Optional[User]:
        """
        Retrieves a user by either their username or email.

        :param username: The username of the user.
        :param email: The email of the user.
        :return: A User instance if found, otherwise None.
        """
        result = await self.db.execute(
            select(User).where(or_(User.username == username, User.email == email))
        )
        return result.scalar()

    async def create_item(self, user_data: UserCreate, hashed_password: str) -> User:
        """
        Creates a new user with the given data and hashed password.

        :param user_data: The user data to create the user.
        :param hashed_password: The hashed password for the user.
        :return: The created User instance.
        """
        user_data.password = hashed_password  # Set the hashed password
        new_user = User(**user_data.model_dump())  # Create a new User entity
        self.db.add(new_user)  # Add the new user to the session
        await self.db.flush()  # Flush the changes to the database
        await self.db.refresh(
            new_user
        )  # Refresh the user instance with the latest data from DB
        return new_user

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieves a user by their username.

        :param username: The username of the user.
        :return: A User instance if found, otherwise None.
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user by their ID.

        :param user_id: The ID of the user.
        :return: A User instance if found, otherwise None.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar()

    async def get_all(self) -> List[User]:
        """
        Retrieves all users.

        :return: A list of User instances.
        """
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def update_item(self, id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Updates the user with the given ID using the provided data.

        :param id: The ID of the user to update.
        :param user_data: The data to update the user with.
        :return: The updated User instance.
        """
        try:
            current_user = await self.get_by_id(id)
            if not current_user:
                raise NotFoundException("User not found")
            for key, value in user_data.model_dump(exclude_none=True).items():
                setattr(
                    current_user, key, value
                )  # Set each attribute from the user_data
            await self.db.flush()  # Commit changes to the database
            await self.db.refresh(
                current_user
            )  # Refresh the user instance with the latest data from DB
            return current_user
        except InvalidFieldError as e:
            raise InvalidFieldError(f"User update failed: {e}")

    async def delete_item(self, id: int) -> bool:
        """
        Deletes a user by their ID.

        :param id: The ID of the user to delete.
        :return: True if the user was deleted, otherwise False.
        """
        user = await self.get_by_id(id)
        if not user:
            return False
        await self.db.delete(user)  # Delete the user from the session
        return True
