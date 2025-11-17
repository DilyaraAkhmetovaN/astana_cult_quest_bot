# handlers/photo_handler.py
import telebot
import traceback
from telebot.types import Message
import cloudinary
import cloudinary.uploader
from utils.db_manager import update_user_photo_status, save_user_photo_url, get_user_language
from utils.quest_manager import get_current_quest_text, advance_quest, is_last_quest
from utils.keyboard_factory import create_inline_keyboard
from handlers.finish_handler import finish_game

# Настройка Cloudinary
cloudinary.config(
    cloud_name="dqw6v5rlg",
    api_key="693713551172145",
    api_secret="tlMIXfpI5OsdasNXQe7ey1Cb9As"
)

def register_photo_handler(bot: telebot.TeleBot):
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message: Message):
        telegram_id = message.from_user.id

        try:
            # Берем фото с наибольшим разрешением
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Загружаем фото в Cloudinary
            upload_result = cloudinary.uploader.upload(
                downloaded_file,
                folder="astana_cult_quest",
                public_id=f"user_{telegram_id}_{photo.file_id}",
                overwrite=True
            )

            # Получаем ссылку
            file_url = upload_result.get("secure_url")
            save_user_photo_url(telegram_id, file_url)

            # Обновление статуса
            update_user_photo_status(telegram_id, status=1)

            # Язык пользователя
            lang = get_user_language(telegram_id)

            # Сообщение «Фото принято»
            if lang == 'kk':
                bot.send_message(telegram_id, "🔥 Керемет! Сурет қабылданды.")
            else:
                bot.send_message(telegram_id, "🔥 Отлично! Фото принято.")

            # ❗ ВАЖНО: переключаем квест на следующий
            advance_quest(telegram_id)

            # Если это был последний квест — финал
            if is_last_quest(telegram_id):
                return finish_game(bot, telegram_id)

            # Получаем текст следующего квеста
            next_text, options = get_current_quest_text(telegram_id, lang)

            if next_text:
                keyboard = create_inline_keyboard(options)
                bot.send_message(telegram_id, next_text, reply_markup=keyboard)
            else:
                finish_game(bot, telegram_id)

        except Exception as e:
            print("❌ Ошибка в обработчике фото:", e)
            traceback.print_exc()
            try:
                bot.send_message(telegram_id, "❌ Произошла ошибка при обработке фото. Попробуйте снова.")
            except Exception:
                pass
