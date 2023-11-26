from datetime import datetime

from aiogoogle import Aiogoogle
from sqlalchemy import select

from app.core.config import settings
from app.services.constants import FORMAT, ROW_COUNT, COLUMN_COUNT, SHEET_ID
from app.models import CharityProject


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    """Создание таблицы."""
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {'title': f'Отчёт на {now_date_time}',
                       'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': SHEET_ID,
                                   'title': 'Лист1',
                                   'gridProperties': {'rowCount': ROW_COUNT,
                                                      'columnCount': COLUMN_COUNT}}}]
    }
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
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    for project in sorted_projects_list:
        new_row = [project['name'], project['delta'], project['description']]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )


async def get_list_sorted_closed_projects(session) -> list[dict[str, int]]:
    """Получение из бд списка закрытых проектов,
    создание сортированного списка по времени сбора средств."""
    db_objs_raw = await session.execute(select(CharityProject).where(
        CharityProject.fully_invested is True))
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
