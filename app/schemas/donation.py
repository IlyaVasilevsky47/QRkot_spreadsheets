from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, PositiveInt


class DonationBase(BaseModel):
    full_amount: Optional[PositiveInt]
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationCreate(DonationBase):
    full_amount: PositiveInt


class DonationDBShort(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDBFull(DonationDBShort):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
