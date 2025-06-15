# keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    """
    Клавиатура с основными командами бота.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/add_stone"),
                KeyboardButton(text="/my_stones")
            ],
            [
                KeyboardButton(text="/map")
            ]
        ],
        resize_keyboard=True,   # Делает кнопки меньше
        one_time_keyboard=False # Клавиатура остается после использования
    )
    return keyboard

def share_location_keyboard():
    """
    Клавиатура для запроса местоположения.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отправить мое местоположение", request_location=True)
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True # Клавиатура скрывается после использования
    )
    return keyboard

def confirm_cancel_keyboard():
    """
    Клавиатура для подтверждения/отмены.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Да"),
                KeyboardButton(text="Нет")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard