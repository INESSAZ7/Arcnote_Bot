from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def send_reminder(bot, user_id, url, summary):
    try:
        await bot.send_message(user_id, f"🔔 Напоминание прочитать статью:\n{url}\n\n{summary}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")
