import view.keyboards as keyboards
import model.database as database
import telebot
from telebot import types
from PIL import Image
import io
import requests
import os
import uuid

class UserController:
    def __init__(self, bot):
        self.bot = bot
        self.products = database.get_products()
        self.user_states = {}