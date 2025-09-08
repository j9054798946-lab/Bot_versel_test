import telebot
import os
from flask import Flask, request
import json

# Получаем переменные окружения
TOKEN = os.environ.get('TELEGRAM_TOKEN')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
PUBLIC_URL = os.environ.get('PUBLIC_URL')

if not TOKEN or not WEBHOOK_SECRET or not PUBLIC_URL:
    raise ValueError("FATAL ERROR: TELEGRAM_TOKEN, WEBHOOK_SECRET, and PUBLIC_URL environment variables must be set.")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Эндпоинт для вебхука и главная страница
@app.route('/', methods=['GET', 'POST'])
def webhook_and_index():
    if request.method == 'POST':
        secret_header = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if secret_header != WEBHOOK_SECRET:
            return "Unauthorized", 401
        
        raw_data = request.stream.read().decode('utf-8')
        update = telebot.types.Update.de_json(raw_data)
        bot.process_new_updates([update])
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
    url = f"https://{PUBLIC_URL}/"
    bot.remove_webhook()
    bot.set_webhook(url=url, secret_token=WEBHOOK_SECRET)
    return f"Webhook set to {url} with a secret token."

# Эндпоинт для проверки информации о вебхуке
@app.route('/get_webhook_info')
def get_webhook_info():
    try:
        info = bot.get_webhook_info()
        info_dict = { "url": info.url, "pending_update_count": info.pending_update_count, "last_error_message": info.last_error_message }
        return json.dumps(info_dict, indent=4)
    except Exception as e:
        return f"Error getting webhook info: {e}"

# Новый эндпоинт для прямого теста отправки сообщения
@app.route('/test_send')
def test_send():
    chat_id = request.args.get('chat_id')
    if not chat_id:
        return "Please provide a 'chat_id' parameter in the URL (e.g., /test_send?chat_id=12345).", 400

    try:
        print(f"Attempting to send a direct test message to chat_id: {chat_id}")
        # Мы намеренно используем try/except здесь, чтобы поймать и показать любую ошибку
        bot.send_message(chat_id, "This is a direct test message from the server.")
        print("Test message API call executed without raising an exception.")
        return f"A test message was sent to chat_id {chat_id}. Check your Telegram and Vercel logs.", 200
    except Exception as e:
        error_message = f"An error occurred while trying to send a test message: {e}"
        print(error_message)
        # Возвращаем ошибку в браузер и в логи, чтобы точно ее увидеть
        return error_message, 500
