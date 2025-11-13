# handlers/photo_handler.py
import telebot
import traceback
from telebot.types import Message
import cloudinary
import cloudinary.uploader
from utils.db_manager import update_user_photo_status, save_user_photo_url, get_user_language
from utils.quest_manager import get_current_quest_text
from utils.keyboard_factory import create_inline_keyboard
from handlers.finish_handler import finish_game

# Настройка Cloudinary
cloudinary.config(
    cloud_name="YOUR_CLOUD_NAME",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET"
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

            # Получаем ссылку на загруженное фото
            file_url = upload_result.get("secure_url")
            if not file_url:
                raise Exception("Не удалось получить ссылку на фото из Cloudinary")

            # Сохраняем ссылку на фото в PostgreSQL
            save_user_photo_url(telegram_id, file_url)

            # Обновляем статус отправки фото
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
