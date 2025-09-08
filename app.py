import telebot
import os
from flask import Flask, request

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Эндпоинт для вебхука и главная страница
@app.route('/', methods=['GET', 'POST'])
def webhook_and_index():
    if request.method == 'POST':
        # Получаем обновление от Telegram
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        # Обрабатываем его
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        # Для GET запросов просто показываем, что бот работает
        return "Bot is running! Use /set_webhook to initialize."

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello from Vercel! The webhook is working correctly!")

# "Секретный" эндпоинт для установки вебхука
@app.route('/set_webhook')
def set_webhook():
    # URL, который Vercel предоставит для нашего приложения
    host = request.headers.get('X-Vercel-Deployment-Url') or request.host
    # Убедимся, что используем HTTPS
    url = f"https://{host}"
    
    bot.remove_webhook()
    bot.set_webhook(url=url)
    return f"Webhook set to {url}"
