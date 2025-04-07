import os
import threading
from flask import Flask, request, jsonify
import requests
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from google_helper import append_expense, get_summary

app = Flask(__name__)

# 環境變數
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def home():
    return "記帳 LINE Bot 啟動中"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        events = parser.parse(body, signature)
    except:
        return "Invalid signature", 400

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            user_id = event.source.user_id
            user_text = event.message.text.strip()

            reply_text = handle_user_message(user_text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )

    return jsonify({"status": "ok"})

def handle_user_message(msg):
    if msg.lower() in ["餘額", "查帳", "總覽"]:
        return get_summary()

    try:
        parts = msg.split()
        if len(parts) == 2:
            item, amount = parts[0], float(parts[1])
            append_expense(item, amount)
            return f"已記錄：{item} {amount} 元"
    except:
        return "❗格式錯誤，請用『品項 金額』格式，例如：早餐 50"

    return "請輸入記帳格式：餐點 金額，例如『午餐 100』或輸入『餘額』查詢總支出"

if __name__ == "__main__":
    app.run(port=5000)
