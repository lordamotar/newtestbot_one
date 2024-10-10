from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

import app.keyboards as kb
import app.database.requests as rq

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(f'Добро пожаловать!', reply_markup=kb.main)


@router.message(F.text == 'Контакты')
async def catalog(message: Message):
    await message.answer('Выберите город', reply_markup=await kb.categories())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали город')
    await callback.message.answer('Выберите адрес',
                                  reply_markup=await kb.items(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('item_'))
async def category(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])
    await callback.answer('Вы выбрали адрес')
    await callback.message.answer(f'Город: {item_data.name}\nАдрес: {item_data.address}\nБудни: {item_data.weekdays_time}\nВыходной: {item_data.weekend_time}\nКонтакты: {item_data.contact}\nГео тег: {item_data.geo_link}')

@router.message(F.text == 'Сервис')
async def catalog(message: Message):
    await message.answer('Выберите город', reply_markup=await kb.categories())

@router.message(F.text == 'Сервис')
async def show_service_cities(message: Message):
    await message.answer('Выберите город для получения информации о сервисе', reply_markup=await kb.service_cities())

@router.callback_query(F.data.startswith('service_city_'))
async def show_service_addresses(callback: CallbackQuery):
    city_name = callback.data.split('_')[2]
    await callback.answer(f'Вы выбрали город: {city_name}')
    await callback.message.answer(f'Выберите адрес сервиса в городе {city_name}', 
                                  reply_markup=await kb.service_items(city_name))

@router.callback_query(F.data.startswith('service_item_'))
async def show_service_details(callback: CallbackQuery):
    service_id = callback.data.split('_')[2]
    service_data = await rq.get_item(service_id)
    await callback.answer(f'Вы выбрали адрес: {service_data.address}')
    await callback.message.answer(
        f'Город: {service_data.name}\n'
        f'Адрес: {service_data.address}\n'
        f'Будни: {service_data.weekdays_time}\n'
        f'Выходные: {service_data.weekend_time}\n'
        f'Контакты: {service_data.contact}\n'
        f'Гео тег: {service_data.geo_link}'
    )