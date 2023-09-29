from http import HTTPStatus

from fastapi import HTTPException
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject

ERORR_NAME = 'Проект с таким именем уже существует!'
ERROR_NOT_FOUND = 'Проект не найден'
ERROR_CLOSED = 'Закрытый проект нельзя редактировать!'
ERROR_INVESTED = 'В проект были внесены средства, не подлежит удалению!'
ERROR_FULL_AMOUNT_UPDATE = (
    'Новая требуемая сумма должна быть больше уже'
    'внесенной в проект суммы'
)


async def check_charity_project_name_duplicate(
    project_name: str,
    session: AsyncSession
) -> None:
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ERORR_NAME
        )


async def check_charity_project_exists(
        project_id: int,
        session: AsyncSession
) -> CharityProject:
    charity_project = await charity_project_crud.get(
        project_id, session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=ERROR_NOT_FOUND
        )
    return charity_project


async def check_charity_project_is_closed(
    project_id: int,
    session: AsyncSession
) -> None:
    charity_project = await (
        charity_project_crud.get(
            project_id, session
        )
    )
    if charity_project.close_date:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ERROR_CLOSED
        )


async def check_charity_project_is_invested(
    project_id: int,
    session: AsyncSession
) -> None:
    charity_project = await (
        charity_project_crud.get(
            project_id, session
        )
    )
    if charity_project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ERROR_INVESTED
        )


async def check_correct_full_amount_update(
    project_id: int,
    session: AsyncSession,
    full_amount: PositiveInt
) -> None:
    charity_project = await (
        charity_project_crud.get(
            project_id, session
        )
    )
    if charity_project.invested_amount > full_amount:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=ERROR_FULL_AMOUNT_UPDATE
        )
