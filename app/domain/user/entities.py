from pydantic import BaseModel
from uuid import UUID, uuid4

class User(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    phone: str
    email: str
    role: str
    is_active: int

    def __init__(
        self,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
        phone: str = "",
        email: str = "",
        role: str = "",
        is_active: int = 1,
    ):
        super().__init__(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            role=role,
            is_active=is_active,
        )


    def __str__(self, username: str):
        self.username = username

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other.id == self.id

    def update_name(self, username: str):
        self.username = username


class City(BaseModel):
    id: int
    name: str

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

class Author(BaseModel):
    id: int
    user_id: int
    city_id: int
    goodreads_link: str
    bank_account_number: str

class Customer(BaseModel):
    id: int
    user_id: int
    subscription_model: str
    wallet_money_amount: int
