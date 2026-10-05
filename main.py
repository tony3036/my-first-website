import json
import os
import pandas as pd

# 讀取兩個檔案的資料（確保專案內同時有這兩個 CSV）
file_updated = (
    'sales_updated_300.csv'
    if os.path.exists('sales_updated_300.csv')
    else 'sales_original_300.csv'
)
file_original = (
    'sales_original_300.csv'
    if os.path.exists('sales_original_300.csv')
    else 'sales_updated_300.csv'
)

df_up = pd.read_csv(file_updated)
df_orig = pd.read_csv(file_original)


# 處理資料的函數
def process_data(df):
  if 'net_revenue' not in df.columns:
    if 'unit_price' in df.columns and 'quantity' in df.columns:
      returned = (
          df['returned_quantity'] if 'returned_quantity' in df.columns else 0
      )
      df['net_revenue'] = df['unit_price'] * (df['quantity'] - returned)
    else:
      df['net_revenue'] = df.iloc[:, -1]

  # 1. 每日銷售額
  daily = df.groupby('sale_date')['net_revenue'].sum().reset_index()
  # 2. 商品銷售額
  prod = df.groupby('product_name')['net_revenue'].sum().reset_index()
  # 3. 分類占比
  cat = df.groupby('category')['net_revenue'].sum().reset_index()

  return {
      'dates': daily['sale_date'].tolist(),
      'daily_rev': daily['net_revenue'].tolist(),
      'products': prod['product_name'].tolist(),
      'prod_rev': prod['net_revenue'].tolist(),
      'categories': cat['category'].tolist(),
      'cat_rev': cat['net_revenue'].tolist(),
  }


data_updated = process_data(df_up)
data_original = process_data(df_orig)

# 產出包含切換按鈕與 JavaScript 動態圖表的 HTML
html_content = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>銷售數據動態切換儀表板</title>
    <!-- 引入 Chart.js 互動圖表庫 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f4f7f6; color: #333; text-align: center; }}
        h1 {{ color: #2c3e50; }}
        .btn-container {{ margin: 20px 0; }}
        button {{ background-color: #3498db; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; margin: 0 5px; transition: 0.3s; }}
        button:hover {{ background-color: #2980b9; }}
        button.active {{ background-color: #e67e22; }}
        .badge {{ background-color: #2ecc71; color: white; padding: 6px 12px; border-radius: 4px; font-size: 14px; }}
        .chart-box {{ width: 80%; max-width: 800px; margin: 30px auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h1>銷售數據分析儀表板</h1>
    <p>目前展示資料來源：<span id="currentSource" class="badge">更新版銷售數據 (sales_updated_300)</span></p>
    
    <div class="btn-container">
        <button id="btnUpdated" class="active" onclick="switchData('updated')">切換至更新版數據</button>
        <button id="btnOriginal" onclick="switchData('original')">切換至原始版數據</button>
    </div>

    <div class="chart-box">
        <h3>每日淨銷售額折線圖</h3>
        <canvas id="dailyChart"></canvas>
    </div>

    <div class="chart-box">
        <h3>各商品淨銷售額長條圖</h3>
        <canvas id="productChart"></canvas>
    </div>

    <script>
        const dataUpdated = {json.dumps(data_updated, ensure_ascii=False)};
        const dataOriginal = {json.dumps(data_original, ensure_ascii=False)};

        let currentData = dataUpdated;

        // 初始化圖表
        const ctxDaily = document.getElementById('dailyChart').getContext('2d');
        const ctxProduct = document.getElementById('productChart').getContext('2d');

        let dailyChart = new Chart(ctxDaily, {{
            type: 'line',
            data: {{
                labels: currentData.dates,
                datasets: [{{
                    label: '淨銷售額 (NTD)',
                    data: currentData.daily_rev,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.1
                }}]
            }}
        }});

        let productChart = new Chart(ctxProduct, {{
            type: 'bar',
            data: {{
                labels: currentData.products,
                datasets: [{{
                    label: '淨銷售額 (NTD)',
                    data: currentData.prod_rev,
                    backgroundColor: '#1abc9c'
                }}]
            }},
            options: {{ indexAxis: 'y' }}
        }});

        function switchData(type) {{
            const sourceSpan = document.getElementById('currentSource');
            const btnUpdated = document.getElementById('btnUpdated');
            const btnOriginal = document.getElementById('btnOriginal');

            if (type === 'updated') {{
                currentData = dataUpdated;
                sourceSpan.innerText = "更新版銷售數據 (sales_updated_300)";
                btnUpdated.classList.add('active');
                btnOriginal.classList.remove('active');
            }} else {{
                currentData = dataOriginal;
                sourceSpan.innerText = "原始版銷售數據 (sales_original_300)";
                btnOriginal.classList.add('active');
                btnUpdated.classList.remove('active');
            }}

            // 更新折線圖資料
            dailyChart.data.labels = currentData.dates;
            dailyChart.data.datasets[0].data = currentData.daily_rev;
            dailyChart.update();

            // 更新長條圖資料
            productChart.data.labels = currentData.products;
            productChart.data.datasets[0].data = currentData.prod_rev;
            productChart.update();
        }}
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
  f.write(html_content)

print('已成功生成具備互動切換按鈕的 index.html 網頁！')
