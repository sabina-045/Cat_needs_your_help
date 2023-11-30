from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models import CharityProject, Donation
from app.crud.base import CRUDBase
from app.crud.charity_project import charityproject_crud
from app.services.investing_service import investment_counting


class ProjectDonationBase:
    """Базовый сервисный класс."""

    async def create_with_investing(
            self,
            obj_in: object,
            session: AsyncSession,
            **kwargs
    ) -> object:
        """Создание объекта с запуском процесса инвестирования."""
        main_object_raw = obj_in.dict()
        main_object_raw['create_date'] = datetime.now()
        if 'user' in kwargs:
            main_object_raw['user_id'] = kwargs['user'].id
            model = CharityProject
            main_object = Donation(**main_object_raw)
        else:
            await charityproject_crud.is_exists_project_name(
                main_object_raw, session)
            model = Donation
            main_object = CharityProject(**main_object_raw)
        while main_object.fully_invested is not True:
            second_object = await CRUDBase.find_oldest_obj(
                self, model, session)
            if second_object:
                investment_counting(main_object, second_object)
                session.add_all([main_object, second_object])
            else:
                session.add(main_object)
                break
        await CRUDBase.create(self, main_object, session)

        return main_object

    async def get_object_or_404(
            self,
            obj_id: int,
            session: AsyncSession,
    ) -> tuple[None, object]:
        """Получение объекта по id либо 404."""
        db_obj = await charityproject_crud.get(obj_id, session)
        if not db_obj:
            raise HTTPException(
                status_code=404,
                detail='Такой проект не найден.')

        return db_obj
