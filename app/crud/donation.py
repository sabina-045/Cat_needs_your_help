from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Donation, User
from app.crud.base import CRUDBase
from app.services.investing_service import investing_service
from app.schemas.donation import DonationCreate


class CRUDDonation(CRUDBase):

    async def create_with_investing(
            self,
            obj_in: DonationCreate,
            user: User,
            session: AsyncSession,) -> Donation:
        """Cоздание пожертвования с подсчетом инвестиций."""
        obj_in_data = obj_in.dict()
        obj_in_data['user_id'] = user.id
        obj_in_data['create_date'] = datetime.now()
        db_obj = self.model(**obj_in_data)
        counted_donation = await investing_service.investing(db_obj, session)

        await session.commit()
        await session.refresh(counted_donation)

        return counted_donation

    async def get_my_donations(
            self,
            user: User,
            session: AsyncSession,) -> list[Donation]:
        """Получение пользователем списка собственных пожертвований."""
        my_donations_raw = await session.execute(
            select(self.model).where(self.model.user_id == user.id))

        return my_donations_raw.scalars().all()


donation_crud = CRUDDonation(Donation)
