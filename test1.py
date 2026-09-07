import time
import requests
import yfinance as yf

# 1. 設定你的 Telegram Bot Token 與 Chat ID
token = "8839048485:AAF6sz6zVRvjVcgs9yQnfrUs-e98GNx5eoY"
chat_id = "6066323383"

# 2. 設定你要查詢的股票代號（Yahoo 財經格式：台積電為 2330.TW，水泥股為 1101.TW）
stocks = ["1101.TW", "2330.TW"]

# 3. 迴圈依序取得股價並發送 Telegram 訊息
for stock_id in stocks:
  try:
    # 使用 yfinance 抓取即時資料
    ticker = yf.Ticker(stock_id)
    todays_data = ticker.history(period="1d")

    if not todays_data.empty:
      # 取得今天最新的一筆收盤價或當前價
      price = todays_data["Close"].iloc[-1]
      message = f"股票 {stock_id} 即時股價為 {price:.2f}"
    else:
      message = f"股票 {stock_id} 目前無法取得資料"

  except Exception as e:
    message = f"股票 {stock_id} 查詢發生錯誤: {e}"

  # 發送至 Telegram
  telegram_url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
  requests.get(telegram_url)
  time.sleep(2)
