import time
import requests
from bs4 import BeautifulSoup

# 1. 設定你要爬取的股票代號列表
stock = ["1101", "2330"]

# 2. 設定你的 Telegram Bot Token 與 Chat ID
token = "8839048485:AAF6sz6zVRvjVcgs9yQnfrUs-e98GNx5eoY"
chat_id = "6066323383"

# 3. 迴圈依序爬取股價並發送 Telegram 訊息
for i in range(len(stock)):
  # 取得目前的股票代號
  stockid = stock[i]

  # 將股票代號代入 Yahoo 股市網址
  url = f"https://tw.stock.yahoo.com/quote/{stockid}.TW"

  # 發送 HTTP 請求
  r = requests.get(url)

  # 解析回應的 HTML
  soup = BeautifulSoup(r.text, "html.parser")

  # 定位股價所在的 HTML 標籤
  price_tag = soup.find(
      "span",
      class_=[
          "Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-down)",
          "Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c)",
          "Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-up)",
      ],
  )

  # 確保有成功抓到股價文字
  if price_tag:
    price = price_tag.getText()

    # 組合回報訊息
    message = f"股票 {stockid} 即時股價為 {price}"

    # 發送訊息至 Telegram
    telegram_url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(telegram_url)

  # 每次發送完暫停 3 秒，避免請求過快
  time.sleep(3)
