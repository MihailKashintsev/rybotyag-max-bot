# -*- coding: utf-8 -*-
"""Самопроверка сопоставления вопросов с темами. Запуск: python3 test_faq.py"""
from faq import match_faq, DEFAULT_ANSWER

CASES = [
    ("Сколько стоит?", "9000"),
    ("а что это вообще такое", "трап-мост"),
    ("какие размеры", "0.7"),
    ("из какого материала сделан", "материала"),
    ("как заказать доставку", "ribotyag.ru"),
    ("есть отзывы?", "отзывы"),
    ("как им пользоваться", "видеоинструкция"),
    ("дайте номер телефона", "926 137-89-92"),
    ("сколько весит в чехле", "не указаны"),
    ("есть телеграм канал?", "t.me"),
    ("расскажи анекдот", DEFAULT_ANSWER),
]

if __name__ == "__main__":
    for question, expected_fragment in CASES:
        answer = match_faq(question)
        assert expected_fragment in answer, f"'{question}' -> '{answer}' (ждали фрагмент '{expected_fragment}')"
    print(f"OK: {len(CASES)} проверок прошли")
