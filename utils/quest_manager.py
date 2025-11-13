# utils/quest_manager.py
import json
from config import QUESTS_FILE
from utils.db_manager import get_user_progress, set_user_progress, get_user_language

def load_quests():
    """Загружает все квесты из JSON-файла"""
    with open(QUESTS_FILE, encoding="utf-8") as f:
        return json.load(f)

def get_current_quest(telegram_id):
    """
    Возвращает текущий квест пользователя с учётом прогресса и языка.
    """
    quests = load_quests()
    progress = get_user_progress(telegram_id)
    if progress >= len(quests):
        return None  # Все квесты пройдены

    # Получаем язык пользователя
    lang = get_user_language(telegram_id)
    if lang not in ["kk", "ru"]:
        lang = "ru"  # По умолчанию русский

    quest_data = quests[progress].get(lang, {})
    return {
        "text": quest_data.get("text", ""),
        "options": quest_data.get("options", []),
        "correct": quest_data.get("correct", ""),
        "photo_task": quest_data.get("photo_task", ""),
    }

def get_current_quest_text(telegram_id, lang=None):
    """
    Возвращает текст квеста и варианты для инлайн-клавиатуры.
    Если передан lang, текст и варианты берутся для этого языка.
    """
    quest = get_current_quest(telegram_id)
    if not quest:
        return None, None

    # Если указан язык, проверяем, есть ли текст и опции для него
    if lang and lang in ["ru", "kk"]:
        quests = load_quests()
        progress = get_user_progress(telegram_id)
        quest_data = quests[progress].get(lang, {})
        text = quest_data.get("text", "")
        options = quest_data.get("options", [])
    else:
        text = quest["text"]
        options = quest["options"]

    return text, options

def advance_quest(telegram_id):
    """Продвигает пользователя к следующему квесту"""
    progress = get_user_progress(telegram_id)
    set_user_progress(telegram_id, progress + 1)

def is_last_quest(telegram_id):
    """Проверяет, является ли текущий квест последним"""
    quests = load_quests()
    progress = get_user_progress(telegram_id)
    return progress >= len(quests) - 1
