from eralchemy2 import render_er
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    posts = relationship("Post", back_populates="user", cascade="all, delete")
    comments = relationship(
        "Comment", back_populates="user", cascade="all, delete")

    followers = relationship(
        "Follow",
        foreign_keys='Follow.followed_id',
        back_populates="followed",
        cascade="all, delete"
    )

    following = relationship(
        "Follow",
        foreign_keys='Follow.follower_id',
        back_populates="follower",
        cascade="all, delete"
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "followers": [follow.follower_id for follow in self.followers],
            "following": [follow.followed_id for follow in self.following]

            # do not serialize the password, it's a security breach
        }


class Post(db.Model):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow)

    user = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }


class Comment(db.Model):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(
        ForeignKey('posts.id'), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }


class Follow(db.Model):
    __tablename__ = 'follows'

    follower_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), primary_key=True)
    followed_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow)

    # Relaciones
    follower = relationship("User", foreign_keys=[
                            follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[
                            followed_id], back_populates="followers")

    def serialize(self):
        return {
            "follower_id": self.follower_id,
            "followed_id": self.followed_id,
            "created_at": self.created_at.isoformat()
        }


# Generar diagrama
try:
    render_er(db.Model, 'diagram.png')
    print("Diagrama generado exitosamente")
except Exception as e:
    print("Hubo un problema generando el diagrama")
    raise e
