import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from handlers.mwre import DataBaseSession
from database.engine import async_session, async_main

from handlers.admin import admin
from handlers.users import router


async def main():
    """ Асинхронная функция, являющаяся точкой входа.

        Эта функция загружает переменные окружения с помощью `load_dotenv()`,
        создаёт экземпляр бота с токеном, указанным в переменной окружения как`TOKEN`,
        создает экземпляр класса диспетчер с подключением необходимых роутеров и
        промежуточного ПО.

        Использует следующие классы:
            - `Bot`: для создания объекта бота.
            - `Dispatcher`: для управления процессом получения и обработки обновлений.
            - `DataBaseSession`: промежуточное программное обеспечение.

        В случае успешного запуска, функция инициирует polling бота для получения
        обновлений и обработки команд.

        Args:
            У функции нет аргументов.

        Returns:
            None: Функция ничего не возращает.

        """
    load_dotenv()
    await async_main()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_routers(router, admin)
    dp.update.middleware(DataBaseSession(session_pool=async_session))
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
