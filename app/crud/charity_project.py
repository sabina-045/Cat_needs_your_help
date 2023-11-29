from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models import CharityProject
from app.crud.base import CRUDBase


class CRUDCharityProject(CRUDBase):

    async def get_closed_projects(
            self,
            session: AsyncSession,
    ) -> list[dict[str, int]]:
        """Получение всех закрытых проектов."""
        db_objs_raw = await session.execute(select(self.model).where(
            self.model.fully_invested is True))

        return db_objs_raw.scalars().all()

    async def check_unique_name(
            self,
            data: dict,
            session: AsyncSession
    ) -> None:
        """При создании/обновлении проекта проверяем
        уникальность имени."""
        obj_raw = await session.execute(select(self.model).where(
            self.model.name == data['name']))
        obj = obj_raw.scalars().first()
        if obj:
            raise HTTPException(
                status_code=400,
                detail='Проект с таким именем уже существует!')


charityproject_crud = CRUDCharityProject(CharityProject)
