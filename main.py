from view.message_handlers import *
from view.bot import bot
import model.orders as orders

if __name__ == "__main__":
    orders.fill_orders_by_customer()
    
    bot.polling(none_stop = True)