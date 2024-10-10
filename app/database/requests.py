from app.database.models import async_session
from app.database.models import User, Category, Item, Service
from sqlalchemy import select


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_item(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == category_id))


async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))

async def get_service_cities():
    async with async_session() as session:
        return await session.scalars(select(Service.name).distinct())

async def get_service_by_city(city_name):
    async with async_session() as session:
        return await session.scalars(select(Service).where(Service.name == city_name))