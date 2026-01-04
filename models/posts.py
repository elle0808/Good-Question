from datetime import datetime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,Text,Integer,JSON,ForeignKey,DateTime
from sqlalchemy.ext.mutable import MutableList
from .base import Base
from typing import List, Optional

# --- 1.User 表格 ---
class UserDB(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)

    # 虛擬連結：讓這個 User 可以直接透過 .posts 看到他所有的文章
    posts: Mapped[List["PostDB"]] = relationship(back_populates="author")

# --- 2.Post 表格 ---
class PostDB(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True) 
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_anonymous: Mapped[bool] = mapped_column(default=False, nullable=False)
    author: Mapped["UserDB"] = relationship(back_populates="posts")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tags: Mapped[List[str]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=lambda: [],
        nullable=False
    )
    comments = relationship("CommentDB", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Post(id={self.id}, slug={self.slug}, title={self.title})"
    
# --- 3.Comment 表格 ---
class CommentDB(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_anonymous: Mapped[bool] = mapped_column(default=False)

    # 外鍵：這條留言屬於哪篇文章？
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    
    # 外鍵：這條留言是誰寫的？
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    # 關聯設定：讓 SQLAlchemy 幫你自動抓作者資料
    author = relationship("UserDB")
    post = relationship("PostDB", back_populates="comments")
