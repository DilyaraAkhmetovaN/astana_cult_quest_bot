# bot.py
import os
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

bot = TeleBot(TOKEN)

# Регистрируем все обработчики
register_start_handler(bot)
register_quest_handler(bot)
register_photo_handler(bot)
register_finish_handler(bot)

if __name__ == "__main__":
    print("✅ Бот запущен и слушает команды...")
    try:
        # Проверка на другие экземпляры бота перед запуском
        # Telegram API не разрешает одновременно несколько getUpdates
        bot.polling(non_stop=True, interval=0, timeout=30)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        traceback.print_exc()
