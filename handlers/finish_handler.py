# handlers/finish_handler.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db_manager import get_user_language
import traceback


def finish_game(bot, chat_id):
    """Финальное сообщение после завершения всех квестов"""
    try:
        lang = get_user_language(chat_id)

        if lang == "kk":
            text = (
                "🎉 Құттықтаймыз! Сіз барлық 10 нысанды өтіп, «Astana CULT QUEST» ойынын сәтті аяқтадыңыз!\n"
                "🏆 Сіздің мәртебеңіз: Ойынды аяқтаушы\n"
                "🎁 Сыйлық: Ұлттық музейге тегін кіру билеті\n"
                "📩 Сыйлық алу үшін төмендегі сілтемеге өтіп, өзіңіздің байланыс деректеріңізді қалдырыңыз:\n"
                "👇🏻 https://docs.google.com/forms/d/e/1FAIpQLSdeVVbaSjrWGWBgiQ8QBxDa7XHre6PnOxL9wiJjpO1u9x0Mvw/viewform?usp=header"
            )
        else:
            text = (
                "🎉 Поздравляем! Вы прошли все 10 объектов и успешно завершили квест «Astana CULT QUEST»!\n"
                "🏆 Ваш статус: Участник, завершивший игру\n"
                "🎁 Приз: Бесплатный билет в Национальный музей\n"
                "📩 Чтобы получить приз, перейдите по ссылке и оставьте свои контактные данные:\n"
                "👇🏻 https://docs.google.com/forms/d/e/1FAIpQLSdeVVbaSjrWGWBgiQ8QBxDa7XHre6PnOxL9wiJjpO1u9x0Mvw/viewform?usp=header"
            )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✅", callback_data="finish_ok"))

        try:
            bot.send_message(chat_id, text, reply_markup=keyboard)
        except Exception as e:
            print("❌ Ошибка при отправке финального сообщения:", e)
            traceback.print_exc()

    except Exception as e:
        print("❌ Ошибка в finish_game:", e)
        traceback.print_exc()


def register_finish_handler(bot):
    """Регистрирует обработчик кнопки завершения"""
    try:
        @bot.callback_query_handler(func=lambda call: call.data == "finish_ok")
        def handle_finish_ok(call):
            try:
                bot.answer_callback_query(call.id)
                lang = get_user_language(call.message.chat.id)
                if lang == "kk":
                    bot.send_message(call.message.chat.id, "✅ Рақмет! Сіздің өтініміңіз тіркелді. Ұйымдастырушылар жақын арада сізге хабарласады.")
                else:
                    bot.send_message(call.message.chat.id, "✅ Спасибо! Ваша заявка зарегистрирована. Организаторы свяжутся с вами в ближайшее время.")
            except Exception as e:
                print("❌ Ошибка при обработке кнопки 'finish_ok':", e)
                traceback.print_exc()
    except Exception as e:
        print("❌ Ошибка при регистрации finish_handler:", e)
        traceback.print_exc()
