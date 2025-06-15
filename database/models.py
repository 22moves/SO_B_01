# database/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String)
    first_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Integer, default=0) # SQLite stores boolean as Integer
    created_at: Mapped[str] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Связь с камнями, которые создал пользователь
    stones: Mapped[list["Stone"]] = relationship("Stone", back_populates="creator")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"


class Stone(Base):
    __tablename__ = 'stones'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    username: Mapped[str | None] = mapped_column(String) # Имя пользователя, который создал камень
    photo_file_id: Mapped[str | None] = mapped_column(String) # Telegram file_id для фотографии
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude: Mapped[float | None] = mapped_column(Float) # Высота над уровнем моря
    created_at: Mapped[str] = mapped_column(DateTime, default=func.now())
    air_quality_index: Mapped[int | None] = mapped_column(Integer) # Индекс качества воздуха (AQI)
    air_quality_description: Mapped[str | None] = mapped_column(String) # Описание качества воздуха
    description: Mapped[str | None] = mapped_column(Text) # Описание камня

    # Связь с создателем камня
    creator: Mapped["User"] = relationship("User", back_populates="stones")

    def __repr__(self):
        return (f"<Stone(id={self.id}, creator_id={self.creator_id}, "
                f"location=({self.latitude}, {self.longitude}), "
                f"description='{self.description[:20] if self.description else ''}...')>")