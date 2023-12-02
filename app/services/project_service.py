from datetime import datetime

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Donation, CharityProject
from app.crud.charity_project import charityproject_crud
from app.services.constants import INVESTED_AMOUNT_DEFAULT
from app.schemas.charity_project import CharityProjectUpdate
from app.services.investing_service import investment
from app.crud.base import CRUDBase


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
            self,
            obj_in: object,
    ) -> CharityProject:
        """Создание проекта."""
        obj_in_data = obj_in.dict()
        await charityproject_crud.is_exists_project_name(
            obj_in_data, self.session)
        obj_in_data['create_date'] = datetime.now()
        charityproject = await charityproject_crud.create(obj_in_data, self.session)
        await self._investing(charityproject)

        return charityproject

    async def _investing(self, charityproject):
        """Запуск инвестирования."""
        while charityproject.fully_invested is not True:
            donation = await CRUDBase.find_oldest_obj(
                self, Donation, self.session)
            if donation:
                investment.investment_counting(charityproject, donation)
                self.session.add_all([charityproject, donation])
            else:
                self.session.add(charityproject)
                break

        await self.session.commit()
        await self.session.refresh(charityproject)

        return charityproject

    async def update(
            self,
            obj_id: int,
            obj_in: CharityProjectUpdate,
    ) -> CharityProject:
        """Обновление проекта. Проект должен быть открытым.
        Новая требуемая сумма не должна быть меньше инвестированной."""
        db_obj = await charityproject_crud.get_object_or_404(obj_id, self.session)
        self._check_updating_project_is_not_closed(db_obj)
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True, exclude_none=True)
        if self._check_item_in_update_data_and_updated(
                update_data, db_obj, name='name'):
            await charityproject_crud.is_exists_project_name(
                update_data, self.session)
        if self._check_item_in_update_data_and_updated(
                update_data, db_obj, name='full_amount'):
            self._check_new_full_amount_is_bigger_than_invested_amount(
                update_data, db_obj)
            self._change_obj_if_new_full_amount_is_equal_invested_amount(
                update_data, db_obj)
        await charityproject_crud.update(db_obj, obj_data, update_data, self.session)

        return db_obj

    async def remove(
            self,
            obj_id: int,
    ) -> CharityProject:
        """Удаление проекта. Проект должен быть открытым и без инвестиций."""
        db_obj = await charityproject_crud.get_object_or_404(obj_id, self.session)

        self._check_deleting_project_is_not_closed_and_has_no_investments(db_obj)
        await charityproject_crud.remove(db_obj, self.session)

        return db_obj

    def _check_deleting_project_is_not_closed_and_has_no_investments(
        self,
        obj: CharityProject
    ) -> None:
        """Проверяем проект перед удалением: он не должен быть закрыт
        и в нем не должно быть инвестиций."""
        if obj.fully_invested:
            raise HTTPException(
                status_code=400,
                detail='В проект были внесены средства, не подлежит удалению!')
        if obj.invested_amount != INVESTED_AMOUNT_DEFAULT:
            raise HTTPException(
                status_code=400,
                detail='В проект были внесены средства, не подлежит удалению!')

    def _check_updating_project_is_not_closed(
            self,
            obj: CharityProject
    ) -> None:
        """Проверяем проект перед обновлением: он не должен быть закрыт."""
        if obj.fully_invested:
            raise HTTPException(
                status_code=400,
                detail='Закрытый проект нельзя редактировать!')

    def _check_new_full_amount_is_bigger_than_invested_amount(
            self,
            data: dict,
            obj: CharityProject
    ) -> None:
        """Перед обновлением проекта проверяем: новое значение full_amount
        не должно быть меньше invested_amount."""
        if obj.invested_amount:
            if data['full_amount'] < obj.invested_amount:
                raise HTTPException(
                    status_code=400,
                    detail='Введенное значение не может быть'
                           'меньше внесенных инвестиций.')

    def _change_obj_if_new_full_amount_is_equal_invested_amount(
        self,
        data: dict,
        obj: CharityProject
    ) -> CharityProject:
        """Перед обновлением проекта проверяем: если новое знач. full_amount
        равно внесенным инвестициям, то проект закрывается."""
        if obj.invested_amount:
            if data['full_amount'] == obj.invested_amount:
                obj.fully_invested = True
                obj.close_date = datetime.now()

                return obj

    def _check_item_in_update_data_and_updated(
        self,
        data: dict,
        obj: CharityProject, name
    ) -> bool:
        """Проверяем, присутствует ли параметр в обновляемых данных
        и изменился ли он по сравнению с параметром в бд."""
        if data.get('name') is not None:
            if data['name'] != obj.name:

                return True
