from model.database import User
from view.keyboards import generate_admin_keyboard, generate_user_keyboard
import controller.admin_controller as admin_controller
import controller.user_controller as user_controller
import view.user_interface as user_interface
import model.orders as orders

class RoleSwitcher:
    def __init__(self, bot):
        self.bot = bot
        self.admin_controller_ = admin_controller.AdminController(bot)
        self.user_controller_ = user_controller.UserController(bot)
        self.user = User()
        orders.fill_orders_by_customer()

    def register_user(self, message):
        if self.user.is_new(message.chat.id):
            self.user.add_new(message.chat.id)
        self.bot.send_message(message.chat.id, 'Получена команда /start')
        print(message.chat.id)

    def choose_admin(self, message):
        if self.user.is_admin(message.chat.id):
            # Сбрасываем состояние пользователя
            chat_id = message.chat.id
            if chat_id in self.admin_controller_.user_states:
                self.admin_controller_.user_states[chat_id] = {}
            # Отображаем клавиатуру администратора
            self.bot.send_message(message.chat.id, 'Админ-панель:', reply_markup=generate_admin_keyboard())
            print(f"Admin panel accessed by chat_id: {chat_id}, state reset.")
        else:
            self.bot.send_message(message.chat.id,"Вы не администратор!")

    def choose_user(self, message):
        # Сбрасываем состояние пользователя
        chat_id = message.chat.id
        if chat_id in self.user_controller_.user_states:
            self.user_controller_.user_states[chat_id] = {}
        # Отображаем клавиатуру юзера
        self.bot.send_message(message.chat.id, 'Юзер-панель:', reply_markup=generate_user_keyboard())
        print(f"User panel accessed by chat_id: {chat_id}, state reset.")


