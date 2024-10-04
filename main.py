import asyncio
from aiogram import Bot, Dispatcher 

from app.handers import router
from app.database.models import async_main

async def main():
    await async_main()
    bot = Bot(token='7298028181:AAFd4VroV6Evvdm9j8Dr7vvuxPfweRty4BA')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot off')
    