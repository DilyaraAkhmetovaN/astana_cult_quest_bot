import sqlite3
from config import DATABASE_PATH


def connect():
    """Подключение к базе данных"""
    conn = sqlite3.connect(DATABASE_PATH)
    return conn


def add_user_if_not_exists(chat_id):
    """Добавляет пользователя, если он ещё не существует"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            language TEXT DEFAULT 'ru',
            progress INTEGER DEFAULT 0,
            photo_sent INTEGER DEFAULT 0,
            finished INTEGER DEFAULT 0
        )
    """)
    cur.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()


def register_user(chat_id, name, age):
    """Регистрирует пользователя с именем и возрастом"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name=?, age=? WHERE chat_id=?", (name, age, chat_id))
    conn.commit()
    conn.close()


def set_user_language(chat_id, lang):
    """Сохраняет язык пользователя"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET language=? WHERE chat_id=?", (lang, chat_id))
    conn.commit()
    conn.close()


def get_user_language(chat_id):
    """Получает язык пользователя"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT language FROM users WHERE chat_id=?", (chat_id,))
    row = cur.fetchone()
    conn.close()
    if row and row[0]:
        return row[0]
    return "ru"  # Значение по умолчанию, если язык не установлен


def set_user_progress(chat_id, progress):
    """Устанавливает текущий прогресс пользователя"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET progress=? WHERE chat_id=?", (progress, chat_id))
    conn.commit()
    conn.close()


def get_user_progress(chat_id):
    """Возвращает текущий прогресс пользователя"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT progress FROM users WHERE chat_id=?", (chat_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def update_user_photo_status(chat_id, status=1):
    """Обновляет статус отправки фото пользователем"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET photo_sent=? WHERE chat_id=?", (status, chat_id))
    conn.commit()
    conn.close()


def mark_user_finished(chat_id):
    """Отмечает пользователя как завершившего игру"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET finished=1 WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()


def update_user(chat_id, name=None, age=None):
    """Обновляет имя и/или возраст пользователя"""
    conn = connect()
    cur = conn.cursor()
    if name is not None:
        cur.execute("UPDATE users SET name=? WHERE chat_id=?", (name, chat_id))
    if age is not None:
        cur.execute("UPDATE users SET age=? WHERE chat_id=?", (age, chat_id))
    conn.commit()
    conn.close()
