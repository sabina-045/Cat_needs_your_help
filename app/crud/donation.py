from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Donation, User
from app.crud.base import CRUDBase


class CRUDDonation(CRUDBase):

    async def get_my_donations(
            self,
            user: User,
            session: AsyncSession,
    ) -> list[Donation]:
        """Получение пользователем списка собственных пожертвований."""
        my_donations_raw = await session.execute(
            select(self.model).where(self.model.user_id == user.id))

        return my_donations_raw.scalars().all()


donation_crud = CRUDDonation(Donation)
