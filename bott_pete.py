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

# Запуск dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def init_users_db():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)"
    )
    conn.commit()
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

PETS = {
    "баунтихантер": "images/bayntixanter.png",
    "белка": "images/belka.jpg",
    "сфил": "images/cfiiill.jpg",
    "чармандер": "images/cpapmander.jpg",
    "фея": "images/fui.jpg",
    "енот": "images/i.png",
    "ико": "images/ioko.jpg",
    "кабан": "images/kaban.png",
    "кот": "images/kot.png",
    "кот-сквиш": "images/kotskvish.png",
    "мипо": "images/mipooo.jpg",
    "некомата": "images/nekomata.jpg",
    "неритантан": "images/neritantan.jpg",
    "красная панда": "images/pandakras.png",
    "зеленый попугай": "images/ptatata.png",
    "сатир": "images/satyr.png",
    "скунс🦨": "images/skyns.png",
    "тибетская лиса🦊": "images/tibetlisa.png",
    "тюлень": "images/tylen.jpg",
    "кошкодев^w^": "images/tyuncat.png",
    "воул-убийца": "images/wolf.png",
    "химера": "images/ximeraa.jpg",
    "хомяк": "images/xomqkk.png",
}

def send_mes_afternoon():
    users = get_all_user_ids()
    if not users:
        return

    pet_name = random.choice(list(PETS.keys()))
    photo_path = PETS[pet_name]

    for user in users:
        try:
            if os.path.exists(photo_path):
                with open(photo_path, "rb") as photo_file:
                    bot.send_photo(
                        chat_id=user,
                        photo=photo_file,
                        caption=f"твой питомка: <b>{pet_name}</b>!",
                        parse_mode="HTML",
                    )
            else:
                print(f"Файл {photo_path} не найден!")
        except Exception as e:
            print(f"Ошибка отправки пользователю {user}: {e}")

schedule.every().day.at("13:30", "Europe/Moscow").do(send_mes_afternoon)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запускаем планировщик задач в фоновом режиме
threading.Thread(target=run_scheduler, daemon=True).start()

@bot.message_handler(commands=["start"])
def start_cmd(message):
    save_user_id(message.from_user.id)
    bot.send_message(message.chat.id, "я запомнив тебяʕ•ᴥ•ʔ!")

# Улучшенная функция запуска бота с автоматическим перезапуском при ошибке
def run_bot():
    print("Starting bot polling...")
    try:
        bot.remove_webhook()
    except Exception as e:
        print(f"Webhook reset error: {e}")

    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
        except Exception as e:
            print(f"Bot polling error: {e}. Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Flask работает в основном потоке
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)
