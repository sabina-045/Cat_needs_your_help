from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


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
            main_object: object,
            session: AsyncSession,
    ) -> None:
        """Создание объекта."""
        await session.commit()
        await session.refresh(main_object)

    async def update(
            self,
            db_obj: object,
            session: AsyncSession,
    ) -> None:
        """Обновление объекта."""
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

    async def get_object_or_404(
            self,
            obj_id: int,
            session: AsyncSession,
    ) -> tuple[None, object]:
        """Получение объекта по id либо 404."""
        db_objs_raw = await session.execute(
            select(self.model).where(self.model.id == obj_id))
        db_obj = db_objs_raw.scalars().first()
        if not db_obj:
            raise HTTPException(
                status_code=404,
                detail='Такой проект не найден.')

        return db_obj

    async def find_oldest_obj(
            self,
            obj: object,
            session: AsyncSession,
    ) -> object:
        """Поиск самого старого открытого объекта в бд."""
        objects_list = await session.execute(
            select(obj).where(obj.fully_invested is not True).order_by(
                obj.create_date))

        return objects_list.scalars().first()
