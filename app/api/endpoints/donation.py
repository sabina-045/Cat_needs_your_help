from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Donation
from app.core.user import current_superuser, current_user
from app.core.db import get_async_session
from app.crud.donation import donation_crud
from app.schemas.donation import DonationCreate, UserDonation, DonationGet
from app.services.investing_service import investing_service


router = APIRouter()


@router.get('/',
            response_model=list[DonationGet],
            response_model_exclude_none=True,
            dependencies=[Depends(current_superuser)])
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session)
) -> list[Donation]:
    """Получение списка пожертвований. Только для суперюзеров."""

    return await donation_crud.get_multi(session)


@router.post('/',
             response_model=UserDonation,
             response_model_exclude_none=True,)
async def create_new_donation(
        donation: DonationCreate,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
) -> Donation:
    """Создание пожертвования."""

    return await investing_service.create_with_investing(
        obj_in=donation, user=user, session=session)


@router.get('/my',
            response_model=list[UserDonation],
            response_model_exclude_none=True,)
async def get_user_own_donations(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
) -> Donation:
    """Получение собственных пожертвований пользователя."""

    return await donation_crud.get_my_donations(user, session)
