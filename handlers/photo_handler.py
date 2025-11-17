# handlers/photo_handler.py
import telebot
import traceback
import cloudinary
import cloudinary.uploader
from telebot.types import Message
from utils.db_manager import save_user_photo_url, get_user_language
from utils.quest_manager import get_current_quest_text
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
        lang = get_user_language(telegram_id)

        try:
            # Берем фото наибольшего качества
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

            file_url = upload_result.get("secure_url")
            if not file_url:
                raise Exception("Не удалось получить URL фото из Cloudinary")

            # Сохраняем ссылку на фото в БД и отмечаем, что фото отправлено
            save_user_photo_url(telegram_id, file_url)

            # Сообщение пользователю о принятии фото
            bot.send_message(
                telegram_id,
                "🔥 Отлично! Фото принято." if lang == "ru" else "🔥 Керемет! Сурет қабылданды."
            )

            # Получаем текст следующего квеста и варианты
            next_quest_text, options = get_current_quest_text(telegram_id, lang)
            print("DEBUG: next_quest_text=", next_quest_text, "options=", options)

            if next_quest_text:
                keyboard = create_inline_keyboard(options)
                bot.send_message(telegram_id, next_quest_text, reply_markup=keyboard)
            else:
                # Если квестов больше нет — завершаем игру
                finish_game(bot, telegram_id)

        except Exception as e:
            print("❌ Ошибка в обработчике фото:", e)
            traceback.print_exc()
            try:
                bot.send_message(
                    telegram_id,
                    "❌ Произошла ошибка при обработке фото. Попробуйте снова." if lang == "ru" else
                    "❌ Суретті өңдеуде қате шықты. Қайталап көріңіз."
                )
            except Exception:
                pass
