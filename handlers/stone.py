# handlers/stone.py
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State # <-- Важно: убедитесь, что State импортирован
from database.models import User, Stone # Важно: Stone модель импортирована
from database.db import AsyncSessionLocal
from states.stone import StoneStates
from aiogram.types import ReplyKeyboardRemove # Для клавиатур

# Дополнительные импорты для API качества воздуха
import httpx
from config import OPENWEATHER_API_KEY # Важно: убедитесь, что OPENWEATHER_API_KEY импортирован и настроен в config.py

router = Router()
logger = logging.getLogger(__name__)

# --- Функция для получения качества воздуха ---
async def get_air_quality(latitude: float, longitude: float) -> tuple[int | None, str | None]:
    if not OPENWEATHER_API_KEY:
        logger.warning("OPENWEATHER_API_KEY not set in config.py. Skipping AQI request.")
        return None, "API ключ для OpenWeatherMap не настроен."

    api_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            response.raise_for_status()

            data = response.json()
            if data and "list" in data and len(data["list"]) > 0:
                aqi_index = data["list"][0]["main"]["aqi"]
                description_map = {
                    1: "Хорошее",
                    2: "Удовлетворительное",
                    3: "Умеренное",
                    4: "Плохое",
                    5: "Очень плохое"
                }
                aqi_description = description_map.get(aqi_index, "Неизвестно")
                return aqi_index, aqi_description
            else:
                logger.warning(f"No AQI data found for ({latitude}, {longitude}): {data}")
                return None, "Данные о качестве воздуха не найдены."
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching AQI for ({latitude}, {longitude}): {e.response.status_code} - {e.response.text}")
        return None, f"Ошибка при запросе качества воздуха (HTTP {e.response.status_code})."
    except httpx.RequestError as e:
        logger.error(f"Request error fetching AQI for ({latitude}, {longitude}): {e}")
        return None, "Ошибка сети при запросе качества воздуха."
    except Exception as e:
        logger.error(f"Unexpected error fetching AQI for ({latitude}, {longitude}): {e}")
        return None, "Неизвестная ошибка при запросе качества воздуха."

