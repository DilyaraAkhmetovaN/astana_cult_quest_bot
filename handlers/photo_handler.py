# handlers/photo_handler.py
import os
import traceback
import telebot
from telebot.types import Message
from utils.db_manager import update_user_photo_status, save_user_photo_path
from utils.language_manager import get_user_language
from utils.quest_manager import get_current_quest_text
from utils.keyboard_factory import create_inline_keyboard

# Папка для сохранения фото
PHOTOS_DIR = "photos"
if not os.path.exists(PHOTOS_DIR):
    os.makedirs(PHOTOS_DIR)

def register_photo_handler(bot: telebot.TeleBot):
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message: Message):
        user_id = message.from_user.id

        try:
            # Получаем язык пользователя
            lang = get_user_language(user_id)

            # Сохраняем фото в папку
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_name = f"{user_id}_{file_info.file_id}.jpg"
            file_path = os.path.join(PHOTOS_DIR, file_name)

            with open(file_path, "wb") as f:
                f.write(downloaded_file)

            # Сохраняем путь к фото в БД
            save_user_photo_path(user_id, file_path)

            # Обновляем статус, что пользователь прислал фото
            update_user_photo_status(user_id, status=1)

            # Сообщение о принятии фото
            try:
                if lang == 'kk':
                    bot.send_message(user_id, "🔥 Керемет! Сурет қабылданды.")
                else:
                    bot.send_message(user_id, "🔥 Отлично! Фото принято.")
            except Exception as e:
                print("❌ Ошибка при отправке сообщения о принятии фото:", e)
                traceback.print_exc()

            # Получаем текст следующего квеста
            next_quest_text, options = get_current_quest_text(user_id, lang)

            if next_quest_text:
                try:
                    # Создаем инлайн-клавиатуру для вопросов/вариантов
                    keyboard = create_inline_keyboard(options)
                    bot.send_message(user_id, next_quest_text, reply_markup=keyboard)
                except Exception as e:
                    print("❌ Ошибка при отправке следующего квеста:", e)
                    traceback.print_exc()
            else:
                # Если квестов больше нет — завершаем игру
                try:
                    from handlers.finish_handler import finish_game
                    finish_game(bot, user_id)
                except Exception as e:
                    print("❌ Ошибка при завершении игры:", e)
                    traceback.print_exc()

        except Exception as e:
            print("❌ Общая ошибка в photo_handler:", e)
            traceback.print_exc()
