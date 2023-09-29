from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_charity_project_exists,
                                check_charity_project_is_closed,
                                check_charity_project_is_invested,
                                check_charity_project_name_duplicate,
                                check_correct_full_amount_update)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investment import process_investment

router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_all_charity_project(
    session: AsyncSession = Depends(get_async_session)
):
    charity_projects = await charity_project_crud.get_multi(session)
    return charity_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True
)
async def create_new_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    await check_charity_project_name_duplicate(charity_project.name, session)
    new_charity_project = await charity_project_crud.create(
        charity_project, session, skipped_saving=True
    )
    session.add_all(process_investment(
        new_charity_project,
        await donation_crud.get_not_invested_objects(
            session
        )
    ))
    await session.commit()
    await session.refresh(new_charity_project)
    return new_charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def partially_update_charity_project(
    project_id: int,
    object_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    charity_project = await check_charity_project_exists(project_id, session)
    await check_charity_project_is_closed(project_id, session)

    if object_in.full_amount is not None:
        await check_correct_full_amount_update(
            project_id, session, object_in.full_amount
        )

    if object_in.name is not None:
        await check_charity_project_name_duplicate(object_in.name, session)

    charity_project = await charity_project_crud.update(
        charity_project, object_in, session
    )
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def remove_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    charity_project = await check_charity_project_exists(project_id, session)
    await check_charity_project_is_invested(project_id, session)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project
