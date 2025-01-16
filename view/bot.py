"""
Содержит объект бота Telegram.

Инициализирует объект бота с помощью токена, полученного от Telegram, из файла .env
Получает токен платёжного провайдера.
"""

import os

import telebot
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токены из переменной окружения
telegram_token = os.getenv("TELEGRAM_TOKEN")
payment_token = os.getenv("PAYMENT_PROVIDER_TOKEN")
# Проверяем, что токен получен
if not telegram_token:
    print(
        "Ошибка: Не найден токен TELEGRAM_TOKEN в .env файле или переменных окружения!"
    )
    exit()

if not payment_token:
    print(
        "Ошибка: Не найден токен PAYMENT_PROVIDER_TOKEN в .env файле или переменных окружения!"
    )
    exit()

# Инициализируем бота
bot = telebot.TeleBot(telegram_token)
"""
Объект бота Telegram.

Используется для взаимодействия с API Telegram, отправки сообщений,
обработки входящих сообщений и других операций.

:type: telebot.TeleBot
"""
