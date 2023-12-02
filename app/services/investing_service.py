from datetime import datetime

from app.models import CharityProject, Donation


def close_full_invested_object(obj):
    """Закрытие проекта или доната."""
    obj.fully_invested = True
    obj.close_date = datetime.now()
    obj.invested_amount = obj.full_amount

    return obj


def investment_counting(
        charityproject: object,
        donation: object
) -> list[CharityProject, Donation]:
    """Подсчет инвестиций."""
    charityproject_diff = (charityproject.full_amount -
                           charityproject.invested_amount)
    donation_diff = (donation.full_amount -
                     donation.invested_amount)

    if charityproject_diff < donation_diff:
        close_full_invested_object(charityproject)
        donation.invested_amount = (donation.invested_amount +
                                    charityproject_diff)

    if charityproject_diff >= donation_diff:
        close_full_invested_object(donation)
        charityproject.invested_amount = (charityproject.invested_amount +
                                          donation_diff)
        if charityproject.full_amount == charityproject.invested_amount:
            close_full_invested_object(charityproject)

    return charityproject, donation
