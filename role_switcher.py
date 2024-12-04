from database import User
#from cryptography.fernet import Fernet
#import keyring
import admin_interface
import user_interface

class RoleSwitcher:
    def __init__(self, bot):
        self.bot = bot
        self.admin_interface_ = admin_interface.AdminInterface(bot)
        self.user_interface_ = user_interface.UserInterface(bot)
        self.register_handlers()
        self.user = User()

    def register_handlers(self):
        @self.bot.message_handler(commands=['admin'])
        def handle_admin(message):
            if self.user.is_admin(message.chat.id):
                # Сбрасываем состояние пользователя
                chat_id = message.chat.id
                if chat_id in self.admin_interface_.user_states:
                    self.admin_interface_.user_states[chat_id] = {}
                # Отображаем клавиатуру администратора
                self.bot.send_message(message.chat.id, 'Админ-панель:', reply_markup=self.admin_interface_.generate_main_keyboard())
                print(f"Admin panel accessed by chat_id: {chat_id}, state reset.")
            else:
                self.bot.send_message(message.chat.id,"Вы не администратор!")      
        
        @self.bot.message_handler(commands=['user'])
        def handle_user(message):
            # Сбрасываем состояние пользователя
            chat_id = message.chat.id
            if chat_id in self.user_interface_.user_states:
                self.user_interface_.user_states[chat_id] = {}
            # Отображаем клавиатуру юзера
            self.bot.send_message(message.chat.id, 'Юзер-панель:', reply_markup=self.user_interface_.generate_main_keyboard())
            print(f"User panel accessed by chat_id: {chat_id}, state reset.")


