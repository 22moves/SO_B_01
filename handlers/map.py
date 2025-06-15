# handlers/map.py
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from keyboards.reply import share_location_keyboard
from aiogram.types import ReplyKeyboardRemove

router = Router()

logger = logging.getLogger(__name__)

user_waiting_for_location = {}

@router.message(Command("map"))
async def show_map_command(message: types.Message):
    user_waiting_for_location[message.from_user.id] = True
    logger.info(f"Пользователь {message.from_user.id} запросил /map. Теперь ждем локацию. user_waiting_for_location: {user_waiting_for_location}")
    await message.answer(
        "Чтобы показать камни на карте, пожалуйста, поделись своим текущим местоположением:",
        reply_markup=share_location_keyboard()
    )

@router.message(F.location) # <-- УБРАТЬ F.user.id.in_(...) ЗДЕСЬ
async def handle_location(message: types.Message):
    """
    Обработчик местоположения. Теперь проверяем флаг ожидания внутри функции.
    """
    # Проверяем, ждем ли мы локацию от этого пользователя
    if message.from_user.id not in user_waiting_for_location or not user_waiting_for_location[message.from_user.id]:
        logger.info(f"Локация от {message.from_user.id} получена, но не ожидалась. user_waiting_for_location: {user_waiting_for_location}")
        # Вы можете решить, что делать в этом случае: проигнорировать, ответить что-то,
        # или просто позволить echo_all обработать (если он ниже).
        return # Не обрабатываем это сообщение здесь, если не ожидали

    logger.info(f"Пользователь {message.from_user.id} отправил локацию. Состояние user_waiting_for_location: {user_waiting_for_location}")
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude

        await message.answer(
            f"Спасибо! Твое местоположение: Широта {latitude}, Долгота {longitude}.\n"
            f"Теперь я могу показать тебе камни на карте (в будущем).",
            reply_markup=ReplyKeyboardRemove()
        )
        user_waiting_for_location.pop(message.from_user.id, None)
        logger.info(f"Локация обработана для {message.from_user.id}. user_waiting_for_location: {user_waiting_for_location}")
    else:
        logger.warning(f"Получено сообщение, помеченное как локация, но message.location отсутствует для {message.from_user.id}.")
        await message.answer("Ошибка: Местоположение не найдено, хотя ожидалось.")


@router.message(F.text) # <-- УБРАТЬ F.user.id.in_(...) ЗДЕСЬ
async def handle_invalid_location_text(message: types.Message):
    """
    Обработчик текстовых сообщений, когда бот "ожидает" местоположение.
    """
    # Проверяем, ждем ли мы локацию от этого пользователя
    if message.from_user.id not in user_waiting_for_location or not user_waiting_for_location[message.from_user.id]:
        logger.info(f"Текст от {message.from_user.id} получен, но не ожидалась локация. user_waiting_for_location: {user_waiting_for_location}")
        return # Не обрабатываем это сообщение здесь, если не ожидали

    logger.info(f"Пользователь {message.from_user.id} отправил текст, когда ожидалась локация. user_waiting_for_location: {user_waiting_for_location}")
    await message.answer("Пожалуйста, отправьте мне ваше местоположение, используя кнопку внизу, или команду /start для перезапуска.")

# Общий хэндлер для всех остальных сообщений, если ни один другой не сработал
# Важно: этот хэндлер должен быть САМЫМ ПОСЛЕДНИМ в файле, чтобы он ловил только то, что не было поймано выше.
@router.message()
async def echo_all(message: types.Message):
    logger.info(f"Необработанное сообщение от {message.from_user.id}: {message.text or message.content_type}. user_waiting_for_location: {user_waiting_for_location}")
    # await message.answer("Извини, я не понял твое сообщение.")