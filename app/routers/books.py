from fastapi import APIRouter, HTTPException, status, Depends

from app.crud.books import get_books, get_book, create_book, update_book, patch_book, delete_book
from app.database.database import SessionDep
from app.database.models import UserModel
from app.dependencies.auth import get_current_admin
from app.schemas.book import BookResponse, Genre, BookCreate, BookUpdate, BookPatch

router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


@router.get(
    "",
    response_model=list[BookResponse],
)
async def read_books(
        db: SessionDep,
        genre: Genre | None = None,
):
    return await get_books(
        db,
        genre.value if genre else None,
    )


@router.get(
    "/{book_id}",
    response_model=BookResponse,
)
async def read_book(
        book_id: int,
        db: SessionDep,
):
    book = await get_book(db, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return book


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_book(
        book_data: BookCreate,
        db: SessionDep,
        current_admin: UserModel = Depends(get_current_admin),
):
    return await create_book(
        db,
        book_data,
    )

@router.put(
    "/{book_id}",
    response_model=BookResponse,
)
async def update_existing_book(
    book_id: int,
    book_data: BookUpdate,
    db: SessionDep,
    current_admin: UserModel = Depends(get_current_admin),
):
    book = await get_book(db, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return await update_book(
        db,
        book,
        book_data,
    )

@router.patch(
    "/{book_id}",
    response_model=BookResponse,
)
async def patch_existing_book(
    book_id: int,
    book_data: BookPatch,
    db: SessionDep,
    current_admin: UserModel = Depends(get_current_admin),
):
    book = await get_book(db, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return await patch_book(
        db,
        book,
        book_data,
    )

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_book(
    book_id: int,
    db: SessionDep,
    current_admin: UserModel = Depends(get_current_admin),
):
    book = await get_book(db, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    await delete_book(
        db,
        book,
    )