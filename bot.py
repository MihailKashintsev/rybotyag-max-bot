#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Бот для MAX, отвечающий на вопросы о товаре РЫБОТЯГ (ribotyag.ru).

Запуск:
    MAX_BOT_TOKEN=<токен от @MasterBot> python3 bot.py

Работает через long polling (GET /updates), без вебхука и своего сервера.
"""
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import certifi

from faq import match_faq

API_BASE = "https://platform-api2.max.ru"
POLL_TIMEOUT = 30
RUSSIAN_ROOT_CA = os.path.join(os.path.dirname(__file__), "russian_trusted_root_ca.pem")


def _build_ssl_context() -> ssl.SSLContext:
    # MAX использует сертификат от НУЦ Минцифры, которого нет в certifi/системном
    # хранилище — доверяем обычным CA (certifi) плюс этому конкретному корню.
    context = ssl.create_default_context(cafile=certifi.where())
    context.load_verify_locations(cafile=RUSSIAN_ROOT_CA)
    return context


SSL_CONTEXT = _build_ssl_context()
GREETING = (
    "Привет! Я отвечу на вопросы о трап-мосте РЫБОТЯГ: цена, характеристики, "
    "материал, как заказать и доставка, отзывы, инструкция. Просто спросите."
)


def api_request(method: str, path: str, token: str, params: dict = None, body: dict = None):
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", token)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=POLL_TIMEOUT + 10, context=SSL_CONTEXT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_message(token: str, chat_id, text: str):
    api_request("POST", "/messages", token, params={"chat_id": chat_id}, body={"text": text})


def recipient_chat_id(update: dict):
    """chat_id для message_created лежит в message.recipient.chat_id; для
    некоторых других событий (bot_started и т.п.) — на верхнем уровне update."""
    message = update.get("message") or {}
    chat_id = message.get("recipient", {}).get("chat_id")
    if chat_id is not None:
        return chat_id
    chat_id = update.get("chat_id")
    if chat_id is not None:
        return chat_id
    return (update.get("user") or {}).get("user_id")


def handle_update(token: str, update: dict):
    update_type = update.get("update_type")

    if update_type == "bot_started":
        chat_id = recipient_chat_id(update)
        if chat_id is not None:
            send_message(token, chat_id, GREETING)
        return

    if update_type != "message_created":
        return
    chat_id = recipient_chat_id(update)
    text = (update.get("message") or {}).get("body", {}).get("text")
    if chat_id is None or not text:
        return
    answer = match_faq(text)
    send_message(token, chat_id, answer)


def run(token: str):
    marker = None
    print("Бот запущен, жду сообщений...")
    while True:
        try:
            params = {"timeout": POLL_TIMEOUT}
            if marker is not None:
                params["marker"] = marker
            result = api_request("GET", "/updates", token, params=params)
            for update in result.get("updates", []):
                handle_update(token, update)
            marker = result.get("marker", marker)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"Сбой сети, повтор через 5с: {exc}", file=sys.stderr)
            time.sleep(5)
        except Exception as exc:  # noqa: BLE001 - бот не должен падать из-за одного плохого апдейта
            print(f"Ошибка обработки: {exc}", file=sys.stderr)
            time.sleep(1)


if __name__ == "__main__":
    bot_token = os.environ.get("MAX_BOT_TOKEN")
    if not bot_token:
        print("Задайте токен бота в переменной окружения MAX_BOT_TOKEN", file=sys.stderr)
        sys.exit(1)
    run(bot_token)
