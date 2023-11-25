from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id))

        return db_obj.scalars().first()

    async def get_multi(
            self,
            session: AsyncSession):
        db_objs = await session.execute(select(self.model))

        return db_objs.scalars().all()
