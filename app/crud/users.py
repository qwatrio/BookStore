from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserModel
from app.schemas.user import UserCreate


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> UserModel | None:
    result = await db.execute(
        select(UserModel).where(UserModel.email == email)
    )

    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    user_data: UserCreate,
    password_hash: str,
) -> UserModel:
    user = UserModel(
        name=user_data.name,
        email=user_data.email,
        password_hash=password_hash,
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user