from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Text, Integer, Boolean,
    ForeignKey, Table, DateTime, func, Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


post_tags_table = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id",  Integer, ForeignKey("tags.id",  ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id:   Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[List["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "users"

    id:            Mapped[int]      = mapped_column(Integer, primary_key=True)
    username:      Mapped[str]      = mapped_column(String(100), unique=True, nullable=False)
    email:         Mapped[str]      = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str]      = mapped_column(Text, nullable=False)
    role_id:       Mapped[int]      = mapped_column(ForeignKey("roles.id"), nullable=False)
    created_at:    Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    role:            Mapped["Role"]              = relationship(back_populates="users")
    social_accounts: Mapped[List["SocialAccount"]] = relationship(back_populates="user")
    posts:           Mapped[List["Post"]]          = relationship(back_populates="author")
    approvals_given: Mapped[List["Approval"]]      = relationship(back_populates="manager")
    telegram_channels: Mapped[List["TelegramChannel"]] = relationship(back_populates="user")


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id:            Mapped[int]            = mapped_column(Integer, primary_key=True)
    user_id:       Mapped[int]            = mapped_column(ForeignKey("users.id"), nullable=False)
    platform:      Mapped[str]            = mapped_column(String(50), nullable=False)
    account_name:  Mapped[Optional[str]]  = mapped_column(String(150))
    access_token:  Mapped[str]            = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]]  = mapped_column(Text)
    expires_at:    Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at:    Mapped[datetime]       = mapped_column(DateTime, server_default=func.current_timestamp())

    user:         Mapped["User"]              = relationship(back_populates="social_accounts")
    publications: Mapped[List["Publication"]] = relationship(back_populates="social_account")

    @property
    def is_token_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at <= datetime.utcnow()


class PostType(Base):
    __tablename__ = "post_types"

    id:   Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship(back_populates="post_type")


class PostStatus(Base):
    __tablename__ = "post_statuses"

    id:   Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship(back_populates="status")


class Post(Base):
    __tablename__ = "posts"

    id:           Mapped[int]            = mapped_column(Integer, primary_key=True)
    title:        Mapped[Optional[str]]  = mapped_column(String(255))
    content:      Mapped[Optional[str]]  = mapped_column(Text)
    author_id:    Mapped[int]            = mapped_column(ForeignKey("users.id"), nullable=False)
    post_type_id: Mapped[Optional[int]]  = mapped_column(ForeignKey("post_types.id"))
    status_id:    Mapped[int]            = mapped_column(ForeignKey("post_statuses.id"), nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at:   Mapped[datetime]       = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at:   Mapped[datetime]       = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    author:      Mapped["User"]              = relationship(back_populates="posts")
    post_type:   Mapped[Optional["PostType"]]= relationship(back_populates="posts")
    status:      Mapped["PostStatus"]        = relationship(back_populates="posts")
    media_items: Mapped[List["Media"]]       = relationship(back_populates="post", cascade="all, delete-orphan")
    tags:        Mapped[List["Tag"]]         = relationship(secondary=post_tags_table, back_populates="posts")
    publications:Mapped[List["Publication"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    approvals:   Mapped[List["Approval"]]    = relationship(back_populates="post", cascade="all, delete-orphan")
    telegram_publications: Mapped[list["TelegramPublication"]] = relationship(back_populates="post", cascade="all, delete-orphan")


class Media(Base):
    __tablename__ = "media"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True)
    post_id:    Mapped[int]      = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    file_url:   Mapped[str]      = mapped_column(Text, nullable=False)
    media_type: Mapped[str]      = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    post: Mapped["Post"] = relationship(back_populates="media_items")


class Tag(Base):
    __tablename__ = "tags"

    id:   Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship(secondary=post_tags_table, back_populates="tags")


class Publication(Base):
    __tablename__ = "publications"

    id:                Mapped[int]           = mapped_column(Integer, primary_key=True)
    post_id:           Mapped[int]           = mapped_column(ForeignKey("posts.id"), nullable=False)
    social_account_id: Mapped[int]           = mapped_column(ForeignKey("social_accounts.id"), nullable=False)
    published_at:      Mapped[Optional[datetime]] = mapped_column(DateTime)
    status:            Mapped[Optional[str]] = mapped_column(String(50))
    response:          Mapped[Optional[str]] = mapped_column(Text)

    post:           Mapped["Post"]          = relationship(back_populates="publications")
    social_account: Mapped["SocialAccount"] = relationship(back_populates="publications")


class Approval(Base):
    __tablename__ = "approvals"

    id:         Mapped[int]          = mapped_column(Integer, primary_key=True)
    post_id:    Mapped[int]          = mapped_column(ForeignKey("posts.id"), nullable=False)
    manager_id: Mapped[int]          = mapped_column(ForeignKey("users.id"), nullable=False)
    approved:   Mapped[bool]         = mapped_column(Boolean, nullable=False)
    comment:    Mapped[Optional[str]]= mapped_column(Text)
    created_at: Mapped[datetime]     = mapped_column(DateTime, server_default=func.current_timestamp())

    post:    Mapped["Post"] = relationship(back_populates="approvals")
    manager: Mapped["User"] = relationship(back_populates="approvals_given")


class TelegramPublication(Base):
    __tablename__ = "telegram_publications"

    id:           Mapped[int]      = mapped_column(Integer, primary_key=True)
    post_id:      Mapped[int]      = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    chat_id:      Mapped[str]      = mapped_column(String(100), nullable=False)  # ID группы
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status:       Mapped[str]      = mapped_column(String(20), default="pending")  # pending / done / failed
    error:        Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    post: Mapped["Post"] = relationship(back_populates="telegram_publications")


class TelegramChat(Base):
    __tablename__ = "telegram_chats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255))
    chat_type: Mapped[str] = mapped_column(String(20))  # private, group, supergroup, channel
    added_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    
    user: Mapped["User"] = relationship()

class TelegramChannel(Base):
    __tablename__ = "telegram_channels"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255))
    chat_type: Mapped[str] = mapped_column(String(20), default="channel")  # channel
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    
    user: Mapped["User"] = relationship(back_populates="telegram_channels")
