from datetime import datetime

from app.models import CharityProject, Donation


def investment_counting(
        charityproject: object,
        donation: object
) -> list[CharityProject, Donation]:
    """Подсчет инвестиций."""
    if charityproject.invested_amount:
        charityproject_diff = (charityproject.full_amount -
                               charityproject.invested_amount)
    else:
        charityproject_diff = charityproject.full_amount
    if donation.invested_amount:
        donation_diff = (donation.full_amount -
                         donation.invested_amount)
    else:
        donation_diff = donation.full_amount

    if charityproject_diff < donation_diff:

        charityproject.fully_invested = True
        charityproject.close_date = datetime.now()
        charityproject.invested_amount = charityproject.full_amount
        if donation.invested_amount:
            donation.invested_amount = (donation.invested_amount +
                                        charityproject_diff)
        else:
            donation.invested_amount = charityproject_diff

    if charityproject_diff >= donation_diff:

        donation.fully_invested = True
        donation.close_date = datetime.now()
        donation.invested_amount = donation.full_amount
        if charityproject.invested_amount:
            charityproject.invested_amount = (charityproject.invested_amount +
                                              donation_diff)
        else:
            charityproject.invested_amount = donation_diff

        if charityproject.full_amount == charityproject.invested_amount:
            charityproject.fully_invested = True
            charityproject.close_date = datetime.now()

    return charityproject, donation
