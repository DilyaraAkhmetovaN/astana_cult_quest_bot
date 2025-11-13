# bot.py
import os
from telebot import TeleBot
from config import TOKEN, DATABASE_URL
from handlers.start_handler import register_start_handler
from handlers.quest_handler import register_quest_handler
from handlers.photo_handler import register_photo_handler
from handlers.finish_handler import register_finish_handler
from utils.db_manager import add_user_if_not_exists, save_user_photo_path

# Создаем папку для фото, если нет
if not os.path.exists("photos"):
    os.makedirs("photos")

bot = TeleBot(TOKEN)

# Регистрируем обработчики
register_start_handler(bot)
register_quest_handler(bot)
register_photo_handler(bot)
register_finish_handler(bot)

# Обработчик фото, чтобы сохранять файл
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id

    try:
        # Берем лучшее качество фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Сохраняем в папку photos/
        file_name = f"photos/{user_id}_{message.photo[-1].file_id}.jpg"
        with open(file_name, "wb") as f:
            f.write(downloaded_file)

        # Сохраняем путь в БД
        save_user_photo_path(user_id, file_name)

    except Exception as e:
        print("❌ Ошибка при сохранении фото:", e)

if __name__ == "__main__":
    print("✅ Бот запущен и слушает команды...")
    try:
        bot.polling(non_stop=True, interval=0, timeout=30)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
