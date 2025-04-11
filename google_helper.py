import gspread
from datetime import datetime
from google.oauth2 import service_account

SPREADSHEET_NAME = "LINE_記帳"
SHEET_NAME = "帳目"

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_path = "/etc/secrets/credentials.json"

    print("📁 嘗試讀取 Google 憑證...")
    try:
        creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scope)
        print("✅ 成功讀取 credentials")
    except Exception as e:
        print(f"❌ 無法讀取 credentials: {str(e)}")
        raise

    try:
        client = gspread.authorize(creds)
        print("🔐 成功授權 gspread")
    except Exception as e:
        print(f"❌ gspread 授權失敗: {str(e)}")
        raise

    try:
        sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
        print("📄 成功打開工作表")
        return sheet
    except Exception as e:
        print(f"❌ 無法打開試算表: {str(e)}")
        raise

def append_expense(item, amount, category):
    try:
        sheet = get_sheet()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, item, amount, category])
        print(f"✅ 已寫入：{now}, {item}, {amount}, {category}")
    except Exception as e:
        print(f"❌ 寫入失敗：{str(e)}")

def get_summary():
    try:
        sheet = get_sheet()
        records = sheet.get_all_records()
        total = sum([float(row["金額"]) for row in records])
        recent = records[-3:] if len(records) > 3 else records
        lines = [f"{r['時間']}：{r['品項']} {r['金額']} 元（{r['分類']}）" for r in recent]
        summary = f"💰 總支出：{total} 元\n" + "\n".join(lines)
        return summary
    except Exception as e:
        print(f"❌ 總覽讀取失敗：{str(e)}")
        return "❌ 無法取得總覽資料"

def get_recent_expenses_for_gpt():
    try:
        sheet = get_sheet()
        records = sheet.get_all_records()
        recent = records[-10:] if len(records) >= 10 else records
        return "\n".join([f"{r['時間']}：{r['品項']} {r['金額']} 元（{r['分類']}）" for r in recent])
    except Exception as e:
        print(f"❌ 取得 GPT 資料失敗：{str(e)}")
        return "❌ 無法取得資料給 GPT"
