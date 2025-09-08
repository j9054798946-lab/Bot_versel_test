import telebot
import os
from flask import Flask, request
import json

# Получаем переменные окружения
TOKEN = os.environ.get('TELEGRAM_TOKEN')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
# URL вашего основного домена, который вы добавите в Vercel
PUBLIC_URL = os.environ.get('PUBLIC_URL')

# Проверяем, что все переменные установлены
if not TOKEN or not WEBHOOK_SECRET or not PUBLIC_URL:
    # Эта ошибка будет видна в логах Vercel при запуске
    raise ValueError("FATAL ERROR: TELEGRAM_TOKEN, WEBHOOK_SECRET, and PUBLIC_URL environment variables must be set.")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Эндпоинт для вебхука и главная страница
@app.route('/', methods=['GET', 'POST'])
def webhook_and_index():
    if request.method == 'POST':
        secret_header = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if secret_header != WEBHOOK_SECRET:
            print(f"Invalid secret token received. Got: '{secret_header}'")
            return "Unauthorized", 401
        
        try:
            raw_data = request.stream.read().decode('utf-8')
            print("--- POST request received with valid secret ---")
            update = telebot.types.Update.de_json(raw_data)
            bot.process_new_updates([update])
            print("Update processed successfully.")
        except Exception as e:
            print(f"Error processing update: {e}")
            
        return 'OK', 200
    else:
        return "Bot is running! Use /set_webhook to initialize."

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "IT'S ALIVE! The bot is finally working correctly!")

# "Секретный" эндпоинт для установки вебхука
@app.route('/set_webhook')
def set_webhook():
    # Теперь мы используем наш постоянный публичный URL
    url = f"https://{PUBLIC_URL}/"
    
    bot.remove_webhook()
    bot.set_webhook(url=url, secret_token=WEBHOOK_SECRET)
    print(f"Webhook set to the permanent URL: {url}")
    return f"Webhook set to {url} with a secret token."

# Эндпоинт для проверки информации о вебхуке
@app.route('/get_webhook_info')
def get_webhook_info():
    try:
        info = bot.get_webhook_info()
        info_dict = {
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "last_error_date": info.last_error_date,
            "last_error_message": info.last_error_message,
            "max_connections": info.max_connections,
            "ip_address": info.ip_address
        }
        return json.dumps(info_dict, indent=4)
    except Exception as e:
        return f"Error getting webhook info: {e}"
