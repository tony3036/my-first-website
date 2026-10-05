import json
import pandas as pd
from sqlalchemy import create_engine

# ==================== 1. 資料庫連線設定 ====================
# 請將下方的 帳號、密碼、主機位址、port、資料庫名稱 換成你實際的 MySQL 資訊
DB_USER = '你的帳號'
DB_PASSWORD = '你的密碼'
DB_HOST = '你的主機位址'
DB_PORT = '3306'
DB_NAME = '你的資料庫名稱'

# 建立 SQLAlchemy 連線引擎
db_connection_str = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
engine = create_engine(db_connection_str)

# 從資料庫中讀取更新版與原始版兩張資料表
try:
  print('正在從資料庫讀取銷售數據...')
  df_up = pd.read_sql('SELECT * FROM sales_updated_300', con=engine)
  df_orig = pd.read_sql('SELECT * FROM sales_original_300', con=engine)
  print('資料庫讀取成功！')
except Exception as e:
  print(f'資料庫連線或讀取失敗，請檢查連線資訊：{e}')
  # 如果連線失敗，可在此處預設空 DataFrame 避免程式崩潰
  df_up = pd.DataFrame()
  df_orig = pd.DataFrame()


# ==================== 2. 資料處理與清洗函數 ====================
def process_data(df):
  if df.empty:
    return {
        'dates': [],
        'daily_rev': [],
        'products': [],
        'prod_rev': [],
        'categories': [],
        'cat_rev': [],
    }

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

# ==================== 3. 生成互動式網頁 index.html ====================
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
        .chart-box {{ width: 80%; max-width: 700px; margin: 30px auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
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
        <h3>1. 每日淨銷售額折線圖</h3>
        <canvas id="dailyChart"></canvas>
    </div>

    <div class="chart-box">
        <h3>2. 各商品淨銷售額長條圖</h3>
        <canvas id="productChart"></canvas>
    </div>

    <div class="chart-box">
        <h3>3. 各分類淨銷售額占比圓餅圖</h3>
        <canvas id="categoryChart"></canvas>
    </div>

    <script>
        const dataUpdated = {json.dumps(data_updated, ensure_ascii=False)};
        const dataOriginal = {json.dumps(data_original, ensure_ascii=False)};

        let currentData = dataUpdated;

        // 初始化圖表
        const ctxDaily = document.getElementById('dailyChart').getContext('2d');
        const ctxProduct = document.getElementById('productChart').getContext('2d');
        const ctxCategory = document.getElementById('categoryChart').getContext('2d');

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

        let categoryChart = new Chart(ctxCategory, {{
            type: 'pie',
            data: {{
                labels: currentData.categories,
                datasets: [{{
                    data: currentData.cat_rev,
                    backgroundColor: ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
                }}]
            }}
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

            // 更新折線圖
            dailyChart.data.labels = currentData.dates;
            dailyChart.data.datasets[0].data = currentData.daily_rev;
            dailyChart.update();

            // 更新長條圖
            productChart.data.labels = currentData.products;
            productChart.data.datasets[0].data = currentData.prod_rev;
            productChart.update();

            // 更新圓餅圖
            categoryChart.data.labels = currentData.categories;
            categoryChart.data.datasets[0].data = currentData.cat_rev;
            categoryChart.update();
        }}
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
  f.write(html_content)

print('已成功從資料庫讀取資料，並產出帶有互動按鈕與三大圖表的 index.html！')
