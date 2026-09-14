import os
import requests

# 從環境變數安全讀取 Telegram 憑證，不寫死在程式碼中
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def check_rain_probability():
  # Open-Meteo API 設定（以桃園市八德區為例，可自行修改經緯度）
  url = "https://api.open-meteo.com/v1/forecast"
  params = {
      "latitude": 24.9387,
      "longitude": 121.2917,
      "daily": "precipitation_probability_max",
      "timezone": "auto",
  }

  try:
    response = requests.get(url, params=params)
    data = response.json()

    # 取得今天（陣列第一筆索引 [0]）的最高降雨機率
    max_prob = data["daily"]["precipitation_probability_max"][0]
    print(f"今日最高降雨機率: {max_prob}%")

    # 判斷是否超過 70%（可依需求調整為 60）
    if max_prob is not None and max_prob > 70:
      message = (
          f"☔️ 天氣提醒：今天下雨機率高達 {max_prob}%！出門記得帶傘喔！"
      )
      send_telegram_message(message)
    else:
      print("今天降雨機率未超過設定門檻，不需發送通知。")

  except Exception as e:
    print(f"獲取天氣資訊發生錯誤: {e}")


def send_telegram_message(message):
  if not TOKEN or not CHAT_ID:
    print("錯誤：未設定 Telegram Token 或 Chat ID 環境變數。")
    return

  telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message}
  response = requests.post(telegram_url, data=payload)
  if response.status_code == 200:
    print("Telegram 通知發送成功！")
  else:
    print(f"Telegram 通知發送失敗: {response.text}")


if __name__ == "__main__":
  check_rain_probability()
