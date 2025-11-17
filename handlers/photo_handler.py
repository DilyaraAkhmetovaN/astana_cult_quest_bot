import telebot
from telebot import types
import os
import cloudinary
import cloudinary.uploader

from database import save_user_photo_url, get_next_quest  # твои функции

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# --- Cloudinary config ---
cloudinary.config(
    cloud_name="dqw6v5rlg",
    api_key="693713551172145",
    api_secret="tlMIXfpI5OsdasNXQe7ey1Cb9As"
)


def register_photo_handler(bot):
    """
    Регистрируем обработчик фотографий.
    """

    @bot.message_handler(content_types=['photo'])
    def photo_handler(message):

        user_id = message.from_user.id

        # --- 1. Загружаем файл с Telegram ---
        try:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
        except Exception as e:
            print(f"ERROR: failed to download photo: {e}")
            bot.reply_to(message, "❌ Ошибка при загрузке фото.")
            return

        # --- 2. Загружаем фото в Cloudinary ---
        try:
            upload_result = cloudinary.uploader.upload(
                downloaded_file,
                folder=f"quest_bot/{user_id}/"
            )
            photo_url = upload_result.get("secure_url")
        except Exception as e:
            print(f"ERROR: Cloudinary upload failed: {e}")
            bot.reply_to(message, "❌ Не удалось загрузить фото в облако.")
            return

        # --- 3. Сохраняем URL в базе ---
        try:
            save_user_photo_url(user_id, photo_url)
        except Exception as e:
            print(f"ERROR: save photo URL failed: {e}")
            bot.reply_to(message, "❌ Ошибка сохранения фото.")
            return

        # --- 4. Получаем следующее задание ---
        try:
            next_quest_text, options = get_next_quest(user_id)

            if not next_quest_text:
                bot.send_message(user_id, "🎉 Квест завершён!")
                return

            print(f"DEBUG (one-time): next_quest_text={next_quest_text}, options={options}")

        except Exception as e:
            print(f"ERROR: get_next_quest failed: {e}")
            bot.send_message(user_id, "❌ Ошибка загрузки следующего задания.")
            return

        # --- 5. Формируем кнопки ---
        markup = types.InlineKeyboardMarkup()
        for option in options:
            markup.add(
                types.InlineKeyboardButton(
                    text=option,
                    callback_data=f"answer|{option}"
                )
            )

        # --- 6. Отправляем вопрос пользователю ---
        bot.send_message(
            user_id,
            f"{next_quest_text}\n\nВыбери правильный ответ:",
            reply_markup=markup
        )

        bot.send_message(
            user_id,
            "📸 Фото загружено! Переходим к следующему заданию."
        )
