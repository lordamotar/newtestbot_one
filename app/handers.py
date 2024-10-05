from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Привет! выбери действие для продолжения', reply_markup=kb.main)


@router.message(F.text == 'Адрса магазинов')
async def catalog(message: Message):
    await message.answer('Выберите город', reply_markup=await kb.categories())
    
    
@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Выберите город')
    await callback.message.answer('Выберите адрес',
                                  reply_markup=await kb.items(callback.data.split('_')[1]))