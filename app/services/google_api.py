from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.models import CharityProject

FORMAT = "%Y/%m/%d %H:%M:%S"
SPREADSHEET_ROWCOUNT = 100
SPREADSHEET_COLUMNCOUNT = 11


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheets_body = dict(
        properties=dict(
            title=f'Отчет на {now_date_time}',
            locale='ru_RU',
        ),
        sheets=[
            dict(
                properties=dict(
                    sheetType='GRID',
                    sheetId=0,
                    title='Лист1',
                    gridProperties=dict(
                        rowCount=SPREADSHEET_ROWCOUNT,
                        columnCount=SPREADSHEET_COLUMNCOUNT,
                    ),
                )
            )
        ],
    )
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheets_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheetid: str,
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
            fileId=spreadsheetid,
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

    table_values = [
        ['Отчет от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание'],
    ]
    table_values.extend([
        list(map(str, [project.name,
                       project.close_date - project.create_date,
                       project.description,
                       ],)) for project in charity_project
    ])

    update_body = {'majorDimension': 'ROWS', 'values': table_values}

    columns_value = max(
        len(items_to_count) for items_to_count in table_values
    )
    rows_value = len(table_values)

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{rows_value}C{columns_value}',
            valueInputOption='USER_ENTERED',
            json=update_body,
        )
    )
    return spreadsheet_id
