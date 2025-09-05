import telebot
import os
from flask import Flask, request

# Получаем токен из переменных окружения
TOKEN = os.environ.get('TELEGRAM_TOKEN')
# URL, который Vercel предоставит для нашего приложения
APP_URL = f"https://{os.environ.get('VERCEL_URL')}"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Endpoint для вебхука
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello! This is a simple bot running on Vercel.")

# Устанавливаем вебхук при запуске, если мы не в локальной среде
if os.environ.get("VERCEL"):
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)

# Добавим простую главную страницу для проверки
@app.route('/')
def index():
    return "Bot is running!"
