import os
import aiohttp
import datetime
import base64
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Импортируем наши модели, движок и базовый класс из models.py
from models import Base, engine, User, Stone

# --- Инициализация и настройка ---

# Загружаем переменные из .env файла (токены)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
AIR_QUALITY_API_KEY = os.getenv("AIR_QUALITY_API_KEY")

# Инициализация FastAPI (для веб-сервера) и Aiogram (для бота)
app = FastAPI()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# "Монтируем" папку с фронтендом, чтобы сервер мог отдавать файлы CSS и JS
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# --- Логика Базы Данных ---

async def init_models():
    """Асинхронная функция для создания таблиц в базе данных при старте."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- Логика Telegram Бота ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    Этот хендлер вызывается на команду /start.
    Регистрирует пользователя и отправляет кнопку для открытия Web App.
    """
    # Регистрируем пользователя в БД, если его там еще нет
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        user_query = await session.execute(select(User).filter(User.telegram_id == message.from_user.id))
        user = user_query.scalar_one_or_none()
        if not user:
            new_user = User(telegram_id=message.from_user.id, username=message.from_user.username)
            session.add(new_user)
            await session.commit()

    # Создаем кнопку, которая открывает наше веб-приложение
    web_app_button = InlineKeyboardButton(
        text="🌍 Открыть карту",
        # ВАЖНО: Не забудьте вставить сюда ваш URL от ngrok!
        web_app=WebAppInfo(url="https://YOUR_NGROK_URL")
    )
    keyboard = InlineKeyboardMarkup().add(web_app_button)
    
    await message.answer(
        "Привет! Я помогу тебе оставлять цифровые 'камни' по всему миру. Нажми кнопку ниже, чтобы открыть карту.",
        reply_markup=keyboard
    )

# --- Логика API для веб-приложения ---

@app.get("/", response_class=FileResponse)
async def get_root():
    """Отдает главную HTML страницу нашего веб-приложения."""
    return FileResponse('frontend/index.html')

@app.post("/api/create_stone")
async def create_stone_api(data: dict = Body(...)):
    """API эндпоинт для создания нового камня."""
    try:
        telegram_id = data['telegram_id']
        
        # 1. Сохраняем фото из Base64 строки
        photo_base64 = data['photo']
        photo_path = f"user_photos/{telegram_id}_{int(datetime.datetime.now().timestamp())}.jpg"
        os.makedirs("user_photos", exist_ok=True)
        image_data = base64.b64decode(photo_base64.split(',')[1])
        with open(photo_path, "wb") as f:
            f.write(image_data)

        # 2. Получаем качество воздуха
        latitude = data['latitude']
        longitude = data['longitude']
        air_quality_index = await get_air_quality(latitude, longitude)
        
        # 3. Сохраняем в БД
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with AsyncSessionLocal() as session:
            new_stone = Stone(
                latitude=latitude,
                longitude=longitude,
                altitude=data.get('altitude'),
                photo_path=photo_path,
                air_quality_index=air_quality_index,
                creator_id=telegram_id
            )
            session.add(new_stone)
            await session.commit()
        
        return {"status": "ok", "message": "Камень успешно создан!"}
    except Exception as e:
        print(f"Error creating stone: {e}") # Выводим ошибку в консоль для отладки
        return {"status": "error", "message": str(e)}

async def get_air_quality(lat, lon):
    """Функция для получения данных о качестве воздуха с OpenWeatherMap."""
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={AIR_QUALITY_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data['list'][0]['main']['aqi']
    return None

# --- Запуск и настройка вебхуков ---

@app.on_event("startup")
async def on_startup():
    """При старте сервера, создаем таблицы и устанавливаем вебхук."""
    await init_models()
    # ВАЖНО: Не забудьте вставить сюда ваш URL от ngrok!
    webhook_url = f"https://YOUR_NGROK_URL/webhook"
    await bot.set_webhook(url=webhook_url)

@app.post("/webhook")
async def telegram_webhook(update: dict):
    """Принимаем обновления от Telegram и передаем их в aiogram."""
    telegram_update = types.Update(**update)
    await dp.process_update(telegram_update)
    return {"ok": True}

@app.on_event("shutdown")
async def on_shutdown():
    """При остановке сервера, удаляем вебхук."""
    await bot.delete_webhook()