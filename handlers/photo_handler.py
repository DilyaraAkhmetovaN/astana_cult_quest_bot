# handlers/photo_handler.py
import os
import telebot
import traceback
from telebot.types import Message
from utils.db_manager import update_user_photo_status, save_user_photo_path, get_user_language
from utils.quest_manager import get_current_quest_text
from utils.keyboard_factory import create_inline_keyboard
from handlers.finish_handler import finish_game

# Папка для хранения фото
PHOTOS_DIR = "photos"
os.makedirs(PHOTOS_DIR, exist_ok=True)

def register_photo_handler(bot: telebot.TeleBot):
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message: Message):
        telegram_id = message.from_user.id

        try:
            # Берем фото с наибольшим разрешением
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Генерируем уникальное имя файла
            file_name = f"{telegram_id}_{photo.file_id}.jpg"
            file_path = os.path.join(PHOTOS_DIR, file_name)
            
            # Сохраняем файл на диск
            with open(file_path, "wb") as f:
                f.write(downloaded_file)

            # Сохраняем путь к фото в базе PostgreSQL
            save_user_photo_path(telegram_id, file_path)

            # Обновляем статус, что пользователь прислал фото
            update_user_photo_status(telegram_id, status=1)

            # Получаем язык пользователя
            lang = get_user_language(telegram_id)

            # Сообщение о принятии фото
            if lang == 'kk':
                bot.send_message(telegram_id, "🔥 Керемет! Сурет қабылданды.")
            else:
                bot.send_message(telegram_id, "🔥 Отлично! Фото принято.")

            # Получаем текст следующего квеста
            next_quest_text, options = get_current_quest_text(telegram_id, lang)

            if next_quest_text:
                # Создаем инлайн-клавиатуру для вариантов ответа
                keyboard = create_inline_keyboard(options)
                bot.send_message(telegram_id, next_quest_text, reply_markup=keyboard)
            else:
                # Если квестов больше нет — завершаем игру
                finish_game(bot, telegram_id)

        except Exception as e:
            print("❌ Ошибка в обработчике фото:", e)
            traceback.print_exc()
            try:
                bot.send_message(telegram_id, "❌ Произошла ошибка при обработке фото. Попробуйте снова.")
            except Exception:
                pass
