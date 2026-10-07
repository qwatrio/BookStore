from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import BookModel
from app.schemas.book import BookCreate, BookPatch, BookUpdate


async def get_books(
    db: AsyncSession,
    genre: str | None = None,
) -> list[BookModel]:

    query = select(BookModel)

    if genre:
        query = query.where(BookModel.genre == genre)

    result = await db.execute(query)

    return list(result.scalars().all())


async def get_book(
    db: AsyncSession,
    book_id: int,
) -> BookModel | None:

    result = await db.execute(
        select(BookModel).where(BookModel.id == book_id)
    )

    return result.scalar_one_or_none()


async def create_book(
    db: AsyncSession,
    book_data: BookCreate,
) -> BookModel:

    book = BookModel(
        title=book_data.title,
        author=book_data.author,
        year=book_data.year,
        isbn=book_data.isbn,
        summary=book_data.summary,
        genre=book_data.genre,
        cover_path=book_data.cover_path,
    )

    db.add(book)

    await db.commit()
    await db.refresh(book)

    return book


async def update_book(
    db: AsyncSession,
    book: BookModel,
    book_data: BookUpdate,
) -> BookModel:

    book.title = book_data.title
    book.author = book_data.author
    book.year = book_data.year
    book.isbn = book_data.isbn
    book.summary = book_data.summary
    book.genre = book_data.genre
    book.cover_path = book_data.cover_path

    await db.commit()
    await db.refresh(book)

    return book


async def patch_book(
    db: AsyncSession,
    book: BookModel,
    book_data: BookPatch,
) -> BookModel:

    update_data = book_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(book, field, value)

    await db.commit()
    await db.refresh(book)

    return book


async def delete_book(
    db: AsyncSession,
    book: BookModel,
) -> None:

    await db.delete(book)
    await db.commit()