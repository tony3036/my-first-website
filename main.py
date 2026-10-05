import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd

# 自動尋找系統內建的中文字型，避免中文亂碼
chosen_font = 'sans-serif'
for f in fm.fontManager.ttflist:
  name = f.name.lower()
  if any(
      k in name
      for k in ['noto sans cjk', 'microsoft jhenghei', 'wqy', 'hei', 'kai']
  ):
    chosen_font = f.name
    break

plt.rcParams['font.family'] = chosen_font
plt.rcParams['axes.unicode_minus'] = False

# 自動動態偵測輸入的檔案是哪一個
if os.path.exists('sales_updated_300.csv'):
  target_file = 'sales_updated_300.csv'
  dataset_label = '更新版銷售數據 (sales_updated_300)'
elif os.path.exists('sales_original_300.csv'):
  target_file = 'sales_original_300.csv'
  dataset_label = '原始版銷售數據 (sales_original_300)'
else:
  target_file = 'sales_updated_300.csv'
  dataset_label = '更新版銷售數據 (sales_updated_300)'

print(f'正在讀取輸入檔案: {target_file} 進行動態圖表繪製...')
df = pd.read_csv(target_file)

# 確保淨營收欄位存在
if 'net_revenue' not in df.columns:
  if 'unit_price' in df.columns and 'quantity' in df.columns:
    returned = df['returned_quantity'] if 'returned_quantity' in df.columns else 0
    df['net_revenue'] = df['unit_price'] * (df['quantity'] - returned)
  else:
    df['net_revenue'] = df.iloc[:, -1]

# 1. 繪製並儲存每日淨銷售額折線圖
daily_rev = df.groupby('sale_date')['net_revenue'].sum()
plt.figure(figsize=(10, 4))
plt.plot(daily_rev.index, daily_rev.values, marker='o', color='b', linewidth=2)
plt.title(f'每日淨銷售額折線圖 ({dataset_label})', fontsize=12)
plt.xlabel('日期')
plt.ylabel('淨銷售額 (NTD)')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('chart_1_daily_revenue.png', dpi=300)
plt.close()

# 2. 繪製並儲存各商品淨銷售額長條圖
product_rev = (
    df.groupby('product_name')['net_revenue'].sum().sort_values(ascending=True)
)
plt.figure(figsize=(10, 4))
product_rev.plot(kind='barh', color='teal')
plt.title(f'各商品淨銷售額長條圖 ({dataset_label})', fontsize=12)
plt.xlabel('淨銷售額 (NTD)')
plt.ylabel('商品名稱')
plt.tight_layout()
plt.savefig('chart_2_product_revenue.png', dpi=300)
plt.close()

# 3. 繪製並儲存各分類淨銷售額占比圓餅圖
category_rev = df.groupby('category')['net_revenue'].sum()
plt.figure(figsize=(6, 6))
plt.pie(
    category_rev.values,
    labels=category_rev.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=['#ff9999', '#66b3ff', '#99ff99'],
)
plt.title(f'各分類淨銷售額占比圓餅圖 ({dataset_label})', fontsize=12)
plt.tight_layout()
plt.savefig('chart_3_category_share.png', dpi=300)
plt.close()

# 自動生成 index.html 網頁
html_content = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>銷售數據分析儀表板</title>
    <style>
        body {{ font-family: '{chosen_font}', Arial, sans-serif; margin: 40px; background-color: #f9f9f9; color: #333; text-align: center; }}
        h1 {{ color: #2c3e50; }}
        .badge {{ background-color: #3498db; color: white; padding: 6px 12px; border-radius: 4px; font-size: 14px; }}
        .chart-container {{ margin: 30px auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; }}
        img {{ max-width: 100%; height: auto; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>銷售數據分析儀表板</h1>
    <p>目前展示資料來源：<span class="badge">{dataset_label}</span></p>
    <p>提示：按下 F5 重新整理即可載入最新圖表。</p>
    
    <div class="chart-container">
        <h3>1. 每日淨銷售額折線圖</h3>
        <img src="chart_1_daily_revenue.png" alt="每日淨銷售額">
    </div>
    <div class="chart-container">
        <h3>2. 各商品淨銷售額長條圖</h3>
        <img src="chart_2_product_revenue.png" alt="各商品淨銷售額">
    </div>
    <div class="chart-container">
        <h3>3. 各分類淨銷售額占比圓餅圖</h3>
        <img src="chart_3_category_share.png" alt="各分類淨銷售額占比">
    </div>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
  f.write(html_content)

print('圖表與 index.html 網頁已成功根據輸入檔案動態更新！')
