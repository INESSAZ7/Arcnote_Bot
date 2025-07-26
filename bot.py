import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from database.connection import get_pg_pool
from config_data.config import Config, load_config
from handlers import start_router, add_link_router

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format
    )
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')
    
    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token
    )
    dp = Dispatcher()

    # Создаём пул соединений с Postgres
    db_pool: psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.db.name,
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
    )

    # Регистрируем роутеры в диспетчере
    dp.include_routers(start_router, add_link_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем поллинг
    try:
        await dp.start_polling(
            bot, db_pool=db_pool
        )
    except Exception as e:
        logger.exception(e)
    finally:
        # Закрываем пул соединений
        await db_pool.close()
        logger.info("Connection to Postgres closed")

asyncio.run(main())
