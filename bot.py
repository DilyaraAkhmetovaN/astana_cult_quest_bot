# bot.py
import os
import time
import traceback
from telebot import TeleBot
from config import TOKEN
from handlers.start_handler import register_start_handler
from handlers.quest_handler import register_quest_handler
from handlers.photo_handler import register_photo_handler
from handlers.finish_handler import register_finish_handler

# Создаем папку для временного хранения фото, если нужно
if not os.path.exists("photos"):
    os.makedirs("photos")

bot = TeleBot(TOKEN, threaded=True, num_threads=5)

# Регистрируем все обработчики
register_start_handler(bot)
register_quest_handler(bot)
register_photo_handler(bot)
register_finish_handler(bot)

if __name__ == "__main__":
    print("✅ Бот запущен и слушает команды...")

    while True:
        try:
            bot.polling(
                non_stop=True,
                interval=0,
                timeout=20,
                long_polling_timeout=30,
                allowed_updates=None
            )
        except Exception as e:
            print("⚠️ Ошибка polling:", e)
            traceback.print_exc()
            time.sleep(3)  # Подождать и перезапустить
