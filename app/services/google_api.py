import copy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.models import CharityProject

FORMAT = "%Y/%m/%d %H:%M:%S"
SPREADSHEET_ROWCOUNT = 100
SPREADSHEET_COLUMNCOUNT = 11
SPREADSHEETS_BODY = dict(
    properties=dict(
        title='Отчет на ',
        locale='ru_RU',
    ),
    sheets=[dict(properties=dict(
        sheetType='GRID',
        sheetId=0,
        title='Лист1',
        gridProperties=dict(
            rowCount=SPREADSHEET_ROWCOUNT,
            columnCount=SPREADSHEET_COLUMNCOUNT,
        ),
    ))],
)
TABLE_HEADER = [
    ['Отчет от', ],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание'],
]
ERROR_ROWS_TOO_BIG = (
    'При создании получаеться {value} строк, больше чем доступно - ' +
    f'{SPREADSHEET_ROWCOUNT}'
)
ERROR_COLUMNS_TOO_BIG = (
    'При создании получаеться {value} столбцов, больше чем доступно - ' +
    f'{SPREADSHEET_COLUMNCOUNT}'
)


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheets_body = copy.deepcopy(SPREADSHEETS_BODY)
    spreadsheets_body['properties']['title'] += now_date_time
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheets_body)
    )
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email,
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        )
    )


async def spreadsheets_update_value(
    spreadsheet_id: str,
    charity_project: list[CharityProject],
    wrapper_services: Aiogoogle,
) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = copy.deepcopy(TABLE_HEADER)
    table_values[0].append(now_date_time)
    table_values.extend([
        list(
            map(
                str, [
                    project.name,
                    project.close_date - project.create_date,
                    project.description,
                ],)) for project in charity_project
    ])

    update_body = {'majorDimension': 'ROWS', 'values': table_values}

    rows_value = len(table_values)
    columns_value = max(map(len, table_values))

    if SPREADSHEET_ROWCOUNT < rows_value:
        raise ValueError(ERROR_ROWS_TOO_BIG.format(
            value=rows_value
        ))
    if SPREADSHEET_COLUMNCOUNT < columns_value:
        raise ValueError(ERROR_COLUMNS_TOO_BIG.format(
            value=columns_value
        ))

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{rows_value}C{columns_value}',
            valueInputOption='USER_ENTERED',
            json=update_body,
        )
    )
    return spreadsheet_id
