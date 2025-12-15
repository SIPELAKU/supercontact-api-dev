import argparse
import asyncio
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from app.db.session import get_async_session
from app.models import Product

faker = Faker()


def generate_sku():
    number = random.randint(1000, 9999)
    return f"SKU-{number}"


async def seed_products(total: int = 10):
    db_gen = get_async_session()
    db = await anext(db_gen)
    for i in range(total):
        product = Product(
            product_name=faker.sentence(nb_words=3),
            price=faker.pyint(min_value=1),
            sku=generate_sku(),
            description=faker.sentence(),
        )
        db.add(product)

    try:
        await db.commit()
    except IntegrityError:
        print("IntegrityError: Failed to create product record")
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed products into the database.")
    parser.add_argument(
        "--total", type=int, default=10, help="Total number of leads to create"
    )
    args = parser.parse_args()

    print(f"Running database seed for {args.total} products...")
    asyncio.run(seed_products(total=args.total))
    print("Seed completed!")
