from sqlalchemy.orm import relationship
from sqlalchemy import event
from app.book.domain.entities import Book, Genre
from app.db.base import mapper_registry
from app.adapters.data_models import *
from app.reservation.domain.entities import Customer, Reservation
from app.user.domain.entities import Author, City, User

# from app.db.database import AsyncSessionLocal


# Define the mapping manually
def start_mappers(mapper_registry):
    mapper_registry.map_imperatively(
        User, user_table,
        properties={
            "author": relationship(Author, back_populates="user", uselist=False, cascade="all, delete-orphan"),
            "customer": relationship(Customer, back_populates="user", uselist=False, cascade="all, delete-orphan"),
        }
    )
    mapper_registry.map_imperatively(City, city_table)
    mapper_registry.map_imperatively(
        Author, author_table,
        properties={
            "user": relationship(User, back_populates="author", uselist=False),
            "city": relationship(City, backref="city", uselist=False)
        }
    )
    mapper_registry.map_imperatively(
        Customer, customer_table,
        properties={
            "user": relationship(User, back_populates="customer", uselist=False),
            "reservations": relationship(Reservation, back_populates="customer", cascade="all, delete-orphan")
        }
    )
    mapper_registry.map_imperatively(Genre, genre_table)
    mapper_registry.map_imperatively(
        Book, book_table,
        properties={
            "genre": relationship(Genre, backref="books"),
            "authors": relationship(Author, secondary=book_author_table, backref="books"),
        }
    )
    mapper_registry.map_imperatively(
        Reservation, reservation_table,
        properties={
            "customer": relationship(Customer, back_populates="reservations"),
            "book": relationship(Book, backref="reservations"),
        }
    )

# create_author_or_customer function is called after a flush event
# @event.listens_for(AsyncSessionLocal, "after_flush")
# def create_author_or_customer(session, flush_context):
#     for instance in session.new:
#         if isinstance(instance, User):
#             if instance.role == "author":
#                 session.add(Author(user_id=instance.id, city_id=1, goodreads_link="", bank_account_number="0000000000000000"))
#             elif instance.role == "customer":
#                 session.add(Customer(user_id=instance.id, subscription_model="free", subscription_end_time=None, wallet_money_amount=0))
