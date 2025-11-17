# handlers/quest_handler.py
import json
import traceback
from telebot import types
from utils.db_manager import get_user_progress, set_user_progress, get_user_language
from handlers.finish_handler import finish_game
from config import QUESTS_FILE

# Загружаем квесты один раз при старте
with open(QUESTS_FILE, encoding='utf-8') as f:
    quests = json.load(f)


def send_quest(chat_id, bot):
    """Отправляет текущее задание пользователю с кнопками и картинкой"""
    try:
        progress = get_user_progress(chat_id)
        lang = get_user_language(chat_id)
        if lang not in ["ru", "kk"]:
            lang = "ru"

        if progress >= len(quests):
            finish_game(bot, chat_id)
            return

        quest = quests[progress].get(lang, {})
        text = quest.get("text", "")
        options = quest.get("options", [])
        image_path = quest.get("image", None)

        if not text:
            bot.send_message(chat_id,
                             "⚠️ Квест табылмады!" if lang == "kk" else "⚠️ Ошибка: текст квеста не найден.")
            return

        keyboard = types.InlineKeyboardMarkup()
        for option in options:
            callback_data = f"answer_{option}_{progress}"
            keyboard.add(types.InlineKeyboardButton(text=option, callback_data=callback_data))

        if image_path:
            try:
                with open(image_path, 'rb') as img:
                    bot.send_photo(chat_id, photo=img, caption=text, reply_markup=keyboard)
            except Exception as e:
                print("❌ Ошибка при отправке картинки:", e)
                bot.send_message(chat_id, text, reply_markup=keyboard)
        else:
            bot.send_message(chat_id, text, reply_markup=keyboard)

    except Exception as e:
        print("❌ Ошибка в send_quest:", e)
        traceback.print_exc()


def register_quest_handler(bot):
    """Регистрирует обработчики квестов и ответов"""

    # Показать квест по команде /quest
    @bot.message_handler(commands=['quest'])
    def handle_quest_command(message):
        try:
            send_quest(message.chat.id, bot)
        except Exception as e:
            print("❌ Ошибка при вызове /quest:", e)
            traceback.print_exc()

    # Начало игры
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

    # Обработка ответов
    @bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
    def handle_answer(call):
        chat_id = call.message.chat.id
        try:
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
                # ✅ сначала обновляем прогресс
                set_user_progress(chat_id, progress + 1)

                bot.answer_callback_query(call.id, text="✅ Дұрыс!" if lang == "kk" else "✅ Верно!")
                if photo_task:
                    bot.send_message(chat_id,
                                     f"✅ Дұрыс! 📸 {photo_task}" if lang == "kk" else f"✅ Верно! 📸 {photo_task}")
                else:
                    # Если фото-задания нет, сразу отправляем следующий квест
                    send_quest(chat_id, bot)
            else:
                bot.answer_callback_query(call.id, text="❌ Қате!" if lang == "kk" else "❌ Неверно!")
                bot.send_message(chat_id,
                                 "Қайтадан байқап көріңіз!" if lang == "kk" else "Попробуйте ещё раз!")

        except Exception as e:
            print("❌ Ошибка в handle_answer:", e)
            traceback.print_exc()
