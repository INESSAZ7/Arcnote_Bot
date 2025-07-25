from aiogram import Router, types
from aiogram.filters import CommandStart

from psycopg.connection_async import AsyncConnection
from database.queries import get_user, create_user

from lexicon.lexicon_ru import LEXICON


start_router = Router()

@start_router.message(CommandStart())
async def start_handler(message: types.Message, db_pool: AsyncConnection):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    async with db_pool.connection() as conn:
        user = await get_user(conn, telegram_id=telegram_id)
        
        if not user:
            await create_user(
                conn,
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            greeting = LEXICON["start_new"].format(first_name=first_name)
            
        else:
            greeting = LEXICON["start_existing"].format(first_name=first_name)

    await message.answer(greeting)
