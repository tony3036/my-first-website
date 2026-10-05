import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd


# 自動尋找系統內建的中文字型 (支援 Ubuntu / Windows / macOS)
def get_chinese_font():
  for f in fm.fontManager.ttflist:
    name = f.name.lower()
    if any(
        k in name
        for k in ['noto sans cjk', 'microsoft jhenghei', 'wqy', 'hei', 'kai']
    ):
      return f.name
  return 'sans-serif'


chosen_font = get_chinese_font()
plt.rcParams['font.family'] = chosen_font
plt.rcParams['axes.unicode_minus'] = False

print(f'已自動套用中文字型: {chosen_font}')
print('正在自動生成 2026年9月 模擬銷售資料...')

# 1. 自動建立 300 筆模擬銷售資料
np.random.seed(42)
dates = pd.date_range(start='2026-09-01', end='2026-09-30')
channels = ['線上官網', '實體門市', '經銷通路']
categories = ['3C家電', '生活用品', '服飾配件']

products = [
    ('P001', '智慧型手機', '3C家電', 15000),
    ('P002', '藍牙耳機', '3C家電', 3000),
    ('P003', '行動電源', '3C家電', 1000),
    ('P004', '環保保溫瓶', '生活用品', 800),
    ('P005', '多功能收納箱', '生活用品', 600),
    ('P006', '香氛精油燈', '生活用品', 1200),
    ('P007', '純棉休閒T恤', '服飾配件', 500),
    ('P008', '防風防水外套', '服飾配件', 2000),
    ('P009', '簡約帆布背包', '服飾配件', 900),
    ('P010', '運動壓力襪', '服飾配件', 350),
]

data = []
sale_id_counter = 1

for day in range(30):
  current_date = dates[day].strftime('%Y-%m-%d')
  for p in products:
    p_id, p_name, cat, price = p
    qty = np.random.randint(10, 25)
    ret = np.random.randint(0, 3)

    if p_id in ['P001', 'P002', 'P003']:
      qty += 8
    if p_id in ['P007', 'P008', 'P009', 'P010']:
      qty += 3
    if p_id == 'P002':
      ret += 1

    data.append({
        'sale_id': f'S{sale_id_counter:04d}',
        'sale_date': current_date,
        'product_id': p_id,
        'product_name': p_name,
        'category': cat,
        'channel': np.random.choice(channels),
        'unit_price': price,
        'quantity': qty,
        'returned_quantity': ret,
    })
  sale_id_counter += 1

df = pd.DataFrame(data)
df['net_revenue'] = df['unit_price'] * (df['quantity'] - df['returned_quantity'])

# 匯出 CSV 檔案
df.to_csv('sales_updated_300.csv', index=False, encoding='utf-8-sig')

# 2. 開始繪製並儲存圖表
daily_rev = df.groupby('sale_date')['net_revenue'].sum()
plt.figure(figsize=(10, 5))
plt.plot(daily_rev.index, daily_rev.values, marker='o', color='b', linewidth=2)
plt.title('2026年9月 每日淨銷售額', fontsize=14)
plt.xlabel('日期')
plt.ylabel('淨銷售額 (NTD)')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('daily_revenue.png', dpi=300)
plt.close()

product_rev = (
    df.groupby('product_name')['net_revenue'].sum().sort_values(ascending=True)
)
plt.figure(figsize=(10, 5))
product_rev.plot(kind='barh', color='teal')
plt.title('各商品淨銷售額分析', fontsize=14)
plt.xlabel('淨銷售額 (NTD)')
plt.ylabel('商品名稱')
plt.tight_layout()
plt.savefig('product_revenue.png', dpi=300)
plt.close()

category_rev = df.groupby('category')['net_revenue'].sum()
plt.figure(figsize=(6, 6))
plt.pie(
    category_rev.values,
    labels=category_rev.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=['#ff9999', '#66b3ff', '#99ff99'],
)
plt.title('各分類淨銷售額占比', fontsize=14)
plt.tight_layout()
plt.savefig('category_share.png', dpi=300)
plt.close()

print('所有圖表與 CSV 檔案已成功自動生成並儲存！')
