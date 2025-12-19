from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class PrefixSequence(StrEnum):
    QUOTATION = 'quotation'


async def get_next_sequence(prefix: PrefixSequence, db: AsyncSession):
    year_suffix = datetime.now(timezone.utc).strftime("%y")
    seq_name = f"{prefix}_{year_suffix}_seq"

    # Pastikan sequence ada
    await db.execute(text(f"""
        CREATE SEQUENCE IF NOT EXISTS {seq_name}
        START WITH 1
        INCREMENT BY 1
    """))

    # Ambil nomor berikutnya
    result = await db.execute(
        text(f"SELECT nextval('{seq_name}')")
    )

    return year_suffix, result.scalar_one()
