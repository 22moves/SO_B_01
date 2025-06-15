# states/stone.py
from aiogram.fsm.state import State, StatesGroup

class StoneStates(StatesGroup):
    """
    States for adding a new stone.
    """
    waiting_for_photo = State()        # Ожидание фотографии камня
    waiting_for_description = State()  # Ожидание описания камня
    waiting_for_location = State()     # Ожидание местоположения камня
    waiting_for_altitude = State()     # Ожидание высоты (необязательно)
    waiting_for_air_quality = State()  # Ожидание индекса качества воздуха (необязательно)
    confirm_stone_data = State()       # Подтверждение введенных данных