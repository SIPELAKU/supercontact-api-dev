from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
    conn.commit()

print("alembic_version table reset successfully.")
