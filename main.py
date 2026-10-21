import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Мини-сервер для ответа Render, чтобы он не думал, что бот упал
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Запускаем веб-сервер в отдельном потоке, чтобы он не мешал боту
threading.Thread(target=run_web_server, daemon=True).start()

# ДАЛЬШЕ ИДЕТ ВАШ ОБЫЧНЫЙ КОД БОТА...

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
