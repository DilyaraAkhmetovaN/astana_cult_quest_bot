# handlers/start_handler.py
from telebot import types
import traceback
import cloudinary
import cloudinary.uploader
from utils.db_manager import add_user_if_not_exists, get_user_language, set_user_language, update_user, save_user_photo_url, update_user_photo_status
from utils.quest_manager import get_current_quest_text
from utils.keyboard_factory import create_inline_keyboard
from handlers.finish_handler import finish_game

cloudinary.config(
    cloud_name="dqw6v5rlg",
    api_key="693713551172145",
    api_secret="tlMIXfpI5OsdasNXQe7ey1Cb9As"
)

def register_start_handler(bot):
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
                bot.send_message(chat_id, "⚠️ Формат неверный, используйте: Имя, Возраст" if lang=="ru" else "⚠️ Деректерді келесідей енгізіңіз: Аты, Жасы")
                return

            name = parts[0]
            try:
                age = int(''.join(filter(str.isdigit, parts[1])))
            except ValueError:
                bot.send_message(chat_id, "⚠️ Введите возраст цифрами" if lang=="ru" else "⚠️ Жасты санмен енгізіңіз")
                return

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

    # Обработка фото после регистрации
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        telegram_id = message.from_user.id
        lang = get_user_language(telegram_id)
        try:
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

            bot.send_message(telegram_id, "🔥 Отлично! Фото принято." if lang=="ru" else "🔥 Керемет! Сурет қабылданды.")

            # Получаем следующий квест
            next_quest_text, options = get_current_quest_text(telegram_id, lang)
            print("DEBUG: next_quest_text=", next_quest_text, "options=", options)  # Отладка

            if next_quest_text:
                keyboard = create_inline_keyboard(options)
                bot.send_message(telegram_id, next_quest_text, reply_markup=keyboard)
            else:
                finish_game(bot, telegram_id)

        except Exception as e:
            print("❌ Ошибка при обработке фото:", e)
            traceback.print_exc()
            bot.send_message(telegram_id,
                             "❌ Произошла ошибка при обработке фото. Попробуйте снова." if lang=="ru" else
                             "❌ Суретті өңдеуде қате шықты. Қайталап көріңіз.")
