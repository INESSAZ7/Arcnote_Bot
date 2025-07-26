from aiogram import Router, types
from aiogram.filters import Command
from utils.link_parser import extract_metadata

from lexicon.lexicon_ru import LEXICON


add_link_router = Router()

@add_link_router.message(Command("add"))
async def add_link_handler(message: types.Message):
    # Ожидаем: /add <url> #category/subcategory HH:MM, но обрабатываем и без категории/времени
    parts = message.text.strip().split()
    url = next((p for p in parts if p.startswith('http')), None)
    category = next((p for p in parts if p.startswith('#')), None)
    time_str = next((p for p in parts if ':' in p), None)

    # Парсим категорию
    if category:
        cat_parts = category.lstrip('#').split('/')
        topic = cat_parts[0]
        subcategory = cat_parts[1] if len(cat_parts) > 1 else ""
    else:
        topic = "без категории"
        subcategory = ""

    # Получаем заголовок, summary и source
    if url:
        title, summary, source = await extract_metadata(url)
    else:
        await message.answer("Пожалуйста, укажите ссылку после /add")
        return

    # Заглушка для времени
    time_display = time_str if time_str else "без времени"

    await message.answer(
        f"Сохранено в тему: {topic}/{subcategory or 'без подкатегории'}\n"
        f"🔖 {title}\n"
        f"🕓 Напоминание в {time_display}\n"
        f"🌐 Source: {source}"
    )


