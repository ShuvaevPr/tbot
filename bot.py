import sqlite3
import validators
import telebot
import random
import re

TOKEN = '7756834267:AAG_LXcS-2PEMSP2bBF-JX5PR3z6857rXjQ'

def create_db():
    conn = sqlite3.connect('links.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def save_link(user_id: int, url: str):
    conn = sqlite3.connect('links.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO links (user_id, url) VALUES (?, ?)", (user_id, url))
    conn.commit()
    conn.close()

def link_exists(user_id: int, url: str) -> bool:
    conn = sqlite3.connect('links.db')
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM links WHERE user_id = ? AND url = ?", (user_id, url))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_random_link(user_id: int) -> str:
    conn = sqlite3.connect('links.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM links WHERE user_id = ?", (user_id,))
    links = cursor.fetchall()

    if links:
        random_link = random.choice(links)
        link_id, link_url = random_link
        cursor.execute("DELETE FROM links WHERE id = ?", (link_id,))
        conn.commit()
        conn.close()
        return link_url

    conn.close()
    return None


def is_valid_url(url: str) -> bool:
    return validators.url(url)

def is_link(text: str) -> bool:
    url_pattern = r'^(https?://)?([a-z0-9]+([-\.:][a-z0-9]+)*\.[a-z]{2,6})(/[^\s]*)?$'
    return bool(re.match(url_pattern, text))

def remind_functionality(message):
    bot.reply_to(message,
                 """Напоминаю, вы можете продолжить отправлять ссылки, просто отправляя их
в этот чат или запросить случайную сохраненную статью через команду /get_article""")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def bot_start(message):
    bot.reply_to(message, """Привет, я бот который поможет не забыть прочитать статьи, найденные тобой в интернете.
- Чтобы я запомнил статью, достаточно передать мне ссылку на нее, например https://example.com.
- Чтобы получить случайную статью, отправь команду /get_article.
Но помни! Отдавая статью тебе на прочтение, она больше не хранится в моей базе, так что тебе точно нужно ее изучить.""")

@bot.message_handler(commands=['get_article'])
def get_article(message):
    user_id = message.from_user.id
    random_link = get_random_link(user_id)
    if random_link:
        bot.reply_to(message, f"Вы хотели прочитать: \n{random_link} \nСамое время это сделать!")
    else:
        bot.reply_to(message, "Пока что вы не сохранили ни одной ссылки. \nЕсли нашли что-то стоящее, я жду!")
    remind_functionality(message)

@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_id = message.from_user.id
    user_message = message.text

    if not is_link(user_message):
        bot.reply_to(message, "Отправьте ссылку на сайт")
        return

    if is_valid_url(user_message):
        if link_exists(user_id, user_message):
            bot.reply_to(message, "Такая ссылка уже существует.")
        else:
            save_link(user_id, user_message)
            bot.reply_to(message, "Сохранил!")
            remind_functionality(message)
    else:
        bot.reply_to(message, "Это не валидный URL! Пожалуйста, отправьте корректную ссылку.")

if __name__ == '__main__':
    create_db()
    bot.polling(none_stop=True)