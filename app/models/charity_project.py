from sqlalchemy import Column, String, Text

from app.models.base import BaseFinance

CHARITY_PROJECT_REPR = (
    'name: {name} '
    'description: {description} '
)


class CharityProject(BaseFinance):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return CHARITY_PROJECT_REPR.format(
            name=self.name,
            description=self.description
        ) + super().__repr__()
