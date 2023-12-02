from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Donation, CharityProject
from app.crud.base import CRUDBase
from app.services.investing_service import investment_counting
from app.crud.donation import donation_crud


class DonationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
            self,
            obj_in: object,
            user: User,
    ) -> Donation:
        """Создание доната."""
        obj_in_data = obj_in.dict()
        obj_in_data['user_id'] = user.id
        obj_in_data['create_date'] = datetime.now()
        donation = await donation_crud.create(obj_in_data, self.session)
        await self._investing(donation)

        return donation

    async def _investing(self, donation):
        """Запуск инвестирования."""
        while donation.fully_invested is not True:
            charityproject = await CRUDBase.find_oldest_obj(
                self, CharityProject, self.session)
            if charityproject:
                investment_counting(charityproject, donation)
                self.session.add_all([charityproject, donation])
            else:
                self.session.add(donation)
                break
        await donation_crud.save_obj_changes_after_invest_counting(
            donation, self.session)

        return donation
