import os
import json
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

# === Telegram Bot Setup ===
API_KEY = os.environ.get("BOT_TOKEN")  # Safer: use Render env var
bot = telebot.TeleBot(API_KEY)
app = Flask(__name__)

# === Load / Save Keywords ===
DATA_FILE = 'keywords.json'
keywords = {}

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        keywords = json.load(f)

def save_keywords():
    with open(DATA_FILE, 'w') as f:
        json.dump(keywords, f, indent=4)

# === Bot Commands ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Start", callback_data="start_add_keyword"))
    bot.send_message(message.chat.id,
        "Welcome to the *Daily Earn Bot!*\n"
        "I can help you auto-reply in your Telegram group using keywords.\n\n"
        "➤ Join our Telegram Group: https://t.me/dailyearn20\n"
        "➤ Subscribe to our YouTube Channel: https://youtube.com/@earningtricks2\n\n"
        "*Tap 'Start' below to add a keyword + link.*",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "start_add_keyword")
def callback_start(call):
    msg = bot.send_message(call.message.chat.id, "Please type your keyword:")
    bot.register_next_step_handler(msg, get_keyword)

def get_keyword(message):
    keyword = message.text.strip().lower()
    if not keyword:
        bot.send_message(message.chat.id, "Keyword cannot be empty.")
        return
    msg = bot.send_message(message.chat.id, "Now send the link or message you want to associate with this keyword:")
    bot.register_next_step_handler(msg, lambda m: save_keyword_pair(m, keyword))

def save_keyword_pair(message, keyword):
    response = message.text.strip()
    keywords[keyword] = response
    save_keywords()
    bot.send_message(message.chat.id, "✅ Your keyword has been saved successfully.")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def auto_reply(message):
    if message.chat.type in ['group', 'supergroup']:
        key = message.text.strip().lower()
        if key in keywords:
            bot.reply_to(message, keywords[key])

@bot.message_handler(commands=['list'])
def list_keywords(message):
    if keywords:
        msg = "\n".join([f"➤ `{k}` → {v}" for k, v in keywords.items()])
        bot.send_message(message.chat.id, f"*Stored Keywords:*\n{msg}", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "No keywords saved yet.")

@bot.message_handler(commands=['remove'])
def remove_keyword(message):
    msg = bot.send_message(message.chat.id, "Type the keyword you want to delete:")
    bot.register_next_step_handler(msg, delete_keyword)

def delete_keyword(message):
    key = message.text.strip().lower()
    if key in keywords:
        del keywords[key]
        save_keywords()
        bot.send_message(message.chat.id, f"✅ Keyword `{key}` removed.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Keyword not found.")

@bot.message_handler(commands=['settings'])
def settings(message):
    bot.send_message(message.chat.id, "Settings feature is coming soon...")

# === Set Bot Commands ===
bot.set_my_commands([
    BotCommand("/start", "Start the bot"),
    BotCommand("/list", "View all keywords"),
    BotCommand("/remove", "Delete a keyword"),
    BotCommand("/settings", "Bot settings"),
])

# === Flask Webhook Routes ===
@app.route('/')
def index():
    return "Bot is running!"

@app.route(f"/webhook/{API_KEY}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
