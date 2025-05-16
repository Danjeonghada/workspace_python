import pandas as pd
import numpy as np
from datetime import datetime
import cx_Oracle
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from xgboost import XGBRegressor

# ✅ 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def predict_future_by_last_12months(dong_name: str):
    conn = cx_Oracle.connect("kwj", "kwj", "192.168.0.44:1521/xe")

    query = """
    SELECT f.YEAR, f.MONTH, (f.PUBLIC_FEE + f.PRIVATE_FEE) AS TOTAL_FEE
    FROM ELECTRICITY_FEE f
    JOIN APARTMENTS a ON f.KAPT_CODE = a.KAPT_CODE
    WHERE a.DONG = :dong
    """
    df = pd.read_sql(query, conn, params={'dong': dong_name})
    conn.close()

    if df.empty:
        print(f"[오류] '{dong_name}' 에 해당하는 데이터가 없습니다.")
        return

    df['DATE'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str))
    df = df.sort_values('DATE')

    ts = df.groupby('DATE')['TOTAL_FEE'].sum().reset_index()
    ts_values = ts['TOTAL_FEE'].values

    window_size = 12
    X, y = [], []
    for i in range(len(ts_values) - window_size):
        X.append(ts_values[i:i + window_size])
        y.append(ts_values[i + window_size])

    if len(X) < 1:
        print(f"[오류] '{dong_name}'의 데이터가 13개월 미만이라 예측할 수 없습니다.")
        return

    model = XGBRegressor(n_estimators=100, learning_rate=0.1)
    model.fit(X, y)

    input_values = ts_values[-12:].tolist()
    future_preds = []

    for _ in range(12):
        input_X = np.array(input_values[-12:]).reshape(1, -1)
        pred = model.predict(input_X)[0]
        future_preds.append(pred)
        input_values.append(pred)

    last_date = ts['DATE'].max()
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=12, freq='MS')
    future_df = pd.DataFrame({'DATE': future_dates, 'PREDICTED_TOTAL_FEE': future_preds})

    plt.figure(figsize=(12, 5))
    plt.plot(ts['DATE'], ts['TOTAL_FEE'], label='기존 전기요금')
    plt.plot(future_df['DATE'], future_df['PREDICTED_TOTAL_FEE'], label='예측 전기요금 (향후 12개월)', linestyle='--')
    plt.title(f'{dong_name} 월별 전기요금 예측')
    plt.xlabel('날짜')
    plt.ylabel('전기요금(원)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return future_df

# 🔽 실행
dong_name = input("예측할 동 이름을 입력하세요 (예: 둔산동): ")
future_df = predict_future_by_last_12months(dong_name)

# 예측 결과 출력 (예측 성공한 경우만)
if future_df is not None:
    print("\n📊 향후 12개월 예측 전기요금:")
    print(future_df.rename(columns={'DATE': '예측월', 'PREDICTED_TOTAL_FEE': '예측 전기요금 (원)'}).to_string(index=False, formatters={
        '예측 전기요금 (원)': lambda x: f"{int(x):,}"  # 천 단위 콤마
    }))
