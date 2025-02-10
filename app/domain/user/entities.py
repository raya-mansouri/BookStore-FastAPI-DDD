class User:
    id: int
    username: str
    first_name: str
    last_name: str
    phone: str
    email: str
    role: str
    password: str
    is_active: bool

    def __str__(self, username: str):
        self.username = username

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other.id == self.id

    def update_name(self, username: str):
        self.username = username


class City:
    id: int
    name: str

    def __str__(self):
        return self.name

class Author:
    id: int
    user_id: int
    city_id: int
    goodreads_link: str
    bank_account_number: str

class Customer:
    id: int
    user_id: int
    subscription_model: str
    wallet_money_amount: int
