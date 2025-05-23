import pandas as pd
from prophet import Prophet
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
import joblib
from tqdm import tqdm
import os

# [1] 엑셀 파일 로딩
filename = "대전_전력사용량_2014_2024.xlsx"
filepath = os.path.join(os.path.dirname(__file__), filename)

if not os.path.exists(filepath):
    raise FileNotFoundError(f"[❌ 파일 없음] '{filepath}' 경로를 확인해주세요.")

df = pd.read_excel(filepath)

# [2] 컬럼명 정리 및 변환
df.columns = df.columns.str.strip()
df.rename(columns={'district': 'dong', 'powerUsage': 'usage'}, inplace=True)

# Prophet용 날짜 컬럼 생성
df['ds'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

# [3] Prophet 예측 수행
prophet_preds = pd.DataFrame()
dong_list = df['dong'].unique()

print("📊 Prophet 예측 시작...")
for dong in tqdm(dong_list):
    df_dong = df[df['dong'] == dong][['ds', 'usage']].copy()
    df_dong = df_dong.rename(columns={'usage': 'y'})

    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    model.fit(df_dong)

    future = model.make_future_dataframe(periods=12, freq='MS')  # 2년 예측
    forecast = model.predict(future)

    forecast_result = forecast[['ds', 'yhat']].copy()
    forecast_result['dong'] = dong
    forecast_result['year'] = forecast_result['ds'].dt.year
    forecast_result['month'] = forecast_result['ds'].dt.month
    forecast_result.rename(columns={'yhat': 'prophet_pred'}, inplace=True)

    prophet_preds = pd.concat([prophet_preds, forecast_result[['dong', 'year', 'month', 'prophet_pred']]])

print("✅ Prophet 예측 완료")

# [4] Prophet 결과 병합
df_all = df.merge(prophet_preds, on=["dong", "year", "month"], how="outer")

# [5] XGBoost 학습 데이터 구성
features = df_all[['dong', 'year', 'month', 'prophet_pred']].copy()
features = pd.get_dummies(features, columns=['dong'])
target = df_all['usage']

# [6] 결측값 제거 후 분할
train_data = pd.concat([features, target], axis=1)
train_data = train_data.dropna(subset=['usage', 'prophet_pred'])

X = train_data.drop(columns=['usage'])
y = train_data['usage']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


print("📈 XGBoost 학습 시작...")
xgb_model = XGBRegressor(n_estimators=300, learning_rate=0.1, random_state=42)
xgb_model.fit(X_train, y_train)
print("✅ XGBoost 학습 완료")

# [7] 예측 결과 저장
df_all = df_all.dropna(subset=['prophet_pred'])  # 예측 가능한 행만 추림
X_all = pd.get_dummies(df_all[['dong', 'year', 'month', 'prophet_pred']], columns=['dong'])
df_all['xgb_pred'] = xgb_model.predict(X_all)

df_all.to_csv("district_forecast_result.csv", index=False)
joblib.dump(xgb_model, "district_xgb_model.pkl")
print("💾 예측 결과 저장 완료: district_forecast_result.csv")
print("💾 모델 저장 완료: district_xgb_model.pkl")
