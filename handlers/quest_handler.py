# handlers/quest_handler.py
import json
import traceback
from telebot import types
from utils.db_manager import get_user_progress, set_user_progress, get_user_language
from config import QUESTS_FILE


# 🔹 Загружаем все квесты один раз при запуске
with open(QUESTS_FILE, encoding='utf-8') as f:
    quests = json.load(f)


def send_quest(chat_id, bot):
    """Отправляет текущее задание пользователю на нужном языке с картинкой"""
    try:
        progress = get_user_progress(chat_id)
        lang = get_user_language(chat_id)

        if lang not in ["ru", "kk"]:
            lang = "ru"

        # 🔸 Если квестов больше нет — завершение игры
        if progress >= len(quests):
            from handlers.finish_handler import finish_game
            finish_game(bot, chat_id)
            return

        # 🔸 Получаем текущий квест на нужном языке
        quest = quests[progress].get(lang, {})
        text = quest.get("text", "")
        options = quest.get("options", [])
        image_path = quest.get("image")  # путь к картинке из JSON

        if not text:
            bot.send_message(
                chat_id,
                "⚠️ Квест табылмады!" if lang == "kk" else "⚠️ Ошибка: текст квеста не найден."
            )
            return

        # 🔸 Создаем inline-кнопки с вариантами ответов
        keyboard = types.InlineKeyboardMarkup()
        for option in options:
            callback_data = f"answer_{option}_{progress}"
            keyboard.add(types.InlineKeyboardButton(text=option, callback_data=callback_data))

        # 🔸 Отправка картинки (если указана)
        if image_path:
            try:
                with open(image_path, 'rb') as img:
                    bot.send_photo(chat_id, photo=img, caption=text, reply_markup=keyboard)
            except Exception as e:
                print("❌ Ошибка при отправке картинки:", e)
                bot.send_message(chat_id, text, reply_markup=keyboard)
        else:
            # Если картинки нет, отправляем только текст
            bot.send_message(chat_id, text, reply_markup=keyboard)

    except Exception as e:
        print("❌ Ошибка в send_quest:", e)
        traceback.print_exc()


def register_quest_handler(bot):
    """Регистрирует обработчики квестов и ответов"""

    # 🔹 Команда /quest — показать текущее задание вручную
    @bot.message_handler(commands=['quest'])
    def handle_quest_command(message):
        try:
            send_quest(message.chat.id, bot)
        except Exception as e:
            print("❌ Ошибка при вызове /quest:", e)
            traceback.print_exc()

    # 🔹 Начало игры после регистрации
    @bot.callback_query_handler(func=lambda call: call.data == "start_game")
    def handle_start_game(call):
        chat_id = call.message.chat.id
        try:
            bot.answer_callback_query(call.id)
            set_user_progress(chat_id, 0)
            send_quest(chat_id, bot)
        except Exception as e:
            print("❌ Ошибка при старте игры:", e)
            traceback.print_exc()

    # 🔹 Обработка ответов игрока
    @bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
    def handle_answer(call):
        try:
            chat_id = call.message.chat.id
            data_parts = call.data.split("_")
            user_answer = data_parts[1]
            progress = int(data_parts[2])
            lang = get_user_language(chat_id)

            if lang not in ["ru", "kk"]:
                lang = "ru"

            quest = quests[progress].get(lang, {})
            correct_answer = quest.get("correct", "")
            photo_task = quest.get("photo_task", "")

            if user_answer == correct_answer:
                # ✅ Верный ответ
                bot.answer_callback_query(call.id, text="✅ Дұрыс!" if lang == "kk" else "✅ Верно!")
                bot.send_message(
                    chat_id,
                    f"✅ Дұрыс! 📸 {photo_task}" if lang == "kk" else f"✅ Верно! 📸 {photo_task}"
                )
                # Обновляем прогресс
                set_user_progress(chat_id, progress + 1)
            else:
                # ❌ Неверный ответ
                bot.answer_callback_query(call.id, text="❌ Қате!" if lang == "kk" else "❌ Неверно!")
                bot.send_message(
                    chat_id,
                    "Қайтадан байқап көріңіз!" if lang == "kk" else "Попробуйте ещё раз!"
                )

        except Exception as e:
            print("❌ Ошибка в handle_answer:", e)
            traceback.print_exc()

    # 🔹 После отправки фото пользователем
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        chat_id = message.chat.id
        try:
            lang = get_user_language(chat_id)
            bot.send_message(
                chat_id,
                "🔥 Керемет! Келесі аялдама:" if lang == "kk" else "🔥 Отлично! Следующая остановка:"
            )
            send_quest(chat_id, bot)
        except Exception as e:
            print("❌ Ошибка при обработке фото:", e)
            traceback.print_exc()
