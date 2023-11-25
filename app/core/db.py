from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from app.core.config import settings
from app.services.constants import INVESTED_AMOUNT_DEFAULT


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime)
    full_amount = Column(Integer)
    close_date = Column(DateTime, default=None)
    fully_invested = Column(Boolean, default=False)
    invested_amount = Column(Integer, default=INVESTED_AMOUNT_DEFAULT)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.database_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    """Асинхронный генератор сессий(crud-зависимоcть)."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
