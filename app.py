import telebot
import os
from flask import Flask, request
import json

# Получаем токены из переменных окружения
TOKEN = os.environ.get('TELEGRAM_TOKEN')
# Этот секрет вы должны установить в настройках Vercel
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Эндпоинт для вебхука и главная страница
@app.route('/', methods=['GET', 'POST'])
def webhook_and_index():
    if request.method == 'POST':
        # Проверяем секретный заголовок
        secret_header = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if secret_header != WEBHOOK_SECRET:
            print(f"Invalid secret token received: {secret_header}")
            return "Forbidden", 403
        
        try:
            raw_data = request.stream.read().decode('utf-8')
            print("--- POST request received with valid secret ---")
            print("Data:", raw_data)

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
    bot.send_message(message.chat.id, "Success! The bot is working with a secure header webhook!")

# "Секретный" эндпоинт для установки вебхука
@app.route('/set_webhook')
def set_webhook():
    host = request.headers.get('X-Vercel-Deployment-Url') or request.host
    # URL теперь снова указывает на корень
    url = f"https://{host}/"
    
    bot.remove_webhook()
    # Устанавливаем вебхук, передавая наш секрет в параметре secret_token
    bot.set_webhook(url=url, secret_token=WEBHOOK_SECRET)
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
