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
    is_active: bool

    def __init__(self, id: UUID | None = None, username: str = ""):
        self.id = id or uuid4()
        self.name = username

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
