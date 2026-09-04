import os
import random
import time
import schedule
import sqlite3
import telebot
from telebot import types
from dotenv import load_dotenv
from flask import Flask
import threading

#запуск енв файла 
load_dotenv
#ывеб 
TOKEN = os.getenv("BOT_TOKEN")
#сощдается бот мой через токе а токен в енв поэт выше дотов
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)



def init_users_db():
    #    создает конект веревку м ежду моим фл питоном и бд что в скобках 
  conn = sqlite3.connect("bot_users.db")
  #инстурмент для оптравки команд в бд курсор 
  cursor = conn.cursor()
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)"
  )
  #все измения зафиксируй   измени сохрани
  conn.commit()
  #закрываем веревек чтобы она не жрала наш комп те не застрнвал в нашемпк 
  conn.close()


init_users_db()


def save_user_id(user_id):
  conn = sqlite3.connect("bot_users.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
  )
  conn.commit()
  conn.close()


def get_all_user_ids():
  conn = sqlite3.connect("bot_users.db")
  cursor = conn.cursor()
  cursor.execute("SELECT user_id FROM users")
  ids = [row[0] for row in cursor.fetchall()]
  conn.close()
  return ids


pets=["баунтихантер ",
      "тюлень",
     " кот-сквиш",
      "красная панда",
     "чармандер",
     " скунс",
    "зеленый попугай", ]


def send_mes_afternoon():
    users = get_all_user_ids()
    message = random.choice(pets)
    for user in users:
        try:
            bot.send_message(user, message)
        except Exception:
         pass


schedule.every().day.at("13:00", "Europe/Moscow").do(send_mes_afternoon)


def run_scheduler():
  while True:
    schedule.run_pending()
    time.sleep(1)


threading.Thread(target=run_scheduler, daemon=True).start()

@bot.message_handler(commands=["start"])
def start_cmd(message):
  save_user_id(message.from_user.id)
  bot.send_message(message.chat.id, "я запомнив тебяʕ•ᴥ•ʔ!")


if __name__ == "__main__":
  flask_thread = threading.Thread(target=run_flask, daemon=True)
  flask_thread.start()

  print("Starting bot polling...")

  try:
    bot.remove_webhook()
  except Exception as e:
    print(f"Webhook reset error: {e}")

  bot.infinity_polling(skip_pending=True)


