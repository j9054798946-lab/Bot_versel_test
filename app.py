import telebot
import os
from flask import Flask, request

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Эндпоинт для приема обновлений от Telegram
@app.route('/', methods=['POST'])
def webhook():
    print("Received webhook update!") # Added for debugging
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return "Unsupported Media Type", 415

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello! This bot is now set up with a webhook.")

# "Секретный" эндпоинт для установки вебхука
@app.route('/set_webhook')
def set_webhook():
    # URL, который Vercel предоставит для нашего приложения
    # Мы берем его из заголовков запроса, чтобы он всегда был правильным
    host = request.headers.get('X-Vercel-Deployment-Url') or request.host
    url = f"https://{host}"
    print(f"Attempting to set webhook to: {url}") # Added for debugging
    
    bot.remove_webhook()
    bot.set_webhook(url=url)
    return f"Webhook set to {url}"

# Главная страница для проверки
@app.route('/health') # Changed route
def index():
    return "Bot is running! Use /set_webhook to initialize."