import os
import time
import schedule
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot

# --- МИНИ-СЕРВЕР ДЛЯ RENDER (чтобы веб-сервис не закрывал порт) ---
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


# --- НАСТРОЙКИ БОТА И КОНТЕНТ ---
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Примеры контента (можете наполнить своими текстами)
MORNING_PRAYERS = "🙏 **Утренние молитвы**\n\nГосподи Иисусе Христе, Сыне Божий, молитв ради Пречистыя Твоея Матере... (ваш текст утренних молитв)"
GOSPEL_OF_DAY = "📖 **Евангелие дня**\n\nЧтение из святого Евангелия... (текст дня)"
QUOTES = [
    "💡 **Цитата 1:** Стяжи дух мирен, и вокруг тебя спасутся тысячи. (прп. Серафим Саровский)",
    "💡 **Цитата 2:** Любите врагов ваших, благотворите ненавидящим вас.",
    "💡 **Цитата 3:** С нами Бог, разумейте, языцы, и покоряйтеся...",
    "💡 **Цитата 4:** Молитва — щит для ума, броня для сердца и меч против дьявола.",
    "💡 **Цитата 5:** Во всем поступайте с людьми так, хотите, чтобы они поступали с вами."
]
EVENING_PRAYERS = "🌙 **Вечерние молитвы**\n\nБоже вечный и Царю всякого создания... (ваш текст вечерних молитв)"

async def send_message_to_channel(text: str):
    if not TOKEN or not CHANNEL_ID:
        print("Ошибка: не заданы BOT_TOKEN или CHANNEL_ID")
        return
    
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        print("Пост по расписанию успешно опубликован!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
    finally:
        await bot.session.close()

def job_morning():
    asyncio.run(send_message_to_channel(MORNING_PRAYERS))

def job_gospel():
    asyncio.run(send_message_to_channel(GOSPEL_OF_DAY))

def job_quotes():
    # Отправляем 5 цитат по очереди или все сразу в одном сообщении
    text = "🌟 **Подборка 5 цитат на сегодня:**\n\n" + "\n\n".join(QUOTES)
    asyncio.run(send_message_to_channel(text))

def job_evening():
    asyncio.run(send_message_to_channel(EVENING_PRAYERS))


# --- РАСПИСАНИЕ (время по UTC, учитывайте часовой пояс) ---
# Например, утром в 07:00, днем евангелие в 09:00, цитаты в 12:00, вечером в 21:00
schedule.every().day.at("07:00").do(job_morning)
schedule.every().day.at("07:30").do(job_gospel)
schedule.every().day.at("12:00").do(job_quotes)
schedule.every().day.at("21:00").do(job_evening)

if __name__ == "__main__":
    print("Бот запущен и следит за расписанием...")
    # Опционально: можно отправить тестовое сообщение при старте, чтобы проверить связь
    asyncio.run(send_message_to_channel("🤖 Бот успешно запущен и переведен на постоянное расписание!"))
    
    while True:
        schedule.run_pending()
        time.sleep(1)
