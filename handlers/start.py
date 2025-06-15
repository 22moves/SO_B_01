# handlers/start.py
from aiogram import Router, types # <-- УБЕДИТЕСЬ, ЧТО Router И types ИМПОРТИРОВАНЫ
# from aiogram.fsm.context import FSMContext # <-- УДАЛИТЬ ЭТУ СТРОКУ
from aiogram.filters import CommandStart
from keyboards.reply import share_location_keyboard

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None: # <-- УДАЛИТЬ state: FSMContext и bot: Bot
    """
    Этот хэндлер реагирует на команду /start и отправляет приветственное сообщение
    с кнопкой для запроса местоположения.
    """
    # await state.clear() # <-- УДАЛИТЬ ЭТУ СТРОКУ
    await message.answer(
        "Привет! Я бот для управления камнями. Для начала, пожалуйста, поделись своим местоположением.",
        reply_markup=share_location_keyboard()
    )