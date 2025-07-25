from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: list[int] # Список админов

@dataclass
class DatabaseConfig:
    name: str
    host: str
    port: int
    user: str
    password: str

@dataclass
class LoggSettings:
    level: str
    format: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    log: LoggSettings


# Создаем функцию, которая будет читать файл .env и возвращать
# экземпляр класса Config с заполненными полями token и admin_ids
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids = env.list("ADMIN_IDS", default=[])
        ),
        db=DatabaseConfig(
            name=env("POSTGRES_DB"),
            host=env("POSTGRES_HOST"),
            port=env.int("POSTGRES_PORT"),
            user=env("POSTGRES_USER"),
            password=env("POSTGRES_PASSWORD"),
        ),
        log = LoggSettings(
            level=env("LOG_LEVEL"),
            format=env("LOG_FORMAT")
        )
    )
