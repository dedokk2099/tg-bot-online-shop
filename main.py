from view.message_handlers import *
from view.bot import bot

if __name__ == "__main__":
    bot.polling(none_stop = True)