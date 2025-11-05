# utils/keyboard_factory.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_inline_keyboard(options):
    """
    Создаёт инлайн-клавиатуру из списка опций
    :param options: список строк с вариантами ответа
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(text=opt, callback_data=opt) for opt in options]
    keyboard.add(*buttons)
    return keyboard

def create_start_language_keyboard():
    """Клавиатура для выбора языка при старте"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Қазақ тілі", callback_data="lang_kk"),
        InlineKeyboardButton("Русский язык", callback_data="lang_ru")
    )
    return keyboard

def create_start_game_button(lang="ru"):
    """Кнопка для начала игры после регистрации"""
    text = "Ойынды бастау" if lang == "kk" else "Начать игру"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text, callback_data="start_game"))
    return keyboard
