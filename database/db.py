import logging
from datetime import datetime, timezone
from typing import Any

from app.bot.enums.roles import UserRole
from psycopg import AsyncConnection

logger = logging.getLogger(__name__)


# def register_user(user_id: int, username: str, first_name: str, last_name: str):
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     # Check if user already exists
#     cursor.execute("SELECT user_id FROM daily_english.users WHERE user_id = %s", (user_id,))
#     if cursor.fetchone() is None:
#         # Insert new user
#         cursor.execute("""
#             INSERT INTO daily_english.users (user_id, username, first_name, last_name)
#             VALUES (%s, %s, %s, %s)
#         """, (user_id, username, first_name, last_name))
#         conn.commit()
    
#     cursor.close()
#     release_db_connection(conn)

async def add_user(
    conn: AsyncConnection,
    *,
    user_id: int,
    username: str | None = None,
    language: str = "ru",
    role: UserRole = UserRole.USER,
    is_alive: bool = True,
    banned: bool = False,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                INSERT INTO users(user_id, username, language, role, is_alive, banned)
                VALUES(
                    %(user_id)s, 
                    %(username)s, 
                    %(language)s, 
                    %(role)s, 
                    %(is_alive)s, 
                    %(banned)s
                ) ON CONFLICT DO NOTHING;
            """,
            params={
                "user_id": user_id,
                "username": username,
                "language": language,
                "role": role,
                "is_alive": is_alive,
                "banned": banned,
            },
        )
    logger.info(
        "User added. Table=`%s`, user_id=%d, created_at='%s', "
        "language='%s', role=%s, is_alive=%s, banned=%s",
        "users",
        user_id,
        datetime.now(timezone.utc),
        language,
        role,
        is_alive,
        banned,
    )


async def get_user(
    conn: AsyncConnection,
    *,
    user_id: int,
) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                SELECT 
                    id,
                    user_id,
                    username,
                    language,
                    role,
                    is_alive,
                    banned,
                    created_at
                    FROM users WHERE user_id = %s;
            """,
            params=(user_id,),
        )
        row = await data.fetchone()
    logger.info("Row is %s", row)
    return row if row else None





