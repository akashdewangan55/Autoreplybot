import telebot

bot = telebot.TeleBot("8403889292:AAH1F2ZhT46F23satXQb0RIZLtvVU4VtMi8")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "✅ Bot is working!")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    print(f"Received: {message.text}")
    bot.send_message(message.chat.id, f"You said: {message.text}")

print("Bot is running...")
bot.infinity_polling()