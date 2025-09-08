import telebot
import os
from flask import Flask, request
import json

# --- Configuration ---
# Load environment variables. These must be set in your Vercel project settings.
TOKEN = os.environ.get('TELEGRAM_TOKEN')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
PUBLIC_URL = os.environ.get('PUBLIC_URL')

# A fatal error will occur on Vercel if these are not set.
if not TOKEN or not WEBHOOK_SECRET or not PUBLIC_URL:
    raise ValueError("FATAL ERROR: TELEGRAM_TOKEN, WEBHOOK_SECRET, and PUBLIC_URL environment variables must be set.")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# --- Main Webhook Handler ---
# This single endpoint receives all updates from Telegram.
@app.route('/', methods=['GET', 'POST'])
def webhook_and_index():
    # A GET request is for health checks (like UptimeRobot) or manual browser checks.
    if request.method == 'GET':
        return "Bot is running!", 200

    # A POST request is an update from Telegram.
    if request.method == 'POST':
        # First, ensure the request is legitimate and from Telegram.
        secret_header = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if secret_header != WEBHOOK_SECRET:
            print("Unauthorized webhook call received.")
            return "Unauthorized", 401
        
        try:
            # Read the update from the request
            raw_data = request.stream.read().decode('utf-8')
            update = telebot.types.Update.de_json(raw_data)
            
            # --- Manual Command Routing ---
            # Manually check for commands instead of using library decorators.
            # This is the most reliable method in a serverless environment.
            if update.message and update.message.text:
                text = update.message.text
                chat_id = update.message.chat.id
                
                print(f"Received message from chat_id {chat_id}: '{text}'")

                # Route commands to their functions
                if text == '/start':
                    handle_start(chat_id)
                # Add more commands here with 'elif'
                # elif text == '/help':
                #     handle_help(chat_id)
                else:
                    # Optional: handle unknown commands or regular text
                    print(f"No handler for text: '{text}'")

        except Exception as e:
            print(f"An error occurred in webhook handler: {e}")
            
        # Always return 'OK' to Telegram to acknowledge receipt of the update.
        return 'OK', 200


# --- Command Handler Functions ---
# Define a separate function for each command for clean code.
def handle_start(chat_id):
    """Handles the /start command."""
    try:
        bot.send_message(chat_id, "Hello! This is a clean, working template for a Vercel bot.")
        print(f"Sent '/start' response to chat_id {chat_id}")
    except Exception as e:
        print(f"Error in handle_start for chat_id {chat_id}: {e}")


# --- Setup Endpoint ---
# A "secret" endpoint to set the webhook URL with Telegram.
# Call this once after each deployment or change to PUBLIC_URL.
@app.route('/set_webhook')
def set_webhook():
    url = f"https://{PUBLIC_URL}/"
    bot.remove_webhook()
    bot.set_webhook(url=url, secret_token=WEBHOOK_SECRET)
    print(f"Webhook set to: {url}")
    return f"Webhook successfully set to {url}"
