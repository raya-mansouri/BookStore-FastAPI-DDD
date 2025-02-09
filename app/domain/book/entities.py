from pydantic import BaseModel
from typing import List

class Genre(BaseModel):
    id: int
    name: str

class Book(BaseModel):
    id: int
    title: str
    isbn: str
    price: int
    genre_id: int
    units: int
    reserved_units: int
    authors: List[int]