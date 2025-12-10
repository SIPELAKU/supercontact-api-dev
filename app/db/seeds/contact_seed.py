import argparse
import asyncio
from uuid import UUID

from faker import Faker
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.db.session import get_async_session
from app.models import Contact, User

faker = Faker()


async def seed_contacts(total: int = 5, user_id: UUID = None):
    db_gen = get_async_session()
    db = await anext(db_gen)
    query = await db.scalars(select(User))
    users = query.all()
    for i in range(total):
        contact = Contact(
            user_id=users[i % len(users)].id if not user_id else None,
            name=faker.name(),
            email=faker.email(),
            company=faker.company(),
            phone=faker.phone_number(),
        )
        db.add(contact)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed leads into the database.")
    parser.add_argument(
        "--total", type=int, default=5, help="Total number of leads to create"
    )
    parser.add_argument(
        "--user_id", type=UUID, help="Assign all leads to this user ID"
    )
    args = parser.parse_args()

    print(f"Running database seed for {args.total} contacts...")
    asyncio.run(seed_contacts(total=args.total, user_id=args.user_id))
    print("Seed completed!")
