# bot.py
import os
from telebot import TeleBot
from config import TOKEN, DATABASE_URL
from handlers.start_handler import register_start_handler
from handlers.quest_handler import register_quest_handler
from handlers.photo_handler import register_photo_handler
from handlers.finish_handler import register_finish_handler
from utils.db_manager import add_user_if_not_exists, save_user_photo_url

# Создаем папку для фото, если нет
if not os.path.exists("photos"):
    os.makedirs("photos")

bot = TeleBot(TOKEN)

# Регистрируем обработчики
register_start_handler(bot)
register_quest_handler(bot)
register_photo_handler(bot)
register_finish_handler(bot)

if __name__ == "__main__":
    print("✅ Бот запущен и слушает команды...")
    try:
        bot.polling(non_stop=True, interval=0, timeout=30)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
