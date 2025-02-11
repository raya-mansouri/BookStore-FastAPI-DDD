from app.domain.user.object_values import SubscriptionModel
from app.exceptions import InvalidFieldError


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

    def __str__(self):
        return f"User(id={self.id}, username={self.username})"
    
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

    def __validate(self, id: int, user_id: int, subscription_model: str, wallet_money_amount: int):
        if not isinstance(user_id, int) or user_id <= 0:
            raise InvalidFieldError("User ID must be a positive integer.")
        
        if subscription_model not in SubscriptionModel:
            raise InvalidFieldError("subscription_model must be one of: 'free', 'plus', 'premium'.")
        
        if not isinstance(wallet_money_amount, int) or wallet_money_amount < 0:
            raise InvalidFieldError("Wallet money amount must be a non-negative integer.")
    
    def __setattr__(self, name, value):
        # Validate before setting any attribute
        if name == 'user_id' and (not isinstance(value, int) or value <= 0):
            raise InvalidFieldError("User ID must be a positive integer.")
        elif name == "subscription_model":
            if value not in SubscriptionModel._value2member_map_:
                raise InvalidFieldError("subscription_model must be one of: 'free', 'plus', 'premium'.")
            else:
                value = SubscriptionModel(value)
        elif name == 'wallet_money_amount' and (not isinstance(value, int) or value < 0):
            raise InvalidFieldError("Wallet money amount must be a non-negative integer.")
        else:
            super().__setattr__(name, value)
    
    def __getattr__(self, name):
        # Handle attribute access if it does not exist
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def validate(self):
        # Re-run the validation logic, could be used for revalidation after changing values
        self.__validate(self.id, self.user_id, self.subscription_model, self.wallet_money_amount)

    def __repr__(self):
        return f"Customer(id={self.id}, user_id={self.user_id}, subscription_model='{self.subscription_model}', wallet_money_amount={self.wallet_money_amount})"
        
    def __eq__(self, other):
        if not isinstance(other, Customer):
            return False
        return self.id == other.id