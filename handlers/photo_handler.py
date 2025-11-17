# handlers/photo_handler.py
import telebot
import traceback
import cloudinary
import cloudinary.uploader
from telebot.types import Message
from utils.db_manager import update_user_photo_status, save_user_photo_url, get_user_language, get_user_progress
from handlers.quest_handler import send_quest
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
            lang = get_user_language(telegram_id)
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            upload_result = cloudinary.uploader.upload(
                downloaded_file,
                folder="astana_cult_quest",
                public_id=f"user_{telegram_id}_{photo.file_id}",
                overwrite=True
            )

            file_url = upload_result.get("secure_url")
            if not file_url:
                raise Exception("Не удалось получить URL фото из Cloudinary")

            save_user_photo_url(telegram_id, file_url)
            update_user_photo_status(telegram_id, status=1)

            bot.send_message(
                telegram_id,
                "🔥 Керемет! Келесі аялдама:" if lang == "kk" else "🔥 Отлично! Следующая остановка:"
            )

            # Отправляем следующий квест после фото
            send_quest(telegram_id, bot)

            print(f"DEBUG: Фото загружено, прогресс={get_user_progress(telegram_id)}")

        except Exception as e:
            print("❌ Ошибка в обработчике фото:", e)
            traceback.print_exc()
            try:
                bot.send_message(telegram_id,
                                 "❌ Суретті өңдеуде қате шықты. Қайталап көріңіз." if lang == "kk" else
                                 "❌ Произошла ошибка при обработке фото. Попробуйте снова.")
            except Exception:
                pass
