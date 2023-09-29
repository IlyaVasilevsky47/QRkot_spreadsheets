from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import BaseFinance

DONATION_REPR = (
    'user_id: {user_id} '
    'comment: {comment} '
)


class Donation(BaseFinance):
    user_id = Column(Integer, ForeignKey(
        'user.id', name='fk_donation_user_id_user'
    ))
    comment = Column(Text)

    def __repr__(self) -> str:
        return DONATION_REPR.format(
            user_id=self.user_id,
            comment=self.comment
        ) + super().__repr__()
