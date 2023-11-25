from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser

from app.crud.charity_project import charityproject_crud
from app.models import CharityProject


router = APIRouter()


@router.post('/',)
            # dependencies=[Depends(current_superuser)],)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)

) -> list[dict[str, int]]:
    """Получение списка закрытых проектов, отсортированных по
    времени сбора инвестиций. Только для суперюзеров."""

    return await charityproject_crud.get_projects_by_completion_rate(
        session, wrapper_services)
