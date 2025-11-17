# handlers/start_handler.py
from telebot import types
import traceback
from utils.db_manager import add_user_if_not_exists, get_user_language, set_user_language, update_user
from handlers.quest_handler import send_quest
from handlers.finish_handler import finish_game

def register_start_handler(bot):
    """Регистрирует стартовую логику бота и регистрацию пользователей"""

    # /start — приветствие и выбор языка
    @bot.message_handler(commands=['start'])
    def start(message):
        try:
            chat_id = message.chat.id
            add_user_if_not_exists(chat_id)

            welcome_text = (
                "🇰🇿\n"
                "👋 Сәлем! «Astana CULT QUEST» интерактивті ойынына қош келдіңіз!\n"
                "🎯 *Мақсат:* қаламызды жаңа қырынан танып, мәдениетпен жақын танысу.\n\n"
                "🇷🇺\n"
                "👋 Привет! Добро пожаловать в интерактивную игру «Astana CULT QUEST»!\n"
                "🎯 *Цель:* узнать город с новой стороны и прикоснуться к культуре.\n\n"
                "🌐 Тілді таңдаңыз / Выберите язык:"
            )

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("🇰🇿 Қазақ тілі", callback_data="lang_kk"),
                types.InlineKeyboardButton("🇷🇺 Русский язык", callback_data="lang_ru")
            )

            bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)

        except Exception as e:
            print("❌ Ошибка в start_handler (/start):", e)
            traceback.print_exc()

    # Выбор языка
    @bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
    def language_choice(call):
        try:
            chat_id = call.message.chat.id
            lang = call.data.split("_")[1]
            set_user_language(chat_id, lang)

            text = (
                "Ойынды бастау үшін тіркеліңіз.\nАтыңызды және жасыңызды енгізіңіз:\n📌 Мысалы: Айгерім, 20 жас"
                if lang=="kk" else
                "Чтобы начать игру, зарегистрируйтесь.\nВведите ваше имя и возраст:\n📌 Например: Айгерим, 22 года"
            )
            bot.send_message(chat_id, text)

        except Exception as e:
            print("❌ Ошибка в start_handler (language_choice):", e)
            traceback.print_exc()

    # Ввод имени и возраста
    @bot.message_handler(func=lambda msg: "," in msg.text)
    def registration_done(message):
        try:
            chat_id = message.chat.id
            user_input = message.text.strip()
            lang = get_user_language(chat_id)
            if lang not in ["ru", "kk"]:
                lang = "ru"

            parts = [p.strip() for p in user_input.split(",", 1)]
            if len(parts) < 2:
                bot.send_message(chat_id,
                                 "⚠️ Формат неверный, используйте: Имя, Возраст" if lang=="ru"
                                 else "⚠️ Деректерді келесідей енгізіңіз: Аты, Жасы")
                return

            name = parts[0]
            try:
                age = int(''.join(filter(str.isdigit, parts[1])))
            except ValueError:
                bot.send_message(chat_id,
                                 "⚠️ Введите возраст цифрами" if lang=="ru"
                                 else "⚠️ Жасты санмен енгізіңіз")
                return

            update_user(chat_id, name=name, age=age)

            # Сообщение после успешной регистрации
            if lang == "kk":
                text = f"✅ Тіркеу сәтті өтті, {name}!\n\n🎮 Ойынды бастау үшін төмендегі батырманы басыңыз:"
                start_btn = "🎮 Ойынды бастау"
            else:
                text = f"✅ Регистрация прошла успешно, {name}!\n\n🎮 Нажмите кнопку ниже, чтобы начать игру:"
                start_btn = "🎮 Начать игру"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(start_btn, callback_data="start_game"))
            bot.send_message(chat_id, text, reply_markup=markup)

        except Exception as e:
            print("❌ Ошибка в start_handler (registration_done):", e)
            traceback.print_exc()
