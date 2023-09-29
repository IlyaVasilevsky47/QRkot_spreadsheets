from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import (DonationCreate, DonationDBFull,
                                  DonationDBShort)
from app.services.investment import process_investment

router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationDBFull],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True
)
async def get_all_donation(
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.post(
    '/',
    response_model=DonationDBShort,
    dependencies=[Depends(current_user)],
    response_model_exclude_none=True
)
async def create_new_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Только для пользователей"""
    new_donation = await donation_crud.create(
        donation,
        session,
        user,
        skipped_saving=True
    )
    session.add_all(process_investment(
        new_donation,
        await charity_project_crud.get_not_invested_objects(
            session
        )
    ))
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/my',
    response_model=list[DonationDBShort],
    dependencies=[Depends(current_user)],
)
async def get_my_donation(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Получает список всех донатов."""
    donations = await donation_crud.get_donations_by_user(
        session, user
    )
    return donations
