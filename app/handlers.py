from aiogram import F, Router, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
    InlineKeyboardButton
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.keyboards as kb
import app.database.requests as rq
from config import MANAGER_ID

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Добро пожаловать!', reply_markup=kb.main)


@router.message(F.text == 'Контакты')
async def catalog(message: Message):
    await message.answer('Выберите город', reply_markup=await kb.categories())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали город')
    await callback.message.answer(
        'Выберите адрес',
        reply_markup=await kb.items(callback.data.split('_')[1])
    )


@router.callback_query(F.data.startswith('item_'))
async def show_item_details(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])
    await callback.answer('Вы выбрали адрес')
    await callback.message.answer(
        f'Город: {item_data.name}\n'
        f'Адрес: {item_data.address}\n'
        f'Будни: {item_data.weekdays_time}\n'
        f'Выходной: {item_data.weekend_time}\n'
        f'Контакты: {item_data.contact}\n'
        f'Гео тег: {item_data.geo_link}'
    )


@router.message(F.text == 'Сервис')
async def show_service_cities(message: Message):
    await message.answer(
        'Выберите город для получения информации о сервисе',
        reply_markup=await kb.service_cities()
    )


@router.callback_query(F.data.startswith('service_city_'))
async def show_service_addresses(callback: CallbackQuery):
    city_name = callback.data.split('_')[2]
    await callback.answer(f'Вы выбрали город: {city_name}')
    await callback.message.answer(
        f'Выберите адрес сервиса в городе {city_name}',
        reply_markup=await kb.service_items(city_name)
    )


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


class FeedbackState(StatesGroup):
    waiting_for_message = State()
    in_chat = State()


@router.message(F.text == 'Связаться с менеджером')
async def start_feedback(message: Message, state: FSMContext):
    await state.set_state(FeedbackState.waiting_for_message)
    await message.answer(
        'Напишите ваше сообщение для менеджера.\n'
        'Мы свяжемся с вами в ближайшее время.',
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.reply_to_message, F.from_user.id == MANAGER_ID)
async def manager_reply(message: Message, state: FSMContext, bot: Bot):
    """Обработчик ответа менеджера на сообщение клиента"""
    try:
        # Получаем ID клиента из текста сообщения
        client_message = message.reply_to_message.text
        if "Новое сообщение от пользователя" in client_message:
            # Извлекаем user_id из сообщения
            user_id = client_message.split("@")[1].split(":")[0]

            # Устанавливаем состояние чата
            await state.set_state(FeedbackState.in_chat)
            await state.update_data(client_id=user_id)

            # Отправляем сообщения обоим участникам
            await bot.send_message(
                user_id,
                "Менеджер присоединился к чату и ответил:\n" + message.text
            )
            await message.answer(
                "Чат начат. Теперь вы можете общаться с клиентом напрямую.\n"
                "Для завершения чата используйте команду /end"
            )
        else:
            # Если это уже активный чат, просто пересылаем сообщение
            data = await state.get_data()
            if data.get("client_id"):
                await bot.send_message(data["client_id"], message.text)

    except Exception as e:
        print(f"Ошибка при начале чата: {e}")
        await message.answer(
            "Ошибка при начале чата. "
            "Убедитесь, что отвечаете на первое сообщение клиента"
        )


