from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

#from app.database.requests import get_cityes, get_cityes_item

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Шины 🛞')],
                                     [KeyboardButton(text='Диски 🛞')],
                                     [KeyboardButton(text='Сервис 🛠️'),
                                     KeyboardButton(text='Адрса магазинов')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')

