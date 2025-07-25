import asyncio
import logging
import os
import sys

from database.connection import get_pg_connection
from config_data.config import Config, load_config
from psycopg import AsyncConnection, Error

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format,
)

logger = logging.getLogger(__name__)


async def main():
    connection: AsyncConnection | None = None

    try:
        connection = await get_pg_connection(
            db_name=config.db.name,
            host=config.db.host,
            port=config.db.port,
            user=config.db.user,
            password=config.db.password,
        )
        async with connection:
            async with connection.transaction():
                async with connection.cursor() as cursor:
                    # Table `users`
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS arcnote.users(
                                id SERIAL PRIMARY KEY,
                                telegram_id BIGINT NOT NULL UNIQUE, -- Telegram user ID
                                username VARCHAR(50), -- @username
                                first_name VARCHAR(50),
                                last_name VARCHAR(50),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ); 
                        """
                    )

                    # Table `links`
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS arcnote.links(
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL REFERENCES arcnote.users(id) ON DELETE CASCADE,
                                url TEXT NOT NULL,
                                lang VARCHAR(10),  -- 'ru', 'en', 'de' и т.д.
                                title TEXT,
                                topic TEXT,
                                subcategory TEXT,
                                summary TEXT,
                                tsv_summary tsvector,
                                resource_type TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            );
                        """
                    )

                    # Table `reminders`
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS arcnote.reminders(
                                    id SERIAL PRIMARY KEY,
                                    link_id INTEGER NOT NULL REFERENCES arcnote.links(id) ON DELETE CASCADE,
                                    remind_at TIMESTAMP NOT NULL,
                                    sent BOOLEAN DEFAULT FALSE,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ); 
                        """
                    )

                    #Indexes                 
                    await cursor.execute(
                        query="""
                            CREATE INDEX idx_links_user ON arcnote.links(user_id);
                            CREATE INDEX idx_links_topic_subcat ON arcnote.links(topic, subcategory);
                            CREATE INDEX idx_links_summary_fts ON arcnote.links USING GIN (tsv_summary);
                            CREATE INDEX idx_reminders_due ON arcnote.reminders(remind_at, sent);
                        """
                    )
                    
                    #Functions
                    await cursor.execute(
                        query="""
                        -- Функцию генерации tsvector с учётом языка
                            CREATE OR REPLACE FUNCTION arcnote.update_tsv_summary() RETURNS trigger AS $$
                            BEGIN
                                IF NEW.lang IS NOT NULL THEN
                                    NEW.tsv_summary := to_tsvector(NEW.lang, COALESCE(NEW.summary, ''));
                                ELSE
                                    NEW.tsv_summary := to_tsvector('simple', COALESCE(NEW.summary, ''));
                                END IF;
                                RETURN NEW;
                            END;
                            $$ LANGUAGE plpgsql;

                        -- Триггер
                            CREATE TRIGGER trg_update_tsv_summary
                            BEFORE INSERT OR UPDATE ON arcnote.links
                            FOR EACH ROW
                            EXECUTE FUNCTION arcnote.update_tsv_summary();
                        """
                    )
                logger.info("Tables, functions and triggers were successfully created")
    except Error as db_error:
        logger.exception("Database-specific error: %s", db_error)
    except Exception as e:
        logger.exception("Unhandled error: %s", e)
    finally:
        if connection:
            await connection.close()
            logger.info("Connection to Postgres closed")


asyncio.run(main())