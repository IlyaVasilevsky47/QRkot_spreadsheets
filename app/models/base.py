from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer

from app.core.db import Base

VALIDATION_VALUE_FULL_AMOUNT = 0
BASE_FINANCE_REPR = (
    'full_amount: {full_amount} '
    'invested_amount: {invested_amount} '
    'fully_invested: {fully_invested} '
    'create_date: {create_date} '
    'close_date: {close_date}'
)


class BaseFinance(Base):
    __abstract__ = True
    __table_args__ = (
        CheckConstraint(
            'full_amount' < 'invested_amount',
            name='check_full_amount_invested_amount'
        ),
        CheckConstraint(
            f'full_amount > {VALIDATION_VALUE_FULL_AMOUNT}',
            name='check_full_amount_positive'
        ),
    )

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    def __repr__(self) -> str:
        return BASE_FINANCE_REPR.format(
            full_amount=self.full_amount,
            invested_amount=self.invested_amount,
            fully_invested=self.fully_invested,
            create_date=self.create_date,
            close_date=self.close_date
        )
