import psycopg
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg.connect(DATABASE_URL, sslmode="require")

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Таблица пользователей
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE,
        name TEXT,
        age INTEGER
    );
    ''')

    # Таблица фотографий
    cur.execute('''
    CREATE TABLE IF NOT EXISTS photos (
        id SERIAL PRIMARY KEY,
        user_id BIGINT REFERENCES users(telegram_id),
        file_path TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    conn.commit()
    cur.close()
    conn.close()
