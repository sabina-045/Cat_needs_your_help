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

    async def is_exists_project_name(
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
        else:

            return True

    async def get_object_or_404(
            self,
            obj_id: int,
            session: AsyncSession,
    ) -> tuple[None, object]:
        """Получение проекта по id либо 404."""
        db_obj = await self.get(obj_id, session)
        if not db_obj:
            raise HTTPException(
                status_code=404,
                detail='Такой проект не найден.')

        return db_obj


charityproject_crud = CRUDCharityProject(CharityProject)
