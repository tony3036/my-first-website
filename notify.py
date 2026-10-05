import os
import requests


def send_telegram_message(message):
  """發送 Telegram 訊息的共用函式"""
  # 從環境變數中讀取 Token 與 Chat ID（這些會安全地存在 GitHub Secrets 中）
  token = os.environ.get('TELEGRAM_BOT_TOKEN')
  chat_id = os.environ.get('TELEGRAM_CHAT_ID')

  if not token or not chat_id:
    print('錯誤：未設定 Telegram Token 或 Chat ID 環境變數！')
    return

  url = f'https://api.telegram.org/bot{token}/sendMessage'
  payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}

  try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
      print('Telegram 訊息發送成功！')
    else:
      print(f'發送失敗，錯誤代碼：{response.status_code}, 內容：{response.text}')
  except Exception as e:
    print(f'連線發生例外錯誤：{e}')
