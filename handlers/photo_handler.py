# handlers/photo_handler.py
import telebot
import traceback
from telebot.types import Message
from utils.db_manager import update_user_photo_status
from utils.language_manager import get_user_language
from utils.quest_manager import get_current_quest_text
from utils.keyboard_factory import create_inline_keyboard


def register_photo_handler(bot: telebot.TeleBot):
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message: Message):
        user_id = message.from_user.id

        try:
            # Обновляем статус, что пользователь прислал фото
            update_user_photo_status(user_id, status=1)

            # Получаем язык пользователя
            lang = get_user_language(user_id)

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
