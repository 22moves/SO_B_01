# main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher, types # Убедитесь, что Router тоже импортирован здесь (это для dp)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
# from aiogram.fsm.storage.memory import MemoryStorage # <-- ЗАКОММЕНТИРОВАТЬ ЭТУ СТРОКУ
# from aiogram.fsm.middleware import FSMContextMiddleware # <-- ЗАКОММЕНТИРОВАТЬ ЭТУ СТРОКУ

from config import BOT_TOKEN
from database.db import init_db
from handlers.start import router as start_router
from handlers.map import router as map_router

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Инициализируем диспетчер (БЕЗ STORAGE)
dp = Dispatcher() # <-- УБРАТЬ storage=storage


# Зарегистрируем роутеры (обработчики)
dp.include_router(start_router)
dp.include_router(map_router)

# Простая функция для запуска бота
async def main() -> None:
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())