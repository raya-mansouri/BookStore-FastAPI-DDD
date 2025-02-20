from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Enum,
    DateTime,
    Table,
    Boolean,
)
from sqlalchemy.sql import func
from app.db.base import metadata

# Table for storing user information
user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, index=True),  # Primary key for user ID
    Column(
        "username", String(50), unique=True, index=True, nullable=False
    ),  # Unique username for the user
    Column("first_name", String(50), nullable=False),  # User's first name
    Column("last_name", String(50), nullable=False),  # User's last name
    Column("phone", String(11), nullable=False),  # User's phone number
    Column(
        "email", String(100), unique=True, nullable=False
    ),  # Unique email for the user
    Column("password", String(255), nullable=False),  # User's hashed password
    Column(
        "role", Enum("admin", "customer", "author", name="user_roles"), nullable=False
    ),  # Enum for user's role (admin, customer, author)
    Column(
        "is_active", Boolean, default=False, nullable=False
    ),  # Whether the user is active or not
)

# Table for storing city information
city_table = Table(
    "city",
    metadata,
    Column("id", Integer, primary_key=True, index=True),  # Primary key for city ID
    Column("name", String(100), unique=True, nullable=False),  # Unique city name
)

# Table for storing genre information for books
genre_table = Table(
    "genre",
    metadata,
    Column("id", Integer, primary_key=True, index=True),  # Primary key for genre ID
    Column("name", String(100), unique=True, nullable=False),  # Unique genre name
)

# Table for storing author information
author_table = Table(
    "author",
    metadata,
    Column("id", Integer, primary_key=True, index=True),  # Primary key for author ID
    Column(
        "user_id", Integer, ForeignKey("user.id"), unique=True, nullable=False
    ),  # Reference to user ID
    Column(
        "city_id", Integer, ForeignKey("city.id"), nullable=False
    ),  # Reference to city ID
    Column("goodreads_link", String(255)),  # Author's Goodreads link
    Column(
        "bank_account_number", String(16), nullable=False
    ),  # Author's bank account number
)

# Table for storing customer information
customer_table = Table(
    "customer",
    metadata,
    Column("id", Integer, primary_key=True, index=True),  # Primary key for customer ID
    Column(
        "user_id", Integer, ForeignKey("user.id"), unique=True, nullable=False
    ),  # Reference to user ID
    Column(
        "subscription_model",
        Enum("free", "plus", "premium", name="subscription_models"),
        nullable=False,
    ),  # Enum for subscription model (free, plus, premium)
    Column(
        "subscription_end_time", DateTime(timezone=True), server_default=func.now()
    ),  # Subscription end time
    Column(
        "wallet_money_amount", Integer, default=0, nullable=False
    ),  # Customer's wallet balance
)

# Table for storing book information
book_table = Table(
    "book",
    metadata,
    Column("id", Integer, primary_key=True, index=True),  # Primary key for book ID
    Column("title", String(255), nullable=False),  # Title of the book
    Column("isbn", String(13), unique=True, nullable=False),  # Unique ISBN for the book
    Column("price", Integer, nullable=False, default=0),  # Price of the book
    Column(
        "genre_id", Integer, ForeignKey("genre.id"), nullable=False
    ),  # Reference to genre ID
    Column("description", String(1000)),  # Description of the book
    Column("units", Integer, nullable=False),  # Total number of book units
    Column(
        "reserved_units", Integer, default=0, nullable=False
    ),  # Number of reserved book units
)

# Table for storing reservation information
reservation_table = Table(
    "reservation",
    metadata,
    Column(
        "id", Integer, primary_key=True, index=True
    ),  # Primary key for reservation ID
    Column(
        "customer_id", Integer, ForeignKey("customer.id"), nullable=False
    ),  # Reference to customer ID
    Column(
        "book_id", Integer, ForeignKey("book.id"), nullable=False
    ),  # Reference to book ID
    Column(
        "start_of_reservation",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),  # Start time of the reservation
    Column(
        "end_of_reservation",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),  # End time of the reservation
    Column("price", Integer, nullable=False),  # Price of the reservation
    Column(
        "status",
        Enum("pending", "active", "completed", name="reservation_status"),
        default="pending",  # Enum for reservation status (pending, active, completed)
    ),
    Column(
        "queue_position", Integer, nullable=True
    ),  # Position in the reservation queue
)

# Table for storing the relationship between books and authors (many-to-many)
book_author_table = Table(
    "book_author",
    metadata,
    Column(
        "book_id", Integer, ForeignKey("book.id"), primary_key=True
    ),  # Reference to book ID
    Column(
        "author_id", Integer, ForeignKey("author.id"), primary_key=True
    ),  # Reference to author ID
)
