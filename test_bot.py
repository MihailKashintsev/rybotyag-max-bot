# -*- coding: utf-8 -*-
"""Самопроверка разбора апдейтов MAX. Запуск: python3 test_bot.py"""
from bot import recipient_chat_id

# Реальный апдейт message_created, пойманный при отладке (chat_id живёт в message.recipient).
REAL_MESSAGE_CREATED = {
    "message": {
        "recipient": {"chat_type": "dialog", "chat_id": 451152440, "user_id": 448024929},
        "timestamp": 1788639617774,
        "body": {"mid": "mid.x", "seq": 1, "text": "Шкшкш"},
        "sender": {"user_id": 5266265, "first_name": "RENDER", "is_bot": False, "name": "RENDER"},
    },
    "timestamp": 1788639617774,
    "user_locale": "ru",
    "update_type": "message_created",
}

BOT_STARTED_TOP_LEVEL_CHAT_ID = {"update_type": "bot_started", "chat_id": 42, "user": {"user_id": 7}}

if __name__ == "__main__":
    assert recipient_chat_id(REAL_MESSAGE_CREATED) == 451152440
    assert recipient_chat_id(BOT_STARTED_TOP_LEVEL_CHAT_ID) == 42
    assert recipient_chat_id({"update_type": "bot_started", "user": {"user_id": 7}}) == 7
    print("OK: recipient_chat_id разбирает оба формата апдейтов")
