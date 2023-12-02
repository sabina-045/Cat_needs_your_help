from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ) -> object:
        """Получение объекта."""
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id))

        return db_obj.scalars().first()

    async def get_multi(
            self,
            session: AsyncSession
    ) -> list[object]:
        """Получение списка объектов."""
        db_objs = await session.execute(select(self.model))

        return db_objs.scalars().all()

    async def create(
            self,
            obj_in_data: dict,
            session: AsyncSession,
    ) -> None:
        """Создание объекта."""
        obj = self.model(**obj_in_data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return obj

    async def save_obj_changes_after_invest_counting(
            self,
            obj: object,
            session: AsyncSession
    ) -> None:
        """Сохранение обновл. объектов после
        подсчета инвестиций."""
        await session.commit()
        await session.refresh(obj)

    async def update(
            self,
            db_obj,
            obj_data,
            update_data,
            session: AsyncSession,
    ) -> None:
        """Обновление объекта."""
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

    async def remove(
            self,
            db_obj: object,
            session: AsyncSession,
    ) -> None:
        """Удаление объекта."""
        await session.delete(db_obj)
        await session.commit()

    async def find_oldest_obj(
            self,
            obj: object,
            session: AsyncSession,
    ) -> object:
        """Поиск самого старого открытого объекта в бд."""
        objects_list = await session.execute(
            select(obj).where(obj.fully_invested.is_(False)).order_by(
                obj.create_date))

        return objects_list.scalars().first()
