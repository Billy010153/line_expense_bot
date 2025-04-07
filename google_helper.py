import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

SPREADSHEET_NAME = "LINE_記帳"
SHEET_NAME = "帳目"

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet

def append_expense(item, amount):
    sheet = get_sheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, item, amount])

def get_summary():
    sheet = get_sheet()
    records = sheet.get_all_records()
    total = sum([float(row['金額']) for row in records])
    recent = records[-3:] if len(records) >= 3 else records
    lines = [f"{r['時間']} - {r['品項']} {r['金額']} 元" for r in recent]
    summary = f"💰 總支出：{total} 元\n" + "\n".join(lines)
    return summary
