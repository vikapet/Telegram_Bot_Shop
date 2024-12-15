import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database.models import Base
from handlers.texts import categories, description_for_info_pages
from database.requests import orm_create_categories, orm_add_banner_description

load_dotenv()
# Создание асинхронного SQLAlchemy движка для работы с базой данных
engine = create_async_engine(url=os.getenv("SQLALCHEMY_URL"), echo=True)
# Создание асинхронного sessionmaker для создания сессий
async_session = async_sessionmaker(engine)


async def async_main():
    """Асинхронная функция для создания таблиц и добавления данных в базу данных.

    Эта функция создает таблицы базы данных, а также добавляет категории товаров и описание к баннеру в базу данных.

    Args:
        У функции нет аргументов.

    Returns:
        None: Функция ничего не возвращает.

    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, description_for_info_pages)
