"""
Точка входа для запуска бота.

Импортирует обработчики сообщений и объект бота, а затем запускает
процесс непрерывного опроса для обработки входящих сообщений.
"""

from view.bot import bot
from view.message_handlers import *

if __name__ == "__main__":
    """
    Запускает процесс непрерывного опроса бота.

    Метод ``bot.polling(none_stop=True)`` запускает бота в режиме
    непрерывного ожидания входящих сообщений.

    """
    bot.polling(none_stop=True)
