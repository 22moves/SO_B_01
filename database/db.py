# database/db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.models import Base # Импортируем нашу "основу" для моделей

# Определяем путь к файлу базы данных
DATABASE_URL = "sqlite+aiosqlite:///./data/stones.db" # Путь к файлу базы данных SQLite

# Создаем асинхронный движок для работы с базой данных
# echo=True означает, что мы будем видеть все SQL-запросы в консоли (полезно для отладки)
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий. Сессия - это как наша рабочая область для взаимодействия с БД.
AsyncSessionLocal = sessionmaker(
    autocommit=False, # Не делать коммит автоматически
    autoflush=False,  # Не сбрасывать изменения автоматически
    bind=engine,      # Привязываем сессию к нашему движку
    class_=AsyncSession, # Указываем, что сессия будет асинхронной
    expire_on_commit=False # Не инвалидировать объекты после коммита
)

async def init_db():
    """
    Инициализирует базу данных: создает папки, если их нет, и все таблицы.
    """
    # Убедимся, что папка для базы данных существует
    db_dir = os.path.dirname(DATABASE_URL.replace("sqlite+aiosqlite:///./", ""))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    async with engine.begin() as conn:
        # Создаем все таблицы, определенные в Base (т.е. нашу таблицу 'stones')
        await conn.run_sync(Base.metadata.create_all)
    print("База данных инициализирована и таблицы созданы!")

async def get_db():
    """
    Функция-генератор для получения асинхронной сессии базы данных.
    Используется для зависимостей в других частях кода.
    """
    async with AsyncSessionLocal() as session:
        yield session

# Пример использования (можно удалить потом, или оставить для теста)
# async def main():
#     await init_db()
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())