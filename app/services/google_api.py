from datetime import datetime, date

from aiogoogle import Aiogoogle
from sqlalchemy.sql import operators, extract
from sqlalchemy import func, column, select, desc
# В секретах лежит адрес вашего личного гугл-аккаунта
from app.core.config import settings
from app.services.constants import FORMAT
from app.models import CharityProject



async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    """Создание таблицы."""
    # Получаем текущую дату для заголовка документа
    now_date_time = datetime.now().strftime(FORMAT)
    # Создаём экземпляр класса Resource
    service = await wrapper_services.discover('sheets', 'v4')
    # Формируем тело запроса
    spreadsheet_body = {
        'properties': {'title': f'Отчёт на {now_date_time}',
                       'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Лист1',
                                   'gridProperties': {'rowCount': 100,
                                                      'columnCount': 11}}}]
    }
    # Выполняем запрос
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheetid = response['spreadsheetId']

    return spreadsheetid


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    """Получение разрешения на доступ."""
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheetid: str,
        sorted_projects_list: list,
        wrapper_services: Aiogoogle
) -> None:
    """Обновление данных в таблице."""
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    # Здесь формируется тело таблицы
    table_values = [
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    # Здесь в таблицу добавляются строчки
    for project in sorted_projects_list:
        new_row = [project['name'], project['delta'], project['description']]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )


async def get_list_sorted_closed_projects(session):
    """Получение из бд списка закрытых проектов,
    создание сортированного списка по времени сбора средств."""
    db_objs_raw = await session.execute(select(CharityProject).where(
            CharityProject.fully_invested == True))
    db_objs = db_objs_raw.scalars().all()
    obj_list = []
    for obj in db_objs:
        delta_time = obj.close_date - obj.create_date
        days = delta_time.days
        if days == 0:
            delta = f'0 day, {delta_time}'
        else:
            delta = f'{delta_time}'
        obj_list.append({'name': obj.name,
                        'delta': delta,
                        'description': obj.description})
    sorted_list = sorted(obj_list, key=lambda x: x['delta'])

    return sorted_list
