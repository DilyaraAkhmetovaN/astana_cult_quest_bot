# utils/db_manager.py
import psycopg
from config import DATABASE_URL
import traceback
from datetime import datetime


def get_connection():
    """Возвращает подключение к базе данных PostgreSQL"""
    return psycopg.connect(DATABASE_URL, autocommit=True)


def add_user_if_not_exists(telegram_id):
    """Добавляет пользователя, если он ещё не существует"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Создание таблицы пользователей
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        telegram_id BIGINT PRIMARY KEY,
                        name TEXT,
                        age INTEGER,
                        language TEXT DEFAULT 'ru',
                        progress INTEGER DEFAULT 0,
                        photo_sent INTEGER DEFAULT 0,
                        finished INTEGER DEFAULT 0
                    );
                """)
                # Добавляем пользователя, если его нет
                cur.execute(
                    "INSERT INTO users (telegram_id) VALUES (%s) ON CONFLICT (telegram_id) DO NOTHING",
                    (telegram_id,)
                )
    except Exception as e:
        print("❌ Ошибка в add_user_if_not_exists:", e)
        traceback.print_exc()


def register_user(telegram_id, name, age):
    """Регистрирует пользователя с именем и возрастом"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET name=%s, age=%s WHERE telegram_id=%s",
                    (name, age, telegram_id)
                )
    except Exception as e:
        print("❌ Ошибка в register_user:", e)
        traceback.print_exc()


def set_user_language(telegram_id, lang):
    """Устанавливает язык пользователя"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET language=%s WHERE telegram_id=%s",
                    (lang, telegram_id)
                )
    except Exception as e:
        print("❌ Ошибка в set_user_language:", e)
        traceback.print_exc()


def get_user_language(telegram_id):
    """Получает язык пользователя"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT language FROM users WHERE telegram_id=%s", (telegram_id,))
                row = cur.fetchone()
                return row[0] if row else "ru"
    except Exception as e:
        print("❌ Ошибка в get_user_language:", e)
        traceback.print_exc()
        return "ru"


def set_user_progress(telegram_id, progress):
    """Устанавливает текущий прогресс пользователя"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET progress=%s WHERE telegram_id=%s", (progress, telegram_id))
    except Exception as e:
        print("❌ Ошибка в set_user_progress:", e)
        traceback.print_exc()


def get_user_progress(telegram_id):
    """Возвращает текущий прогресс пользователя"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT progress FROM users WHERE telegram_id=%s", (telegram_id,))
                row = cur.fetchone()
                return row[0] if row else 0
    except Exception as e:
        print("❌ Ошибка в get_user_progress:", e)
        traceback.print_exc()
        return 0


def update_user_photo_status(telegram_id, status=1):
    """Обновляет статус отправки фото пользователем"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET photo_sent=%s WHERE telegram_id=%s", (status, telegram_id))
    except Exception as e:
        print("❌ Ошибка в update_user_photo_status:", e)
        traceback.print_exc()


def mark_user_finished(telegram_id):
    """Отмечает пользователя как завершившего игру"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET finished=1 WHERE telegram_id=%s", (telegram_id,))
    except Exception as e:
        print("❌ Ошибка в mark_user_finished:", e)
        traceback.print_exc()


def update_user(telegram_id, name=None, age=None):
    """Обновляет имя и/или возраст пользователя"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if name is not None:
                    cur.execute("UPDATE users SET name=%s WHERE telegram_id=%s", (name, telegram_id))
                if age is not None:
                    # Преобразуем возраст к числу, если он в формате "22 года" или "20 жас"
                    try:
                        age_int = int(''.join(filter(str.isdigit, str(age))))
                    except ValueError:
                        age_int = None
                    if age_int is not None:
                        cur.execute("UPDATE users SET age=%s WHERE telegram_id=%s", (age_int, telegram_id))
    except Exception as e:
        print("❌ Ошибка в update_user:", e)
        traceback.print_exc()


def save_user_photo_url(telegram_id, url):
    """Сохраняет URL фото пользователя (Cloudinary)"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Создание таблицы фото, если её нет
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS photos (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT REFERENCES users(telegram_id),
                        url TEXT,
                        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Сохраняем URL
                cur.execute(
                    "INSERT INTO photos (user_id, url) VALUES (%s, %s)",
                    (telegram_id, url)
                )
    except Exception as e:
        print("❌ Ошибка в save_user_photo_url:", e)
        traceback.print_exc()
