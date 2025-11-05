import json
from config import LANG_KK_PATH, LANG_RU_PATH

# Загружаем тексты из файлов
with open(LANG_KK_PATH, encoding='utf-8') as f:
    texts_kk = json.load(f)

with open(LANG_RU_PATH, encoding='utf-8') as f:
    texts_ru = json.load(f)

# Словарь для хранения выбранного языка пользователей
user_languages = {}  # {user_id: 'kk' или 'ru'}

def set_user_language(user_id, language_code):
    """
    Устанавливаем язык пользователя.
    language_code: 'kk' или 'ru'
    """
    if language_code not in ['kk', 'ru']:
        raise ValueError("Unsupported language code")
    user_languages[user_id] = language_code

def get_user_language(user_id):
    """
    Получаем язык пользователя. По умолчанию 'ru'.
    """
    return user_languages.get(user_id, 'ru')

def get_text(user_id, key):
    """
    Получаем текст для пользователя по ключу в выбранном языке.
    key: ключ из texts_kk.json / texts_ru.json
    """
    lang = get_user_language(user_id)
    if lang == 'kk':
        return texts_kk.get(key, "")
    return texts_ru.get(key, "")
