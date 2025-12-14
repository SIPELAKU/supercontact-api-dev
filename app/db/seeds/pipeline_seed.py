import argparse
import asyncio
import random
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from faker import Faker
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.db.session import get_async_session
from app.models import Contact, Pipeline, DealStage

faker = Faker()


async def seed_pipelines(total: int = 10, contact_id: Optional[UUID] = None):
    db_gen = get_async_session()
    db = await anext(db_gen)
    query = await db.scalars(select(Contact))
    contacts = query.all()

    now = datetime.now(timezone.utc)
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month_start = (this_month_start + timedelta(days=32)).replace(day=1)

    for i in range(total):
        delta_seconds = int((next_month_start - this_month_start).total_seconds())
        expected_close = this_month_start + timedelta(seconds=random.randint(0, delta_seconds))
        pipeline = Pipeline(
            deal_name=faker.name(),
            client_account=contacts[i % len(contacts)].id if not contact_id else contact_id,
            deal_stage=random.choice(list([DealStage.CLOSED_WON, DealStage.CLOSED_LOST])),
            expected_close_date=expected_close,
            amount=faker.pyint(min_value=1),
            probability_of_close=faker.pyint(min_value=1, max_value=100),
            notes=faker.sentence(),
        )
        db.add(pipeline)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed leads into the database.")
    parser.add_argument(
        "--total", type=int, default=10, help="Total number of leads to create"
    )
    parser.add_argument(
        "--contact_id", type=UUID, help="Assign all leads to this user ID"
    )
    args = parser.parse_args()

    print(f"Running database seed for {args.total} pipelines...")
    asyncio.run(seed_pipelines(total=args.total, contact_id=args.contact_id))
    print("Seed completed!")
