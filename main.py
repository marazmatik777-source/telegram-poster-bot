import asyncio
import os
from aiogram import Bot

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

async def send_test_post():
    if not TOKEN or not CHANNEL_ID:
        print("Ошибка: не заданы переменные окружения BOT_TOKEN или CHANNEL_ID")
        return
        
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text="🤖 *Привет! Бот успешно запущен в облаке Render!*", parse_mode="Markdown")
        print("Пост успешно опубликован!")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(send_test_post())
