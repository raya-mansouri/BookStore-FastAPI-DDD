from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Enum, DateTime, Table, Boolean
from sqlalchemy.sql import func
from app.db.base import metadata

# Define tables
user_table = Table(
    "user", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String(50), unique=True, index=True, nullable=False),
    Column("first_name", String(50), nullable=False),
    Column("last_name", String(50), nullable=False),
    Column("phone", String(11), nullable=False),
    Column("email", String(100), unique=True, nullable=False),
    Column("password", String(255), nullable=False),
    Column("role", Enum("admin", "customer", "author", name="user_roles"), nullable=False),
    Column("is_active", Boolean, default=False, nullable=False)
)

city_table = Table(
    "city", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String(100), unique=True, nullable=False)
)

genre_table = Table(
    "genre", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String(100), unique=True, nullable=False)
)

author_table = Table(
    "author", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("user.id"), unique=True, nullable=False),
    Column("city_id", Integer, ForeignKey("city.id"), nullable=False),
    Column("goodreads_link", String(255)),
    Column("bank_account_number", String(16), nullable=False)
)

customer_table = Table(
    "customer", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("user.id"), unique=True, nullable=False),
    Column("subscription_model", Enum("free", "plus", "premium", name="subscription_models"), nullable=False),
    Column("subscription_end_time", DateTime(timezone=True), server_default=func.now()),
    Column("wallet_money_amount", Integer, default=0, nullable=False)
)

book_table = Table(
    "book", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String(255), nullable=False),
    Column("isbn", String(13), unique=True, nullable=False),
    Column("price", Integer, nullable=False, default=0),
    Column("genre_id", Integer, ForeignKey("genre.id"), nullable=False),
    Column("description", String(1000)),
    Column("units", Integer, nullable=False),
    Column("reserved_units", Integer, default=0, nullable=False)
)

reservation_table = Table(
    "reservation", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("customer_id", Integer, ForeignKey("customer.id"), nullable=False),
    Column("book_id", Integer, ForeignKey("book.id"), nullable=False),
    Column("start_of_reservation", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("end_of_reservation", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("price", Integer, nullable=False),
    Column("status", Enum("pending", "active", "completed", name="reservation_status"), default="pending"),
    Column("queue_position", Integer, nullable=True)
)

book_author_table = Table(
    "book_author", metadata,
    Column("book_id", Integer, ForeignKey("book.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("author.id"), primary_key=True)
)