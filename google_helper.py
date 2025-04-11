
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file('/etc/secrets/credentials.json')

SPREADSHEET_NAME = "LINE_記帳"
SHEET_NAME = "帳目"
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_path = "/etc/secrets/credentials.json"
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet

def append_expense(item, amount, category):
    sheet = get_sheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, item, amount, category])

def get_summary():
    sheet = get_sheet()
    records = sheet.get_all_records()
    total = sum(float(row['金額']) for row in records)
    recent = records[-3:] if len(records) >= 3 else records
    lines = [f"{r['時間']}：{r['品項']} {r['金額']} 元（{r['分類']}）" for r in recent]
    return f"💰 總支出：{total:.0f} 元
" + "
".join(lines)

def get_recent_expenses_for_gpt():
    sheet = get_sheet()
    records = sheet.get_all_records()
    recent = records[-10:] if len(records) >= 10 else records
    return "\n".join(
        [f"{r['時間']}：{r['品項']} {r['金額']} 元（{r['分類']}）" for r in recent]
    )
