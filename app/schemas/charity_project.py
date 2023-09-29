from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

TIME_NOW = (datetime.now()).isoformat(timespec='minutes')


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str]
    full_amount: Optional[PositiveInt]

    class Config:
        extra = Extra.forbid
        min_anystr_length = 1


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., max_length=100)
    description: str
    full_amount: PositiveInt


class CharityProjectUpdate(CharityProjectBase):
    pass


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