# --- Функция для отображения и подтверждения данных ---
async def display_and_confirm_stone_data(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    photo_id = user_data.get('photo_file_id', 'N/A')
    desc = user_data.get('description', 'N/A')
    lat = user_data.get('latitude', 'N/A')
    lon = user_data.get('longitude', 'N/A')
    alt = user_data.get('altitude', 'Н/Д') # Изменил 'N/A' на 'Н/Д' для русского
    aqi = user_data.get('air_quality_index', 'Н/Д')
    aq_desc = user_data.get('air_quality_description', 'Неизвестно') # Значение по умолчанию

    confirmation_text = (
        "Пожалуйста, проверьте данные:\n\n"
        f"📸 Фото ID: `{photo_id[:10]}...`\n" # Укоротим для читаемости
        f"📝 Описание: {desc}\n"
        f"📍 Локация: Широта {lat}, Долгота {lon}\n"
        f"⛰️ Высота: {alt} м.\n"
        f"💨 Качество воздуха (AQI): {aqi} ({aq_desc})\n\n" # Исправил aq_desc or 'Нет описания'
        "Все верно? Отправьте 'да' для сохранения или 'нет' для отмены."
    )
    await message.answer(confirmation_text, parse_mode='Markdown')
    await state.set_state(StoneStates.confirm_stone_data)
    logger.info(f"User {message.from_user.id} awaiting confirmation.")

# --- Хэндлеры для FSM StoneStates ---
@router.message(Command("add_stone"))
async def cmd_add_stone(message: types.Message, state: FSMContext):
    await message.answer("Отправьте, пожалуйста, фотографию камня.")
    await state.set_state(StoneStates.waiting_for_photo)
    logger.info(f"User {message.from_user.id} started adding a stone.")

@router.message(StoneStates.waiting_for_photo, F.photo)
async def process_stone_photo(message: types.Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id # Берем самое большое разрешение фото
    await state.update_data(photo_file_id=photo_file_id)
    await message.answer("Теперь отправьте описание камня (что это за камень, где найден и т.д.).")
    await state.set_state(StoneStates.waiting_for_description)
    logger.info(f"User {message.from_user.id} uploaded photo: {photo_file_id}")

@router.message(StoneStates.waiting_for_photo, ~F.photo)
async def process_stone_photo_invalid(message: types.Message):
    await message.answer("Это не фотография. Пожалуйста, отправьте фотографию камня.")
    logger.info(f"User {message.from_user.id} sent non-photo in waiting_for_photo state.")


@router.message(StoneStates.waiting_for_description, F.text)
async def process_stone_description(message: types.Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await message.answer("Отправьте, пожалуйста, местоположение камня (используйте кнопку 'Отправить местоположение').")
    await state.set_state(StoneStates.waiting_for_location)
    logger.info(f"User {message.from_user.id} provided description: {description[:50]}...")

@router.message(StoneStates.waiting_for_description, ~F.text)
async def process_stone_description_invalid(message: types.Message):
    await message.answer("Это не текстовое описание. Пожалуйста, отправьте описание камня.")
    logger.info(f"User {message.from_user.id} sent non-text in waiting_for_description state.")


@router.message(StoneStates.waiting_for_location, F.location)
async def process_stone_location(message: types.Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    await state.update_data(latitude=latitude, longitude=longitude)

    # Получаем качество воздуха здесь
    air_quality_index, air_quality_description = await get_air_quality(latitude, longitude)
    await state.update_data(
        air_quality_index=air_quality_index,
        air_quality_description=air_quality_description
    )
    logger.info(f"Got AQI: {air_quality_index} ({air_quality_description}) for ({latitude}, {longitude})")

    await message.answer("Хотите добавить высоту над уровнем моря? Отправьте число или 'пропустить'.", reply_markup=ReplyKeyboardRemove())
    await state.set_state(StoneStates.waiting_for_altitude)
    logger.info(f"User {message.from_user.id} provided location: ({latitude}, {longitude})")


@router.message(StoneStates.waiting_for_location, ~F.location)
async def process_stone_location_invalid(message: types.Message):
    await message.answer("Это не местоположение. Пожалуйста, отправьте местоположение камня.")
    logger.info(f"User {message.from_user.id} sent non-location in waiting_for_location state.")


@router.message(StoneStates.waiting_for_altitude)
async def process_stone_altitude(message: types.Message, state: FSMContext):
    altitude = None
    if message.text and message.text.lower() != 'пропустить':
        try:
            altitude = float(message.text)
        except ValueError:
            await message.answer("Неверный формат высоты. Пожалуйста, введите число или 'пропустить'.")
            return

    await state.update_data(altitude=altitude)
    # Переходим к подтверждению данных
    await display_and_confirm_stone_data(message, state)
    logger.info(f"User {message.from_user.id} provided altitude: {altitude}")

# --- Хэндлеры для подтверждения и сохранения ---
from sqlalchemy import select # Добавьте этот импорт в начало файла handlers/stone.py
@router.message(StoneStates.confirm_stone_data, F.text.lower() == 'да')
async def save_stone_data(message: types.Message, state: FSMContext, user_db: User):
    data = await state.get_data()

    required_fields = ['photo_file_id', 'description', 'latitude', 'longitude']
    if not all(field in data and data[field] is not None for field in required_fields):
        await message.answer("Ошибка: Не все обязательные данные для камня были собраны. Пожалуйста, начните заново /add_stone.")
        logger.error(f"Missing required fields for user {user_db.id}: {data}")
        await state.clear()
        return

    new_stone = Stone(
        creator_id=user_db.id,
        username=user_db.username,
        photo_file_id=data['photo_file_id'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        altitude=data.get('altitude'),
        air_quality_index=data.get('air_quality_index'),
        air_quality_description=data.get('air_quality_description'),
        description=data['description']
    )

    db_session = data.get("db_session")

    if not db_session:
        logger.error("Database session not found in state data.")
        await message.answer("Ошибка: Проблема с подключением к базе данных. Попробуйте позже.")
        await state.clear()
        return

    try:
        db_session.add(new_stone)
        await db_session.commit()
        await db_session.refresh(new_stone)
        await message.answer("Камень успешно добавлен!")
        logger.info(f"User {message.from_user.id} successfully added stone ID: {new_stone.id}")
    except Exception as e:
        await message.answer("Произошла ошибка при сохранении камня. Попробуйте еще раз.")
        logger.error(f"Error saving stone for user {message.from_user.id}: {e}")
        await db_session.rollback()
    finally:
        await state.clear()

@router.message(StoneStates.confirm_stone_data, F.text.lower() == 'нет')
async def cancel_confirm_stone_data(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Сохранение камня отменено.")
    logger.info(f"User {message.from_user.id} cancelled stone data confirmation.")

@router.message(StoneStates.confirm_stone_data)
async def confirm_stone_data_invalid(message: types.Message):
    await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")

# --- Хэндлер для команды /my_stones ---
@router.message(Command("my_stones"))
async def cmd_my_stones(message: types.Message, user_db: User, db_session: AsyncSessionLocal):
    if not user_db:
        await message.answer("Пожалуйста, начните с команды /start, чтобы я мог вас зарегистрировать.")
        return

    stmt = select(Stone).where(Stone.creator_id == user_db.id).order_by(Stone.created_at.desc())
    result = await db_session.execute(stmt)
    user_stones = result.scalars().all()

    if not user_stones:
        await message.answer("Вы еще не добавили ни одного камня. Используйте /add_stone, чтобы добавить первый!")
        return

    response_text = "<b>Ваши добавленные камни:</b>\n\n"
    for i, stone in enumerate(user_stones, 1):
        created_at_str = stone.created_at.strftime("%Y-%m-%d %H:%M") if stone.created_at else 'Н/Д'
        response_text += (
            f"<b>{i}. Камень ID:</b> <code>{stone.id}</code>\n"
            f"  <b>Описание:</b> {stone.description or '<i>Нет описания</i>'}\n"
            f"  <b>Координаты:</b> {stone.latitude:.4f}, {stone.longitude:.4f}\n"
            f"  <b>Высота:</b> {stone.altitude or '<i>Н/Д</i>'} м\n"
            f"  <b>AQI:</b> {stone.air_quality_index or '<i>Н/Д</i>'} ({stone.air_quality_description or '<i>Неизвестно</i>'})\n"
            f"  <b>Создан:</b> {created_at_str}\n"
            f"  <b>Фото ID:</b> <code>{stone.photo_file_id[:10] if stone.photo_file_id else '<i>Нет фото</i>'}...</code>\n\n"
        )
        # Если сообщение становится слишком длинным, отправляем его частями
        if len(response_text) > 3500 and i < len(user_stones):
            await message.answer(response_text, parse_mode='HTML')
            response_text = ""

    if response_text.strip():
        await message.answer(response_text, parse_mode='HTML')

    logger.info(f"User {user_db.id} requested their stones. Found {len(user_stones)} stones.")