from sqlalchemy.orm import relationship
from sqlalchemy import event
from app.book.domain.entities import Book, Genre
from app.db.base import mapper_registry
from app.adapters.data_models import *
from app.reservation.domain.entities import Customer, Reservation
from app.user.domain.entities import Author, City, User


# Define the mapping manually for each entity to its corresponding table
def start_mappers(mapper_registry):
    # Mapping for the User entity and its relationships with Author and Customer
    mapper_registry.map_imperatively(
        User,
        user_table,
        properties={
            "author": relationship(
                Author,
                back_populates="user",
                uselist=False,
                cascade="all, delete-orphan",
            ),  # One-to-one relationship with Author
            "customer": relationship(
                Customer,
                back_populates="user",
                uselist=False,
                cascade="all, delete-orphan",
            ),  # One-to-one relationship with Customer
        },
    )

    # Mapping for the City entity
    mapper_registry.map_imperatively(City, city_table)

    # Mapping for the Author entity and its relationships with User and City
    mapper_registry.map_imperatively(
        Author,
        author_table,
        properties={
            "user": relationship(
                User, back_populates="author", uselist=False
            ),  # One-to-one relationship with User
            "city": relationship(
                City, backref="city", uselist=False
            ),  # One-to-one relationship with City
        },
    )

    # Mapping for the Customer entity and its relationships with User and Reservation
    mapper_registry.map_imperatively(
        Customer,
        customer_table,
        properties={
            "user": relationship(
                User, back_populates="customer", uselist=False
            ),  # One-to-one relationship with User
            "reservations": relationship(
                Reservation, back_populates="customer", cascade="all, delete-orphan"
            ),  # One-to-many relationship with Reservation
        },
    )

    # Mapping for the Genre entity
    mapper_registry.map_imperatively(Genre, genre_table)

    # Mapping for the Book entity and its relationships with Genre and Author (many-to-many)
    mapper_registry.map_imperatively(
        Book,
        book_table,
        properties={
            "genre": relationship(
                Genre, backref="books"
            ),  # Many-to-one relationship with Genre
            "authors": relationship(
                Author, secondary=book_author_table, backref="books"
            ),  # Many-to-many relationship with Author
        },
    )

    # Mapping for the Reservation entity and its relationships with Customer and Book
    mapper_registry.map_imperatively(
        Reservation,
        reservation_table,
        properties={
            "customer": relationship(
                Customer, back_populates="reservations"
            ),  # Many-to-one relationship with Customer
            "book": relationship(
                Book, backref="reservations"
            ),  # Many-to-one relationship with Book
        },
    )
