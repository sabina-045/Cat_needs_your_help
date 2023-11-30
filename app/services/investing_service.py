from datetime import datetime

from app.models import CharityProject, Donation


def investment_counting(
        main_object: object,
        second_object: object
) -> list[CharityProject, Donation]:
    """Подсчет инвестиций."""
    if main_object.invested_amount:
        main_object_sum = (main_object.full_amount -
                           main_object.invested_amount)
    else:
        main_object_sum = main_object.full_amount
    if second_object.invested_amount:
        second_object_sum = (second_object.full_amount -
                             second_object.invested_amount)
    else:
        second_object_sum = second_object.full_amount

    if main_object_sum < second_object_sum:
        main_object.fully_invested = True
        main_object.close_date = datetime.now()
        main_object.invested_amount = main_object.full_amount
        if second_object.invested_amount:
            second_object.invested_amount = (second_object.invested_amount +
                                             main_object_sum)
        else:
            second_object.invested_amount = main_object_sum

    if main_object_sum > second_object_sum:
        if main_object.invested_amount:
            main_object.invested_amount = (main_object.invested_amount +
                                           second_object_sum)
        else:
            main_object.invested_amount = second_object_sum
            second_object.fully_invested = True
            second_object.close_date = datetime.now()
            second_object.invested_amount = second_object.full_amount

    if main_object_sum == second_object_sum:
        main_object.fully_invested = True
        second_object.fully_invested = True
        main_object.close_date = datetime.now()
        second_object.close_date = datetime.now()
        main_object.invested_amount = main_object.full_amount
        second_object.invested_amount = second_object.full_amount

    return main_object, second_object
