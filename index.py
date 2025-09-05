from flask import Flask, request, abort
import telebot
import os

# Вставьте ваш токен сюда (временно для теста)
TOKEN = "8242128097:AAG_NqmWEbMqiaN5lFfMUtC1_Gt_2gLuF4w"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello! This is a simple bot running on Vercel.")

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

# Endpoint для установки webhook
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    # Получаем URL текущего приложения
    host = request.host
    webhook_url = f"https://{host}/webhook"
    
    # Удаляем старый webhook
    bot.remove_webhook()
    # Устанавливаем новый
    bot.set_webhook(url=webhook_url)
    
    return f"Webhook set to {webhook_url}"

# Главная страница для проверки
@app.route('/')
def index():
    return "Hello, this is a simple Telegram bot running on Vercel!"

# Запуск приложения
if __name__ == '__main__':
    app.run()