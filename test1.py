import time
import requests
from bs4 import BeautifulSoup

# 1. 設定你的 Telegram Bot Token 與 Chat ID
token = "8839048485:AAF6sz6zVRvjVcgs9yQnfrUs-e98GNx5eoY"
chat_id = "6066323383"

# --- 【強制測試】先發送一則訊息，確認 Telegram 通訊正常 ---
test_url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text=GitHub_Bot測試連線成功！"
requests.get(test_url)

# 2. 設定你要爬取的股票代號列表
stock = ["1101", "2330"]

# 3. 迴圈依序爬取股價並發送 Telegram 訊息
for i in range(len(stock)):
  stockid = stock[i]
  url = f"https://tw.stock.yahoo.com/quote/{stockid}.TW"

  r = requests.get(url)
  soup = BeautifulSoup(r.text, "html.parser")

  price_tag = soup.find(
      "span",
      class_=[
          "Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-down)",
          "Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c)",
          "Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-up)",
      ],
  )

  if price_tag:
    price = price_tag.getText()
    message = f"股票 {stockid} 即時股價為 {price}"
  else:
    message = f"股票 {stockid} 抓取不到股價標籤（爬蟲需調整）"

  telegram_url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
  requests.get(telegram_url)
  time.sleep(3)
