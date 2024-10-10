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
