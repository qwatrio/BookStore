from enum import Enum

from pydantic import BaseModel, ConfigDict


class Genre(str, Enum):
    CLASSIC = "classic"
    NON_FICTION = "non_fiction"
    PROSE = "prose"
    PSYCHOLOGY = "psychology"
    HORROR = "horror"


class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    isbn: str
    summary: str
    genre: Genre
    cover_path: str


class BookUpdate(BaseModel):
    title: str
    author: str
    year: int
    isbn: str
    summary: str
    genre: Genre
    cover_path: str


class BookPatch(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    isbn: str | None = None
    summary: str | None = None
    genre: Genre | None = None
    cover_path: str | None = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: int
    isbn: str
    summary: str
    genre: Genre
    cover_path: str

    model_config = ConfigDict(from_attributes=True)