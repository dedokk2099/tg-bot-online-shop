from controller import admin_controller
from controller import user_controller
from model import orders
from model.database import User
from view.keyboards import generate_admin_keyboard, generate_user_keyboard


class RoleSwitcher:
    """
    По роли определяет пользователя и переключает на соответствующий интерфейс
    """

    def __init__(self, bot):
        """
        Инициализирует бот, корзину, интерфейсы пользователя и администратора, заполняются списки товаров и заказов
        """
        self.bot = bot
        self.admin_controller_ = admin_controller.AdminController(bot)
        self.user_controller_ = user_controller.UserController(bot)
        self.user = User()
        orders.fill_all_items()
        orders.fill_orders_by_customer()

    def register_user(self, message):
        """
        Проверяет наличие пользователя в базе, если его нет - записывает в базу
        """
        if self.user.is_new(message.chat.id):
            self.user.add_new(message.chat.id)
        self.bot.send_message(message.chat.id, "Получена команда /start")
        print(message.chat.id)

    def choose_admin(self, message):
        """
        Проверяет по идентификатору чата роль пользователя и если это администратор, то отображает соответствующий интерфейс
        """
        if self.user.is_admin(message.chat.id):
            # Сбрасываем состояние пользователя
            chat_id = message.chat.id
            if chat_id in self.admin_controller_.user_states:
                self.admin_controller_.user_states[chat_id] = {}
            # Отображаем клавиатуру администратора
            self.bot.send_message(
                message.chat.id, "Админ-панель:", reply_markup=generate_admin_keyboard()
            )
            print(f"Admin panel accessed by chat_id: {chat_id}, state reset.")
        else:
            self.bot.send_message(message.chat.id, "Вы не администратор!")

    def choose_user(self, message):
        """
        Отображает интерфейс пользователя
        """
        # Сбрасываем состояние пользователя
        chat_id = message.chat.id
        if chat_id in self.user_controller_.user_states:
            self.user_controller_.user_states[chat_id] = {}
        # Отображаем клавиатуру юзера
        self.bot.send_message(
            message.chat.id, "Юзер-панель:", reply_markup=generate_user_keyboard()
        )
        print(f"User panel accessed by chat_id: {chat_id}, state reset.")
