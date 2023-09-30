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
TABLE_VALUES = [
    ['Отчет от', ],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание'],
]
ERROR_ROWS_COLUMNS_VALUE = (
    'Получилось строк - {rows_value},'
    'а столбцов - {columns_value}, но'
    'количество строк не должно превышать {rowcount}, '
    'a столбцов - {columncount}'
)


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheets_body = SPREADSHEETS_BODY.copy()
    spreadsheets_body['properties']['title'] += now_date_time
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheets_body)
    )
    return response['spreadsheetId']


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
    table_values = TABLE_VALUES.copy()
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

    if (
        SPREADSHEET_ROWCOUNT < rows_value or
        SPREADSHEET_COLUMNCOUNT < columns_value
    ):
        raise ValueError(
            ERROR_ROWS_COLUMNS_VALUE.format(
                rows_value=rows_value,
                columns_value=columns_value,
                rowcount=SPREADSHEET_ROWCOUNT,
                columncount=SPREADSHEET_COLUMNCOUNT
            )
        )

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{rows_value}C{columns_value}',
            valueInputOption='USER_ENTERED',
            json=update_body,
        )
    )
    return spreadsheet_id
