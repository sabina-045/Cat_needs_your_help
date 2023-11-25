from sqlalchemy import select
from fastapi import HTTPException

from app.models import CharityProject
from app.services.constants import INVESTED_AMOUNT_DEFAULT


def check_deleting_project_is_not_closed_and_has_no_investments(
        obj: CharityProject) -> None:
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


def check_updating_project_is_not_closed(obj: CharityProject) -> None:
    """Проверяем проект перед обновлением: он не должен быть закрыт."""
    if obj.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!')


def check_new_full_amount_is_bigger_than_invested_amount(
        data: dict, obj: CharityProject) -> None:
    """Перед обновлением проекта проверяем: новое значение full_amount
    не должно быть меньше invested_amount."""
    if obj.invested_amount:
        if data['full_amount'] < obj.invested_amount:
            raise HTTPException(
                status_code=400,
                detail='Введенное значение не может быть'
                       'меньше внесенных инвестиций.')


async def check_unique_name(data: dict, model, session) -> None:
    """При создании/обновлении проекта проверяем
    уникальность имени."""
    obj_raw = await session.execute(select(model).where(
        model.name == data['name']))
    obj = obj_raw.scalars().first()
    if obj:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!')
