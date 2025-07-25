import logging
from datetime import datetime, timezone
from typing import Any


from psycopg import AsyncConnection

logger = logging.getLogger(__name__)



async def create_user(
    conn: AsyncConnection,
    *,
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                INSERT INTO arcnote.users(telegram_id, username, first_name, last_name)
                VALUES(
                    %(telegram_id)s, 
                    %(username)s, 
                    %(first_name)s, 
                    %(last_name)s
                ) ON CONFLICT DO NOTHING;
            """,
            params={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name
            },
        )
    logger.info(f"User added. Table=`arcnote.users`, telegram_id={telegram_id}, created_at='{datetime.now(timezone.utc)}', username='{username}', first_name='{first_name}', last_name='{last_name}'"
    )


async def get_user(
    conn: AsyncConnection,
    *,
    telegram_id: int
) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                SELECT 
                    id,
                    telegram_id,
                    username,
                    first_name,
                    last_name,
                    created_at
                    FROM arcnote.users WHERE telegram_id = %s;
            """,
            params=(telegram_id,),
        )
        row = await data.fetchone()
    logger.info("Row is %s", row)
    return row if row else None





