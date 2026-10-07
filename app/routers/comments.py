from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.books import get_book
from app.crud.comments import (
    create_comment,
    delete_comment,
    get_book_comments,
    get_comment,
)
from app.database.database import SessionDep
from app.database.models import UserModel
from app.dependencies.auth import (
    get_current_admin,
    get_current_user,
)
from app.schemas.comments import (
    CommentCreate,
    CommentResponse,
)


router = APIRouter(
    tags=["Comments"],
)


@router.get(
    "/books/{book_id}/comments",
    response_model=list[CommentResponse],
)
async def read_book_comments(
    book_id: int,
    db: SessionDep,
):
    book = await get_book(db, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return await get_book_comments(
        db,
        book_id,
    )


@router.post(
    "/books/{book_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_book_comment(
    book_id: int,
    comment_data: CommentCreate,
    db: SessionDep,
    current_user: UserModel = Depends(get_current_user),
):
    book = await get_book(db, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    comment = await create_comment(
        db,
        book_id,
        current_user.id,
        comment_data,
    )

    return comment


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_comment(
    comment_id: int,
    db: SessionDep,
    current_admin: UserModel = Depends(get_current_admin),
):
    comment = await get_comment(
        db,
        comment_id,
    )

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    await delete_comment(
        db,
        comment,
    )
