from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_categories, get_category_item, get_service_cities, get_service_by_city

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Контакты')],
                                     [KeyboardButton(text='Сервис')],
                                     [KeyboardButton(text='Шины'),
                                      KeyboardButton(text='Диски')],
                                     [KeyboardButton(text='Чат с оператором'),
                                      KeyboardButton(text='О нас')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='back_to_main'))
    return keyboard.adjust(2).as_markup()


async def items(category_id):
    all_items = await get_category_item(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.address, callback_data=f"item_{item.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='back_to_main'))
    return keyboard.adjust(2).as_markup()

async def service_cities():
    all_cities = await get_service_cities()
    keyboard = InlineKeyboardBuilder()
    for city in all_cities:
        keyboard.add(InlineKeyboardButton(text=city, callback_data=f"service_city_{city}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='back_to_main'))
    return keyboard.adjust(2).as_markup()

async def service_items(city_name):
    services = await get_service_by_city(city_name)
    keyboard = InlineKeyboardBuilder()
    for service in services:
        keyboard.add(InlineKeyboardButton(text=service.address, callback_data=f"service_item_{service.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='back_to_main'))
    return keyboard.adjust(2).as_markup()
