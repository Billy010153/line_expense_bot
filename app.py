import os
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from google_helper import append_expense, get_summary, get_recent_expenses_for_gpt
from openai import OpenAI

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "記帳 + GPT 自動分類啟動中"

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
            user_text = event.message.text.strip()
            reply_text = handle_user_message(user_text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )

    return jsonify({"status": "ok"})

def auto_classify_item(item_name):
    prompt = f"請幫我判斷「{item_name}」屬於哪一類消費，只回傳分類名稱，不要多餘文字。分類例如：餐飲、交通、娛樂、日用品、收入、其他。"
    messages = [
        {"role": "system", "content": "你是一個記帳機器人，擅長幫使用者標記分類"},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content.strip()

def handle_user_message(msg):
    if msg.lower() in ["餘額", "查帳", "總覽"]:
        return get_summary()
    elif msg.startswith("/ai"):
        question = msg.replace("/ai", "").strip()
        if not question:
            return "請輸入問題，例如：/ai 我這週花了多少錢？"
        try:
            data = get_recent_expenses_for_gpt()
            messages = [
                {"role": "system", "content": "你是一位記帳分析師，請根據使用者最近的支出資料，以親切自然的語氣回答問題。"},
                {"role": "user", "content": f"這是最近的記帳紀錄：\n{data}\n\n{question}"}
            ]
            response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"❗ GPT 查詢錯誤：{str(e)}"

    try:
        parts = msg.split()
        amount = float(parts[-1])
        item = " ".join(parts[:-1])
        category = auto_classify_item(item)
        append_expense(item, amount, category)
        return f"✅ 已記錄：{item} {amount} 元（分類：{category}）"
    except Exception as e:
        return f"❗ 格式錯誤，請用『品項 金額』格式，例如：早餐 50\n或錯誤：{str(e)}"

if __name__ == "__main__":
    app.run(port=5000)
