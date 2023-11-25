from datetime import datetime

from sqlalchemy import select

from app.models import CharityProject, Donation


class InvestingService:
    """Класс для обслуживания процесса инвестирования."""

    async def _find_oldest_obj(self, obj, session) -> object:
        """Поиск самого старого открытого объекта в бд."""
        objects_list = await session.execute(
            select(obj).where(obj.fully_invested is not True).order_by(
                obj.create_date))

        return objects_list.scalars().first()

    async def investing(self, main_object, session) -> object:
        """Запуск процесса инвестирования."""
        if isinstance(main_object, CharityProject):
            model = Donation
        if isinstance(main_object, Donation):
            model = CharityProject
        while main_object.fully_invested is not True:
            second_object = await self._find_oldest_obj(model, session)
            if second_object:
                self._investment_counting(main_object, second_object)
                session.add_all([main_object, second_object])
            else:
                session.add(main_object)
                break

        return main_object

    def _investment_counting(self, main_object, second_object
                             ) -> list[CharityProject, Donation]:
        """Подсчет инвестиций."""
        if main_object.invested_amount:
            main_object_sum = main_object.full_amount - main_object.invested_amount
        else:
            main_object_sum = main_object.full_amount
        if second_object.invested_amount:
            second_object_sum = second_object.full_amount - second_object.invested_amount
        else:
            second_object_sum = second_object.full_amount

        if main_object_sum < second_object_sum:
            main_object.fully_invested = True
            main_object.close_date = datetime.now()
            main_object.invested_amount = main_object.full_amount
            if second_object.invested_amount:
                second_object.invested_amount = second_object.invested_amount + main_object_sum
            else:
                second_object.invested_amount = main_object_sum

        if main_object_sum > second_object_sum:
            if main_object.invested_amount:
                main_object.invested_amount = main_object.invested_amount + second_object_sum
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


investing_service = InvestingService()
