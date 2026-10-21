import os
import time
import schedule
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot
from aiogram.types import FSInputFile

# Импортируем большую базу цитат из отдельного файла
from quotes import QUOTES_DATABASE

# --- 1. МИНИ-СЕРВЕР ДЛЯ RENDER (поддержание портов) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Запускаем веб-сервер в фоновом потоке
threading.Thread(target=run_web_server, daemon=True).start()


# --- 2. НАСТРОЙКИ БОТА И КОНТЕНТ ---
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

MORNING_PRAYERS = (
    "🙏 **Утренние молитвы**\n\n"
    "Господи Иисусе Христе, Сыне Божий, молитв ради Пречистыя Твоея Матере "
    "и всех святых, помилуй нас. Слава Тебе, Боже наш, слава Тебе."
)

GOSPEL_OF_DAY = (
    "📖 **Евангелие дня**\n\n"
    "«Светильник для ноги Твоей — слово Твое и свет для стези моей.» (Пс. 118:105)\n\n"
    "Читаем и размышляем над Святым Писанием сегодняшнего дня."
)

EVENING_PRAYERS = (
    "🌙 **Вечерние молитвы**\n\n"
    "Боже вечный и Царю всякого создания, сподобивый мя и в сей час достигнути, "
    "прости ми грехи, яже содеях в сей день делом, словом и помышлением."
)

# Индекс для циклического перебора цитат
quote_index = 0

async def send_message_to_channel(text: str, photo_path: str = None):
    if not TOKEN or not CHANNEL_ID:
        print("Ошибка: не заданы BOT_TOKEN или CHANNEL_ID")
        return
    
    bot = Bot(token=TOKEN)
    try:
        if photo_path and os.path.exists(photo_path):
            photo = FSInputFile(photo_path)
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=text, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        print("Пост успешно опубликован!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
    finally:
        await bot.session.close()

def job_morning():
    asyncio.run(send_message_to_channel(MORNING_PRAYERS))

def job_gospel():
    asyncio.run(send_message_to_channel(GOSPEL_OF_DAY))

def job_quotes():
    global quote_index
    daily_quotes = []
    # Берем 5 цитат по очереди из базы
    for _ in range(5):
        daily_quotes.append(QUOTES_DATABASE[quote_index])
        quote_index = (quote_index + 1) % len(QUOTES_DATABASE) # Зацикливаем список
    
    text = "🌟 **Подборка 5 цитат на сегодня:**\n\n" + "\n\n".join(daily_quotes)
    asyncio.run(send_message_to_channel(text))

def job_evening():
    asyncio.run(send_message_to_channel(EVENING_PRAYERS))


# --- 3. РАСПИСАНИЕ (время по UTC) ---
schedule.every().day.at("04:00").do(job_morning)   # Утренние молитвы (~7:00 по МСК)
schedule.every().day.at("05:00").do(job_gospel)    # Евангелие дня
schedule.every().day.at("09:00").do(job_quotes)    # 5 цитат
schedule.every().day.at("18:00").do(job_evening)   # Вечерние молитвы (~21:00 по МСК)

if __name__ == "__main__":
    print("Бот запущен и переведен на автономный режим с базой в quotes.py...")
    
    # Проверка связи при старте
    asyncio.run(send_message_to_channel("🤖 Бот успешно обновлен! База на 150 цитат подключена."))
    
    while True:
        schedule.run_pending()
        time.sleep(1)
