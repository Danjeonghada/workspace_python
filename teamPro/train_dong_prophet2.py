import pandas as pd
from prophet import Prophet
from tqdm import tqdm

# [1] 데이터 불러오기
df = pd.read_excel("동별세대당전기요금.xlsx")

# [2] Prophet 결과 저장용 DataFrame
prophet_preds = pd.DataFrame()

# [3] dong 리스트 추출
dong_list = df['dong'].unique()

# [4] 동별 Prophet 모델 생성 및 예측
for dong in tqdm(dong_list):
    df_dong = df[df['dong'] == dong][['year', 'month', 'final_monthly_fee']].copy()
    df_dong['ds'] = pd.to_datetime(df_dong[['year', 'month']].assign(day=1))
    df_dong['y'] = df_dong['final_monthly_fee']

    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    model.fit(df_dong[['ds', 'y']])

    # 향후 12개월 예측 (마지막 날짜 기준 12개월)
    future = model.make_future_dataframe(periods=12, freq='MS')
    forecast = model.predict(future)

    forecast_result = forecast[['ds', 'yhat']].copy()
    forecast_result['dong'] = dong

    # year, month 컬럼 분해
    forecast_result['year'] = forecast_result['ds'].dt.year
    forecast_result['month'] = forecast_result['ds'].dt.month
    forecast_result.rename(columns={'yhat': 'prophet_pred'}, inplace=True)

    prophet_preds = pd.concat([prophet_preds, forecast_result[['dong', 'year', 'month', 'prophet_pred']]])

# [5] Prophet 예측 결과 저장 (선택사항)
prophet_preds.to_csv("prophet_predictions.csv", index=False)

# [6] (선택) 원래 데이터와 병합해서 XGBoost/LGBM 학습에 활용 가능
df = df.merge(prophet_preds, on=["dong", "year", "month"], how="left")
