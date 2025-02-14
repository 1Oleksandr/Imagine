from datetime import datetime, date
import enum
import uuid
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    func,
    Table,
    extract,
    Enum,
    ForeignKey,
    Boolean,
)

from sqlalchemy.sql.sqltypes import Date, DateTime
from sqlalchemy_utils import EmailType
from fastapi_users_db_sqlalchemy import generics

from sqlalchemy.orm import DeclarativeBase

from src.conf.constants import (
    TAG_MAX_LENGTH,
    PHOTO_PATH_LENGTH,
    TRANSFORM_PATH_LENGTH,
    PHOTO_MAX_DESCRIPTION_LENGTH,
    COMMENT_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    TOKEN_MAX_LENGTH,
    AVATAR_PATH_LENGTH,
)


class Base(DeclarativeBase): ...


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(TAG_MAX_LENGTH), nullable=False, unique=True
    )


photo_m2m_tag = Table(
    "photo_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Datefield:
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )


class Photo(Base, Datefield):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(PHOTO_PATH_LENGTH), nullable=False)
    description: Mapped[str] = mapped_column(
        String(PHOTO_MAX_DESCRIPTION_LENGTH), nullable=False
    )
    path_transform: Mapped[str] = mapped_column(
        String(TRANSFORM_PATH_LENGTH), nullable=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    comment: Mapped["Comment"] = relationship(
        "Comment", backref="photos", cascade="all, delete-orphan"
    )
    rating: Mapped["Rating"] = relationship(
        "Rating", backref="photos", cascade="all, delete-orphan"
    )
    tags = relationship("Tag", secondary=photo_m2m_tag, backref="photos")
    public_photo_id: Mapped[str] = mapped_column(
        String(PHOTO_PATH_LENGTH), nullable=False
    )


class Comment(Base, Datefield):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opinion: Mapped[str] = mapped_column(String(COMMENT_MAX_LENGTH), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base, Datefield):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        generics.GUID(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=True)
    username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH), nullable=False, unique=True
    )
    email: Mapped[str] = mapped_column(
        String(EMAIL_MAX_LENGTH), nullable=False, unique=True
    )
    password: Mapped[str] = mapped_column(String(PASSWORD_MAX_LENGTH), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(TOKEN_MAX_LENGTH), nullable=True)
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.user, nullable=False
    )
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    banned_at: Mapped[date] = mapped_column(Date, nullable=True)
    avatar: Mapped[str] = mapped_column(String(AVATAR_PATH_LENGTH), nullable=True)
    photo: Mapped["Photo"] = relationship(
        "Photo", backref="users", cascade="all, delete-orphan"
    )
    comment: Mapped["Comment"] = relationship(
        "Comment", backref="users", cascade="all, delete-orphan"
    )
    rating: Mapped["Rating"] = relationship(
        "Rating", backref="users", cascade="all, delete-orphan"
    )


class Rating(Base, Datefield):
    __tablename__ = "ratings"
    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(nullable=False)
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
