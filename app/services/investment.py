from datetime import datetime

from app.models import BaseFinance

VALUE_OF_INVESTED_AMOUNT = 0


def process_investment(
    target: BaseFinance, sources: list[BaseFinance]
) -> list[BaseFinance]:
    target.invested_amount = (
        target.invested_amount
        if target.invested_amount
        else VALUE_OF_INVESTED_AMOUNT
    )
    updated_sources = []
    for source in sources:
        to_invest = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount
        )

        for db_object in [source, target]:
            db_object.invested_amount += to_invest
            if db_object.full_amount == db_object.invested_amount:
                db_object.fully_invested = True
                db_object.close_date = datetime.now()
                if db_object == source:
                    updated_sources.append(source)

        if target.fully_invested:
            break

    return updated_sources
