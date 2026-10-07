from datetime import datetime
import enum
from sqlalchemy import Enum, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER
    )

    comments: Mapped[list["CommentModel"]] = relationship(
        back_populates="user"
    )


class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    year: Mapped[int]
    isbn: Mapped[str] = mapped_column(String(20), unique=True)

    summary: Mapped[str] = mapped_column(Text)

    genre: Mapped[str] = mapped_column(String(50))

    cover_path: Mapped[str] = mapped_column(String(500))

    comments: Mapped[list["CommentModel"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan"
    )


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    text: Mapped[str] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE")
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )

    user: Mapped["UserModel"] = relationship(
        back_populates="comments"
    )

    book: Mapped["BookModel"] = relationship(
        back_populates="comments"
    )
