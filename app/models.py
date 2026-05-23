from sqlalchemy import ForeignKey, String, Text, DateTime, func, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class PostTag(Base):
    __tablename__ = "post_tags"
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    
    # Связь "многие-ко-многим" с постами через таблицу-посредник post_tags
    posts: Mapped[List["Post"]] = relationship(secondary="post_tags", back_populates="tags")

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("post_types.id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("post_statuses.id"))
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Связи для автоматической подгрузки данных (Eager Loading)
    tags: Mapped[List["Tag"]] = relationship(secondary="post_tags", back_populates="posts")
    media: Mapped[List["Media"]] = relationship(back_populates="post", cascade="all, delete-orphan")

class Media(Base):
    __tablename__ = "media"
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    file_url: Mapped[str] = mapped_column(Text)
    media_type: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    post: Mapped["Post"] = relationship(back_populates="media")

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    platform: Mapped[str] = mapped_column(String(50))
    account_name: Mapped[Optional[str]] = mapped_column(String(150))
    access_token: Mapped[str] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())