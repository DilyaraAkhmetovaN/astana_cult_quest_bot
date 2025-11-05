from telebot import types
import traceback
from utils.db_manager import add_user_if_not_exists, get_user_language, set_user_language, update_user


def register_start_handler(bot):
    # Команда /start — приветствие и выбор языка
    @bot.message_handler(commands=['start'])
    def start(message):
        try:
            chat_id = message.chat.id
            add_user_if_not_exists(chat_id)

            # Приветственное сообщение на двух языках
            welcome_text = (
                "🇰🇿\n"
                "👋 Сәлем! «Astana CULT QUEST» интерактивті ойынына қош келдіңіз!\n"
                "Бұл ойын арқылы сіз Астананың мәдени және тарихи нысандарын аралап, қызықты тапсырмаларды орындайсыз.\n"
                "🎯 *Мақсат:* қаламызды жаңа қырынан танып, мәдениетпен жақын танысу.\n"
                "Бұл ойын «Тарих және мәдениет саласындағы волонтерлікті дамыту» жобасы аясында жүзеге асырылуда.\n\n"
                "🇷🇺\n"
                "👋 Привет! Добро пожаловать в интерактивную игру «Astana CULT QUEST»!\n"
                "С помощью этой игры вы посетите культурные и исторические объекты Астаны и выполните увлекательные задания.\n"
                "🎯 *Цель:* узнать город с новой стороны и прикоснуться к культуре.\n"
                "Игра проводится в рамках проекта «Развитие волонтёрства в сфере истории и культуры».\n\n"
                "🌐 Тілді таңдаңыз / Выберите язык:"
            )

            # Кнопки выбора языка
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("🇰🇿 Қазақ тілі", callback_data="lang_kk"),
                types.InlineKeyboardButton("🇷🇺 Русский язык", callback_data="lang_ru")
            )

            bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)

        except Exception as e:
            print("❌ Ошибка в start_handler (/start):", e)
            traceback.print_exc()

    # Выбор языка пользователем
    @bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
    def language_choice(call):
        try:
            chat_id = call.message.chat.id
            lang = call.data.split("_")[1]
            set_user_language(chat_id, lang)

            if lang == "kk":
                text = (
                    "👋 Сәлем! «Astana CULT QUEST» ойынына қош келдіңіз!\n\n"
                    "Ойынды бастау үшін тіркеліңіз.\n"
                    "Атыңызды және жасыңызды енгізіңіз:\n📌 Мысалы: Айгерім, 20 жас"
                )
            else:
                text = (
                    "👋 Привет! Добро пожаловать в игру «Astana CULT QUEST»!\n\n"
                    "Чтобы начать игру, зарегистрируйтесь.\n"
                    "Введите ваше имя и возраст:\n📌 Например: Айгерим, 22 года"
                )

            bot.send_message(chat_id, text)

        except Exception as e:
            print("❌ Ошибка в start_handler (language_choice):", e)
            traceback.print_exc()

    # Обработка имени и возраста
    @bot.message_handler(func=lambda msg: "," in msg.text)
    def registration_done(message):
        try:
            chat_id = message.chat.id
            user_input = message.text.strip()
            lang = get_user_language(chat_id)
            if lang not in ["ru", "kk"]:
                lang = "ru"

            # Проверка правильности формата
            if "," not in user_input:
                if lang == "kk":
                    bot.send_message(chat_id, "⚠️ Деректерді келесідей енгізіңіз: Айгерім, 20 жас")
                else:
                    bot.send_message(chat_id, "⚠️ Введите данные в формате: Айгерим, 22 года")
                return

            # Разделяем имя и возраст
            parts = [p.strip() for p in user_input.split(",", 1)]
            name = parts[0]
            age = parts[1] if len(parts) > 1 else ""

            # Сохраняем данные пользователя
            update_user(chat_id, name=name, age=age)

            # Сообщение после успешной регистрации
            if lang == "kk":
                text = (
                    f"✅ Тіркеу сәтті өтті, {name}!\n\n"
                    "🎮 Ойынды бастау үшін төмендегі батырманы басыңыз:"
                )
                start_btn = "🎮 Ойынды бастау"
            else:
                text = (
                    f"✅ Регистрация прошла успешно, {name}!\n\n"
                    "🎮 Нажмите кнопку ниже, чтобы начать игру:"
                )
                start_btn = "🎮 Начать игру"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(start_btn, callback_data="start_game"))
            bot.send_message(chat_id, text, reply_markup=markup)

        except Exception as e:
            print("❌ Ошибка в start_handler (registration_done):", e)
            traceback.print_exc()
