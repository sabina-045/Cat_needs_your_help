from datetime import datetime

from sqlalchemy import select
from fastapi import HTTPException

from app.models import CharityProject


async def get_object_or_404(obj_id, model, session) -> None:
    """Получение объекта по id либо 404."""
    db_obj = await session.execute(select(model).where(model.id == obj_id))
    if not db_obj:
        raise HTTPException(
            status_code=404,
            detail='Такой проект не найден.')

    return db_obj.scalars().first()


def check_new_full_amount_is_equal_invested_amount(
    data: dict, obj: CharityProject
) -> CharityProject:
    """Перед обновлением проекта проверяем: если новое знач. full_amount
    равно внесенным инвестициям, то проект закрывается."""
    if obj.invested_amount:
        if data['full_amount'] == obj.invested_amount:
            obj.fully_invested = True
            obj.close_date = datetime.now()

            return obj


def check_item_in_update_data_and_updated(
    data: dict, obj: CharityProject, name
) -> bool:
    """Проверяем, присутствует ли параметр в обновляемых данных
    и изменился ли он по сравнению с параметром в бд."""
    if data.get('name') is not None:
        if data['name'] != obj.name:

            return True
