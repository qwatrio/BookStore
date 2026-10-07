from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import CommentModel
from app.schemas.comments import CommentCreate


async def get_book_comments(
    db: AsyncSession,
    book_id: int,
) -> list[CommentModel]:

    result = await db.execute(
        select(CommentModel)
        .options(selectinload(CommentModel.user))
        .where(CommentModel.book_id == book_id)
        .order_by(CommentModel.created_at)
    )

    return list(result.scalars().all())


async def create_comment(
    db: AsyncSession,
    book_id: int,
    user_id: int,
    comment_data: CommentCreate,
) -> CommentModel:

    comment = CommentModel(
        text=comment_data.text,
        book_id=book_id,
        user_id=user_id,
    )

    db.add(comment)

    await db.commit()

    result = await db.execute(
        select(CommentModel)
        .options(selectinload(CommentModel.user))
        .where(CommentModel.id == comment.id)
    )

    return result.scalar_one()


async def get_comment(
    db: AsyncSession,
    comment_id: int,
) -> CommentModel | None:

    result = await db.execute(
        select(CommentModel).where(
            CommentModel.id == comment_id
        )
    )

    return result.scalar_one_or_none()


async def delete_comment(
    db: AsyncSession,
    comment: CommentModel,
) -> None:

    await db.delete(comment)
    await db.commit()