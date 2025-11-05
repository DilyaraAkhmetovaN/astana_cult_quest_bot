# utils/quest_manager.py
import json
from config import QUESTS_FILE
from utils.db_manager import get_user_progress, set_user_progress, get_user_language

def load_quests():
    """Загружает все квесты из JSON-файла"""
    with open(QUESTS_FILE, encoding="utf-8") as f:
        return json.load(f)

def get_current_quest(chat_id):
    """
    Возвращает текущий квест пользователя в зависимости от языка.
    """
    quests = load_quests()
    progress = get_user_progress(chat_id)
    if progress >= len(quests):
        return None  # Все квесты пройдены

    # Получаем язык пользователя
    lang = get_user_language(chat_id)
    if lang not in ["kk", "ru"]:
        lang = "ru"  # По умолчанию русский

    quest = quests[progress].get(lang, {})

    return {
        "text": quest.get("text", ""),
        "options": quest.get("options", []),
        "correct": quest.get("correct", ""),
        "photo_task": quest.get("photo_task", ""),
    }

def advance_quest(chat_id):
    """Продвигает пользователя к следующему квесту"""
    progress = get_user_progress(chat_id)
    set_user_progress(chat_id, progress + 1)

def get_current_quest_text(chat_id):
    """Возвращает текст и варианты для инлайн-клавиатуры"""
    quest = get_current_quest(chat_id)
    if not quest:
        return None, None
    return quest["text"], quest["options"]

def is_last_quest(chat_id):
    """Проверяет, является ли текущий квест последним"""
    quests = load_quests()
    progress = get_user_progress(chat_id)
    return progress >= len(quests) - 1
