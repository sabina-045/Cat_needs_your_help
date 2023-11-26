from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from aiogoogle import Aiogoogle

from app.models import CharityProject
from app.crud.base import CRUDBase
from app.services.validators import (
    check_deleting_project_is_not_closed_and_has_no_investments,
    check_unique_name,
    check_new_full_amount_is_bigger_than_invested_amount,
    check_updating_project_is_not_closed,)
from app.services.investing_service import investing_service
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectUpdate)
from app.services.crud_service import (
    get_object_or_404,
    check_new_full_amount_is_equal_invested_amount,
    check_item_in_update_data_and_updated)
from app.services.google_api import (
    get_list_sorted_closed_projects,
    spreadsheets_create,
    set_user_permissions,
    spreadsheets_update_value)


class CRUDCharityProject(CRUDBase):

    async def create_with_investing(
            self,
            obj_in: CharityProjectCreate,
            session: AsyncSession,) -> CharityProject:
        """Cоздание проекта с подсчетом инвестиций."""
        obj_in_data = obj_in.dict()
        obj_in_data['create_date'] = datetime.now()
        await check_unique_name(obj_in_data, CharityProject, session)
        db_obj = self.model(**obj_in_data)
        counted_project = await investing_service.investing(db_obj, session)

        await session.commit()
        await session.refresh(counted_project)

        return counted_project

    async def remove(
            self,
            obj_id: int,
            session: AsyncSession,) -> CharityProject:
        """Удаление проекта. Проект должен быть открытым и без инвестиций."""
        db_obj = await get_object_or_404(obj_id, CharityProject, session)
        check_deleting_project_is_not_closed_and_has_no_investments(db_obj)

        await session.delete(db_obj)
        await session.commit()

        return db_obj

    async def update(
            self,
            obj_id: int,
            obj_in: CharityProjectUpdate,
            session: AsyncSession,) -> CharityProject:
        """Обновление проекта. Проект должен быть открытым.
        Новая требуемая сумма не должна быть меньше инвестированной."""
        db_obj = await get_object_or_404(obj_id, CharityProject, session)
        check_updating_project_is_not_closed(db_obj)
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True, exclude_none=True)
        if check_item_in_update_data_and_updated(update_data, db_obj, name='name'):
            await check_unique_name(update_data, CharityProject, session)
        if check_item_in_update_data_and_updated(update_data, db_obj, name='full_amount'):
            check_new_full_amount_is_bigger_than_invested_amount(update_data, db_obj)
            check_new_full_amount_is_equal_invested_amount(update_data, db_obj)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        return db_obj

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
            wrapper_services: Aiogoogle) -> list[dict[str, int]]:
        """Метод получения закр. сортир. проектов по времени сбора средств
        и записи данных в таблицу."""
        sorted_projects_list = await get_list_sorted_closed_projects(session)
        spreadsheetid = await spreadsheets_create(wrapper_services)
        await set_user_permissions(spreadsheetid, wrapper_services)
        await spreadsheets_update_value(spreadsheetid,
                                        sorted_projects_list,
                                        wrapper_services)

        return sorted_projects_list


charityproject_crud = CRUDCharityProject(CharityProject)
