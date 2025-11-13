# utils/db_manager.py
import psycopg2
from config import DATABASE_URL
import traceback

def get_connection():
    """Возвращает подключение к базе данных PostgreSQL"""
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def add_user_if_not_exists(telegram_id):
    """Добавляет пользователя, если он ещё не существует"""
    try:
        conn = get_connection()
        cur = conn.cursor()
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
        conn.commit()
    except Exception as e:
        print("❌ Ошибка в add_user_if_not_exists:", e)
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


def register_user(telegram_id, name, age):
    """Регистрирует пользователя с именем и возрастом"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET name=%s, age=%s WHERE telegram_id=%s",
            (name, age, telegram_id)
        )
        conn.commit()
    except Exception as e:
        print("❌ Ошибка в register_user:", e)
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


def set_user_language(telegram_id, lang):
    """Устанавливает язык пользователя"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET language=%s WHERE telegram_id=%s",
            (lang, telegram_id)
        )
        conn.commit()
    except Exception as e:
        print("❌ Ошибка в set_user_language:", e)
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


def get_user_language(telegram_id):
    """Получает язык пользователя"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT language FROM users WHERE telegram_id=%s", (telegram_id,))
        row = cur.fetchone()
        return row[0] if row else "ru"
    except Exception as e:
        print("❌ Ошибка в get_user_language:", e)
        traceback.print_exc()
        return "ru"
    finally:
        cur.close()
        conn.close()


def set_user_progress(telegram_id, progress):
    """Устанавливает текущий прогресс пользователя"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET progress=%s WHERE telegram_id=%s", (progress, telegram_id))
        conn.commit()
    except Exception as e:
        print("❌ Ошибка в set_user_progress:", e)
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


def get_user_progress(telegram_id):
    """Возвращает текущий прогресс пользователя"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT progress FROM users WHERE telegram_id=%s", (telegram_id,))
        row = cur.fetchone()
        return row[0] if row else 0
    except Exception as e:
        print("❌ Ошибка в get_user_progress:", e)
        traceback.print_exc()
        return 0
    finally:
        cur.close()
        conn.close()


def update_user_photo_status(telegram_id, status=1):
    """Обновляет статус отправки фото пользователем"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET photo_sent=%s WHERE telegram_id=%s", (status, telegram_id))
        conn.commit()
    except Exception as e:
        print("❌ Ошибка в update_user_photo_status:", e)
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


def mark_user_finished(telegram_id):
    """Отмечает пользователя как завершившего игру"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET finished=1 WHERE telegram_id=%s", (telegram_id,))
        conn.commit()
    except Exception as e:
        print("❌ Ошибка в mark_user_finished:", e)
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

def update_user(telegram_id, name=None, age=None):
    """Обновляет имя и/или возраст пользователя"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        if name is not None:
            cur.execute("UPDATE users SET name=%s WHERE telegram_id=%s", (name, telegram_id))
        if age is not None:
            cur.execute("UPDATE users SET age=%s WHERE telegram_id=%s", (age, telegram_id))
        conn.commit()
    except Exception as e:
        print("❌ Ошибка в update_user:", e)
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()



def save_user_photo_path(telegram_id, file_path):
    """Сохраняет путь к фото пользователя"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Создание таблицы фото, если её нет
        cur.execute("""
            CREATE TABLE IF NOT EXISTS photos (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(telegram_id),
                file_path TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Сохраняем путь к фото
        cur.execute(
            "INSERT INTO photos (user_id, file_path) VALUES (%s, %s)",
            (telegram_id, file_path)
        )
        conn.commit()
    except Exception as e:
        print("❌ Ошибка в save_user_photo_path:", e)
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()
