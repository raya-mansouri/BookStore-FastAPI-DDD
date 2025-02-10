from pydantic import BaseModel
from typing import List

class Genre:
    id: int
    name: str

class Book:
    id: int
    title: str
    isbn: str
    price: int
    genre_id: int
    units: int
    reserved_units: int
    authors: List[int]