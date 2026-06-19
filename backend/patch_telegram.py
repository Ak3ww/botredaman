import sys
content = open('C:/BotRedaman/backend/telegram_bot.py', 'r', encoding='utf-8').read()

imports = '''import requests
import sqlite3
import time
import os
import json
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton'''
content = content.replace('import requests\nimport sqlite3\nimport time\nimport os\nimport json', imports)

bot_init = '''TOKEN = _cfg.get("telegram_token", "")
            DASHBOARD_URL = _cfg.get("dashboard_url", "http://127.0.0.1:8000")
    except:
        pass

bot = telebot.TeleBot(TOKEN)'''
content = content.replace('TOKEN = _cfg.get("telegram_token", "")\n            DASHBOARD_URL = _cfg.get("dashboard_url", "http://127.0.0.1:8000")\n    except:\n        pass', bot_init)

old_send = '''def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print(f"Telegram API Error (bot): {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Error send_message: {e}")

def send_message_with_buttons(chat_id, text, buttons):
    """buttons = list of list of {"text": ..., "callback_data": ...}"""
    reply_markup = {"inline_keyboard": buttons}
    send_message(chat_id, text, reply_markup=reply_markup)

def edit_message(chat_id, message_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print(f"Telegram API Error (edit): {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Error edit_message: {e}")

def answer_callback(callback_query_id, text=""):
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass'''

new_send = '''def send_message(chat_id, text, reply_markup=None):
    try:
        markup = None
        if reply_markup and "inline_keyboard" in reply_markup:
            markup = InlineKeyboardMarkup()
            for row in reply_markup["inline_keyboard"]:
                btn_row = []
                for btn in row:
                    url = btn.get("url")
                    cb_data = btn.get("callback_data")
                    btn_row.append(InlineKeyboardButton(text=btn["text"], url=url, callback_data=cb_data))
                markup.row(*btn_row)
        bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)
    except Exception as e:
        logging.error(f"Error send_message: {e}")

def send_message_with_buttons(chat_id, text, buttons):
    reply_markup = {"inline_keyboard": buttons}
    send_message(chat_id, text, reply_markup=reply_markup)

def edit_message(chat_id, message_id, text, reply_markup=None):
    try:
        markup = None
        if reply_markup and "inline_keyboard" in reply_markup:
            markup = InlineKeyboardMarkup()
            for row in reply_markup["inline_keyboard"]:
                btn_row = []
                for btn in row:
                    url = btn.get("url")
                    cb_data = btn.get("callback_data")
                    btn_row.append(InlineKeyboardButton(text=btn["text"], url=url, callback_data=cb_data))
                markup.row(*btn_row)
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)
    except Exception as e:
        logging.error(f"Error edit_message: {e}")

def answer_callback(callback_query_id, text=""):
    try:
        bot.answer_callback_query(callback_query_id, text)
    except:
        pass'''

content = content.replace(old_send, new_send)

old_main = '''def main():
    print("✅ Bot NOC Redaman - Listener aktif...")
    last_update_id = 0

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id}&timeout=30"
            res = requests.get(url, timeout=35).json()

            if res.get("ok"):
                for update in res["result"]:
                    last_update_id = update["update_id"] + 1

                    # Handle pesan teks
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text    = update["message"]["text"]
                        msg_id  = update["message"]["message_id"]
                        if text.startswith("/"):
                            handle_command(chat_id, text, message_id=msg_id)

                    # Handle tombol inline keyboard
                    elif "callback_query" in update:
                        handle_callback(update["callback_query"])

        except Exception as e:
            print("Error polling Telegram:", e)

        time.sleep(1)'''

new_main = '''@bot.message_handler(commands=['start', 'status', 'kritis', 'cari', 'cek', 'set_reminder'])
def bot_handle_command(message):
    handle_command(message.chat.id, message.text, message.message_id)

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/'))
def bot_handle_any_command(message):
    handle_command(message.chat.id, message.text, message.message_id)

@bot.callback_query_handler(func=lambda call: True)
def bot_handle_callback(call):
    callback_query = {
        "id": call.id,
        "message": {"chat": {"id": call.message.chat.id}, "message_id": call.message.message_id},
        "data": call.data
    }
    handle_callback(callback_query)

def main():
    print("✅ Bot NOC Redaman - Listener aktif (Powered by Telebot)...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            logging.error(f"Telebot polling error: {e}")
            time.sleep(5)'''

content = content.replace(old_main, new_main)

with open('C:/BotRedaman/backend/telegram_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patch complete!')