@router.callback_query(F.data.startswith("accept_chat:"))
async def accept_chat(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if str(callback.from_user.id) != MANAGER_ID:
        return

    user_id = callback.data.split(":")[1]
    print(f"Debug: принятие чата для пользователя {user_id}")

    # Устанавливаем состояние для менеджера
    await state.set_state(FeedbackState.in_chat)
    await state.update_data(client_id=user_id)

    # Создаем новый FSMContext для клиента и устанавливаем состояние
    client_state = FSMContext(
        storage=state.storage,
        key=f"user_{user_id}"  # Добавляем префикс user_ к ключу
    )
    await client_state.set_state(FeedbackState.in_chat)
    await client_state.update_data(client_id=MANAGER_ID)

    print("Debug: состояние установлено для менеджера и клиента")

    # Уведомляем менеджера
    await callback.message.edit_text(
        callback.message.text +
        "\n\nЧат принят. Можете отвечать на сообщения клиента.",
        reply_markup=None
    )

    # Уведомляем клиента
    await bot.send_message(
        user_id,
        "Менеджер принял ваш чат. Теперь вы можете общаться с менеджером.",
        reply_markup=kb.main  # Возвращаем основную клавиатуру
    )


@router.message(FeedbackState.in_chat)
async def handle_chat_message(message: Message, state: FSMContext, bot: Bot):
    """Обработчик сообщений в активном чате"""
    data = await state.get_data()
    client_id = data.get("client_id")

    print(f"Debug: получено сообщение от {message.from_user.id}")
    print(f"Debug: текущее состояние чата: {data}")

    if not client_id:
        print("Debug: client_id не найден в состоянии")
        await message.answer(
            "Ошибка: чат не активен",
            reply_markup=kb.main
        )
        await state.clear()
        return

    try:
        if str(message.from_user.id) == MANAGER_ID:
            # Сообщение от менеджера клиенту
            print(f"Debug: отправка сообщения клиенту {client_id}")
            await bot.send_message(client_id, message.text)
            await message.answer("✓ Сообщение отправлено клиенту")
        else:
            # Сообщение от клиента менеджеру
            print(f"Debug: отправка сообщения менеджеру {MANAGER_ID}")
            await bot.send_message(
                MANAGER_ID,
                f"Сообщение от клиента {message.from_user.id}:\n{message.text}"
            )
            await message.answer("✓ Сообщение отправлено менеджеру")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")
        await message.answer(
            "Ошибка при отправке сообщения. Попробуйте позже.",
            reply_markup=kb.main
        )


@router.message(Command("end"))
async def end_chat(message: Message, state: FSMContext, bot: Bot):
    if str(message.from_user.id) != MANAGER_ID:
        return

    data = await state.get_data()
    client_id = data.get("client_id")
    if client_id:
        # Очищаем состояние клиента
        client_state = FSMContext(storage=state.storage, key=client_id)
        await client_state.clear()

        # Отправляем уведомления
        await bot.send_message(
            client_id,
            "Чат завершен менеджером. Если у вас появятся новые вопросы, "
            "вы можете снова воспользоваться кнопкой 'Связаться с менеджером'",
            reply_markup=kb.main
        )
        await message.answer("Чат завершен", reply_markup=kb.main)
        await state.clear()
    else:
        await message.answer("Активный чат не найден")


@router.message(FeedbackState.waiting_for_message)
async def process_feedback(message: Message, state: FSMContext, bot: Bot):
    if not message.text:
        await message.answer(
            'Не удалось отправить сообщение. Пожалуйста, попробуйте позже.',
            reply_markup=kb.main
        )
        await state.clear()
        return

    try:
        username = message.from_user.username or "Неизвестный пользователь"
        user_id = message.from_user.id

        # Создаем инлайн-кнопку для принятия чата
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(
            text="Принять чат",
            callback_data=f"accept_chat:{user_id}"
        ))

        await bot.send_message(
            MANAGER_ID,
            f"Новое сообщение от пользователя @{username}:\n\n{message.text}",
            reply_markup=keyboard.as_markup()
        )
        await message.answer(
            'Ваше сообщение отправлено менеджеру. Ожидайте ответа.',
            reply_markup=kb.main
        )
        # Сохраняем ID пользователя в состоянии
        await state.update_data(user_id=user_id)
    except Exception:
        await message.answer(
            'Не удалось отправить сообщение. Пожалуйста, попробуйте позже.',
            reply_markup=kb.main
        )
    finally:
        await state.clear()
