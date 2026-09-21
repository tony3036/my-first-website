import os
import requests

# 依照規範：透過環境變數安全讀取 Telegram Token 與 Chat ID，不直接寫入程式碼
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def get_commute_advice():
  # 設定地點經緯度（以桃園市為例）
  lat = 24.9937
  lon = 121.3010

  # 1. 取得天氣資料 (Open-Meteo Weather API)
  weather_url = "https://api.open-meteo.com/v1/forecast"
  weather_params = {
      "latitude": lat,
      "longitude": lon,
      "daily": "temperature_2m_max,precipitation_probability_max",
      "timezone": "auto",
  }

  # 2. 取得空氣品質資料 (Open-Meteo Air Quality API)
  aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
  aqi_params = {
      "latitude": lat,
      "longitude": lon,
      "current": "us_aqi",
  }

  try:
    # 發送天氣請求並檢查 HTTP 狀態碼
    weather_res = requests.get(weather_url, params=weather_params)
    if weather_res.status_code != 200:
      send_telegram_message(
          f"⚠️ 系統錯誤：無法取得天氣資料 (HTTP {weather_res.status_code})"
      )
      return

    weather_data = weather_res.json()
    max_temp = weather_data["daily"]["temperature_2m_max"][0]
    max_rain_prob = weather_data["daily"]["precipitation_probability_max"][0]

    # 發送空氣品質請求並檢查 HTTP 狀態碼
    aqi_res = requests.get(aqi_url, params=aqi_params)
    if aqi_res.status_code != 200:
      send_telegram_message(
          f"⚠️ 系統錯誤：無法取得空氣品質資料 (HTTP {aqi_res.status_code})"
      )
      return

    aqi_data = aqi_res.json()
    current_aqi = aqi_data["current"]["us_aqi"]

    print(
        f"數據取得成功 -> 最高溫: {max_temp}°C, 降雨機率: {max_rain_prob}%,"
        f" AQI: {current_aqi}"
    )

    # 組合基本資訊內容
    msg_lines = [
        "🏙️ 【智慧通勤風險通知】",
        f"🌡️ 今日最高溫：{max_temp}°C",
        f"☔️ 最高降雨機率：{max_rain_prob}%",
        f" AQI 空氣品質指數：{current_aqi}",
        "---------------------",
        "💡 通勤建議：",
    ]

    # 使用多個 if 條件產生同時成立的通勤建議
    has_advice = False

    # 降雨機率達 60% 時提醒攜帶雨傘
    if max_rain_prob is not None and max_rain_prob >= 60:
      msg_lines.append(
          f"• 降雨機率達 {max_rain_prob}%，出門記得攜帶雨傘！🌂"
      )
      has_advice = True

    # 最高溫度達 33°C 時提醒防曬與補充水分
    if max_temp is not None and max_temp >= 33:
      msg_lines.append(f"• 氣溫高達 {max_temp}°C，請注意防曬與補充水分！☀️💦")
      has_advice = True

    # AQI 達 100 時提醒佩戴口罩
    if current_aqi is not None and current_aqi >= 100:
      msg_lines.append(f"• AQI 達 {current_aqi}（不良），建議外出佩戴口罩！😷")
      has_advice = True

    # 所有條件正常時，顯示適合外出通勤
    if not has_advice:
      msg_lines.append("• 天氣晴朗舒適，非常適合外出通勤！✨")

    final_message = "\n".join(msg_lines)
    send_telegram_message(final_message)

  except Exception as e:
    error_msg = f"⚠️ 系統執行發生例外錯誤: {e}"
    print(error_msg)
    send_telegram_message(error_msg)


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
  get_commute_advice()
