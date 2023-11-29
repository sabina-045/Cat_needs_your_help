from datetime import datetime

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation
from app.crud.base import CRUDBase
from app.crud.charity_project import charityproject_crud
from app.services.constants import INVESTED_AMOUNT_DEFAULT
from app.schemas.charity_project import CharityProjectUpdate


class InvestingService:
    """Класс работы с проектами и процессом инвестирования."""

    async def create_with_investing(
            self,
            obj_in: object,
            session: AsyncSession,
            **kwargs
    ) -> object:
        """Создание проекта с запуском процесса инвестирования."""
        main_object_raw = obj_in.dict()
        main_object_raw['create_date'] = datetime.now()
        if 'user' in kwargs:
            main_object_raw['user_id'] = kwargs['user'].id
            model = CharityProject
            main_object = Donation(**main_object_raw)
        else:
            await charityproject_crud.check_unique_name(
                main_object_raw, session)
            model = Donation
            main_object = CharityProject(**main_object_raw)
        while main_object.fully_invested is not True:
            second_object = await CRUDBase.find_oldest_obj(
                self, model, session)
            if second_object:
                self._investment_counting(main_object, second_object)
                session.add_all([main_object, second_object])
            else:
                session.add(main_object)
                break
        await CRUDBase.create(self, main_object, session)

        return main_object

    def _investment_counting(
            self,
            main_object: object,
            second_object: object
    ) -> list[CharityProject, Donation]:
        """Подсчет инвестиций."""
        if main_object.invested_amount:
            main_object_sum = (main_object.full_amount -
                               main_object.invested_amount)
        else:
            main_object_sum = main_object.full_amount
        if second_object.invested_amount:
            second_object_sum = (second_object.full_amount -
                                 second_object.invested_amount)
        else:
            second_object_sum = second_object.full_amount

        if main_object_sum < second_object_sum:
            main_object.fully_invested = True
            main_object.close_date = datetime.now()
            main_object.invested_amount = main_object.full_amount
            if second_object.invested_amount:
                second_object.invested_amount = (second_object.invested_amount +
                                                 main_object_sum)
            else:
                second_object.invested_amount = main_object_sum

        if main_object_sum > second_object_sum:
            if main_object.invested_amount:
                main_object.invested_amount = (main_object.invested_amount +
                                               second_object_sum)
            else:
                main_object.invested_amount = second_object_sum
                second_object.fully_invested = True
                second_object.close_date = datetime.now()
                second_object.invested_amount = second_object.full_amount

        if main_object_sum == second_object_sum:
            main_object.fully_invested = True
            second_object.fully_invested = True
            main_object.close_date = datetime.now()
            second_object.close_date = datetime.now()
            main_object.invested_amount = main_object.full_amount
            second_object.invested_amount = second_object.full_amount

        return main_object, second_object

    async def update_project(
            self,
            obj_id: int,
            obj_in: CharityProjectUpdate,
            session: AsyncSession,
    ) -> CharityProject:
        """Обновление проекта. Проект должен быть открытым.
        Новая требуемая сумма не должна быть меньше инвестированной."""
        db_obj = await charityproject_crud.get_object_or_404(obj_id, session)
        self._check_updating_project_is_not_closed(db_obj)
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True, exclude_none=True)
        if self._check_item_in_update_data_and_updated(
                update_data, db_obj, name='name'):
            await charityproject_crud.check_unique_name(
                update_data, session)
        if self._check_item_in_update_data_and_updated(
                update_data, db_obj, name='full_amount'):
            self._check_new_full_amount_is_bigger_than_invested_amount(
                update_data, db_obj)
            self._check_new_full_amount_is_equal_invested_amount(
                update_data, db_obj)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        await charityproject_crud.update(db_obj, session)

        return db_obj

    async def remove_project(
            self,
            obj_id: int,
            session: AsyncSession,
    ) -> CharityProject:
        """Удаление проекта. Проект должен быть открытым и без инвестиций."""
        db_obj = await charityproject_crud.get_object_or_404(obj_id, session)

        self._check_deleting_project_is_not_closed_and_has_no_investments(db_obj)
        await charityproject_crud.remove(db_obj, session)

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

    def _check_new_full_amount_is_equal_invested_amount(
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


investing_service = InvestingService()
