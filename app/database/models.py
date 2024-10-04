from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'Users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    

class Category(Base):
    __tablename__ = 'Categories'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    
    
class Item(Base):
    __tablename__ = 'Items'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    address: Mapped[str] = mapped_column(String(60))
    weekdays_time: Mapped[str] = mapped_column(String(60))
    weekend_time: Mapped[str] = mapped_column(String(60))
    contact: Mapped[str] = mapped_column(String(60))
    geo_link: Mapped[str] = mapped_column(String(60))
    cityes: Mapped[int] = mapped_column(ForeignKey('Categories.id'))
    
async def async_main():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all) 