from datetime import datetime

from app.models import CharityProject, Donation


class InvestmentCount:

    def _close_full_invested_object(self, obj):
        """Закрытие проекта или доната."""
        obj.fully_invested = True
        obj.close_date = datetime.now()
        obj.invested_amount = obj.full_amount

        return obj

    def investment_counting(
            self,
            charityproject: object,
            donation: object
    ) -> list[CharityProject, Donation]:
        """Подсчет инвестиций."""
        charityproject_diff = (charityproject.full_amount -
                               charityproject.invested_amount)
        donation_diff = (donation.full_amount -
                         donation.invested_amount)

        if charityproject_diff <= donation_diff:
            self._close_full_invested_object(charityproject)
            donation.invested_amount = (donation.invested_amount +
                                        charityproject_diff)
            if donation.invested_amount == donation.full_amount:
                self._close_full_invested_object(donation)

        if charityproject_diff > donation_diff:
            self._close_full_invested_object(donation)
            charityproject.invested_amount = (charityproject.invested_amount +
                                              donation_diff)

        return charityproject, donation


investment = InvestmentCount()
